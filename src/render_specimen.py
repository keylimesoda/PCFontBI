#!/usr/bin/env python3
"""Render a reproducible specimen using only the built fonts and Pillow."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from bitmap_styles import strike
from build_font import cp437_codepoints, load_rom

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "specimen.png"
FONT_DIR = ROOT / "fonts"
FACES = ("Regular", "Bold", "Italic", "Bold Italic")
FILES = {style: FONT_DIR / f"IBMVGA8x16TUI-{style.replace(' ', '')}.ttf" for style in FACES}

BG = "#0e151d"
CARD = "#17242b"
CARD2 = "#122029"
INK = "#edf0dc"
MUTED = "#a5b7ae"
GRID = "#30414a"
ACCENTS = ("#f4cb78", "#fb966e", "#88d6cb", "#c0aff4")


def font(style="Regular", size=27):
    return ImageFont.truetype(str(FILES[style]), size)


def draw_text(draw, xy, value, style="Regular", size=27, color=INK):
    draw.text(xy, value, font=font(style, size), fill=color)


def mixed(draw, x, y, segments, size=26):
    for string, style, color in segments:
        f = font(style, size)
        draw.text((x, y), string, font=f, fill=color)
        x += f.getlength(string)


def box(draw, xy, fill, outline=None, radius=16):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=2)


def pixel_glyph(draw, glyph, x, y, color):
    # Two columns on either side show potential italic overhang. The nominal
    # sixteen fine columns remain the same width in every style.
    pixel_w, pixel_h = 10, 13
    draw.rectangle((x + 20, y, x + 180, y + 208), outline="#678086", width=2)
    draw.line((x + 100, y, x + 100, y + 208), fill="#3d5259", width=1)
    draw.line((x, y + 156, x + 200, y + 156), fill="#526465", width=1)
    for row, xs in enumerate(glyph):
        for gx in xs:
            left = x + (gx + 2) * pixel_w
            top = y + row * pixel_h
            draw.rectangle((left, top, left + pixel_w - 1, top + pixel_h - 1), fill=color)


def main():
    W, H = 1800, 1380
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line((0, y, W, y), fill=(14 + y // 300, 21 + y // 240, 29 + y // 200))
    d.rectangle((0, 0, 18, H), fill=ACCENTS[0])
    draw_text(d, (63, 34), "IBM VGA 8x16 TUI", size=70, color=INK)
    draw_text(d, (68, 114), "V0.2    FOUR REAL FACES / ONE FIXED CELL", size=25, color=ACCENTS[0])
    d.line((60, 161, 1740, 161), fill=GRID, width=2)

    headings = ("01 / ROM", "02 / HEAVIER", "03 / ROW-STEPS", "04 / COMBINED")
    examples = (
        ("Original IBM geometry", "Aa Bb 8@%&", "fn main() { return 1; }"),
        ("Edited half-pixels", "Aa Bb 8@%&", "fn main() { return 1; }"),
        ("Distinct italic pixels", "Aa Bb 8@%&", "fn main() { return 1; }"),
        ("Corrected combination", "Aa Bb 8@%&", "fn main() { return 1; }"),
    )
    for i, style in enumerate(FACES):
        x, y = 60 + 420 * i, 185
        box(d, (x, y, x + 399, y + 286), CARD, GRID)
        d.rectangle((x + 2, y + 2, x + 397, y + 8), fill=ACCENTS[i])
        draw_text(d, (x + 21, y + 24), headings[i], size=20, color=ACCENTS[i])
        draw_text(d, (x + 21, y + 62), style.upper(), style=style, size=36)
        draw_text(d, (x + 21, y + 111), examples[i][0], size=19, color=MUTED)
        draw_text(d, (x + 21, y + 150), examples[i][1], style=style, size=34)
        draw_text(d, (x + 21, y + 211), examples[i][2], style=style, size=24, color=ACCENTS[i])

    draw_text(d, (62, 511), "ONE CHARACTER, FOUR DRAWINGS", size=33, color=INK)
    draw_text(d, (62, 559), "The ROM g, then three bitmap strikes; each square is a real design pixel.", size=21, color=MUTED)
    rom = load_rom(ROOT / "upstream" / "VGA8.F16.b64")
    g_rows = rom[cp437_codepoints()[ord("g")]]
    for i, style in enumerate(FACES):
        x, y = 60 + 420 * i, 605
        box(d, (x, y, x + 399, y + 322), CARD2, GRID)
        draw_text(d, (x + 23, y + 16), style.upper(), size=23, color=ACCENTS[i])
        pixel_glyph(d, strike(g_rows, style, "g"), x + 96, y + 59, ACCENTS[i])
        draw_text(d, (x + 22, y + 281), "16 x 16 working grid", size=17, color=MUTED)

    draw_text(d, (62, 970), "IN A TUI", size=34)
    draw_text(d, (1005, 970), "AT THE RASTER", size=34)
    box(d, (60, 1020, 963, 1318), CARD, GRID)
    box(d, (995, 1020, 1739, 1318), CARD, GRID)
    draw_text(d, (82, 1036), "CODE, CHROME, AND FOUR SGR STYLES", size=19, color=ACCENTS[0])
    d.line((80, 1073, 943, 1073), fill=GRID, width=2)
    draw_text(d, (84, 1083), "┌───────────────────────────────────────────────┐", size=26, color=MUTED)
    mixed(d, 84, 1116, [("│  ", "Regular", MUTED), ("fn ", "Bold", ACCENTS[1]),
                        ("shade", "Bold", INK), ("(pixel: u8) -> u8 {", "Regular", INK)])
    mixed(d, 84, 1149, [("│    ", "Regular", MUTED),
                        ("// designed row-step italic, not runtime shear", "Italic", ACCENTS[2])])
    mixed(d, 84, 1182, [("│    ", "Regular", MUTED), ("return ", "Bold", ACCENTS[1]),
                        ("pixel", "Regular", INK), (" + ", "Regular", INK),
                        ("1", "Bold Italic", ACCENTS[3]), (";", "Regular", INK)])
    draw_text(d, (84, 1215), "│  }    ├───────┤   ░▒▓█  ⠿  ", size=26, color=INK)
    draw_text(d, (84, 1248), "└───────────────────────────────────────────────┘", size=26, color=MUTED)

    draw_text(d, (1018, 1039), "16 PX EM  /  2X NEAREST ZOOM", size=20, color=ACCENTS[2])
    small = Image.new("RGB", (350, 81), CARD)
    sd = ImageDraw.Draw(small)
    sd.text((8, 3), "bold: 8B @%&  MW", font=font("Bold", 16), fill=INK)
    sd.text((8, 29), "italic: fgjr(){}", font=font("Italic", 16), fill=ACCENTS[2])
    sd.text((8, 55), "both: 0123 abc", font=font("Bold Italic", 16), fill=ACCENTS[3])
    img.paste(small.resize((700, 162), Image.Resampling.NEAREST), (1015, 1080))
    draw_text(d, (1018, 1265), "TRUE TYPE  /  FIXED 424-UNIT ADVANCE", size=18, color=MUTED)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print(OUT)


if __name__ == "__main__":
    main()
