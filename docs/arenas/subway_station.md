# Subway Station

Subway Station is registered as map **16**, namespace `subway_station`, in the
Backstabbed++ source save. The full build is preserved. All 24 player spawns use
the connected central platform; no crossings, barriers, terrain edits, or other
geometry repairs have been applied.

The second-floor north and south concourses now have the user-requested
furnishings described below. The original architecture, shops, stairs, platform
spawns, carriage links and unrestricted boundary behavior are retained.

## Source and attribution

- Build: **Subway Station - Original Build**, by **KnotXackly**.
- Original post: https://www.minecraftmaps.com/51929-subway-station-original-build
- Reuse terms recorded during source preview: reuse in builds/maps with credit
  to KnotXackly and a link to the original map post when publishing.
- Original archive: `map-previewer/maps/subway-station/source.zip` (preserved,
  ignored by Git), SHA-256
  `f4d5ce673917aff4350e12ee981d9c63698705fdc42670cd83fdc41b3c12e7d6`.
- Original save: `map-previewer/maps/subway-station/world/Train Station`.
  Actual level/chunk version: **1.20.4**, DataVersion **3700**.
- Target profile: Minecraft **1.21.4**, NeoForge **21.4.158**, from `mmc-pack.json`.
- Publication credits also ship inside `mcm.zip`, at
  `data/subway_station/credits.txt`, and in the resource-pack poster model.

## Import and play region

The coordinate transform is `(x, y, z) → (x + 20480, y, z + 20480)`, with no
rotation or scale. Visible source bounds `(-12, -60, -214)` through
`(57, -27, 169)` become `(20468, -60, 20266)` through `(20537, -27, 20649)`.
The visible build measures **70 × 34 × 384 blocks**, with a **26,880 m²** footprint
and 98,245 visible blocks. The preview crops Y to −60…−27; the import preserves
all sections of the selected chunks, including invisible blocks and the base.

The 125 imported chunks occupy previously unused region files `r.39.39.mca`,
`r.39.40.mca`, `r.40.39.mca`, and `r.40.40.mca`. Their inclusive chunk envelope is
X **20464…20543**, Z **20256…20655**. All 238 block entities were preserved:
148 signs, 16 hanging signs, 24 barrels, 16 hoppers, 8 furnaces, 4 banners, and
22 command blocks. The source contains no decorative entities to import.
The three nonempty spawn/teleport commands were cleared, and all command blocks
were made nonautomatic. The source level metadata/datapacks were not installed.

The recorded arena predicate covers the main station, with X **20470.3…20535.7**
at its lowest band, Z **20356.3…20555.7**, and player-feet Y **−59…−28**. Nine
vertical bands narrow the width with the vaulted ceiling. The low track beds,
tunnel extensions, roof/exterior, and other dimensions are outside this recorded
footprint. **Automatic boundary-return teleportation is disabled by user
request.** The predicate remains for documenting the footprint and validating
spawns. It does not move players. The original station geometry is unchanged;
no physical barriers or global world border were added.

The central platform gives the spawn pool one connected set of walking routes.
The original track beds are 1.5 blocks below the platforms, so separate side
platform spawns would depend on crossing the original trains and dividers.
Keeping all spawns on the central platform avoids redesigning those routes.
The complete station remains imported, with the surrounding main-hall surfaces
available inside the arena predicate. Exact spawns, import hashes, source
commands and provenance are recorded in [subway_station.json](subway_station.json).

Registration is idempotent. Voting loads 5 × 25 chunks and schedules activation
after loading. Activation removes the old runtime spawn pool and creates
24 player/scrap markers plus one spectator marker. Reset cancels pending
activation, removes station runtime markers, restores 3,858 original interactive
states/container inventories, and unloads the arena chunks through the shared
map lifecycle. Reload preserves an active round and cleans up an inactive arena.

For a direct local selection, while no round is active:

```mcfunction
/function subway_station:select
```

## Travel between carriages

