# Bagger 288

Bagger 288 by **KAIZEN87** is map **18**, namespace `bagger_288`.
It is selectable in normal lobby voting and the map-toggle board. Direct selection,
while no round is active, uses `/function bagger_288:select`.

## Source and version

- Original post: https://www.minecraftmaps.com/52537-bagger-288-survival-base
- Download: `map-previewer/maps/52537-bagger-288-survival-base/source.zip`, SHA-256 `b264865bbd42716710382518af7940c44120acfee86606f333bec06d7161365a`.
- Original world: `map-previewer/maps/52537-bagger-288-survival-base/world/Bagger 288 by Kaizen87`. It remains unchanged.
- Actual source level/chunk version: **1.21.8 / DataVersion 4440**.
- Target: **Minecraft Java 1.21.4 / DataVersion 4189**, NeoForge profile **21.4.158**.
- The source license notices and creator credits are retained in the download and
  inside the game datapack at `data/bagger_288/`. Notices state all rights reserved and
  personal use; the current terms link is https://www.patreon.com/posts/license-usage-70505678.
  The integration/release checks described here create local artifacts.

All actual imported palette states were checked against 1.21.4's state definitions.
Source sign/item text components were converted to 1.21.4 JSON strings. Downloaded
level metadata, datapacks, POIs and natural structure references were not installed.
The selected source chunks contain no decorative entities requiring translation;
unrelated natural mobs and cave minecarts were not imported. Source command blocks
are inspected and disabled by the importer; no source commands took control.

## Placement and playable region

The transform is `(x, y, z) → (x + 28672, y, z + 28672)`, without rotation or scale.
The main build is bounded by source `[-87, -51, 16]` through `[81, 42, 76]`,
or destination `[28585, -51, 28688]` through `[28753, 42, 28748]`. This envelope measures
**169 × 94 × 61 blocks** (X × Y × Z). It records the main architecture;
the source chunks also preserve the surrounding base/terrain context.

The import adds **72 chunks** in previously unused region files:
`region/r.55.56.mca`, `region/r.56.56.mca`.
Block states and all **1195 block entities** in those
chunks are retained, including signs, banners, inventories and decorative details.

The playable area follows **three main-body working decks**. Containment uses
**243 per-height rectangles** derived from the connected architecture, with a
one-block movement margin. The inclusive outer envelope is X 28584…28755,
feet Y -50…47, Z 28687…28750; the union narrows
at each height. This envelope alone is not the arena. Detached scenery, the ocean,
low source ground, accidental caves and other dimensions are excluded.

A living, queued participant outside the mask, in fluid, or with feet at/below
**Y −45.5** is eliminated through `mcm:game/playerdeath`. The lower wheel/tread
footprint is checked first: falling onto it announces **`"<player>" got squashed
by giant wheels`**. Other falls announce `"<player>" fell off Bagger 288`.
The wheel footprint comes from the saved tread blocks at Y ≤ −47, expanded by
the player's 0.3-block radius; it catches players before the highest tread landing
at Y −46. Exact hazard boxes are in [bagger_288_wheels.json](bagger_288_wheels.json).
The working decks at Y −40 and above remain safe.

Boundary-return teleportation is removed, including the arena-editor-generated
tick path. Both tick paths use the same ordered checks. Feet/head fluid checks use
actual 1.21.4 block tags. Spectating, dead, unqueued/lobby players, other maps and
reset states are excluded. Waiting players acquire an arena participant tag only
after entering the play region; the rules also cover grace and normal play.

## Spawns and lifecycle

The original integration had **24 distinct player/scrap spawns** and one spectator
marker. The current arena-editor override contains **23 player/scrap spawns** and
one spectator marker; its edited positions, rotations, blocks and bounds are
preserved by this repair. Each actual
saved destination has collision-shape clearance for a 0.6 × 1.8 player, full-footprint
support at its exact height (including carpets/slabs), no fluid/damage hazard, at
least two supported local exits, and membership in the connected build. Exact
positions, exit checks, predicates and source/destination transforms are recorded
in [bagger_288.json](bagger_288.json).

Voting loads 72 chunks and schedules guarded activation after
loading. Activation rebuilds the marker pool without duplicates. Reset cancels
pending activation, removes the map runtime/participant tags and restores
**3007 original interactive states, dry cells or block-entity records**.
All chunk-load rectangles stay within the vanilla 256-chunk per-command limit.
Reload preserves an active round; inactive reload/reset unloads its arena chunks.
Original cave spawners outside the play region retain their saved blocks and NBT;
round setup delays them so they do not introduce mobs during play.

## Voting poster

The built-in imagegen poster reuses the webpage excavator as an intricate black-ink-on-white engineering drawing. The large title sits in a bottom title block; inaccurate generated dimension numbers were removed.

- Texture: `.minecraft/resourcepacks/backstabbed-resource/assets/bagger_288/textures/posters/bagger_288.png`.
- Item/model: `assets/bagger_288/items/posters/bagger_288.json` and `assets/bagger_288/models/posters/bagger_288.json`.
- Atlas: `assets/minecraft/atlases/blocks.json`.
- Voting display: `mcm:lobby/voting/map_position_id`, map ID 18.
- English/Simplified Chinese labels: `assets/bagger_288/lang/`.

The model uses the established flat 2:3 face, model Z=8 and display X offset −0.01,
placing the face in front of each booth backing. Final prompts, methods, source
images, attribution and asset hashes are in [kaizen_posters.json](kaizen_posters.json).

