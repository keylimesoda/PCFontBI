#!/usr/bin/env python3
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
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
    styles = set()
    advances = None
    cmaps = None
    for path in FONTS:
        f = TTFont(path)
        assert name(f, 1) == "IBM VGA 8x16 TUI"
        style = name(f, 2)
        styles.add(style)
        assert f["post"].isFixedPitch != 0
        assert f["hhea"].ascent == 896 and f["hhea"].descent == -128
        h = f["hmtx"].metrics
        these_advances = {g: aw for g,(aw,lsb) in h.items()}
        assert set(these_advances.values()) == {424}, f"non-mono advance in {path.name}"
        if advances is None: advances = these_advances
        else: assert these_advances == advances, f"advance map differs in {path.name}"
        cmap = set(f.getBestCmap())
        for cp in [0x2500,0x2502,0x2514,0x2518,0x2588,0x2592,0x2800,0x28FF,0xE0B0,0xE0B3]:
            assert cp in cmap, f"U+{cp:04X} missing from {path.name}"
        if cmaps is None: cmaps = cmap
        else: assert cmap == cmaps, f"charset differs in {path.name}"
    assert styles == EXPECTED, styles
    print(f"OK: 4 faces, {len(cmaps)} Unicode codepoints, identical 424-unit advances")

if __name__ == "__main__":
    main()
