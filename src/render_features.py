#!/usr/bin/env python3
"""Review real shaped font output at native size and integer enlargement."""
from pathlib import Path
from PIL import Image, ImageDraw
from icon_data import ICONS
from ligatures import SEQUENCES
from shaping import Shaper
from render_specimen import BG, INK, ACCENT, label

ROOT=Path(__file__).resolve().parents[1]

def main():
    regular=Shaper(ROOT/'fonts/PCFontBI-Regular.ttf')
    bold=Shaper(ROOT/'fonts/PCFontBI-Bold.ttf')
    im=Image.new('RGB',(1280,1670),BG);d=ImageDraw.Draw(im)
    def line(text,x,y,scale=2,face=regular,enabled=True,color=INK):
        mask=face.render(text,enabled)
        assert set(mask.tobytes())<={0,255}
        mask=mask.resize((mask.width*scale,mask.height*scale),Image.Resampling.NEAREST)
        im.paste(color,(x,y),mask)
    label(d,(48,30),'PCFontBI / the modern terminal',42,INK)
    label(d,(48,90),'v0.4   /   one-bit icons   /   contextual code ligatures',22,ACCENT)
    label(d,(48,140),'The same eight-pixel cell. A few more things worth saying.',22)
    d.line((48,187,1232,187),fill='#344355')
    label(d,(48,214),'29 operators, drawn on the grid',28,INK)
    label(d,(48,258),'Literal',18);label(d,(433,258),'Contextual / Regular',18);label(d,(818,258),'Contextual / Bold',18)
    groups=[SEQUENCES[i:i+5] for i in range(0,len(SEQUENCES),5)]
    for i,group in enumerate(groups):
        text='  '.join(group);y=294+i*42
        line(text,48,y,enabled=False)
        line(text,433,y)
        line(text,818,y,face=bold)
    label(d,(48,558),'Each source character keeps its own glyph, cell and cursor position. OpenType calt.',18,ACCENT)
    d.line((48,604,1232,604),fill='#344355')
    label(d,(48,630),'99 original pixel icons',28,INK)
    label(d,(48,675),'384 Nerd Font mappings. Upright in every style. Each icon below is enlarged 3x.',18)
    for i,(name,entry) in enumerate(ICONS.items()):
        x=48+(i%11)*108;y=723+(i//11)*68
        cp=int(next(iter(entry['mappings'].values())),16)
        line(chr(cp),x+28,y,3,color=ACCENT)
        label(d,(x,y+47),name,11)
    d.line((48,1360,1232,1360),fill='#344355')
    label(d,(48,1384),'A real shaped run / native 16px',22,INK)
    line('if (ready != null && count >= 3) { result = data?.value ?? fallback; }',48,1423,1)
    line('if (ready != null && count >= 3) { result = data?.value ?? fallback; }',48,1455,2)
    label(d,(48,1512),'Plus a matching companion: all 10,617 named Nerd Fonts 3.5.1 codepoints.',20,ACCENT)
    label(d,(48,1545),'Companion artwork is automatically fitted to one bit; intricate logos lose detail in eight pixels.',17)
    label(d,(48,1582),'Preview uses HarfBuzz + FreeType. No gray font pixels; integer enlargement only.',17)
    label(d,(48,1615),'Ligatures need a shaping terminal or editor. Stock Foot displays the literal characters.',17)
    im.save(ROOT/'docs/features.png',optimize=True)
    print(ROOT/'docs/features.png')

if __name__=='__main__':main()
