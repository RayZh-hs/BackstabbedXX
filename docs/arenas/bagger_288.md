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

A living, queued participant outside the mask, in a fluid block, or in a waterlogged
block returns to `[28673.5, -40, 28715.5]`, a validated spawn. Feet and head fluid
checks use actual 1.21.4 block tags. Spectating, dead, unqueued/lobby players, other
maps and reset states are excluded. Waiting players acquire an arena participant
tag only after entering the play region; active rounds enforce containment during
grace and normal play. No global world border or new physical barriers are used.

## Spawns and lifecycle

There are **24 distinct player/scrap spawns** and one spectator marker. Each actual
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

`make test` passes **37 tests**. The maintained previewer passes **8 tests**.
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
