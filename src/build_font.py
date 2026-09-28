#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from bitmap_styles import strike
from optical_outlines import optical_glyph, ANGLE

UPM = 1024
PX_Y = 64
PX_X = 53               # 8 * 53 = 424; ~5:6 pixel aspect, close to 640x400 on 4:3
ADVANCE = PX_X * 8
TOP = 14 * PX_Y          # 896
BOTTOM = TOP - 16 * PX_Y # -128
ASCENT = TOP
DESCENT = BOTTOM
ITALIC_DEGREES = ANGLE
FAMILY = "IBM VGA 8x16 TUI"
VERSION = "0.2.1"

# CP437's 0x01..0x1F and 0x7F are graphic characters on IBM PCs, not Unicode controls.
CP437_GRAPHICS = {
    0x01: 0x263A, 0x02: 0x263B, 0x03: 0x2665, 0x04: 0x2666,
    0x05: 0x2663, 0x06: 0x2660, 0x07: 0x2022, 0x08: 0x25D8,
    0x09: 0x25CB, 0x0A: 0x25D9, 0x0B: 0x2642, 0x0C: 0x2640,
    0x0D: 0x266A, 0x0E: 0x266B, 0x0F: 0x263C, 0x10: 0x25BA,
    0x11: 0x25C4, 0x12: 0x2195, 0x13: 0x203C, 0x14: 0x00B6,
    0x15: 0x00A7, 0x16: 0x25AC, 0x17: 0x21A8, 0x18: 0x2191,
    0x19: 0x2193, 0x1A: 0x2192, 0x1B: 0x2190, 0x1C: 0x221F,
    0x1D: 0x2194, 0x1E: 0x25B2, 0x1F: 0x25BC, 0x7F: 0x2302,
}

# Useful modern Unicode aliases whose exact historical IBM forms already exist.
ALIASES = {
    0x00A0: 0x0020,  # NBSP -> space
    0x2010: 0x002D,  # hyphen
    0x2011: 0x002D,  # non-breaking hyphen
    0x2012: 0x002D,  # figure dash
    0x2013: 0x002D,  # en dash (pixel-cell compromise)
    0x2212: 0x002D,  # mathematical minus
    0x2018: 0x0027, 0x2019: 0x0027,
    0x201C: 0x0022, 0x201D: 0x0022,
    0x25B6: 0x25BA,  # black right-pointing triangle
    0x25C0: 0x25C4,  # black left-pointing triangle
}

# Shapes that should remain structurally upright and un-emboldened in every face.
def structural(cp: int) -> bool:
    return (0x2500 <= cp <= 0x259F) or (0x2800 <= cp <= 0x28FF) or (0xE0B0 <= cp <= 0xE0B3)


def cp437_codepoints() -> Dict[int, int]:
    """Return mapping Unicode codepoint -> source byte index."""
    out: Dict[int, int] = {}
    for b in range(256):
        if b == 0:
            continue
        if b in CP437_GRAPHICS:
            cp = CP437_GRAPHICS[b]
        elif b < 0x20:
            continue
        else:
            cp = ord(bytes([b]).decode("cp437"))
        out.setdefault(cp, b)
    return out


def load_rom(path: Path) -> List[List[int]]:
    if path.suffix.lower() == ".b64":
        data = base64.b64decode(path.read_text())
    else:
        data = path.read_bytes()
    if len(data) != 4096:
        raise ValueError(f"Expected 4096 bytes for 256x16 VGA font; got {len(data)}")
    glyphs = []
    for i in range(256):
        rows = data[i * 16:(i + 1) * 16]
        glyphs.append([int(x) for x in rows])
    return glyphs


def _rect(pen: TTGlyphPen, x0: float, y0: float, x1: float, y1: float):
    # Clockwise contour.
    pen.moveTo((round(x0), round(y0)))
    pen.lineTo((round(x0), round(y1)))
    pen.lineTo((round(x1), round(y1)))
    pen.lineTo((round(x1), round(y0)))
    pen.closePath()


