# Roadmap

## v0.3.0 — native pixel family (implemented)

- Restore square 8×16 pixels and preserve Regular's exact ROM raster.
- Store explicit ASCII Bold, Italic and Bold Italic bitmap masters.
- Redraw italic lowercase, refine dense joins, preserve counters and spacing.
- Ship four matching TTFs and one-bit BDFs under the PCFontBI name.
- Verify all 550 glyphs per face at 16px and 32px, including structural shapes.
- Show native text, mixed styles, light/dark backgrounds and a glyph atlas.

## Review on the target display

- Compare the actual 16px raster in Foot on the OLED with WRGB smoothing bypassed for this font.
- Verify effective physical pixel size at the user's preferred compositor scale.
- Inspect long reading sessions, dense punctuation and mixed regular/italic runs.
- Refine letters from actual screenshots; keep both native-size and enlarged evidence.

## Further optical work

- Refine CP437 accents and non-ASCII styles individually; the current fallback is conservative but not fully curated.
- Design additional native strikes only where a useful target size is identified. 20px and 24px need their own pixel decisions.
- Expand to AcPlus multilingual coverage without sacrificing explicit source attribution or pixel review.

The v0.2 half-pixel experiment and v0.2.1 antialiased outline revision remain available in Git history.
