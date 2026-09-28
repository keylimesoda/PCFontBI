# IBM VGA 8x16 TUI

A four-face, terminal-oriented family built from the classic IBM VGA 8x16 raster design:

- **Regular** — faithful 8x16 pixel geometry at VGA/CRT-corrected aspect
- **Bold** — a separately generated bold face using fractional-pixel weight, not a 1-pixel smear
- **Italic** — a real installed italic face with controlled 6.5° designed oblique geometry
- **Bold Italic** — the same italic design applied to the bold face

The goal is simple: make the old IBM VGA look work in modern TUIs without asking FreeType/fontconfig/the terminal to fake bold and italic at runtime.

![specimen](docs/specimen.png)

## Why this exists

The Oldschool PC Font Pack explicitly documents the problem: these fonts historically had no bold/italic family, and modern renderers usually synthesize them with "smear and shear". That can look especially bad on an 8-pixel-wide raster-derived design.

This project makes the styles actual font files with consistent family/style metadata and **identical monospace cell metrics across all four faces**.

## Design choices

### Aspect-corrected regular

The source is the authentic IBM VGA `VGA8.F16` 8x16 raster (stored as Base64 text in the repository for portable GitHub/API handling). The outlines use a roughly 5:6 horizontal:vertical source-pixel ratio (`53 x 64` font units), matching the non-square pixel character of 640x400 VGA displayed at 4:3. The fixed advance is 424 units at 1024 UPM.

### Bold that does not eat the counters

A full source-pixel embolden is enormous on an 8-pixel-wide design. The Bold face adds only 8 font units per side (~0.15 source pixel), plus a very small vertical expansion. This makes weight visible under antialiasing without turning `e`, `a`, `8`, `B`, `@`, etc. into bricks.

### Italic without wrecking the UI

Italic is generated into its own outlines at build time. Text glyphs use a restrained 6.5° slant around the cell center. Structural glyphs stay upright in **all** faces:

- box drawing
- block elements and shades
- Braille
- Powerline separators

That means italic comments can lean while TUI borders stay straight.

### Modern TUI coverage

The historical CP437 glyphs are present, plus terminal-oriented additions:

- complete Unicode Block Elements (`U+2580..U+259F`)
- complete Braille Patterns (`U+2800..U+28FF`)
- basic Powerline separators (`U+E0B0..U+E0B3`)
- common punctuation aliases (smart quotes, Unicode minus/hyphen variants, NBSP)

Current v0.1 contains **550 Unicode codepoints**. The main missing piece versus `AcPlus` is its broader ~780-glyph multilingual extension; porting those glyphs is on the roadmap.

## Install

```bash
mkdir -p ~/.local/share/fonts/ibm-vga8x16-tui
cp fonts/*.ttf ~/.local/share/fonts/ibm-vga8x16-tui/
fc-cache -f
```

Verify:

```bash
fc-match "IBM VGA 8x16 TUI"
fc-list | grep "IBM VGA 8x16 TUI"
```

### Foot

```ini
font=IBM VGA 8x16 TUI:size=12
font-bold=IBM VGA 8x16 TUI:style=Bold:size=12
font-italic=IBM VGA 8x16 TUI:style=Italic:size=12
font-bold-italic=IBM VGA 8x16 TUI:style=Bold Italic:size=12
```

The original raster is 16 pixels high. A size that lands near a 16-pixel rendered height (or an integer multiple) will retain the strongest pixel character.

## Build

Requires Python 3 and `fontTools`; Pillow is used only for the specimen image.

```bash
python -m pip install -r requirements.txt
make all
```

Outputs:

```text
fonts/IBMVGA8x16TUI-Regular.ttf
fonts/IBMVGA8x16TUI-Bold.ttf
fonts/IBMVGA8x16TUI-Italic.ttf
fonts/IBMVGA8x16TUI-BoldItalic.ttf
```

Run just the invariant tests:

```bash
make test
```

The tests verify that all four faces have the same character set, the same 424-unit fixed advance, valid style metadata, and core TUI glyph coverage.

## Status

**v0.1 is usable, but intentionally conservative.** The four faces are real and correctly style-linked; the Regular face is faithful to the source raster; and structural TUI glyphs are protected from bold/italic distortion.

The next quality pass is manual tuning of the high-risk ASCII glyphs (`a e f g j k r s 8 B M W @ % & { } ( )`) after testing in Foot/Ghostty/Kitty at real terminal sizes, followed by importing the remaining AcPlus multilingual glyph repertoire.

## Source / attribution

The historical raster source is `VGA8.F16` from VileR's `vga-text-mode-fonts` collection:

- <https://github.com/viler-int10h/vga-text-mode-fonts>
- <https://int10h.org/oldschool-pc-fonts/>

VileR's Oldschool PC Font Pack documents both the aspect-correct (`Ac`) variants and the lack of native bold/italic faces. The pack is distributed under CC BY-SA 4.0.

This derivative family and its build sources are released under **CC BY-SA 4.0**. See `LICENSE` and `ATTRIBUTION.md`.


## Automated builds

GitHub Actions rebuilds and tests all four TTF faces plus the specimen image from source on each source change.