def bitmap_glyph(rows: List[int], style_name: str, character: str | None = None, *, keep_structural: bool = False):
    pen = TTGlyphPen(None)
    pixels = strike(rows, "Regular" if keep_structural else style_name, character)
    for row, xs in enumerate(pixels):
        y1 = TOP - row * PX_Y
        y0 = y1 - PX_Y
        xs = sorted(xs)
        for start in range(len(xs)):
            if start and xs[start] == xs[start - 1] + 1:
                continue
            end = start
            while end + 1 < len(xs) and xs[end + 1] == xs[end] + 1:
                end += 1
            # Merge adjacent half-source-pixel squares into one row contour.
            _rect(pen, round(xs[start] * PX_X / 2), y0,
                  round((xs[end] + 1) * PX_X / 2), y1)
    return pen.glyph()


def empty_glyph():
    return TTGlyphPen(None).glyph()


def block_glyph(cp: int):
    """Programmatic Unicode Block Elements U+2580..U+259F for TUI coverage."""
    pen = TTGlyphPen(None)
    # Coordinates are fractions of the cell width/height.
    def rect_frac(x0, y0, x1, y1):
        _rect(pen, ADVANCE * x0, BOTTOM + (TOP - BOTTOM) * y0,
              ADVANCE * x1, BOTTOM + (TOP - BOTTOM) * y1)

    if cp == 0x2580: rect_frac(0, .5, 1, 1)      # upper half
    elif cp == 0x2581: rect_frac(0, 0, 1, 1/8)
    elif cp == 0x2582: rect_frac(0, 0, 1, 2/8)
    elif cp == 0x2583: rect_frac(0, 0, 1, 3/8)
    elif cp == 0x2584: rect_frac(0, 0, 1, 4/8)
    elif cp == 0x2585: rect_frac(0, 0, 1, 5/8)
    elif cp == 0x2586: rect_frac(0, 0, 1, 6/8)
    elif cp == 0x2587: rect_frac(0, 0, 1, 7/8)
    elif cp == 0x2588: rect_frac(0, 0, 1, 1)
    elif cp == 0x2589: rect_frac(0, 0, 7/8, 1)
    elif cp == 0x258A: rect_frac(0, 0, 6/8, 1)
    elif cp == 0x258B: rect_frac(0, 0, 5/8, 1)
    elif cp == 0x258C: rect_frac(0, 0, 4/8, 1)
    elif cp == 0x258D: rect_frac(0, 0, 3/8, 1)
    elif cp == 0x258E: rect_frac(0, 0, 2/8, 1)
    elif cp == 0x258F: rect_frac(0, 0, 1/8, 1)
    elif cp == 0x2590: rect_frac(.5, 0, 1, 1)
    elif cp in (0x2591, 0x2592, 0x2593):
        # Dither fills, density 25/50/75%; use a deterministic 2x2 pattern.
        density = {0x2591: 1, 0x2592: 2, 0x2593: 3}[cp]
        for ry in range(8):
            for rx in range(4):
                if ((rx + ry * 2) % 4) < density:
                    _rect(pen, rx * ADVANCE/4, BOTTOM + ry * (TOP-BOTTOM)/8,
                          (rx+1)*ADVANCE/4, BOTTOM + (ry+1)*(TOP-BOTTOM)/8)
    elif cp == 0x2594: rect_frac(0, 7/8, 1, 1)
    elif cp == 0x2595: rect_frac(7/8, 0, 1, 1)
    elif cp == 0x2596: rect_frac(0, 0, .5, .5)
    elif cp == 0x2597: rect_frac(.5, 0, 1, .5)
    elif cp == 0x2598: rect_frac(0, .5, .5, 1)
    elif cp == 0x2599:
        rect_frac(0, 0, .5, 1); rect_frac(.5, 0, 1, .5)
    elif cp == 0x259A:
        rect_frac(0, .5, .5, 1); rect_frac(.5, 0, 1, .5)
    elif cp == 0x259B:
        rect_frac(0, .5, 1, 1); rect_frac(0, 0, .5, .5)
    elif cp == 0x259C:
        rect_frac(0, .5, 1, 1); rect_frac(.5, 0, 1, .5)
    elif cp == 0x259D: rect_frac(.5, .5, 1, 1)
    elif cp == 0x259E:
        rect_frac(.5, .5, 1, 1); rect_frac(0, 0, .5, .5)
    elif cp == 0x259F:
        rect_frac(.5, 0, 1, 1); rect_frac(0, 0, .5, .5)
    return pen.glyph()


