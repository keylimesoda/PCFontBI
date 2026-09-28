# An IBM design brief, with hindsight

Preserve what works in the original: recognizable silhouettes, economical cells and predictable terminal geometry. Use later lessons about optical weight, italic construction and code legibility within a real pixel budget.

## Decisions

1. **The display grid is the design grid.** Every point lies on a 64-unit grid in a 1024-unit em. At 16px, a design pixel is exactly one screen pixel. Use square pixels on today's panels rather than trying to reproduce CRT proportions through fractional horizontal scaling.
2. **Regular is the reference.** The original ROM bytes remain unchanged, and the rendered Regular is tested against them pixel-for-pixel.
3. **Bold spends space carefully.** Add a whole pixel to selected narrow leading strokes. Leave horizontal bars alone where they are already dark. Preserve holes in B, 8 and round forms. The M/m/W/w masters receive explicit whole-pixel join edits so their dense centers do not simply become heavier slabs.
4. **Italic has its own lowercase.** A single-storey a, reshaped bowls, a short f foot, a controlled j descender and a simpler r give the style a distinct voice. Uppercase and numerals retain more of the VGA skeleton with a two-pixel stepped lean. All ASCII styles are stored as explicit bitmaps, not sheared at font-rendering time.
5. **Spacing is shared.** All four styles fit the same eight-pixel cell. Alphanumerics reserve the rightmost column, allowing mixed styles without collisions. Some inherited symbols intentionally span the whole cell.
6. **Terminal rules remain rules.** Borders, fills and Braille do not lean or grow in Bold. Powerline diagonals use pixel stairs. Adjacent block rectangles are united so even their shared edges do not produce gray seams.
7. **Judge small text first.** The specimen includes native text, potentially confusable shapes, mixed styles and both background polarities. Enlargements are nearest-neighbor views of those same native rasters.

## Editable masters

`strikes.json` contains Bold, Italic and Bold Italic. Each style maps a four-digit Unicode value to sixteen hexadecimal bytes, from the top row downward. Each byte contains eight one-bit pixels, most-significant bit on the left. For example, `18` lights columns 3 and 4 (zero-based). A full glyph string is 32 hexadecimal characters.

There are 95 printable ASCII masters per styled face. The initial weight and staircase candidates were derived from the ROM; lowercase Italic and selected crowded joins were then edited explicitly. The build reads the frozen masters. It does not regenerate them from the styling rules.

The remaining CP437 repertoire uses the conservative rules in `src/pixel_strikes.py`. Their visual refinement, especially accented letters, is a separate remaining task. Do not describe the entire repertoire as individually hand-drawn.

`src/grid_outlines.py` traces the union of the pixels into TTF contours. `src/export_bdf.py` exports the verified 16px raster and refuses to threshold gray pixels. The two output formats must reproduce the same bits.

## What changed from v0.2.1

| | v0.2.1 | v0.3.0 |
| --- | --- | --- |
| Source pixel at 16px | 0.828125 × 1 screen pixels | 1 × 1 screen pixels |
| Cell advance at 16px | 6.625px | 8px |
| Bold | Fractional outline expansion | Selected whole pixels |
| Italic | Continuous 6° oblique | Stepped bitmap masters, redrawn lowercase |
| Gray edge pixels | Expected from geometry | None in the verified native raster |
| Native bitmap export | None | Four one-bit BDFs |

We borrow the discipline of period bitmap work, not a claim of historical reconstruction. X11 Courier was a useful reference for restrained stroke weight and intentional diagonals. Its glyphs were not copied. This is a new VGA derivative for modern use.

## v0.4: icons and operators

`icons.json` holds 99 authored one-bit designs and their 384 upstream Nerd Font mappings. Familiar silhouettes win over logo detail; some language symbols become compact monograms. Existing VGA codepoints retain priority. The symbols remain upright in Bold and Italic, just like box drawing.

`src/ligatures.py` draws 29 operator sequences over a shared multi-cell canvas, then cuts each drawing into ordinary eight-pixel glyphs. Contextual substitutions preserve one glyph and cluster per character. Longest sequences run first; operator-run guards prevent partial substitutions inside unsupported longer combinations. Operators remain upright, with intentional whole-pixel Bold variants. This is a visual convenience, not a change to program text or token semantics.

The full Nerd Fonts repertoire lives in a separate companion. Its frozen one-bit masters are automatically fitted from the pinned upstream font, not individually redesigned. Four style records share identical outlines so fallback does not need synthetic bold or italic. This separates source licensing and lets the original core icons take precedence. Full coverage does not imply equal optical quality: intricate logos are candidates for future manual replacement.
