# PCFontBI v0.4 features

## Programming sequences

OpenType `calt` enables these 29 exact sequences:

`!=` `!==` `==` `===` `<=` `>=` `->` `<-` `=>` `<=>` `<->` `-->` `<--` `==>` `<==` `<<` `>>` `<<<` `>>>` `::` `:=` `&&` `||` `++` `--` `..` `...` `??` `?.`

Every character retains its own 512-unit advance and HarfBuzz cluster. The original text is unchanged. These are contextual substitutions rather than one wide replacement glyph. An editor may still choose its own cursor/selection rendering, so review that behavior in the actual application.

Only complete operator runs are matched: for example `====`, `----`, `!!=`, `>>>=`, `->>` and `???` remain literal. Disable `calt` to disable every contextual alternate. Other ASCII text is unaffected. BDF cannot represent these features.

## Nerd Font coverage

The four PCFontBI core faces contain 99 authored icon designs at 384 mapped positions. The original CP437 heart overlaps one mapping, giving 933 total core codepoints. See `design/icons.json` for every name, codepoint and sixteen-row bitmap.

The separate PCFontBI Symbols collection contains four style records, each with all 10,617 distinct named codepoints from the pinned Nerd Fonts 3.5.1 `glyphnames.json`. Aliases can share an outline. `nf-cod-blank` (U+EC03) is intentionally empty; every other mapped symbol has visible pixels. Automatic fitting can make distinct complex symbols look alike on this small grid.

`./install.sh` installs four core TTFs, one four-face TTC and a per-user Fontconfig rule which appends PCFontBI Symbols when PCFontBI is requested. Fontconfig selects the core whenever it has a glyph. For applications that bypass Fontconfig, configure PCFontBI Symbols as the fallback family explicitly; installing only a core TTF does not give full Nerd Font coverage. Keep both families at the same physical pixel size. Every symbol uses a single 8px cell at 16px.

## Application support

- Foot: icons via fallback; literal operators. Its grapheme shaping does not join programming sequences across characters.
- Kitty: contextual shaping supported. `disable_ligatures` controls cursor-related display and `font_features` can override features.
- Ghostty: contextual shaping supported. `font-feature = -calt` disables these alternates.
- Editors: use a shaping-capable renderer and enable contextual alternates. Application settings differ.

The automated tests exercise HarfBuzz, FreeType and Fontconfig, not these applications' full UI paths. Fractional display scale or non-native font sizes can still soften or distort output.

Official references: [Foot release notes](https://codeberg.org/dnkl/foot/src/branch/master/CHANGELOG.md), [Kitty configuration](https://sw.kovidgoyal.net/kitty/conf/), [Ghostty configuration](https://ghostty.org/docs/config/reference), [HarfBuzz default features](https://harfbuzz.github.io/shaping-opentype-features.html), [Nerd Fonts mappings](https://github.com/ryanoasis/nerd-fonts/tree/v3.5.1).
