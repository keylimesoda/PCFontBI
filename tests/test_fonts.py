#!/usr/bin/env python3
"""End-to-end checks for grid fidelity and the small text design contract."""
from pathlib import Path
import sys
from collections import deque
from PIL import Image, ImageFont
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from build_font import cp437_codepoints, load_rom, structural
from pixel_strikes import DESIGNS
from export_bdf import raster

STYLES = ('Regular', 'Bold', 'Italic', 'Bold Italic')


def holes(image):
    # Four-connected background, including an explicit exterior border.
    w, h = image.size
    background = {(x,y) for y in range(-1,h+1) for x in range(-1,w+1)
                  if not (0 <= x < w and 0 <= y < h) or not image.getpixel((x,y))}
    count = 0
    while background:
        start = next(iter(background)); background.remove(start)
        queue = deque([start]); exterior = False
        while queue:
            x,y = queue.popleft()
            exterior |= x in (-1,w) or y in (-1,h)
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if p in background:
                    background.remove(p); queue.append(p)
        count += not exterior
    return count


def main():
    rom = load_rom(ROOT/'upstream/VGA8.F16.b64')
    cp437 = cp437_codepoints()
    expected_ascii = {f'{cp:04X}' for cp in range(32,127)}
    assert set(DESIGNS) == set(STYLES)-{'Regular'}
    for face in DESIGNS.values():
        assert set(face) == expected_ascii
        assert all(len(bytes.fromhex(rows)) == 16 for rows in face.values())
    fonts = {}; masks = {}; cmaps = []
    for style in STYLES:
        path = ROOT/'fonts'/f"PCFontBI-{style.replace(' ','')}.ttf"
        tt = TTFont(path); fonts[style] = tt
        assert tt['name'].getDebugName(1) == 'PCFontBI'
        assert tt['name'].getDebugName(2) == style
        assert tt['name'].getDebugName(5) == 'Version 0.3.0'
        assert tt['head'].unitsPerEm == 1024
        assert tt['post'].isFixedPitch
        assert tt['hhea'].ascent == 896 and tt['hhea'].descent == -128
        assert tt['hhea'].lineGap == 0
        assert tt['OS/2'].usWeightClass == (700 if 'Bold' in style else 400)
        assert bool(tt['head'].macStyle & 1) == ('Bold' in style)
        assert bool(tt['head'].macStyle & 2) == ('Italic' in style)
        cmap = tt.getBestCmap(); cmaps.append(set(cmap))
        assert len(cmap) == 550
        assert tt['OS/2'].sxHeight == tt['glyf'][cmap[ord('x')]].yMax
        assert tt['OS/2'].sCapHeight == tt['glyf'][cmap[ord('H')]].yMax
        ft16 = ImageFont.truetype(str(path),16)
        ft32 = ImageFont.truetype(str(path),32)
        masks[style] = {}
        for cp, name in cmap.items():
            glyph = tt['glyf'][name]
            advance, bearing = tt['hmtx'][name]
            assert advance == 512
            assert bearing == getattr(glyph,'xMin',0)
            coords, ends, _ = glyph.getCoordinates(tt['glyf'])
            for x,y in coords:
                assert x % 64 == y % 64 == 0, (style, hex(cp), 'off-grid')
                assert 0 <= x <= 512 and -128 <= y <= 896, (style, hex(cp), 'overhang')
            start = 0
            for end in ends:
                contour = list(coords[start:end+1]); start = end+1
                assert all(a[0] == b[0] or a[1] == b[1]
                           for a,b in zip(contour,contour[1:]+contour[:1])), (style,hex(cp),'diagonal outline')
            native = raster(ft16,chr(cp)); masks[style][cp] = native
            assert set(native.tobytes()) <= {0,255}, (style,hex(cp),'gray at 16px')
            assert raster(ft32,chr(cp),2).tobytes() == native.resize((16,32),Image.Resampling.NEAREST).tobytes(), (style,hex(cp),'32px changed design')
            if cp in cp437 and (style == 'Regular' or structural(cp)):
                expected = rom[cp437[cp]]
            elif 32 <= cp < 127:
                expected = bytes.fromhex(DESIGNS[style][f'{cp:04X}'])
            else:
                expected = None
            if expected is not None:
                actual = [sum(128 >> x for x in range(8) if native.getpixel((x,y))) for y in range(16)]
                assert actual == list(expected), (style,hex(cp),'source raster mismatch')
        # Independent BDF parsing: bitmap export must match the TTF exactly.
        blocks = path.with_suffix('.bdf').read_text().split('STARTCHAR ')[1:]
        assert len(blocks) == len(cmap)
        for block in blocks:
            lines = block.splitlines()
            cp = int(next(l for l in lines if l.startswith('ENCODING ')).split()[1])
            i = lines.index('BITMAP')+1
            rows = [int(line,16) for line in lines[i:i+16]]
            expected = masks[style][cp]
            assert rows == [sum(128 >> x for x in range(8) if expected.getpixel((x,y))) for y in range(16)]
        for a,b in ('0O','1I','Il','li','ao','gq','hn'):
            assert masks[style][ord(a)].tobytes() != masks[style][ord(b)].tobytes(), (style,a,b,'confusable identical')
        # Letters and digits keep a one-pixel gutter, even in mixed styles.
        # Original VGA symbols such as * deliberately use the whole cell.
        for cp in map(ord, 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'):
            assert all(masks[style][cp].getpixel((7,y)) == 0 for y in range(16)), (style,chr(cp),'lost gutter')
    assert all(c == cmaps[0] for c in cmaps)
    for cp in cmaps[0]:
        if structural(cp):
            assert len({masks[s][cp].tobytes() for s in STYLES}) == 1, hex(cp)
    # Bold must not fill the enclosed spaces in the common round forms.
    for roman,bold in (('Regular','Bold'),('Italic','Bold Italic')):
        for c in 'ABDOPQR0689abdegopq':
            assert holes(masks[bold][ord(c)]) >= holes(masks[roman][ord(c)]), (bold,c,'closed counter')
        phrase = 'The quick brown fox jumps over 0123456789 @%&'
        ink = [sum(sum(masks[s][ord(c)].tobytes()) for c in phrase) for s in (roman,bold)]
        ratio = ink[1]/ink[0]
        assert 1.05 < ratio < 1.30, (bold,ratio)
        print(f'{bold}: {100*(ratio-1):.1f}% more ink in native sample')
    for f in fonts.values(): f.close()
    print('OK: four faces, 550 codepoints each; exact 16px rasters, exact 2x at 32px, no gray pixels; BDF parity')


if __name__ == '__main__':
    main()
