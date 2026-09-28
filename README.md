# IBM VGA 8x16 TUI

A four-face terminal family derived from the IBM VGA 8×16 raster. **v0.2.1** corrects the overly dark Bold and rough stepped Italic in the first v0.2 experiment.

![Matched-size readability comparison](docs/specimen.png)

## The four faces

| Face | Default design |
| --- | --- |
| Regular | Original 8×16 ROM silhouette at a 53:64 horizontal/vertical source-pixel aspect. |
| Bold | Modest horizontal outline weight, limited by counter space. Dense M/m/W/w/@/&/% receive a smaller increase. |
| Italic | A continuous 6° oblique, with local adjustments to the j dot and f foot. |
| Bold Italic | The same counter-aware weight and continuous slant combined. |

The default is deliberately an optically adjusted **oblique**. The original bitmap outline remains visible, but the slant does not add a second staircase along every stem.

All neighboring row rectangles are united before styling. The resulting contours have no internal row boundaries. Existing small counters retain at least their original width; larger counters retain at least one source pixel. This is a geometric floor, not a promise of a whole illuminated screen pixel at every output size.

The former 16×16 bitmap experiment remains available for comparison:

~~~sh
python src/build_font.py --design bitmap --out /tmp/vga-bitmap-trial
~~~

The two designs use the same family/style names; install only the chosen build.

### What the optical revision changes

At a 16-pixel em, the test phrase's total grayscale ink increased about **9.5%** in the revised Bold over Regular, versus about **21%** in the bitmap trial. These are measurements of one test render, not a readability score.

The old half-pixel cuts in M/W have been removed from the default. Such details were too small to survive typical terminal rasterization cleanly. The comparison uses identical text, color, size and rendering, with nearest-neighbor enlargement and native-size samples.

### Terminal geometry and coverage

All four faces share a character map, 424-unit advance, 896-unit ascent, −128-unit descent and zero line gap. Correct side bearings include limited italic overhang. Box drawing, blocks, Braille and basic Powerline separators have identical upright geometry in every face. Minus, underscore, equals, plus and vertical bar stay upright in italic styles.

The font covers **550 Unicode codepoints**: CP437 mapped to Unicode, Block Elements, Braille Patterns, four Powerline separators, and punctuation aliases. Full AcPlus multilingual coverage remains future work.

These are unhinted outline TTFs. Slanted strokes and the aspect-corrected source-pixel width still require antialiasing at most screen sizes. The specimen is a FreeType/Pillow render; it does not simulate WRGB subpixels or prove the result in a particular terminal.

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

The four fonts pass checks for source geometry area, preserved counters, fixed advances, side bearings, structural glyph identity and a conservative 16-pixel Bold weight budget. Those checks complement visual inspection; they cannot establish readability.

The remaining optical check is in your Foot installation on the target OLED at your actual scale and font size. Future repertoire work covers the missing extended Latin, Greek, Cyrillic and Hebrew glyphs from AcPlus.

## Source and license

The source raster is VileR's VGA8.F16 dump of the IBM VGA 8×16 character set. The Oldschool PC Font Pack publishes reproductions under CC BY-SA 4.0. This project credits both sources and shares the derivative under **CC BY-SA 4.0**. See [ATTRIBUTION.md](ATTRIBUTION.md) and [LICENSE](LICENSE).
