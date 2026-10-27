# Underwater Base

Underwater Base by **KAIZEN87** is map **19**, namespace `underwater_base`.
It is selectable in normal lobby voting and the map-toggle board. Direct selection,
while no round is active, uses `/function underwater_base:select`.

## Source and version

- Original post: https://www.minecraftmaps.com/52536-underwater-base
- Download: `map-previewer/maps/52536-underwater-base/source.zip`, SHA-256 `d36da68bb12f5f4cc380ccb44bb852155101c5188dc3420762427b58b7cbc114`.
- Original world: `map-previewer/maps/52536-underwater-base/world/Underwater Base by Kaizen87`. It remains unchanged.
- Actual source level/chunk version: **1.21.8 / DataVersion 4440**.
- Target: **Minecraft Java 1.21.4 / DataVersion 4189**, NeoForge profile **21.4.158**.
- The source license notices and creator credits are retained in the download and
  inside the game datapack at `data/underwater_base/`. Notices state all rights reserved and
  personal use; the current terms link is https://www.patreon.com/posts/license-usage-70505678.
  The integration/release checks described here create local artifacts.

All actual imported palette states were checked against 1.21.4's state definitions.
Source sign/item text components were converted to 1.21.4 JSON strings. Downloaded
level metadata, datapacks, POIs and natural structure references were not installed.
The selected source chunks contain no decorative entities requiring translation;
unrelated natural mobs and cave minecarts were not imported. Source command blocks
are inspected and disabled by the importer; no source commands took control.

## Placement and playable region

The transform is `(x, y, z) → (x + 38400, y, z + 26624)`, without rotation or scale.
The main build is bounded by source `[-5455, 36, 5825]` through `[-5393, 62, 5920]`,
or destination `[32945, 36, 32449]` through `[33007, 62, 32544]`. This envelope measures
**63 × 27 × 96 blocks** (X × Y × Z). It records the main architecture;
the source chunks also preserve the surrounding base/terrain context.

The import adds **72 chunks** in previously unused region files:
`region/r.64.63.mca`.
Block states and all **447 block entities** in those
chunks are retained, including signs, banners, inventories and decorative details.

The playable area follows **dry interiors of the three connected main modules**. Containment uses
**233 per-height rectangles** derived from the connected architecture, with a
one-block movement margin. The inclusive outer envelope is X 32944…33009,
feet Y 40…66, Z 32448…32546; the union narrows
at each height. This envelope alone is not the arena. Detached scenery, the ocean,
low source ground, accidental caves and other dimensions are excluded.

**Boundary-return teleportation is disabled.** Containment is physical: **six
exterior hatch cells** are full barrier blocks, with non-interactive `block_display`
entities preserving each hatch's original block state and appearance. Players
cannot flip these hatches open. Interior doors and decorative trapdoors remain
interactive; both bubble lifts remain usable. Water and positions outside the
old mask no longer trigger automatic returns or elimination.

Exact source/destination coordinates and before/after/display states are in
[underwater_base_exits.json](underwater_base_exits.json). With all other doors and
trapdoors treated as open, the saved collision geometry still connects all spawns
and both internal lifts without reaching the ocean or the build's exterior edges.
The old predicate remains available for spawn/geometry inspection.

## Spawns and lifecycle

There are **24 distinct player/scrap spawns** and one spectator marker. Each actual
saved destination has collision-shape clearance for a 0.6 × 1.8 player, full-footprint
support at its exact height (including carpets/slabs), no fluid/damage hazard, at
least two supported local exits, and membership in the connected build. Exact
positions, exit checks, predicates and source/destination transforms are recorded
in [underwater_base.json](underwater_base.json).

