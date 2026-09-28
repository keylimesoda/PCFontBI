#!/usr/bin/env python3
"""Rebuild the pinned, one-bit companion strike from Nerd Fonts 3.5.1.

This imports the full repertoire, not hand-authored optical corrections.
Every output glyph is fitted to an integer 7x12 area of an 8x16 cell.
The normal offline build reads the checked-in compressed bitmap masters.
"""
from pathlib import Path
import argparse, hashlib, io, json, gzip, urllib.request
from PIL import Image, ImageFont
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
REVISION='b894ea7803af6aade63d60a4381e006098ec9c4d'
SHA256='fe471e538392f51910faab985fa8e192a39dd3426125edd15b71b3680df0e749'
URL=f'https://raw.githubusercontent.com/ryanoasis/nerd-fonts/{REVISION}/patched-fonts/NerdFontsSymbolsOnly/SymbolsNerdFontMono-Regular.ttf'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path)
    args=parser.parse_args()
    data=args.source.read_bytes() if args.source else urllib.request.urlopen(URL,timeout=60).read()
    assert hashlib.sha256(data).hexdigest()==SHA256, 'Upstream file changed'
    source=TTFont(io.BytesIO(data));font=ImageFont.truetype(io.BytesIO(data),128)
    names=json.loads(gzip.decompress((ROOT/'upstream/nerd-fonts/glyphnames.json.gz').read_bytes()))
    codepoints=sorted({int(v['code'],16) for k,v in names.items() if k!='METADATA'})
    bitmaps={};empty=[]
    for cp in codepoints:
        assert cp in source.getBestCmap()
        mask=font.getmask(chr(cp),mode='L')
        image=Image.frombytes('L',mask.size,bytes(mask));bounds=image.getbbox()
        if bounds is None:
            if cp==0xEC03:  # nf-cod-blank is deliberately empty upstream.
                bitmaps[f'{cp:04X}']=bytes(16).hex()
            else:empty.append(cp)
            continue
        image=image.crop(bounds)
        scale=min(7/image.width,12/image.height)
        width=max(1,min(7,round(image.width*scale)));height=max(1,min(12,round(image.height*scale)))
        image=image.resize((width,height),Image.Resampling.BOX)
        # A lower threshold than half-coverage retains thin icon strokes on
        # this tiny grid; coverage values never reach the emitted font.
        threshold=max(1,min(80,round(image.getextrema()[1]*0.5)))
        image=image.point(lambda v:255 if v>=threshold else 0)
        assert image.getbbox(), f'Icon vanished: U+{cp:04X}'
        cell=Image.new('L',(8,16));cell.paste(image,((7-width)//2,(16-height)//2))
        rows=bytes(sum(128>>x for x in range(8) if cell.getpixel((x,y))) for y in range(16))
        bitmaps[f'{cp:04X}']=rows.hex()
    assert not empty, f'Blank upstream icons: {empty}'
    result={'source':URL,'revision':REVISION,'sha256':SHA256,'version':'3.5.1',
            'method':'128px grayscale -> aspect-fit 7x12 BOX -> coverage >=min(80,half peak) -> one bit; centered in 8x16',
            'glyphs':bitmaps}
    dest=ROOT/'upstream/nerd-fonts/pixel-symbols.json.gz'
    dest.write_bytes(gzip.compress((json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print(f'{len(bitmaps)} named Nerd Font codepoints -> {dest} ({dest.stat().st_size} bytes)')


if __name__=='__main__':main()