The four trains each have six carriages. At each internal carriage end,
right-click the aqua **Previous carriage / Next carriage** text to move into
the adjacent carriage on the same train. Each of the five joins has a link in
both directions: **40 clickable labels** in total. Labels are translated into
English and Simplified Chinese, with English fallbacks for older client packs.
The first and last carriages have no link leading beyond the train.

These are voluntary, local teleports through the existing end walls. They move
only the clicking player, retain the player's view direction, and land on a
validated aisle floor in the next carriage. Queued, living participants can use
them while this arena is selected and waiting or playing. Spectators, dead
players, distant players, other maps and ended rounds cannot use them.

The implementation uses `text_display` labels and `interaction` hitboxes with
player-specific advancement rewards. It adds no blocks. Activation and active
round reload refresh the labels without duplication; the existing runtime tag
removes both labels and hitboxes on reset. Train positions, wall positions and
all destinations are recorded in [subway_station_carriages.json](subway_station_carriages.json).
The generator is `scripts/subway_station_carriages.py`; the original import
configuration also invokes it so reconfiguration preserves this behavior.

For an existing save, stop its writers and take the full backup described
below before running `python3 scripts/update_subway_station.py`. Reload the
datapack afterward. An inactive reload follows the game's normal lobby reset;
select the station again to inspect it. During an active station round, the
reload hook refreshes only the carriage links and preserves the round.

The trains remain stationary. Smooth display-entity animation supplies no
collision surface to carry players. A moving train that supports walking and
combat needs a moving-collision implementation in a compatible mod.

## Second-floor furnishings

The 26 October 2026 furnishing update now contains **581 blocks** in the two upper
concourses, starting at feet Y **−48**. These are additions into air or invisible
light cells; no original architectural block or block entity is replaced.

- Twelve five-seat bench rows with iron armrests, planted dividers and planters.
- Six cyan ticket machines and four red/yellow drinks and snack cabinets.
- Two departures/network information boards and 26 waxed information/menu signs.
- Four floor-standing barrel tables with chairs, a north coffee counter and a south
  books/news counter with shallow canopies and lanterns.
- Four waste bins. All decoration uses vanilla blocks and needs no skin service.

