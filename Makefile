PYTHON ?= python3

.PHONY: all build test specimen clean
all: build test specimen

build:
	$(PYTHON) src/build_font.py

test: build
	$(PYTHON) tests/test_fonts.py

specimen: build
	$(PYTHON) src/render_specimen.py

clean:
	rm -f fonts/*.ttf docs/specimen.png
