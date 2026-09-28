# Attribution

## IBM VGA raster design

This project derives the Regular glyph geometry from the IBM VGA 8x16 hardware raster character set.

The raw source payload included here as `upstream/VGA8.F16.b64` decodes byte-for-byte to `VGA8.F16`, obtained from VileR's `vga-text-mode-fonts` collection:

https://github.com/viler-int10h/vga-text-mode-fonts/blob/master/FONTS/PC-IBM/VGA8.F16

SHA-256 of the decoded source file:

`a8bad6fd78475a6bc2a05438c19207a9bb8c0f4f4099f60384e158cdc3eba580`

VileR / int10h.org also publishes the Oldschool PC Font Pack, including aspect-corrected (`Ac`) and expanded (`Plus`) TrueType derivatives:

https://int10h.org/oldschool-pc-fonts/

The Oldschool PC Font Pack is published under Creative Commons Attribution-ShareAlike 4.0 International.

## This derivative

The TUI family conversion, style generation, Unicode terminal additions, tests, and documentation are a derivative work produced for keylimesoda. They are distributed under the same CC BY-SA 4.0 terms.
