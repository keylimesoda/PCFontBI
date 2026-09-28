#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "specimen.png"
faces = [
    ("Regular", ROOT / "fonts/IBMVGA8x16TUI-Regular.ttf"),
    ("Bold", ROOT / "fonts/IBMVGA8x16TUI-Bold.ttf"),
    ("Italic", ROOT / "fonts/IBMVGA8x16TUI-Italic.ttf"),
    ("Bold Italic", ROOT / "fonts/IBMVGA8x16TUI-BoldItalic.ttf"),
]
samples = [
    "The quick brown fox jumps over 0123456789",
    "fn main() { if (x != 0) return x->value; }",
    "┌────────── TUI ──────────┐  ░▒▓█  ",
    "│ Braille: ⠀⠁⠉⠛⣿         │",
    "└─────────────────────────┘",
]
size = 32
fonts = [(label, ImageFont.truetype(str(path), size=size)) for label,path in faces]
W,H = 1500, 980
im = Image.new("RGB", (W,H), "white")
d = ImageDraw.Draw(im)
y = 20
for label,font in fonts:
    d.text((20,y), label, fill="black", font=font)
    y += 40
    for s in samples:
        d.text((40,y), s, fill="black", font=font)
        y += 38
    y += 18
im.save(OUT)
print(OUT)
