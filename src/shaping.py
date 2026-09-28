"""A real HarfBuzz + FreeType preview path; never substitute glyph art by hand."""
from pathlib import Path
import freetype
import uharfbuzz as hb
from PIL import Image

class Shaper:
    def __init__(self,path,size=16,index=0):
        self.path=Path(path);self.size=size
        self.hb=hb.Font(hb.Face(self.path.read_bytes(),index));self.hb.scale=(1024,1024)
        self.ft=freetype.Face(str(self.path),index=index);self.ft.set_pixel_sizes(0,size)

    def shape(self,text,enabled=True):
        buffer=hb.Buffer();buffer.add_str(text);buffer.guess_segment_properties()
        hb.shape(self.hb,buffer,{'calt':enabled})
        return list(buffer.glyph_infos),list(buffer.glyph_positions)

    def render(self,text,enabled=True):
        infos,positions=self.shape(text,enabled)
        width=round(sum(p.x_advance for p in positions)*self.size/1024)
        image=Image.new('L',(max(1,width),self.size))
        x=0
        for info,position in zip(infos,positions):
            self.ft.load_glyph(info.codepoint,freetype.FT_LOAD_RENDER|freetype.FT_LOAD_NO_HINTING|freetype.FT_LOAD_TARGET_NORMAL)
            slot=self.ft.glyph;bitmap=slot.bitmap
            if bitmap.width and bitmap.rows:
                raw=bytes(bitmap.buffer)
                if bitmap.pitch!=bitmap.width:
                    raw=b''.join(raw[y*bitmap.pitch:y*bitmap.pitch+bitmap.width] for y in range(bitmap.rows))
                mask=Image.frombytes('L',(bitmap.width,bitmap.rows),raw)
                px=round((x+position.x_offset)*self.size/1024)+slot.bitmap_left
                py=round(14*self.size/16-position.y_offset*self.size/1024)-slot.bitmap_top
                image.paste(mask,(px,py))
            x+=position.x_advance
        return image
