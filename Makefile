PYTHON ?= python3
VERSION ?=
export VERSION

.DEFAULT_GOAL := all
.PHONY: all pack resourcepack map release preview test-preview test clean

all: pack

pack:
	$(PYTHON) scripts/build.py pack

resourcepack:
	$(PYTHON) scripts/build.py resourcepack

map:
	$(PYTHON) scripts/build.py map

release:
	$(PYTHON) scripts/build.py release

preview:
	node map-previewer/preview.mjs --open

test-preview:
	npm --prefix map-previewer test

test:
	$(PYTHON) -m unittest discover -s tests

clean:
	rm -rf -- dist
