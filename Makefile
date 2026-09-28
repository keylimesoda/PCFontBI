PYTHON ?= python3

.PHONY: all build test specimen clean
all: build test specimen

build:
	$(PYTHON) src/build_font.py
	$(PYTHON) src/export_bdf.py

test: build
	$(PYTHON) tests/test_fonts.py

specimen: build
	$(PYTHON) src/render_specimen.py

clean:
	rm -f fonts/PCFontBI-*.ttf fonts/PCFontBI-*.bdf docs/specimen.png docs/glyph-atlas.png
