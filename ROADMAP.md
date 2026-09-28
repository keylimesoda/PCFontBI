# Roadmap

## v0.2 — bitmap-strike redesign (implemented)

- Replace outline expansion/shear with separately generated bitmap strikes.
- Keep Regular's original 8×16 geometry; draw style pixels on a 16×16 horizontal-resolution grid.
- Apply and document individual repairs to difficult ASCII glyphs.
- Keep TUI structural glyphs and join-sensitive operators upright.
- Check font metadata, counters, advance widths, side bearings and a 16-pixel specimen.

## v0.2 optical review

- Inspect in Foot on the target OLED at actual 16/32-pixel em sizes and preferred compositor scale.
- Review tightly packed code, punctuation and italics beside both neighboring cells.
- Tune corrected glyphs after seeing grayscale and WRGB-aware terminal rasterization.
- Compare Ghostty and Kitty if available.

## v0.3 — AcPlus repertoire parity

- Import/recreate the remaining multilingual glyphs from the expanded AcPlus family.
- Preserve identical coverage and cell metrics in all four faces.
- Review extended Latin, Greek, Cyrillic and Hebrew styles individually.

## Optional terminal extras

- More Powerline glyphs and heavy Unicode box-drawing forms.
- Nerd Font patch build, kept separate from the core family.
