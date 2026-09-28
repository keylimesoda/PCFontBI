#!/usr/bin/env python3
from pathlib import Path
import sys

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bitmap_styles import CORRECTIONS, from_rom, strike, to_rom  # noqa: E402
from build_font import cp437_codepoints, load_rom  # noqa: E402

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
    assert all(to_rom(from_rom(glyph)) == glyph for glyph in rom), "Regular must reproduce the ROM"
    cp437 = cp437_codepoints()
    assert CORRECTIONS["Italic"]["j"] and CORRECTIONS["Bold Italic"]["g"]
    for style in EXPECTED:
        for ch in map(chr, range(32, 127)):
            glyph = strike(rom[cp437[ord(ch)]], style, ch)
            assert len(glyph) == 16
            xs = [x for row in glyph for x in row]
            assert all(-2 <= x <= 17 for x in xs), f"{style} {ch} exceeds one source pixel of overhang"
            if style == "Bold":
                assert all(0 <= x < 16 for x in xs), f"{style} {ch} escapes its cell"
    for style in ("Bold", "Bold Italic"):
        # This is the legibility constraint a full source-pixel smear violates.
        for ch, y in (("8", 3), ("B", 3), ("@", 4)):
            row = strike(rom[cp437[ord(ch)]], style, ch)[y]
            assert any(x not in row for x in range(min(row) + 1, max(row))), f"counter closed in {style} {ch}"

    styles = set()
    advances = None
    cmaps = None
    font_objects = {}
    for path in FONTS:
        f = TTFont(path)
        assert name(f, 1) == "IBM VGA 8x16 TUI"
        assert name(f, 5) == "Version 0.2.0"
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
    print(f"OK: 4 faces, {len(cmaps)} Unicode codepoints, identical 424-unit advances")

if __name__ == "__main__":
    main()
