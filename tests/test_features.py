#!/usr/bin/env python3
"""Real shaping, pixel fidelity, complete mapping, and family fallback checks."""
from pathlib import Path
import sys,json,gzip,os,shutil,subprocess,tempfile
from PIL import Image,ImageFont
from fontTools.ttLib import TTFont,TTCollection
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ligatures import SEQUENCES,artwork
from shaping import Shaper
from icon_data import ICONS,ICON_ROWS,SYMBOL_ROWS
from export_bdf import raster


def expected_bitmap(rows,width=8):
    image=Image.new('L',(width,16))
    for y,row in enumerate(rows):
        for x in row:image.putpixel((x,y),255)
    return image


def main():
    for style in ('Regular','Bold','Italic','BoldItalic'):
        path=ROOT/'fonts'/f'PCFontBI-{style}.ttf';tt=TTFont(path)
        shaper=Shaper(path);double=Shaper(path,32)
        assert 'GSUB' in tt
        assert {r.FeatureTag for r in tt['GSUB'].table.FeatureList.FeatureRecord}=={'calt'}
        assert all(advance==512 for advance,_ in tt['hmtx'].metrics.values())
        for index,seq in enumerate(SEQUENCES):
            for text in (seq,'a'+seq+'b',' '+seq+' '):
                info,pos=shaper.shape(text)
                assert len(info)==len(text)
                assert [i.cluster for i in info]==list(range(len(text))), (style,text,'cursor clusters')
                assert all(p.x_advance==512 and p.y_advance==p.x_offset==p.y_offset==0 for p in pos)
                start=text.index(seq)
                assert [tt.getGlyphName(i.codepoint) for i in info[start:start+len(seq)]]==[f'lig{index:02d}.part{j}' for j in range(len(seq))], (style,text)
                disabled,_=shaper.shape(text,False)
                assert [i.codepoint for i in disabled]==[tt.getGlyphID(tt.getBestCmap()[ord(c)]) for c in text]
            native=shaper.render(seq)
            expected=expected_bitmap(artwork(seq,'Bold' in style),len(seq)*8)
            assert native.tobytes()==expected.tobytes(), (style,seq,'art mismatch')
            assert set(native.tobytes())<={0,255}
            assert double.render(seq).tobytes()==native.resize((native.width*2,32),Image.Resampling.NEAREST).tobytes()
        for text in ('====','----','>>>=','->>','!!=','???','::::','....','!===','/* */','hello world'):
            info,_=shaper.shape(text)
            assert [i.codepoint for i in info]==[tt.getGlyphID(tt.getBestCmap()[ord(c)]) for c in text], (style,text,'partial operator substitution')
        # Every unencoded contextual part also stays inside its own cell.
        for name in tt.getGlyphOrder():
            if not name.startswith('lig'):continue
            g=tt['glyf'][name]
            if g.numberOfContours:
                assert 0<=g.xMin<=g.xMax<=512 and -128<=g.yMin<=g.yMax<=896
                assert all(x%64==0 and y%64==0 for x,y in g.coordinates)
        tt.close()
    names=json.loads(gzip.decompress((ROOT/'upstream/nerd-fonts/glyphnames.json.gz').read_bytes()))
    wanted={int(value['code'],16) for name,value in names.items() if name!='METADATA'}
    assert names['METADATA']['version']=='3.5.1'
    assert set(SYMBOL_ROWS)==wanted and len(wanted)==10617
    assert len(ICONS)==99 and len(ICON_ROWS)==384
    for icon in ICONS.values():
        for name,cp in icon['mappings'].items():assert int(names[name]['code'],16)==int(cp,16)
    path=ROOT/'fonts/PCFontBI-Symbols.ttc';collection=TTCollection(path)
    assert len(collection.fonts)==4
    reference=collection.fonts[0]
    for index,(font,style) in enumerate(zip(collection.fonts,('Regular','Bold','Italic','Bold Italic'))):
        assert font['name'].getDebugName(1)=='PCFontBI Symbols'
        assert font['name'].getDebugName(2)==style
        assert font['OS/2'].usWeightClass==(700 if 'Bold' in style else 400)
        assert bool(font['head'].macStyle&2)==('Italic' in style)
        assert set(font.getBestCmap())==wanted
        assert all(w==512 for w,_ in font['hmtx'].metrics.values())
        assert font['glyf'].compile(font)==reference['glyf'].compile(reference)
        for glyph in font['glyf'].glyphs.values():
            glyph.expand(font['glyf'])
            if glyph.numberOfContours:
                assert 0<=glyph.xMin<=glyph.xMax<=512 and -128<=glyph.yMin<=glyph.yMax<=896
                assert all(x%64==0 and y%64==0 for x,y in glyph.coordinates)
    # Raster every symbol once; all four faces share exactly the same outlines.
    ft=ImageFont.truetype(str(path),16,index=0);ft32=ImageFont.truetype(str(path),32,index=0)
    for cp,rows in SYMBOL_ROWS.items():
        image=raster(ft,chr(cp))
        expected=expected_bitmap([{x for x in range(8) if byte&(128>>x)} for byte in rows])
        assert image.tobytes()==expected.tobytes(),hex(cp)
        assert raster(ft32,chr(cp),2).tobytes()==image.resize((16,32),Image.Resampling.NEAREST).tobytes(),hex(cp)
        assert any(image.tobytes()) or cp==0xEC03,hex(cp) # upstream nf-cod-blank
    collection.close()
    if shutil.which('fc-match'):
        with tempfile.TemporaryDirectory(prefix='pcfontbi-fc-') as work:
            conf=Path(work)/'fonts.conf'
            conf.write_text(f'<fontconfig><dir>{ROOT}/fonts</dir><cachedir>{work}/cache</cachedir><include>{ROOT}/config/60-PCFontBI-symbols.conf</include></fontconfig>')
            env={**os.environ,'FONTCONFIG_FILE':str(conf)}
            core=TTFont(ROOT/'fonts/PCFontBI-Regular.ttf').getBestCmap()
            fallback=min(wanted-set(core))
            for style in ('Regular','Bold','Italic','Bold Italic'):
                result=subprocess.check_output(['fc-match','--format','%{family}|%{style}',f'PCFontBI:style={style}:charset={fallback:x}'],env=env,text=True)
                assert result==f'PCFontBI Symbols|{style}',result
            original=subprocess.check_output(['fc-match','--format','%{family}','PCFontBI:charset=41'],env=env,text=True)
            assert original=='PCFontBI',original
        print('Fontconfig: correct core/symbol fallback and all four styles')
    print(f'OK: {len(SEQUENCES)} ligatures x 4 faces; cell/cluster preservation; 99 icons / 384 mappings; all 10,617 companion codepoints at 16px and 32px')

if __name__=='__main__':main()