The materials follow the station's warm wood and dark stone accents. Reference
photographs were reviewed from [Sellex's STC interchange seating project](https://www.sellex.es/es/proyectos/terminales/intercambiador-stc)
and [Omrania's Western Station interiors](https://omrania.com/insights/metro-station-interior-design-enhances-comfort-and-sustainability/):
long station benches, grouped ticket machines, legible information boards and
small refreshment areas arranged around open circulation routes. Local copies
of the reference images are retained only in the ignored preview directory.

The bounded recipe is [subway_station_furnishings.mjs](../../scripts/builds/subway_station_furnishings.mjs),
generated with the installed **minecraft-builder-skill** and DataVersion **4189**.
The exact palette, destination coordinates, references and backup record are in
[subway_station_furnishings.json](subway_station_furnishings.json). Regenerate it
from the installed skill directory with:

```sh
node scripts/run-build.mjs \
  '/home/rayzh/Documents/AppData/minecraft/Modpacks/Backstabbed++/scripts/builds/subway_station_furnishings.mjs' \
  --out-dir '/home/rayzh/Documents/AppData/minecraft/Modpacks/Backstabbed++/map-previewer/maps/subway-station/furnishings' \
  --data-version 4189
```

The importer, `scripts/furnish_subway_station.py`, defaults to a read-only plan.
Installation requires `--install --backup <verified-current-save.zip>`, holds
Minecraft's save lock, and refuses to overwrite existing architecture. Take a
new full backup before any later installation. It preserves the exact stored
bytes of untouched chunks and all unrelated chunk tags/block entities. Only
changed chunk palettes and lighting are rewritten. Round activation/reset also
restore **93** furniture states (buttons, decorative trapdoors and four barrels)
and clear the barrel inventories through
`subway_station:furnishings/restore`; reconfiguration preserves that hook.

Validation for this update:

- All **31** repository tests pass. Saved block states, sign NBT, six-block-wide
  central aisles, cross-routes to the stairs and connected upper-floor walking
  regions are covered. No new isolated walkable pockets were introduced.
- For the initial furnishing pass, an isolated **Minecraft Java 1.21.4** server checked every furnishing after
  loading, explicit neighbour updates, round reset, datapack reload and arena
  activation: **2,945** successful block checks. Sign text and waxing were
  checked through the server too. This was an automated server check, not a
  human multiplayer playtest or a graphical NeoForge-client check.
- Byte comparisons against the full backup confirm that only the four metro
  region files and `datapacks/mcm.zip` changed among all **944** save files.
  Only the existing station restore function and its new furnishing subfunction
  differ inside the ZIP. Unrelated blocks, entities and chunk metadata are
  preserved.
- `make resourcepack map` verifies packaging of the updated host save.

Installed-save exports, north/south previews, screenshots, reference photos and
the detailed installation/runtime/preservation reports are under
`map-previewer/maps/subway-station/furnishings/` (Git ignored). Open either
`installed-north.nbt` or `installed-south.nbt` with the maintained previewer.

Before the first write, Minecraft saved and closed and the backup helper
verified the complete save under `dev/`:

```text
dev/world-backups/20261026T144800716343Z-subway-before-second-floor-furnishings-7ae36760.zip
SHA-256: 7ab3dab514547780adc07d52b0b00aa02d398244e52489188f3bc46935455e3f
944 files, approximately 163 MiB compressed
```

Verify it with the backup helper's `--verify` option. To restore, stop Minecraft,
move the current save aside, and extract the archive's world folder back under
`.minecraft/saves/`; retain the archive and moved-aside save. The top-level
`backup-manifest.json` is backup metadata and does not belong inside the world.

The subsequent table correction replaces the four fence-and-slab tables with
single barrels sitting on the floor and removes their tabletop flower pots.
It changes exactly **12 block positions** in four chunks, with two region files
and the furniture reset subfunction affected. The chairs retain their positions.
The saved-block and route tests also verify that the two blocks above every
barrel are air. Barrel inventories are emptied during round reset. The previous
placement manifest is required through `--previous-manifest` when installing
this revision, so only exact, previously authored furniture may be replaced or
removed. A fresh verified full-save backup was taken before this correction:

```text
dev/world-backups/20261026T151252631494Z-subway-before-barrel-tables-fe8580c7.zip
SHA-256: cfc72133bed7652575acb842b3e739eb8a64a1d8c495d60feaf4355ca94a01d9
944 files
```

The correction's plan, installation and preservation reports are retained under
`dev/metro-furnishings/tables/`; its preview is under
`map-previewer/maps/subway-station/furnishings/table-fix/`. All 31 repository tests
pass after the table correction, and the host-map archive has been rebuilt.

## Voting poster

The 1024 × 1536 PNG was generated with **OpenAI built-in imagegen**, inspected,
installed, and checked in a graphical Minecraft 1.21.4 client. Its final prompt
is in [poster-art.md](../poster-art.md#subway-station-prompt).

- Texture: `.minecraft/resourcepacks/backstabbed-resource/assets/subway_station/textures/posters/subway_station.png`
- Model: `assets/subway_station/models/posters/subway_station.json`
- Item definition: `assets/subway_station/items/posters/subway_station.json`
- Atlas: `assets/minecraft/atlases/blocks.json`
- Vote display: `mcm:lobby/voting/map_position_id`, map ID 16.
- English and Simplified Chinese labels/messages: `assets/subway_station/lang/`.

The flat model is placed at X 27.99 in the first booth, in front of its X=28
backing block. Poster cleanup precedes display creation. Both details have
regression coverage and were checked through repeated normal voting shuffles.

## Verification

The carriage update was exercised in an isolated **Minecraft Java 1.21.4**
server using actual client interaction packets: all **40 directed links**,
repeated clicks, inactive/other-map/spectator/dead-player guards, movement
across the old boundary, active reload, reset and reactivation passed.
All destinations were checked against the saved blocks and collision shapes,
including exact support on the bottom-half iron trapdoor floors and a clear
step into each aisle. Evidence is retained under
`map-previewer/maps/subway-station/carriage-update/runtime-results.json`.

The following records describe the original integration, before boundary
teleportation was disabled and carriage links were added:

- `make test`: **24 passed**, including six station checks for actual saved
  collision volumes, full-cube support, platform membership, connected walking
  routes, boundary edges/exclusions, lifecycle scope, disabled source commands,
  and poster placement/cleanup. Collision fixtures come from the installed
  Minecraft Java 1.21.4 `minecraft-data` / `prismarine-block` state geometry;
  unknown states fail instead of being assumed passable.
- `npm --prefix map-previewer test`: **8 passed**.
- `make release VERSION=1.1.1-alpha-subway-station`: client, resource-pack and
  separate host-map archives built locally. This is a local verification build;
  no Git tag or published release was created.
- Minecraft **1.21.4 vanilla server and graphical client**, using a separate
  copied save: normal voting/poster display, selection, repeated activation,
  role assignment, grace period, active round, all 24 final destination spawns,
  walking, boundary returns, reload and reset were exercised.
- Actual active-round escape tests: north/south tunnels, west/east exterior,
  low track bed, above the roof, and the Nether. All returned the live client
  to the safe central position. Scope checks excluded spectating/dead players,
  inactive states and another selected arena.
- The original source save's existing 918 non-datapack files are byte-for-byte
  unchanged against the verified pre-import backup. Only the gameplay ZIP and
  four new region files change the source save. Unrelated ZIP entries are
  preserved, with no duplicate ZIP member names.

The NeoForge 21.4.158 profile itself was not launched. The client/server tests
above establish actual vanilla 1.21.4 behavior; they are not a multiplayer
balance test with human players.

Local evidence is retained under
`map-previewer/maps/subway-station/integration/`, including destination preview
NBT/metadata, `runtime-spawns.json`, `runtime-escapes.json`, `runtime-voting.json`,
`runtime-walk.json`, preservation checks, screenshots and the test-server logs.
The destination preview can be opened with:

```sh
npm --prefix map-previewer run preview -- \
  --nbt "$PWD/map-previewer/maps/subway-station/integration/destination.nbt" --open
```

## Backup and recovery

Before the carriage update, a checksum-verified full snapshot of the working
save was taken while its host process was stopped:

```text
.minecraft/backups/map-integration/20261026T132949950707Z-subway-before-carriage-links-a2ea7838.zip
SHA-256: f41295867a9058802b41f8d7427852eba2b9894d734a0583e15741c51b7225e3
944 source-save files
```

The original language files are retained separately in
`map-previewer/maps/subway-station/carriage-update/original-lang/`. To roll back
this update, use this full-save snapshot and those language files; keep
Minecraft stopped while restoring. Rebuild the resource pack afterward.

A full, checksum-verified snapshot was taken before importing:

```text
.minecraft/backups/map-integration/20261026T081117381036Z-subway-before-import-120bb3a8.zip
SHA-256: 5212010a51f4ab0a4547a184bdb303f3847db5fb5a8f7a8a87477350fbd2d8bd
919 source-save files
```

To verify it again:

```sh
python .agents/skills/backstabbed-map-creator/scripts/backup_world.py \
  --verify '.minecraft/backups/map-integration/20261026T081117381036Z-subway-before-import-120bb3a8.zip'
```

To restore, stop Minecraft and any server writing this save, verify the archive,
move the current world folder aside, and extract the archived world folder back
under `.minecraft/saves/`. Retain the archive and moved-aside world. The backup
contains a top-level `backup-manifest.json` as well as the world folder; only
the world folder belongs under `saves/`. Restore the matching resource-pack
source from version control if reverting its new poster references too.

The optional importer is `scripts/import_subway_station.py`; it requires the
preserved download, uses `nbtlib`, and refuses occupied destination region files.
`scripts/configure_subway_station.py` installs the lifecycle/resource references
without replacing unrelated datapack entries. Keep Minecraft stopped when
using either on the source save.
