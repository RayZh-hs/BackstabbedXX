# Project scripts

This directory contains reusable development and release tools:

- `build.py`: build the client modpack, resource pack, and versioned map archives.
- `launch.py`: launch the working copy, optionally with a disposable local playtest.
- `local_playtest.py` and `local_playtest/LocalPlaytest.java`: stage the playtest
  world and build its helper mod.
- `nbt.py`: read and update world names for map packaging.
- `release_notes.py`: generate release notes from Git history.

Completed one-time map imports, repairs, generators, and datapack migrations
have been removed. Their results are already saved in the tracked world,
datapacks, and resource-pack source. Arena manifests and verification records
remain in `docs/arenas/`; the retired scripts are available in Git history.

For future arena changes, use the project skills linked from `AGENTS.md` and
the maintained `arena-editor/` and `map-previewer/` tools.
