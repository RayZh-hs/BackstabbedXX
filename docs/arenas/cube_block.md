# Cube Block

Map 23 (`cube_block`, voting tag `CubeBlock`) ports the main overworld cube by
XxRexRaptorxX from [Cube Block on CurseForge](https://www.curseforge.com/minecraft/worlds/cube-block).
The v5.4 download is CurseForge file 2764936. Its normal save actually has
DataVersion 1343 (Minecraft 1.12.2), despite the download's 1.14.4 label. The
included legacy Gravity Edition depends on StarMine and was not selected.

The original ZIP and its unmodified saves, author text, wallpaper references,
and reuse notices are retained under `map-previewer/maps/cube-block/source/`.
The listing states All Rights Reserved. The archive's INFO gives
CC BY-NC-ND 4.0 and prohibits copying or redistribution without permission.
Publication permission has not been established. This is a local integration;
the original resource pack is not imported.

The selected source chunks are X 1–7, Z −16–−10. A disposable copy was upgraded
using the vanilla Minecraft 1.21.4 server's `--forceUpgrade --eraseCache` path.
Only those 49 converted chunks are imported. Source data outside the main cube,
including its additional star, nether and end cubes, is excluded. The transform
is translation `(49136, 0, 49408)` with no rotation. Imported block geometry
occupies `(49176, 0, 49164)` through `(49233, 102, 49249)`; lower cells are the
cube's existing waterfalls. Block states and useful block entities are retained.
Survival inventories and loot tables are cleared, mob spawners are disabled,
and source structures, scheduled control and datapacks are not imported.
Valid source decorations and animals are retained with new deterministic UUIDs;
living decorations have no AI or trades. Survival hostiles and loose item drops
are omitted. The original legacy save contains duplicate UUIDs and an invalid
skull block entity; vanilla conversion resolves or rejects these before import.

There are 32 distinct player/scrap locations on the connected upper ground,
all at Y ≥ 86, supported by full blocks with clear standing/head volumes.
They belong to a 1,298-node connected walk/jump route graph and have at least
three neighbouring route nodes each. The closest pair is 6.08 blocks apart
horizontally. The destination block data is checked by
`tests/test_cube_block.py`; no spawn relies on the source's interior survival
spawn position, a tree canopy, a partial snow layer, or a reset door.

Living queued participants receive the installed Gravity Changer mod's
`gravity_changer:grappling_hook` in hotbar slot 0 when the round starts. The
ordinary mod cooldown applies. Hooks and arena items are cleaned up on death,
leave and reset. The arena permits movement around every face and the underside
within X 49164–49246, Y 26–126, Z 49152–49262 in the overworld. Leaving that
volume returns participants to a validated spawn during preparation and
eliminates them during active play. Spectators, lobby players and dead players
are excluded. This gives room for grappler travel while excluding other arenas.

The final voting texture is
`assets/cube_block/textures/posters/cube_block.png`, with matching item and
model definitions. It was generated using the built-in OpenAI imagegen tool
and inspected at 1024 × 1536. The revised artwork has a muted natural palette,
airy sky, its title in the lower right, and a small footer at the lower left.
It follows the actual tower, cottage, corner pool and contrasting biome faces.
The generation prompt is recorded in `docs/poster-art.md`.

The conversion was opened and safely stopped under vanilla Minecraft 1.21.4.
The Lodestone browser preview rendered successfully at
`http://127.0.0.1:5193/`; a screenshot is retained beside the local source.
The final installed datapack was also exercised in Minecraft 1.21.4 with
NeoForge 21.4.158 and the installed Gravity Changer mod. All 32 destination
spawns passed native player collision and standing-support checks. Native
mechanics assertions passed for real hook grants/components, two actual mod
projectiles with distinct owners, owner-specific cleanup preserving an unmarked
hook and unrelated inventory, participant/state guards, grace return with
gravity reset, active elimination, and repeated activation/reset. These checks
run after the arena chunks load; an initial test that launched hooks immediately
after a remote teleport into an unloaded arena was corrected to allow chunk and
entity visibility to settle. The gameplay cleanup command required no change.

A four-player round also passed normal startup, role assignment, the grace
period and normal round-end cleanup. All four participants retained their
grappler after receiving role loadouts. The muted voting poster rendered in the
actual client after correcting the direct selector's absolute coordinates.

Automated gameplay results are retained in
`dev/map-ports/playtest/gameplay-pass.txt`; focused poster results and screenshots
are beside it. The consolidated record is
`docs/arenas/2026-10-map-port-verification.json`. This is native client/server
verification; a human multiplayer playthrough was not performed.
