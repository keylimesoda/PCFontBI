# Pinned Nerd Fonts inputs

- Project: [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts), Ryan L McIntyre and the original icon-set authors.
- Version: **3.5.1**.
- Revision: `b894ea7803af6aade63d60a4381e006098ec9c4d`.
- Source font: `patched-fonts/NerdFontsSymbolsOnly/SymbolsNerdFontMono-Regular.ttf` at that revision.
- SHA-256: `fe471e538392f51910faab985fa8e192a39dd3426125edd15b71b3680df0e749`.

`glyphnames.json.gz` is the upstream name/codepoint manifest, compressed without a variable timestamp. Its 10,617 distinct named codepoints define the coverage contract; this is not a claim to include every unassigned private-use character.

`pixel-symbols.json.gz` stores our derived one-bit bitmap masters plus source metadata. To regenerate them, run `python tools/import_nerd_symbols.py` (network required) or supply the matching downloaded font with `--source PATH`. The importer verifies the source hash, renders each glyph at 128px, crops its ink bounds, preserves aspect ratio while fitting within 7×12 pixels, BOX-resamples, thresholds at the lower of 80/255 or half peak coverage, and centers on an 8×16 cell. Grayscale exists only in that import stage. The resulting stored masters and font outlines contain only on/off pixels. FreeType/Pillow version changes can affect import results; ordinary builds use the checked-in masters offline.

These are automatic fits, not 10,617 individually authored pixel icons. Detailed logos can lose distinguishing features. `nf-cod-blank` U+EC03 remains deliberately blank; the importer rejects unexpected empty symbols. The build gives the derivative the new family name **PCFontBI Symbols** and stores four style records with identical symbol shapes in one TTC. No IBM ROM artwork is copied into this companion.

## Attribution and licenses

The Nerd Fonts collection's MIT notice is retained in `LICENSE`. The unmodified `UPSTREAM-README.md` records its icon-set authors, source URLs, versions and license declarations, including its unresolved Font Logos licensing label. Available set-specific notices from the pinned repository are retained under `licenses/`. Those source terms are preserved; this conversion does not relicense the imported artwork under the core family’s CC BY-SA license. See the linked upstream projects for the authoritative licensing of each icon set.

The core's `design/icons.json` instead contains original drawings with Nerd Font-compatible mappings. It is not derived by thresholding these imported masters.
