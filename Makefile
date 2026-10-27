PYTHON ?= python3
UV ?= uv
LAUNCH_ARGS ?=
LOCAL ?= 0
VERSION ?=
export VERSION

.DEFAULT_GOAL := all
.PHONY: all pack launch --local resourcepack map release preview test-preview test clean

all: pack

pack:
	$(PYTHON) scripts/build.py pack

launch: pack
	$(UV) run --no-project --with portablemc==4.4.1 $(PYTHON) scripts/launch.py $(if $(or $(filter 1,$(LOCAL)),$(filter --local,$(MAKECMDGOALS))),--local) $(LAUNCH_ARGS)

# GNU Make requires the option separator: make launch -- --local
--local:
	@:

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
