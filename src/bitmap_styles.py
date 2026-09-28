"""Archived 16x16 bitmap experiment, available with --design bitmap.

Each original 8x16 source pixel occupies two horizontal strike pixels.  That
extra resolution allows a half-source-pixel increase in weight. Coordinates
x=0..15 are the nominal cell; italic ink may overhang. All decisions happen
before TrueType outlines are made. The original ROM bytes are never rewritten.
"""

from __future__ import annotations

from typing import Sequence

Bitmap = tuple[frozenset[int], ...]


def from_rom(rows: Sequence[int]) -> Bitmap:
    return tuple(frozenset(2 * x + dx for x in range(8) if row & (1 << (7 - x)) for dx in (0, 1)) for row in rows)


def to_rom(glyph: Bitmap) -> list[int]:
    """Lossless ROM export of Regular's doubled pixels."""
    if len(glyph) != 16 or any(x < 0 or x > 15 for row in glyph for x in row):
        raise ValueError("glyph has overhang or is not 16x16")
    if any(((2*x in row) != (2*x+1 in row)) for row in glyph for x in range(8)):
        raise ValueError("glyph is not an unmodified 8x16 ROM bitmap")
    return [sum(1 << (7-x) for x in range(8) if 2*x in row) for row in glyph]


def _runs(row: frozenset[int]) -> list[tuple[int, int]]:
    if not row:
        return []
    xs = sorted(row)
    runs = []
    start = prev = xs[0]
    for x in xs[1:]:
        if x != prev + 1:
            runs.append((start, prev))
            start = x
        prev = x
    runs.append((start, prev))
    return runs


def bold_strike(glyph: Bitmap) -> Bitmap:
    """Add whole, selected pixels while preserving at least one-pixel counters.

    This is a starter strike; authored CORRECTIONS below take priority.
    Narrow stems grow by one *fine* pixel. Opposite stems may both grow only
    when the gap is sufficiently open; tight counters retain their space.
    """
    out = []
    for row in glyph:
        runs = _runs(row)
        pixels = set(row)
        if len(runs) == 1:
            lo, hi = runs[0]
            if hi - lo < 14:
                candidates = ([lo - 1, hi + 1] if (lo + hi) >= 15 else [hi + 1, lo - 1])
                for x in candidates:
                    if 0 <= x < 16 and x not in row:
                        pixels.add(x)
                        break
        else:
            for i, (lo, hi) in enumerate(runs):
                if hi - lo >= 7:
                    continue
                left_gap = lo - runs[i - 1][1] - 1 if i else lo
                right_gap = runs[i + 1][0] - hi - 1 if i + 1 < len(runs) else 15 - hi
                # Inner contours get priority; never close a counter.
                choices = [(-1, left_gap), (1, right_gap)] if i == len(runs) - 1 else [(1, right_gap), (-1, left_gap)]
                for direction, gap in choices:
                    x = (lo - 1) if direction < 0 else (hi + 1)
                    if gap >= 3 and 0 <= x < 16 and x not in pixels:
                        pixels.add(x)
                        break
        out.append(frozenset(pixels))
    return tuple(out)


def italic_strike(glyph: Bitmap) -> Bitmap:
    """Discrete row offsets across the ink height, like a bitmap strike.

    The center zone stays on the ROM grid. Tall forms move right at the top
    and left at the baseline; descenders can overhang another source pixel.
    """
    shifts = (2, 2, 2, 2, 1, 1, 1, 0, 0, -1, -1, -1, -2, -2, -2, -2)
    return tuple(frozenset(x + shifts[y] for x in row) for y, row in enumerate(glyph))


# Fine-pixel corrections after making the initial strikes. Each row maps to
# (pixels to erase, pixels to ink); x is relative to the 16-column cell.
# These are intentionally individual choices, not a morphological filter.
CORRECTIONS: dict[str, dict[str, dict[int, tuple[tuple[int, ...], tuple[int, ...]]]]] = {
    "Bold": {
        "M": {5: ((7, 8), ())},          # notch the otherwise solid upper V
        "m": {6: ((7,), ())},
        "W": {9: ((7,), ())},          # hint at the bottom valley
        "w": {10: ((7,), ())},
        "@": {7: ((6,), ()), 8: ((6,), ())},
        "&": {7: ((6,), ())},
    },
    "Italic": {
        "a": {11: ((), (13,))},        # a visible exit stroke
        "f": {2: ((), (12,)), 11: ((-1,), (7,))},
        "g": {14: ((7,), (-2, -1))},   # open, leftward descender
        "j": {2: ((14, 15), (10, 11)), 3: ((14, 15), (10, 11)),
              14: ((9,), (1,))},
        "r": {6: ((14,), ()), 7: ((12, 13), ())},
        "{": {2: ((15,), ()), 11: ((12,), ())},
        "}": {2: ((9,), ()), 11: ((1,), ())},
    },
    "Bold Italic": {
        "M": {5: ((8, 9), ())},
        "m": {6: ((8,), ())},
        "W": {9: ((6,), ())},
        "w": {10: ((6,), ())},
        "a": {11: ((), (13,))},
        "f": {2: ((), (13,)), 11: ((-1,), (8,))},
        "g": {14: ((8,), (-2, -1))},
        "j": {2: ((15,), (10,)), 3: ((15,), (10,)),
              14: ((9,), (0,))},
        "r": {6: ((14,), ()), 7: ((13,), ())},
        "@": {7: ((6,), ()), 8: ((6,), ())},
        "&": {7: ((6,), ())},
        "{": {2: ((15,), ()), 11: ((12,), ())},
        "}": {2: ((10,), ()), 11: ((1,), ())},
    },
}

# Broken baseline joins look worse than upright operators in a TUI. The
# center-aligned vertical bar is also used as a common text-mode border.
UPRIGHT_OPERATORS = frozenset("-_=+|")


def strike(rows: Sequence[int], style: str, character: str | None = None) -> Bitmap:
    base = from_rom(rows)
    if style == "Regular":
        return base
    if character in UPRIGHT_OPERATORS:
        return bold_strike(base) if style in ("Bold", "Bold Italic") else base
    if style == "Bold":
        candidate = bold_strike(base)
    elif style == "Italic":
        candidate = italic_strike(base)
    elif style == "Bold Italic":
        candidate = italic_strike(bold_strike(base))
    else:
        raise ValueError(style)
    if character in CORRECTIONS[style]:
        mutable = [set(row) for row in candidate]
        for y, (erase, ink) in CORRECTIONS[style][character].items():
            mutable[y].difference_update(erase)
            mutable[y].update(ink)
        return tuple(frozenset(row) for row in mutable)
    return candidate
