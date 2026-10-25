PYTHON ?= python3
VERSION ?=
export VERSION

.DEFAULT_GOAL := all
.PHONY: all pack resourcepack map release test clean

all: pack

pack:
	$(PYTHON) scripts/build.py pack

resourcepack:
	$(PYTHON) scripts/build.py resourcepack

map:
	$(PYTHON) scripts/build.py map

release:
	$(PYTHON) scripts/build.py release

test:
	$(PYTHON) -m unittest discover -s tests

clean:
	rm -rf -- dist
