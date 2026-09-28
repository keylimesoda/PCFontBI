"""One-bit 8x16 designs, never fractional pixels or continuous shears.

The reviewed ASCII faces live in design/strikes.json: sixteen hexadecimal
bytes per character, most-significant bit at the left. Regular always comes
directly from the ROM. Other CP437 characters use conservative fallback rules;
these are not represented as individually authored designs.
"""
from __future__ import annotations

import json
from pathlib import Path

DESIGNS = json.loads((Path(__file__).resolve().parents[1] / "design/strikes.json").read_text())
UPRIGHT = frozenset("-_=+|")


def pixels(rows):
    return tuple(frozenset(x for x in range(8) if byte & (128 >> x)) for byte in rows)


def bytes_from_pixels(rows):
    return [sum(128 >> x for x in row) for row in rows]


def strengthen(rows):
    """Grow the leading narrow stroke; leave a full pixel inside every gap.

    Only one addition per row. Broad horizontal strokes and packed M/W joins
    are already heavy. Never spend their counter pixels on extra darkness.
    """
    result = []
    for row in pixels(rows):
        out = set(row)
        if row:
            lo = min(row)
            hi = lo
            while hi + 1 in row:
                hi += 1
            if hi - lo < 2 and hi + 1 <= 6 and hi + 2 not in row:
                out.add(hi + 1)
        result.append(out)
    return bytes_from_pixels(result)


def lean(rows):
    """Fallback staircase for non-ASCII; ASCII has explicit bitmap masters."""
    shifts = (1, 1, 1, 1, 1, 1, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1)
    result = []
    for y, row in enumerate(pixels(rows)):
        # Keep complete strokes and accents inside the cell. At a full-width
        # row there is no room to lean; preserve it rather than clip its ink.
        shift = max(-min(row), min(shifts[y], 7-max(row))) if row else 0
        result.append({x + shift for x in row})
    return bytes_from_pixels(result)


def strike(rows, style, character=None, *, keep_structural=False):
    if keep_structural or style == "Regular":
        return pixels(rows)
    if style not in DESIGNS:
        raise ValueError(style)
    key = f"{ord(character):04X}" if character else None
    if key in DESIGNS[style]:
        return pixels(bytes.fromhex(DESIGNS[style][key]))
    candidate = list(rows)
    if "Italic" in style and character not in UPRIGHT:
        candidate = lean(candidate)
    if "Bold" in style:
        candidate = strengthen(candidate)
    return pixels(candidate)
