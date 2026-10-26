# Backstabbed++ integration contracts

These are navigation anchors from the current repository, not a frozen schema.
Inspect the current files before selecting IDs, coordinates, tags, or behavior.

## Source world and datapack

- Target version/loader: root `mmc-pack.json` (currently Java 1.21.4 / NeoForge).
- Source world:
  `.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/`.
- Game datapack: `datapacks/mcm.zip` inside that save. Read ZIP members directly
  or extract into a working directory. When updating the ZIP, preserve unrelated
  entries and replace entries rather than appending duplicate filenames.
- Source builds can be imported as a region/structure, but do not overwrite
  the game's `level.dat`, entire `region/` directory, or gameplay datapack with
  a downloaded world's versions.
- Local source downloads/previews: `map-previewer/maps/` (Git ignored).
- Private backups: `.minecraft/backups/` (Git ignored).

`data/yacht/` and `data/river_bank/` demonstrate recently integrated, separate
arena namespaces. Choose an unused ID after inspecting the current registry;
their current IDs (15 and 14) are examples, not reserved slots for a new map.

Useful members of `mcm.zip`:

| Purpose | ZIP member(s) |
| --- | --- |
| Register voting marker and map ID | `data/<arena>/function/register.mcfunction`; `data/mcm/function/load.mcfunction` |
| Activate selected map | `data/mcm/function/lobby/voting/end.mcfunction`; `data/<arena>/function/activate.mcfunction` |
| Voting poster | `data/mcm/function/lobby/voting/map_position_id.mcfunction` |
| Round start / time / player teleport | `data/mcm/function/maps/start.mcfunction`; `data/mcm/function/maps/tptospawn.mcfunction` |
| Per-round map behavior and containment | `data/mcm/function/game/loops/ingame.mcfunction`; `data/<arena>/function/functionality.mcfunction` |
| Arena geometry and death limits | `data/<arena>/predicate/arena.json`; e.g. `data/yacht/predicate/below_death_line.json` |
| Reset and unload | `data/mcm/function/maps/reset.mcfunction`; `data/<arena>/function/reset.mcfunction`; `restore_blocks.mcfunction` where used |
| Options, translations, spectator behavior | Inspect references to existing arena IDs/names under `data/mcm/` and the resource pack |

Existing vote markers use `MapVote`, a map-specific tag, and the `MapValues`
objective. The chosen map is tracked by `$selectedMap CmdData`; active rounds
currently use `$gamestate CmdData = 1`. Verify these before copying commands.

The current spawn selector looks for `PlayerSpawn` markers and tracks
`Occupied`. Existing activations tag runtime entities with `MapEntity` and an
arena-specific runtime tag. Do not let stale markers from another map enter
the spawn pool. Copy the relevant marker/cleanup contract, not old coordinates.
Check spectator and scrap spawns where the arena uses them.

Containment examples differ: River Bank returns out-of-region players to a
spawn; Yacht uses `mcm:game/playerdeath` and a separate death line. Follow the
intended map/game policy rather than assuming one consequence for every map.
Scope checks to queued, live, non-spectating participants in the selected map.
Yacht's arena predicate uses a union of position ranges to follow its shape.

## Resource-pack poster chain

Resource-pack source:
`.minecraft/resourcepacks/backstabbed-resource/`.

For namespace `<arena>`, the current custom poster pattern is:

1. `assets/<arena>/textures/posters/<arena>.png`: imagegen artwork.
2. `assets/<arena>/models/posters/<arena>.json`: model using that texture.
3. `assets/<arena>/items/posters/<arena>.json`: item definition referencing the
   model (`type: minecraft:model`).
4. `assets/minecraft/atlases/blocks.json`: include the new texture in the atlas,
   following current `single` entries for custom namespaces.
5. `mcm:lobby/voting/map_position_id`: the voting item display references
   `<arena>:posters/<arena>` through its `minecraft:item_model` component.

Use the existing model's orientation/display settings and artwork's proportions
so the poster fits its voting display. `docs/poster-art.md` contains the current
generation style and prompts (vertical 2:3 artwork); extend it with the new map's
actual final prompt. Preserve namespace credits and map-author attribution.
Inspect the finished PNG and its rendered display; validate it is not a missing
texture or a broken model.

## Verification and packaging

- `tests/test_yacht_spawns.py` demonstrates checking saved blocks, clear feet
  and head cells, and membership in the connected ship. Adapt that principle
  to the new arena instead of copying Yacht's block exclusions or hull seed.
  More complex standing surfaces require collision/state-aware checks.
- `tests/test_resources.py` checks voting item definitions, models, textures,
  PNG validity, and atlas stitching across registered voting posters.
- Add map-specific spawn/region tests where they catch actual regressions.
  Check points just inside and outside each boundary, excluded surrounding
  objects, and spawn/return points. Static predicate tests complement actual
  in-game escape tests.
- `make test` runs the existing Python checks.
- `make resourcepack` rebuilds the resource-pack ZIP from its source directory.
- `make release VERSION=<version>` builds client, resource-pack, and separate
  host-map archives; see root `README.md`. Keep the source world name unchanged.
- A source or import process that depends on a running world must finish and
  flush safely before packaging/backup. Avoid editing a save while Minecraft
  is writing it.