def braille_glyph(cp: int):
    pen = TTGlyphPen(None)
    bits = cp - 0x2800
    # dot -> (column,row), rows laid out on a 2x4 grid.
    dot_pos = {1:(0,0),2:(0,1),3:(0,2),4:(1,0),5:(1,1),6:(1,2),7:(0,3),8:(1,3)}
    xs = [PX_X * 2, PX_X * 5]
    ys = [TOP - PX_Y*2, TOP - PX_Y*5, TOP - PX_Y*8, TOP - PX_Y*11]
    dot_w = PX_X
    dot_h = PX_Y * 2
    for d in range(1,9):
        if bits & (1 << (d-1)):
            col,row = dot_pos[d]
            x0 = xs[col]
            y1 = ys[row]
            _rect(pen, x0, y1-dot_h, x0+dot_w, y1)
    return pen.glyph()


def powerline_glyph(cp: int):
    pen = TTGlyphPen(None)
    mid = (TOP + BOTTOM) / 2
    if cp == 0xE0B0:  # solid right triangle
        pen.moveTo((0, BOTTOM)); pen.lineTo((ADVANCE, mid)); pen.lineTo((0, TOP)); pen.closePath()
    elif cp == 0xE0B2:  # solid left triangle
        pen.moveTo((ADVANCE, BOTTOM)); pen.lineTo((0, mid)); pen.lineTo((ADVANCE, TOP)); pen.closePath()
    elif cp == 0xE0B1:  # thin right chevron
        w = max(18, PX_X//2)
        pen.moveTo((0, BOTTOM)); pen.lineTo((w, BOTTOM)); pen.lineTo((ADVANCE, mid)); pen.lineTo((w, TOP)); pen.lineTo((0, TOP)); pen.lineTo((ADVANCE-w, mid)); pen.closePath()
    elif cp == 0xE0B3:  # thin left chevron
        w = max(18, PX_X//2)
        pen.moveTo((ADVANCE, BOTTOM)); pen.lineTo((ADVANCE-w, BOTTOM)); pen.lineTo((0, mid)); pen.lineTo((ADVANCE-w, TOP)); pen.lineTo((ADVANCE, TOP)); pen.lineTo((w, mid)); pen.closePath()
    return pen.glyph()


def glyph_name(cp: int) -> str:
    return f"uni{cp:04X}" if cp <= 0xFFFF else f"u{cp:X}"


@dataclass(frozen=True)
class Style:
    name: str
    weight: int
    bold: bool = False
    italic: bool = False

STYLES = [
    Style("Regular", 400),
    Style("Bold", 700, bold=True),
    Style("Italic", 400, italic=True),
    Style("Bold Italic", 700, bold=True, italic=True),
]


def build_style(rom: List[List[int]], style: Style, out_path: Path, design: str = "optical"):
    source = cp437_codepoints()
    glyph_order = [".notdef"]
    glyf = {".notdef": empty_glyph()}
    cmap: Dict[int, str] = {}

    # Historical CP437 glyphs first.
    cp_to_name: Dict[int, str] = {}
    for cp in sorted(source):
        name = glyph_name(cp)
        cp_to_name[cp] = name
        glyph_order.append(name)
        keep = structural(cp)
        draw_glyph = bitmap_glyph if design == "bitmap" else optical_glyph
        glyf[name] = draw_glyph(rom[source[cp]], style.name, chr(cp), keep_structural=keep)
        cmap[cp] = name

    # Aliases reuse the exact historical glyph outline.
    for cp, target in sorted(ALIASES.items()):
        if cp in cmap or target not in cp_to_name:
            continue
        name = glyph_name(cp)
        glyph_order.append(name)
        glyf[name] = glyf[cp_to_name[target]]
        cmap[cp] = name

    # Complete Block Elements range (replaces/extends CP437 entries when missing only).
    for cp in range(0x2580, 0x25A0):
        if cp in cmap:
            continue
        name = glyph_name(cp)
        glyph_order.append(name)
        glyf[name] = block_glyph(cp)
        cmap[cp] = name

    # Braille patterns: common in TUIs, charts, spinners and status dashboards.
    for cp in range(0x2800, 0x2900):
        name = glyph_name(cp)
        glyph_order.append(name)
        glyf[name] = braille_glyph(cp)
        cmap[cp] = name

    # Minimal Powerline separators. Structural glyphs remain identical in all faces.
    for cp in range(0xE0B0, 0xE0B4):
        name = glyph_name(cp)
        glyph_order.append(name)
        glyf[name] = powerline_glyph(cp)
        cmap[cp] = name

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)

    # Fixed advance width in every face is the critical TUI invariant.
    metrics = {}
    for g in glyph_order:
        glyf[g].recalcBounds(glyf)
        # The advance remains fixed. The side bearing records true ink bounds,
        # including the occasional one-pixel italic overhang.
        metrics[g] = (ADVANCE, getattr(glyf[g], "xMin", 0))
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT, lineGap=0)

    ps_style = style.name.replace(" ", "")
    ps_name = f"IBMVGA8x16TUI-{ps_style}"
    fb.setupNameTable({
        "familyName": FAMILY,
        "styleName": style.name,
        "uniqueFontIdentifier": f"{FAMILY} {style.name} {VERSION}",
        "fullName": f"{FAMILY} {style.name}",
        "psName": ps_name,
        "version": f"Version {VERSION}",
        "copyright": "IBM VGA raster design; TUI derivative by keylimesoda. Source compilation by VileR/int10h.org. CC BY-SA 4.0.",
        "manufacturer": "keylimesoda",
        "designer": "IBM VGA source; TUI family derivative",
        "description": ("Experimental bitmap-strike styles; compare with the optical default."
                        if design == "bitmap" else
                        "Aspect-corrected IBM VGA 8x16 terminal family with counter-aware weight, continuous oblique and upright TUI geometry."),
        "licenseDescription": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        "licenseInfoURL": "https://creativecommons.org/licenses/by-sa/4.0/",
    })
    fb.setupOS2(
        sTypoAscender=ASCENT,
        sTypoDescender=DESCENT,
        sTypoLineGap=0,
        usWinAscent=ASCENT,
        usWinDescent=-DESCENT,
        usWeightClass=style.weight,
        usWidthClass=5,
        sxHeight=7 * PX_Y,
        sCapHeight=11 * PX_Y,
    )
    fb.setupPost(italicAngle=(-ITALIC_DEGREES if style.italic else 0), isFixedPitch=1,
                 underlinePosition=-90, underlineThickness=45)
    fb.setupMaxp()

    font = fb.font
    # The four checked-in TTFs should rebuild byte-for-byte on any machine.
    # This is 2026-09-28 00:00 UTC, expressed in TrueType's 1904 epoch.
    font["head"].created = font["head"].modified = 3873398400
    font.recalcTimestamp = False
    font["head"].macStyle = (1 if style.bold else 0) | (2 if style.italic else 0)
    fs = 0
    if style.italic: fs |= 1 << 0
    if style.bold: fs |= 1 << 5
    if not style.bold and not style.italic: fs |= 1 << 6
    font["OS/2"].fsSelection = fs
    font["OS/2"].achVendID = "TUI "
    if style.italic:
        font["hhea"].caretSlopeRise = 1000
        font["hhea"].caretSlopeRun = round(math.tan(math.radians(ITALIC_DEGREES)) * 1000)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    font.save(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="upstream/VGA8.F16.b64")
    parser.add_argument("--out", default="fonts")
    parser.add_argument("--design", choices=("optical", "bitmap"), default="optical",
                        help="optical is the readable default; bitmap preserves the earlier experiment")
    args = parser.parse_args()

    rom = load_rom(Path(args.source))
    out = Path(args.out)
    for style in STYLES:
        filename = f"IBMVGA8x16TUI-{style.name.replace(' ', '')}.ttf"
        build_style(rom, style, out / filename, args.design)
        print(out / filename)

if __name__ == "__main__":
    main()
