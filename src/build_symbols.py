#!/usr/bin/env python3
"""Separate pixel companion: retain the upstream glyph collection's licenses."""
from pathlib import Path
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTCollection
from copy import deepcopy
from build_font import pixel_glyph, empty_glyph, glyph_name, STYLES
from pixel_strikes import pixels
from icon_data import SYMBOL_ROWS

ROOT=Path(__file__).resolve().parents[1]

def main():
    order=['.notdef'];cmap={};glyphs={'.notdef':empty_glyph()};canonical={}
    for cp,rows in sorted(SYMBOL_ROWS.items()):
        if rows not in canonical:
            name=glyph_name(cp);canonical[rows]=name
            order.append(name);glyphs[name]=pixel_glyph(pixels(rows))
        cmap[cp]=canonical[rows]
    fb=FontBuilder(1024,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap);fb.setupGlyf(glyphs)
    for g in glyphs.values():g.recalcBounds(glyphs)
    fb.setupHorizontalMetrics({name:(512,getattr(g,'xMin',0)) for name,g in glyphs.items()})
    fb.setupHorizontalHeader(ascent=896,descent=-128,lineGap=0)
    fb.setupNameTable({'familyName':'PCFontBI Symbols','styleName':'Regular',
        'uniqueFontIdentifier':'PCFontBI Symbols 0.4.0','fullName':'PCFontBI Symbols',
        'psName':'PCFontBI-Symbols','version':'Version 0.4.0',
        'copyright':'Nerd Fonts glyph collection: Ryan L McIntyre and the original icon-set authors. Pixel conversion by keylimesoda.',
        'description':'One-bit 8x16 companion derived from Nerd Fonts 3.5.1; full named codepoint repertoire. Not individually hand-drawn.',
        'licenseDescription':'Retains the Nerd Fonts glyph-set licenses. See upstream/nerd-fonts/LICENSE, UPSTREAM-README.md and licenses/.',
        'licenseInfoURL':'https://github.com/ryanoasis/nerd-fonts/tree/v3.5.1/patched-fonts/NerdFontsSymbolsOnly'})
    fb.setupOS2(sTypoAscender=896,sTypoDescender=-128,sTypoLineGap=0,usWinAscent=896,usWinDescent=128,usWeightClass=400)
    fb.setupPost(isFixedPitch=1,underlinePosition=-64,underlineThickness=64);fb.setupMaxp()
    f=fb.font;f['head'].created=f['head'].modified=3873398400;f.recalcTimestamp=False
    f['OS/2'].fsSelection=64;f['OS/2'].achVendID='PCBI'
    template=f;collection=TTCollection()
    for style in STYLES:
        f=deepcopy(template)
        suffix=style.name.replace(' ','')
        for platform,encoding,language in ((3,1,0x409),(1,0,0)):
            for nameid,value in {2:style.name,3:f'PCFontBI Symbols {style.name} 0.4.0',
                4:f'PCFontBI Symbols {style.name}',6:f'PCFontBI-Symbols-{suffix}'}.items():
                f['name'].setName(value,nameid,platform,encoding,language)
        f['OS/2'].usWeightClass=style.weight
        f['OS/2'].fsSelection=(1 if style.italic else 0)|(32 if style.bold else 0)|(64 if not style.bold and not style.italic else 0)
        f['head'].macStyle=(1 if style.bold else 0)|(2 if style.italic else 0)
        collection.fonts.append(f)
    path=ROOT/'fonts/PCFontBI-Symbols.ttc';collection.save(path,shareTables=True);print(path)

if __name__=='__main__':main()
