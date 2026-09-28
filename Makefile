PYTHON ?= python3

.PHONY: all build test specimen clean
all: build test specimen

build:
	$(PYTHON) src/build_font.py
	$(PYTHON) src/build_symbols.py
	$(PYTHON) src/export_bdf.py

test: build
	$(PYTHON) tests/test_fonts.py
	$(PYTHON) tests/test_features.py

specimen: build
	$(PYTHON) src/render_specimen.py
	$(PYTHON) src/render_features.py

clean:
	rm -f fonts/PCFontBI-*.ttf fonts/PCFontBI-*.bdf fonts/PCFontBI-*.ttc docs/specimen.png docs/glyph-atlas.png docs/features.png
