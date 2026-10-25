PYTHON ?= python3

.DEFAULT_GOAL := all
.PHONY: all pack resourcepack clean

all: pack

pack:
	$(PYTHON) scripts/build.py pack

resourcepack:
	$(PYTHON) scripts/build.py resourcepack

clean:
	rm -rf -- dist
