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
originally occupied `(49176, 0, 49164)` through `(49233, 102, 49249)`;
the lowest cells were exterior waterfalls. After the water repair below, saved
geometry occupies `(49176, 38, 49164)` through `(49233, 102, 49249)`.
Block states and useful block entities are retained.
Survival inventories and loot tables are cleared, mob spawners are disabled,
and source structures, scheduled control and datapacks are not imported.
Valid source decorations and animals are retained with new deterministic UUIDs;
living decorations have no AI or trades. Survival hostiles and loose item drops
are omitted. The original legacy save contains duplicate UUIDs and an invalid
skull block entity; vanilla conversion resolves or rejects these before import.

There are 32 distinct shared player/scrap locations across all six exterior
faces: six on top, six underneath, and five on each side. Each marker stores
gravity pointing into its supporting face, opposite the outward normal, at
strength 1.0. The player body rotates with that orientation; upside-down and
sideways players have full-block support and clear body space. Persistent
jungle foliage on the north face is usable support; water, invisible barriers,
cacti, partial blocks, and interior pockets are excluded.

Each point belongs to its face's largest connected walk/jump route graph and
has at least three neighbouring route nodes. Points are selected by increasing
their separation across the face, with six-block clearance from points on
previously selected faces. `tests/cube_geometry.py` reproduces the selection
from the saved blocks, and `tests/test_cube_block.py` checks the installed
markers, rotated body volumes, support, spacing, routes, and arena membership.

The shared spawn selector delegates Cube Block to `cube_block:spawn`. It
selects one unoccupied marker, applies that marker's gravity synchronously via
the bundled host mod's `arena_spawn_gravity` command, then teleports to the same
marker and marks it occupied. Applying gravity before teleporting prevents
rotation from displacing an upside-down spawn later. Scrap uses the existing
Gravity Changer marker bridge. Grace-period escape still returns to the safe
top contact at `(49196.5, 88, 49202.5)` with downward gravity.

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

Water containment repair, 30 October 2026: the original survival cube's water
had exposed west/south faces and an unsupported underside. Its imported pending
fluid ticks, or later neighbour updates, could extend waterfalls down to Y −64.
The repair retains all 2,698 water cells inside the main 40-block cube,
`(49181, 47, 49196)` through `(49220, 86, 49235)`, including cave streams.
It removes 3,608 exterior water cells and installs 857 invisible barrier cells:
137 on the west face at X 49180, 152 on the south face at Z 49236, and 568
under the water at Y 46. Existing wooden supports remain. These barriers occupy
one block outside the exposed water and have normal barrier collision; the
pool's open top remains accessible. Spawns, routes and the arena predicate
remain unchanged. The saved physical lining persists across activation/reset;
no global fluid setting or recurring cleanup command is needed.

The full stopped save was archived and checksum-verified before the repair:
`.minecraft/backups/map-integration/20261030T130756164848Z-cube-block-before-water-fix-f7a9e82b.zip`,
SHA-256 `3a2fb13a403d7e3d86f15a3255a3e363f3ac160191fcac5e23f0fc1a752bf46d`.
To restore, stop Minecraft, verify the archive using the project skill's
`backup_world.py --verify`, move the current save aside, then extract the archived
world folder under `.minecraft/saves/`. Keep the backup throughout.

The bounded recipe and application tool are retained locally in
`dev/cube-water-repair/`. The installed `minecraft-builder-skill` generated
`map-previewer/maps/cube-block-water-repair/cube-block-water-patch.nbt` with
DataVersion 4189 and automatic block-state updates disabled. Its context was
inspected in the interactive Lodestone preview before import. The applier
checked every previous state against the plan, changed only seven chunks in
`region/r.96.96.mca`, removed obsolete ticks at replaced cells, and invalidated
affected chunk light/height caches for recalculation. Comparison with the full
backup confirmed that this region is the only changed save file; all original
solid blocks, block entities, decorative entities, POI and datapack data remain.

Verification used a disposable copy in Minecraft 1.21.4 / NeoForge 21.4.158.
Every retained water cell received a native fluid tick (2,698 initially, 2,723
after the interior streams settled). Three subsequent scans of the full arena
chunk footprint, from Y −64 through 102, found zero exterior water; all 2,556
original interior water source positions remained sources. Native collision
and support checks passed at all 32 spawns. The existing grappler ownership,
cleanup, grace return, active escape elimination, and repeated activation/reset
checks passed, followed by normal four-player startup, role assignment, grace
and round-end reset. Results and the disposable harness are retained in
`dev/cube-water-check/results.txt` and its adjacent files. The repaired geometry
was visually inspected in the Lodestone context preview; a human multiplayer
playthrough was not performed. `make test` passed all 25 tests, and
`make resourcepack map` rebuilt the resource pack and host-map archive.

Six-face spawn update, 31 October 2026: player and scrap markers now use the
distribution and inward normals described above. Sideways and underside
contacts have a 0.001-block outward gap to avoid Gravity Changer's tiny
positive-axis bounding-box offset. The closest two points are 6.043 blocks
apart. A verified full-save snapshot was taken before the datapack change:
`.minecraft/backups/map-integration/20261030T174708002370Z-cube-face-spawns-before-fix-28de3fa2.zip`,
SHA-256 `7e9f26da568d4cd573ed4243759a6b7376e91d12e33132ea70e14b4cb856f885`.
Restore it using the stopped-save verification/extraction procedure above.

The native fixture at `merchant-bridge/tests/FaceChecks.java`, launched with
`merchant-bridge/tests/run_cube.py`, passed 308 assertions in a disposable
Minecraft 1.21.4 / NeoForge 21.4.158 world. All 32 player destinations and all
32 real scrap drops passed their actual rotated collision/support checks.
Player base, applied and previous gravity agree before the spawn teleport;
occupancy selection/reuse, invalid configuration rejection, ordinary spawning
for other arenas, and repeated activation passed. A normal four-player round
passed role assignment, grace period, living-player/grappler checks, collision
after ticking, round-end marker cleanup and downward lobby return. Results are
retained in `dev/cube-face-check/results.txt`; this was automated client/server
verification, without a human multiplayer playthrough.

The focused Cube Block/host bridge suite passed 12 tests. `make test` ran 26
tests, with 22 passing and four existing Middle Ages problems (one failure,
three errors). Those same Middle Ages problems were reproduced against the
committed datapack: the tests expect the old activation/spawn layout and do not
understand its current `entity_properties` predicate. `make resourcepack map
pack` built the resource pack, host map and client pack successfully.
