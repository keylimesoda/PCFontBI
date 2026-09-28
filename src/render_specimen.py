#!/usr/bin/env python3
"""Matched-size comparison, rendered through the same FreeType/Pillow path."""
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image, ImageDraw, ImageFont
from build_font import STYLES, build_style, load_rom

ROOT = Path(__file__).resolve().parents[1]
BG, INK, MUTED = "#171b24", "#e8e9e0", "#a6b8c3"
SAMPLE = ("The quick brown fox 0123456789",
          "8B eao @%& MWmw fgjr {}[]()",
          "if (flag) { return gjr; }")


def font(folder, style, size):
    return ImageFont.truetype(str(folder / f"IBMVGA8x16TUI-{style.replace(' ', '')}.ttf"), size)


def caption(draw, x, y, text, size=24, color=INK):
    draw.text((x, y), text, font=ImageFont.load_default(size=size), fill=color)


def main():
    image = Image.new("RGB", (1440, 1270), BG)
    d = ImageDraw.Draw(image)
    caption(d, 42, 28, "IBM VGA TUI / readability revision", 40)
    caption(d, 44, 88, "Same text, color, and renderer. 16 px text enlarged 3x without smoothing.", 23, MUTED)
    d.line((44, 137, 1396, 137), fill="#3d4a55", width=2)
    with TemporaryDirectory(prefix="vga-bitmap-") as work:
        bitmap = Path(work)
        rom = load_rom(ROOT / "upstream" / "VGA8.F16.b64")
        for style in STYLES:
            build_style(rom, style, bitmap / f"IBMVGA8x16TUI-{style.name.replace(' ', '')}.ttf", design="bitmap")
        for col, (label, folder) in enumerate((
            ("v0.2 / bitmap experiment", bitmap),
            ("v0.2.1 / optical revision", ROOT / "fonts"),
        )):
            x = 44 + col * 708
            caption(d, x, 168, label, 29)
            for row, style in enumerate(("Bold", "Italic", "Bold Italic")):
                y = 230 + row * 270
                caption(d, x, y, style, 24, MUTED)
                small = Image.new("RGB", (212, 65), BG)
                sd = ImageDraw.Draw(small)
                for line, text in enumerate(SAMPLE):
                    sd.text((3, line * 22), text, font=font(folder, style, 16), fill=INK)
                image.paste(small.resize((636, 195), Image.Resampling.NEAREST), (x, y+38))

    d.line((44, 1050, 1396, 1050), fill="#3d4a55", width=2)
    caption(d, 44, 1072, "Optical revision at native size", 26)
    for row, size in enumerate((16, 20, 24)):
        y = 1113 + row * 41
        caption(d, 44, y, f"{size} px", 19, MUTED)
        x = 134
        for style in ("Regular", "Bold", "Italic", "Bold Italic"):
            f = font(ROOT / "fonts", style, size)
            d.text((x, y), "8B eao @%& fgjr", font=f, fill=INK)
            x += 300
    out = ROOT / "docs" / "specimen.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    main()
