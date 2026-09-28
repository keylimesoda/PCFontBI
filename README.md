# IBM VGA 8x16 TUI

A four-face terminal family derived from the IBM VGA 8×16 raster. **v0.2** replaces v0.1's outline expansion and continuous shear with discrete bitmap strikes.

![Four faces, pixel designs and TUI specimen](docs/specimen.png)

## The four faces

| Face | Design |
| --- | --- |
| Regular | The original 8×16 ROM pixels, scaled to a 53:64 horizontal/vertical pixel aspect. |
| Bold | A separate 16×16 working bitmap. Each original pixel spans two horizontal design pixels, so stems can gain half a source pixel without closing small counters. |
| Italic | A separate bitmap with discrete row offsets, plus hand-corrected a, f, g, j, r, { and }. |
| Bold Italic | Its own strike with separately corrected M, m, W, w, a, f, g, j, r, @, &, { and }. |

The base algorithms produce broad CP437 coverage. The listed corrections are individually edited; **the other letters are not claimed to be individually hand-drawn**. See [src/bitmap_styles.py](src/bitmap_styles.py) for the strike grids and pixel edits.

Regular keeps the source raster untouched. The other strikes are converted to TrueType outlines **only after** their pixels are chosen. No renderer-side fake styles are required.

### Terminal geometry

All four faces have the same family name, character map, 424-unit advance, 896-unit ascent, −128-unit descent and zero line gap. Actual italic left bearings are recorded, including up to one source pixel of overhang. Box drawing, blocks, Braille and basic Powerline separators have identical upright outlines in every face. The minus sign, underscore, equals, plus and vertical bar also remain upright in the italic styles so joined rules and code operators do not become broken or crooked.

The font covers **550 Unicode codepoints**: the CP437 repertoire mapped to Unicode, Block Elements, Braille Patterns, four Powerline separators, and common punctuation aliases. This is **not** yet the complete multilingual AcPlus repertoire. Glyphs outside the current set use terminal/fontconfig fallback.

The 16×16 grid is a *design grid*, not an embedded bitmap strike at one size: these files are standard outline TTFs. At non-integral output sizes, antialiasing still depends on the renderer.

## Install on Omarchy / Linux

Download or clone this repository, then run:

~~~sh
./install.sh
fc-list | grep 'IBM VGA 8x16 TUI'
~~~

You can also copy all four files from [fonts](fonts/) into ~/.local/share/fonts/ibm-vga8x16-tui/ and run fc-cache -f.

### Foot

~~~ini
font=IBM VGA 8x16 TUI:size=12
font-bold=IBM VGA 8x16 TUI:style=Bold:size=12
font-italic=IBM VGA 8x16 TUI:style=Italic:size=12
font-bold-italic=IBM VGA 8x16 TUI:style=Bold Italic:size=12
~~~

Start near a 16-pixel font em (roughly 12 pt at 96 DPI) and compare 16 and 32 physical pixels. A 9 pt em at 96 DPI compresses the 16 vertical source rows into about 12 output pixels. Your compositor scale and Foot DPI settings can change the actual result.

## Build and inspect

Requires Python 3, fontTools and Pillow:

~~~sh
python -m pip install -r requirements.txt
make all
~~~

This writes the four TTFs to fonts/ and the poster to docs/specimen.png. Run make test for source fidelity, font metadata, equal widths, true side bearings, counter openness and structural-glyph identity checks. GitHub Actions regenerates these binaries and the specimen from source.

## Status and next design passes

v0.2 is a reviewable font-design prototype. The pixel-grid specimen and generated TTFs have been inspected and tested, but actual rendering in your Foot installation on the 42-inch OLED remains a worthwhile final optical check. Priority glyphs to assess there: M W m w 8 B @ % & f g j, adjacent italic punctuation, and long box-drawing runs at your preferred size.

The next repertoire milestone is the missing extended Latin, Greek, Cyrillic and Hebrew glyphs from the larger AcPlus family, with the same metrics and deliberate style review.

## Source and license

The source raster is VileR's VGA8.F16 dump of the IBM VGA 8×16 character set. The Oldschool PC Font Pack publishes reproductions under CC BY-SA 4.0. This project credits both sources and shares the derivative under **CC BY-SA 4.0**. See [ATTRIBUTION.md](ATTRIBUTION.md) and [LICENSE](LICENSE).
