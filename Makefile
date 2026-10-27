PYTHON ?= python3
UV ?= uv
LAUNCH_ARGS ?=
LOCAL ?= 0
VERSION ?=
EDIT_CONFIG ?= arena-editor/config.local.json
export VERSION

.DEFAULT_GOAL := all

# GNU Make treats the optional arena name as another goal. Handle this form
# separately so a name such as 'test' never accidentally runs another recipe.
ifeq ($(firstword $(MAKECMDGOALS)),edit)
ifneq ($(word 3,$(MAKECMDGOALS)),)
$(error Usage: make edit [arena_name])
endif
export BBE_EDIT_ARENA := $(word 2,$(MAKECMDGOALS))
export BBE_EDIT_CONFIG := $(EDIT_CONFIG)
.PHONY: edit $(BBE_EDIT_ARENA)
edit:
	$(UV) run arena-editor/editor.py edit
ifneq ($(BBE_EDIT_ARENA),)
ifneq ($(BBE_EDIT_ARENA),edit)
$(BBE_EDIT_ARENA):
	@:
endif
endif
else
.PHONY: all pack launch --local resourcepack map release preview test-preview test-editor test clean

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

test-editor:
	$(UV) run --no-project --with nbtlib==2.0.4 $(PYTHON) -m unittest discover -s arena-editor/tests -v

test:
	$(PYTHON) -m unittest discover -s tests

clean:
	rm -rf -- dist
endif