## Compatibility repair and backup

Bagger 288 needs no block substitutions or geometry repair. Its original architecture
and decorative block states are preserved.

A checksum-verified full-save backup was taken while the host save had no writer:

```text
.minecraft/backups/map-integration/20261026T165452608726Z-kaizen-bases-before-import-7d3cd058.zip
SHA-256: 2f87de1dd768d4277bb17d5642ac9f164f757bdcbec657be7e0bbcac75c96dbd
923 source files
```

The original affected source worlds were also snapshotted before the repair:

```text
Meridian: .minecraft/backups/map-integration/20261026T170707209508Z-meridian-before-compatibility-5efef739.zip
SHA-256: 5a6be47e2ddd9a9218b3f592fec5875dbb37f72acc465cc27d76916138ada864
Underwater: .minecraft/backups/map-integration/20261026T170707650861Z-underwater-before-compatibility-507e2c19.zip
SHA-256: 1c7ed2876fbb12bf38dcd98eff776113118217e4232884a3dbd5774140a9fdcc
```

To restore, stop the affected Minecraft writer, verify the archive with
`.agents/skills/backstabbed-map-creator/scripts/backup_world.py --verify <archive>`,
move the current world aside, and extract the archived world folder under its
original parent. Retain the backup and moved-aside save. Do not extract the
archive's top-level `backup-manifest.json` into a world. Resource-pack changes can
be reverted separately from version control. The original downloaded archives
remain available for recovery.

## Verification

The 2026-10-27 containment repair passes **52 repository tests**, including actual
saved tread landing surfaces, safe spawn volumes, editor override handling, and
physical Underwater Base escape routes. The following live evidence also records
the original integration checks; updated repair evidence is stored separately at
`map-previewer/maps/containment-fix/runtime/`.

The maintained previewer previously passed **8 tests**.
The repair's isolated vanilla 1.21.4 server validated all **23 edited Bagger
spawns**, wheel and general fall deaths through both tick paths, spectator/lobby/
inactive-map guards, and a real client gravity fall into the wheels. All wheel
deaths displayed `"SealTester" got squashed by giant wheels` exactly, including
the automatic gravity test. The same run checked **24 Underwater spawns**, six
real client hatch right-clicks, and reset/reload/reactivation. These are automated
vanilla checks; the NeoForge client profile and human multiplayer balance were
not playtested for this repair.
Both repaired maps also completed normal **four-player round starts**, role
assignment (one murderer and three innocents), and the full grace period. Results
are recorded in `round-results.json` in the repair's runtime directory.
The repository checks validate all 72 installed spawns, collision shapes, connected
build membership, actual boundary predicates, exclusions, lifecycle scope,
compatibility substitutions and the complete poster reference chain.

The isolated live checks passed **72 stable destination spawns**, **18 escapes**,
**18 scope guards**, **112 saved replacement checks**, and **three normal four-player
rounds** (one per arena, including role assignment and the completed grace period).
Underwater Base's water escape test deliberately enters water inside its allowed
geometry mask. Twenty normal voting shuffles included all three new maps, with
exactly seven displays on each shuffle. Repeated registration and reset before
scheduled activation also passed.

`make release VERSION=1.1.1-alpha-kaizen-bases` built and CRC-verified the client,
resource-pack and separate host-world ZIPs in `dist/`. No release/tag was published.
Against the full pre-import snapshot, the only modified existing world file is
`datapacks/mcm.zip`; the other **922 original files** remain byte-for-byte unchanged.
Seven new region files hold the imported builds.

Live evidence is retained under `map-previewer/maps/kaizen-bases/runtime/`:
`runtime-results.json`, `compatibility-results.json`, `round-results.json`,
server/client logs, and graphical client screenshots. The destination spawn views
are also available through the maintained Lodestone previewer under
`map-previewer/maps/kaizen-bases/spawn-previews/`.

The live checks use an isolated **vanilla Minecraft Java 1.21.4** server and graphical
client, with automated players. They cover normal selection/loading, all 24 spawns
per arena, escapes (including another dimension), spectator/dead/unqueued/inactive
and other-map guards, reload, repeated activation, reset, and reactivation. The
NeoForge profile itself and human multiplayer balance are not verified by those
checks. No user save or existing client is used as the test world.

Reproduction tools are `scripts/import_kaizen_bases.py`,
`scripts/plan_kaizen_geometry.py`, `scripts/plan_kaizen_spawns.py`, and
`scripts/configure_kaizen_bases.py`. They use preserved source/previews under the
ignored `map-previewer/maps/` directory. Import refuses existing destination
regions; back up the stopped save before applying any later map repair.

## Containment repair backup (2026-10-27)

The stopped full save was snapshotted and checksum-verified before installation:

```text
.minecraft/backups/map-integration/20261027T101411138725Z-bagger-underwater-before-seals-74059f54.zip
SHA-256: 57a442c4f3382d6da3b971843bbaab577f26280aeb28b79d6811623d99e76454
935 files
```

Use the verify/move-aside/extract procedure above to restore. The backup includes
the existing arena-editor changes. The repair changes only `datapacks/mcm.zip`
and Underwater Base's `region/r.64.63.mca` inside the save; Bagger's block, entity
and POI files retain their exact pre-repair bytes. Death translations are also
updated in the resource-pack source. The generator is
[arena_containment.py](../../scripts/arena_containment.py); the bounded installer
is [update_arena_containment.py](../../scripts/update_arena_containment.py).
