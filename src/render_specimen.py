#!/usr/bin/env python3
"""Native-size and integer-enlarged specimens; no thresholding or blur filter."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from export_bdf import raster

ROOT = Path(__file__).resolve().parents[1]
BG, PANEL, INK, MUTED, ACCENT = '#111923', '#192330', '#e8ede7', '#98aabb', '#90d7be'
STYLES = ('Regular','Bold','Italic','Bold Italic')


def font(style, size=16):
    return ImageFont.truetype(str(ROOT/'fonts'/f"PCFontBI-{style.replace(' ','')}.ttf"), size)


def label(draw, pos, text, size=20, fill=MUTED):
    draw.text(pos, text, font=ImageFont.load_default(size=size), fill=fill)


def strip(text, style, *, light=False):
    image = Image.new('RGB',(len(text)*8,16), '#e8ede7' if light else BG)
    ImageDraw.Draw(image).text((0,14),text,font=font(style),fill=BG if light else INK,anchor='ls')
    return image


def specimen():
    im=Image.new('RGB',(1280,1420),BG);d=ImageDraw.Draw(im)
    label(d,(48,28),'PCFontBI',54,INK)
    label(d,(49,99),'VGA character. Every pixel deliberate.',25,ACCENT)
    label(d,(1025,47),'v0.3 / 8 x 16',22,ACCENT)
    label(d,(49,143),'One-bit designs / square pixels / four faces / 550 codepoints',19)
    d.line((48,185,1232,185),fill='#344355',width=1)
    samples=('The quick brown fox jumps over the lazy dog.',
             '0OQ 1Il| 8B6G  rn m  vv w  @%&  {}[]()')
    descriptions={
        'Regular':'Original IBM VGA pixels',
        'Bold':'Selective weight; open M/W joins',
        'Italic':'Stepped stems; redrawn lowercase',
        'Bold Italic':'Weight and slant on the same grid',
    }
    for i,style in enumerate(STYLES):
        y=214+i*210
        label(d,(48,y),style,25,INK)
        label(d,(400,y+4),descriptions[style],19)
        label(d,(1101,y+4),'16px x 3',18,ACCENT)
        for j,text in enumerate(samples):
            line=strip(text,style)
            im.paste(line.resize((line.width*3,48),Image.Resampling.NEAREST),(48,y+40+j*51))
        label(d,(48,y+153),'Native 16px',16)
        im.paste(strip('The quick brown fox jumps over 0123456789. if (flag) { return gjr; }',style),(205,y+154))
        d.line((48,y+193,1232,y+193),fill='#273445',width=1)
    label(d,(48,1083),'A terminal, at native size',23,INK)
    # Real 8x16 cells and true mixed-style runs. No proportional layout.
    d.rectangle((48,1124,665,1302),fill=BG,outline='#344355')
    title='─ PCFontBI / build '
    cells=[
        [('Regular','┌'+title+'─'*(58-len(title))+'┐')],
        [('Regular','│ '),('Bold','PASS'),('Regular','  4 faces   550 glyphs   16px / 32px                  │')],
        [('Regular','│ '),('Italic','Every pixel has a job.'),('Regular','                                    │')],
        [('Regular','│                                                          │')],
        [('Regular','│ '),('Bold','if'),('Regular',' (ready) { '),('Bold Italic','return'),('Regular',' glyphs[0]; }                       │')],
        [('Regular','│ ░░▒▒▓▓██  ⠁⠃⠇⠏⠟⠿⣿  '),('Italic','a f g j r'),('Regular','                          │')],
        [('Regular','└'+'─'*58+'┘')],
    ]
    # Pad each interior row by cell count rather than hand-spaced text.
    for row,runs in enumerate(cells):
        content=''.join(t for _,t in runs)
        if content.startswith('│'):
            style,last=runs[-1]; before=last.rstrip('│').rstrip()
            used=sum(len(t) for _,t in runs[:-1])+len(before)
            runs[-1]=(style,before+' '*(59-used)+'│')
        assert sum(len(text) for _,text in runs) == 60
        x=72
        for style,text in runs:
            im.paste(strip(text,style),(x,1147+row*16));x+=len(text)*8
    label(d,(720,1083),'Also on a light background',23,INK)
    d.rectangle((720,1124,1232,1302),fill='#e8ede7')
    for i,style in enumerate(STYLES):
        im.paste(strip('0O 1Il rn m  {}[]  a f g j',style,light=True),(740,1147+i*36))
    label(d,(48,1340),'Designed for 16 physical pixels and integer multiples.',21,ACCENT)
    label(d,(48,1374),'Specimen: grayscale FreeType rendering. No gray font pixels at the native grid; enlargement uses nearest neighbor.',16)
    im.save(ROOT/'docs/specimen.png',optimize=True)


def atlas():
    # All printable ASCII in every face, plus structural and extended checks.
    chars=[chr(cp) for cp in range(32,127)]
    chars+=list('éäñüçßÆæΩπΣµαΓδ∞√≡±≤≥÷≈°·░▒▓█▀▄▌▐┌┐└┘├┤┬┴┼═║╬⠿⣿')
    cols=12; tile_w=100; tile_h=126; top=112
    rows=(len(chars)+cols-1)//cols
    im=Image.new('RGB',(cols*tile_w+80,top+rows*tile_h+46),BG);d=ImageDraw.Draw(im)
    label(d,(40,24),'PCFontBI / glyph review',35,INK)
    label(d,(40,72),'Each cell: Regular, Bold, Italic, Bold Italic. Native 16px glyphs enlarged exactly 2x.',18)
    fts={s:font(s) for s in STYLES}
    for i,c in enumerate(chars):
        x=40+(i%cols)*tile_w;y=top+(i//cols)*tile_h
        label(d,(x,y),f'U+{ord(c):04X}',14)
        for j,s in enumerate(STYLES):
            mask=raster(fts[s],c).resize((16,32),Image.Resampling.NEAREST)
            d.rectangle((x+(j%2)*37,y+24+(j//2)*42,x+(j%2)*37+15,y+55+(j//2)*42),fill=PANEL)
            im.paste(INK,(x+(j%2)*37,y+24+(j//2)*42),mask)
    im.save(ROOT/'docs/glyph-atlas.png',optimize=True)


if __name__=='__main__':
    (ROOT/'docs').mkdir(exist_ok=True)
    specimen();atlas()
    print(ROOT/'docs/specimen.png')
    print(ROOT/'docs/glyph-atlas.png')