Voting loads 72 chunks and schedules guarded activation after
loading. Activation rebuilds the marker pool without duplicates. Reset cancels
pending activation, removes the map runtime/participant tags and restores
interactive states, dry cells, block-entity records and the six exit barriers.
The original hatch reset commands are removed, so reset cannot reopen a seal.
Activation creates exactly six hatch displays; repeated activation replaces the
previous displays, active reload preserves them, and reset removes them.
All chunk-load rectangles stay within the vanilla 256-chunk per-command limit.
Reload preserves an active round; inactive reload/reset unloads its arena chunks.
Reset also clears incoming seawater from **3178 originally dry cells**
(623 bounded fill commands) and restores 619 fragile-decoration
states/NBT records after draining. Original ocean water is retained. A live test
deliberately flooded all 24 spawn cells; reset restored their exact dry block types,
and they remained dry after reactivation and subsequent ticks.

Original cave spawners outside the play region retain their saved blocks and NBT;
round setup delays them so they do not introduce mobs during play.

## Voting poster

The built-in imagegen poster reuses the webpage deep-sea base scene, with a large right-aligned title below the open upper water.

- Texture: `.minecraft/resourcepacks/backstabbed-resource/assets/underwater_base/textures/posters/underwater_base.png`.
- Item/model: `assets/underwater_base/items/posters/underwater_base.json` and `assets/underwater_base/models/posters/underwater_base.json`.
- Atlas: `assets/minecraft/atlases/blocks.json`.
- Voting display: `mcm:lobby/voting/map_position_id`, map ID 19.
- English/Simplified Chinese labels: `assets/underwater_base/lang/`.

The model uses the established flat 2:3 face, model Z=8 and display X offset −0.01,
placing the face in front of each booth backing. Final prompts, methods, source
images, attribution and asset hashes are in [kaizen_posters.json](kaizen_posters.json).

## Compatibility repair and backup

The user explicitly approved **4 decoration substitutions** for
1.21.4 compatibility. Exact before/after states and source positions are recorded
in [underwater_base_compatibility.json](underwater_base_compatibility.json). Bushes became ferns, dry
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

The 2026-10-27 containment repair passes **52 repository tests**, including all six
saved barrier cells, display/reset wiring, spawn routes, preserved lifts and
physical ocean isolation with interactive blocks treated as fully open. The
following records also describe the original integration checks; updated repair
evidence is under `map-previewer/maps/containment-fix/runtime/`.

The maintained previewer previously passed **8 tests**.
The repair's isolated vanilla 1.21.4 server validated **47 actual spawns** across
both repaired arenas, **six real client right-click attempts** on the sealed
hatches, unchanged internal bubble columns, removal of water/exterior return
teleports, and repeated activation, active reload, reset and reactivation with
exactly six displays. Test commands and results are in `test.cjs` and
`results.json` under the repair's runtime directory. These are automated vanilla
checks; the NeoForge client profile and human multiplayer balance were not
playtested for this repair.
Both repaired maps also completed normal **four-player round starts**, role
assignment (one murderer and three innocents), and the full grace period; see
`round-results.json` in the repair's runtime directory.
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

## Exit-sealing repair (2026-10-27)

The six barrier placements were generated with `minecraft-builder-skill` using
[underwater_exit_seals.mjs](../../scripts/builds/underwater_exit_seals.mjs),
DataVersion 4189. A Lodestone browser preview showed the repair in the original
architecture, using magenta glass only as inspection proxies for invisible
barriers. The installed patch contains exactly six `minecraft:barrier` blocks.
The installer checks every original hatch state before replacing it and preserves
all block entities and unrelated chunk payloads. Visual hatch displays are created
by the datapack during activation. Original downloads/worlds are unchanged.

The full stopped save backup, including the existing arena-editor changes, is:

```text
.minecraft/backups/map-integration/20261027T101411138725Z-bagger-underwater-before-seals-74059f54.zip
SHA-256: 57a442c4f3382d6da3b971843bbaab577f26280aeb28b79d6811623d99e76454
935 files
```

Use the verify/move-aside/extract procedure above to restore. Only
`region/r.64.63.mca` (six blocks in two chunks) and `datapacks/mcm.zip` differ from
this save snapshot. The source resource pack also adds Bagger death translations.
The bounded installer is
[update_arena_containment.py](../../scripts/update_arena_containment.py); rerunning
[configure_kaizen_bases.py](../../scripts/configure_kaizen_bases.py) also retains
these containment policies through the shared generator.
