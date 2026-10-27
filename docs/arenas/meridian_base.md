# Meridian Base

Meridian Base by **KAIZEN87** is map **17**, namespace `meridian_base`.
It is selectable in normal lobby voting and the map-toggle board. Direct selection,
while no round is active, uses `/function meridian_base:select`.

## Source and version

- Original post: https://www.minecraftmaps.com/52535-meridian-base
- Download: `map-previewer/maps/52535-meridian-base/source.zip`, SHA-256 `a0d66e3e936a4eac41ef92bb494897275c42f4a72a3e7f2aed6d5ed490df1875`.
- Original world: `map-previewer/maps/52535-meridian-base/world/Meridian Base by Kaizen87`. It remains unchanged.
- Actual source level/chunk version: **1.21.8 / DataVersion 4440**.
- Target: **Minecraft Java 1.21.4 / DataVersion 4189**, NeoForge profile **21.4.158**.
- The source license notices and creator credits are retained in the download and
  inside the game datapack at `data/meridian_base/`. Notices state all rights reserved and
  personal use; the current terms link is https://www.patreon.com/posts/license-usage-70505678.
  The integration/release checks described here create local artifacts.

All actual imported palette states were checked against 1.21.4's state definitions.
Source sign/item text components were converted to 1.21.4 JSON strings. Downloaded
level metadata, datapacks, POIs and natural structure references were not installed.
The selected source chunks contain no decorative entities requiring translation;
unrelated natural mobs and cave minecarts were not imported. Source command blocks
are inspected and disabled by the importer; no source commands took control.

## Placement and playable region

The transform is `(x, y, z) → (x + 24576, y, z + 24576)`, without rotation or scale.
The main build is bounded by source `[-97, -33, -84]` through `[109, 18, 116]`,
or destination `[24479, -33, 24492]` through `[24685, 18, 24692]`. This envelope measures
**207 × 52 × 201 blocks** (X × Y × Z). It records the main architecture;
the source chunks also preserve the surrounding base/terrain context.

The import adds **210 chunks** in previously unused region files:
`region/r.47.47.mca`, `region/r.47.48.mca`, `region/r.48.47.mca`, `region/r.48.48.mca`.
Block states and all **766 block entities** in those
chunks are retained, including signs, banners, inventories and decorative details.

The playable area follows **ring deck and upper main-platform walking surfaces**. Containment uses
**825 per-height rectangles** derived from the connected architecture, with a
one-block movement margin. The inclusive outer envelope is X 24513…24650,
feet Y -32…22, Z 24491…24675; the union narrows
at each height. This envelope alone is not the arena. Detached scenery, the ocean,
low source ground, accidental caves and other dimensions are excluded.

A living, queued participant outside the mask, in a fluid block, or in a waterlogged
block returns to `[24582.5, -29, 24576.5]`, a validated spawn. Feet and head fluid
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
in [meridian_base.json](meridian_base.json).

Voting loads 210 chunks and schedules guarded activation after
loading. Activation rebuilds the marker pool without duplicates. Reset cancels
pending activation, removes the map runtime/participant tags and restores
**5644 original interactive states, dry cells or block-entity records**.
All chunk-load rectangles stay within the vanilla 256-chunk per-command limit.
Reload preserves an active round; inactive reload/reset unloads its arena chunks.
Original cave spawners outside the play region retain their saved blocks and NBT;
round setup delays them so they do not introduce mobs during play.

## Voting poster

The final PNG is the user-supplied sunset image, copied unchanged. Its large title is at the bottom. Earlier built-in imagegen variants reused the original webpage screenshot.

- Texture: `.minecraft/resourcepacks/backstabbed-resource/assets/meridian_base/textures/posters/meridian_base.png`.
- Item/model: `assets/meridian_base/items/posters/meridian_base.json` and `assets/meridian_base/models/posters/meridian_base.json`.
- Atlas: `assets/minecraft/atlases/blocks.json`.
- Voting display: `mcm:lobby/voting/map_position_id`, map ID 17.
- English/Simplified Chinese labels: `assets/meridian_base/lang/`.

The model uses the established flat 2:3 face, model Z=8 and display X offset −0.01,
placing the face in front of each booth backing. Final prompts, methods, source
images, attribution and asset hashes are in [kaizen_posters.json](kaizen_posters.json).

## Compatibility repair and backup

The user explicitly approved **108 decoration substitutions** for
1.21.4 compatibility. Exact before/after states and source positions are recorded
in [meridian_base_compatibility.json](meridian_base_compatibility.json). Bushes became ferns, dry
grasses became dead bushes, wildflowers became pink petals, and the single dried-ghast
ornament in Underwater Base became a skeleton skull. Firefly particles are lost.
The building structure, floors, passages and routes were preserved.

The sparse repair was generated with **minecraft-builder-skill** using
[scripts/builds/kaizen_compatibility.mjs](../../scripts/builds/kaizen_compatibility.mjs),
DataVersion 4189, and previewed in context before import. The importer verifies
that the NBT contains exactly the approved replacements and that every original
cell matches before applying it. Untouched cells, block entities and states remain.

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
