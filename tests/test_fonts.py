#!/usr/bin/env python3
from pathlib import Path
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.areaPen import AreaPen
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from build_font import cp437_codepoints, load_rom  # noqa: E402
from optical_outlines import source_runs, styled_runs  # noqa: E402

FONTS = sorted((ROOT / "fonts").glob("IBMVGA8x16TUI-*.ttf"))
EXPECTED = {"Regular", "Bold", "Italic", "Bold Italic"}

def name(font, name_id):
    for rec in font["name"].names:
        if rec.nameID == name_id:
            try:
                return rec.toUnicode()
            except Exception:
                pass
    return None

def main():
    assert len(FONTS) == 4, f"expected 4 faces, found {len(FONTS)}"
    rom = load_rom(ROOT / "upstream" / "VGA8.F16.b64")
    cp437 = cp437_codepoints()
    for cp, index in cp437.items():
        original = source_runs(rom[index])
        bold = styled_runs(rom[index], "Bold", chr(cp))
        for row, heavier in zip(original, bold):
            for i in range(len(row)-1):
                gap = row[i+1][0]-row[i][1]
                assert heavier[i+1][0]-heavier[i][1] >= min(gap, 53), f"counter narrowed below one source pixel: {chr(cp)}"

    styles = set()
    advances = None
    cmaps = None
    font_objects = {}
    for path in FONTS:
        f = TTFont(path)
        assert name(f, 1) == "IBM VGA 8x16 TUI"
        assert name(f, 5) == "Version 0.2.1"
        style = name(f, 2)
        styles.add(style)
        font_objects[style] = f
        assert f["post"].isFixedPitch != 0
        assert f["hhea"].ascent == 896 and f["hhea"].descent == -128
        h = f["hmtx"].metrics
        these_advances = {g: aw for g,(aw,lsb) in h.items()}
        assert set(these_advances.values()) == {424}, f"non-mono advance in {path.name}"
        for g, (aw, lsb) in h.items():
            assert lsb == getattr(f["glyf"][g], "xMin", 0), f"incorrect bearing: {style} {g}"
        if advances is None: advances = these_advances
        else: assert these_advances == advances, f"advance map differs in {path.name}"
        cmap = set(f.getBestCmap())
        for cp in [0x2500,0x2502,0x2514,0x2518,0x2588,0x2592,0x2800,0x28FF,0xE0B0,0xE0B3]:
            assert cp in cmap, f"U+{cp:04X} missing from {path.name}"
        if cmaps is None: cmaps = cmap
        else: assert cmap == cmaps, f"charset differs in {path.name}"
    assert styles == EXPECTED, styles
    regular = font_objects["Regular"]
    glyph_set = regular.getGlyphSet()
    for cp, index in cp437.items():
        pen = AreaPen(glyph_set)
        glyph_set[regular.getBestCmap()[cp]].draw(pen)
        expected_area = sum(byte.bit_count() for byte in rom[index])*53*64
        assert abs(pen.value) == expected_area, f"ROM geometry area changed: U+{cp:04X}"
    for style, f in font_objects.items():
        for cp in range(33, 127):
            g = f["glyf"][f.getBestCmap()[cp]]
            assert -53 <= g.xMin and g.xMax <= 477, f"excess overhang: {style} {chr(cp)}"
    for cp in (0x2500, 0x2502, 0x2514, 0x2588, 0x2592, 0x2800, 0x28FF, 0xE0B0, 0xE0B3):
        contours = []
        for style in EXPECTED:
            f = font_objects[style]
            glyph = f["glyf"][f.getBestCmap()[cp]]
            coords, endpoints, flags = glyph.getCoordinates(f["glyf"])
            contours.append((list(coords), list(endpoints), list(flags)))
        assert all(contour == contours[0] for contour in contours[1:]), f"structural U+{cp:04X} changed between styles"
    assert font_objects["Italic"]["head"].macStyle & 2
    assert font_objects["Bold"]["head"].macStyle & 1
    for f in font_objects.values():
        f.close()
    # A real-size raster weight budget catches the overly dark bitmap trial.
    # This does not prove readability; the matched-size specimen is reviewed too.
    ink = []
    for style in ("Regular", "Bold"):
        f = ImageFont.truetype(str(ROOT / "fonts" / f"IBMVGA8x16TUI-{style}.ttf"), 16)
        sample = Image.new("L", (400, 24))
        ImageDraw.Draw(sample).text((4, 0), "The quick brown fox jumps over 0123456789 @%&", font=f, fill=255)
        ink.append(sum(sample.tobytes()))
    assert 1.02 < ink[1]/ink[0] < 1.17, f"16px bold weight outside budget: {ink[1]/ink[0]:.3f}"
    print(f"OK: 4 faces, {len(cmaps)} Unicode codepoints, identical 424-unit advances")

if __name__ == "__main__":
    main()
