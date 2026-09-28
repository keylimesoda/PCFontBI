#!/usr/bin/env python3
"""Export one-bit BDF strikes after validating the TTF's native raster.

The TTF is a lossless grid-outline wrapper around the bitmap designs. Refuse
any gray pixel, so this export can never silently threshold or hide blur.
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def raster(font, char, scale=1):
    image = Image.new('L', (8*scale, 16*scale))
    ImageDraw.Draw(image).text((0, 14*scale), char, font=font, fill=255, anchor='ls')
    return image


def export(path):
    tt = TTFont(path)
    style = tt['name'].getDebugName(2)
    weight = 'bold' if 'Bold' in style else 'medium'
    slant = 'i' if 'Italic' in style else 'r'
    ft = ImageFont.truetype(str(path), 16)
    properties = {
        'FAMILY_NAME': '"PCFontBI"', 'WEIGHT_NAME': f'"{weight.title()}"',
        'SLANT': f'"{slant.upper()}"', 'SETWIDTH_NAME': '"Normal"',
        'PIXEL_SIZE': '16', 'POINT_SIZE': '120',
        'RESOLUTION_X': '96', 'RESOLUTION_Y': '96',
        'SPACING': '"C"', 'AVERAGE_WIDTH': '80',
        'FONT_ASCENT': '14', 'FONT_DESCENT': '2',
        'CHARSET_REGISTRY': '"ISO10646"', 'CHARSET_ENCODING': '"1"',
        'DEFAULT_CHAR': '63',
        'COPYRIGHT': '"IBM VGA design; derivative by keylimesoda; VileR source. CC BY-SA 4.0."',
    }
    cmap = tt.getBestCmap()
    lines = ['STARTFONT 2.1', 'COMMENT PCFontBI 0.3.0; see ATTRIBUTION.md and LICENSE',
             f'FONT -PCFontBI-PCFontBI-{weight}-{slant}-normal--16-120-96-96-c-80-iso10646-1',
             'SIZE 12 96 96', 'FONTBOUNDINGBOX 8 16 0 -2',
             f'STARTPROPERTIES {len(properties)}']
    lines += [f'{k} {v}' for k, v in properties.items()]
    lines += ['ENDPROPERTIES', f'CHARS {len(cmap)}']
    for cp, name in sorted(cmap.items()):
        mask = raster(ft, chr(cp))
        assert set(mask.tobytes()) <= {0, 255}, f'Gray pixel in {style} U+{cp:04X}'
        lines += [f'STARTCHAR {name}', f'ENCODING {cp}', 'SWIDTH 500 0',
                  'DWIDTH 8 0', 'BBX 8 16 0 -2', 'BITMAP']
        for y in range(16):
            lines.append(f'{sum(128 >> x for x in range(8) if mask.getpixel((x,y))):02X}')
        lines.append('ENDCHAR')
    lines.append('ENDFONT')
    dest = path.with_suffix('.bdf')
    dest.write_text('\n'.join(lines)+'\n')
    tt.close()
    return dest


if __name__ == '__main__':
    for p in sorted((ROOT/'fonts').glob('PCFontBI-*.ttf')):
        print(export(p))
