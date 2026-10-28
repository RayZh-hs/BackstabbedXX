# KLUT-27 integration

KLUT-27 is Bekulainen's vertical spaceship with interior cabins, market terraces,
a hangar, exterior parkour and six elevator columns. Source:
https://www.planetminecraft.com/project/klut-27-spaceship-mothership-space-station-work-in-progress/

The source page requires the author's permission before reuse in another build,
plus credit and a link. This task is a requested local integration; permission
for public redistribution has not been established. Do not represent the map
as freely licensed. Simple Elevators is by Supercam19.

## Source and placement

The untouched download is `CandidateMaps/08_KLUT27/klut-27.zip` in the parent
workspace, SHA-256
`0f31e0db0b0c4885cfa2a5411a9aa40bbf62b1786586a73d952130660fa04e46`.
The actual source data version is 3700 (Java 1.20.4). The target instance and
gameplay datapack use Java 1.21.4. Native Minecraft data fixing upgrades source
chunks when they load; no script falsely relabels the source DataVersion.

Arena namespace `klut27`, ID **20**. Translation is **(+36864, 0, +36864)**,
without rotation. Visible build bounds, including the antenna, transform from
`(-5,-64,-2)..(24,46,50)` to `(36859,-64,36862)..(36888,46,36914)`.
Fifteen source chunks are imported, covering
`(36848,-64,36848)..(36895,319,36927)`. All original block states, block
entities, paintings, frames, armor stands and resident entities are preserved.
Entity positions, hanging anchors, villager memory positions and UUIDs are
translated/remapped. The lone command block's milk-give command is disabled in
the integrated copy so it cannot target unrelated players. No build geometry
was altered. The standalone copy retains the original command.

The preview is `map-previewer/maps/klut27/klut27.nbt` with adjacent metadata;
its export omitted Y -64, one antenna block, and was visually inspected in the
maintained browser viewer. The import retains that block. The main build is a
mustard-yellow and pale-trimmed upper hull, exposed crowded terraces and a
dark tapering underside; the poster reflects those features.

## Standalone installation and elevator migration

The standalone save is installed as **KLUT-27 - 1.21.4 Fixed** in the
Backstabbed++ Prism instance. It is a full clone of the preserved original,
with `doFireTick=false` and a replacement `simpleelevators-1.21.4.zip`.
The old ZIP remains in the untouched source and verified backup.
The original empty Bukkit wrapper's metadata is also updated from format 26
to 61; it adds no gameplay resources.

`scripts/klut27_elevators.py` produces format 61 with singular `function`,
`advancement`, `recipe`, function-tag and block-tag directories. Detection uses
the modern `lock` item predicate, recipes use the modern result/ingredient
format, and the give command uses item components. The search starts aligned
to the current elevator's block column, finds the next landing within 120
blocks, teleports one block above it and preserves the player's rotation.
Jump ascends; crouch descends. Both directions apply a 10-tick cooldown.

Landing checks preserve all 18 original stops. Feet require collision-free
air/sign cells. The head may be air, a non-colliding wall sign, or a closed top
trapdoor: its underside is 1.8125 blocks above the feet, above a 1.8-block
player. No elevator route is repaired by deleting the original trapdoors.
The source columns are:

| X,Z | Elevator block Y |
|---|---|
| 8,9 | -36, -33, -27, -21, -16, -13, -7, 27 |
| 3,3 | 25, 29 |
| 8,6 | 27, 32 |
| 8,15 | 15, 27 |
| 8,20 | 6, 10 |
| 8,19 | 25, 29 |

For integrated coordinates add 36864 to X and Z. Player feet are at Y + 1.
The integrated namespace is `klut27_elevators`. It has no global tick tag;
KLUT-27's waiting/active lifecycle calls it only for map 20. Only queued,
living, non-spectating participants inside the ship with actual applied DOWN
gravity can use these world-Y elevators. The mod's `gravity bridge is_down`
command supplies the direction check. Search markers are removed after each
call, on load and on reset.

The original lava remains at `(6,10,19)` in standalone and
`(36870,10,36883)` in the integrated arena. `doFireTick=false` prevents the
documented ignition risk while preserving the map design. It is already false
in the source main world and is reasserted by elevator load and activation.

## Spawns, routes and containment

There are **28 distinct player/scrap spawn markers**, distributed through an
elevator-linked component of the actual ship: lower cabins, central exterior
decks and upper decks. Each has `data:{gravity_direction:"down",
gravity_strength:1.0d}`. Full collision-cube support and clear standing volume
are checked against the destination Anvil blocks. Partial stairs/slabs, fluids,
hazards and transient doors are not used as spawn support.

Markers default to DOWN at strength 1.0. Selecting or entering KLUT-27 does
not automatically switch players to side or inverted gravity. Direction changes
come from the mod's gravity items or explicit commands; ordinary round/reset
behavior restores the intended default. Scrap metadata can be read by the
gravity bridge without implying an automatic player-gravity transition.

`klut27.json` records every source/destination spawn and the walking/elevator
route to central anchor `(36873.5,16,36879.5)`. Route edges use adjacent walkable
cells with at most a one-block step, or consecutive stops in the same elevator
column. All intermediate stops are retained. The six `gravity_test_positions`
record actual full-block faces with clear rotated body volume for manual
direction tests; these are test contacts, not automatic side-gravity spawns.
UP, SOUTH and EAST contacts sit 0.000002 blocks away from their support face
to account for the mod's 0.000001-block positive-axis collision-box adjustment.

The playable region is a union of **239 boxes** generated from the actual
ship's footprint in four-block vertical bands. Padding allows jumps and
side/inverted body volume around the hull. The detached lower antenna below
the lowest cabin, distant void, wrong dimensions and positions above the ship
are excluded. During waiting/grace/active play, an out-of-region live queued
participant is eliminated through `mcm:game/playerdeath`. Spectators, dead
players, lobby players and other maps are exempt. There is no global world
border and no return-teleport loop.

Activation recreates markers after cleanup, restores 984 original interactive
block states and forceloads only the 15 imported chunks. Reset and reload clear
scheduled activation, runtime/search markers and chunk tickets. Ordinary
source decoration is not tagged `MapEntity` and survives round cleanup.

## Poster and packaging

The generated 1024 × 1536 PNG is
`.minecraft/resourcepacks/backstabbed-resource/assets/klut27/textures/posters/klut27.png`.
It was generated with the built-in imagegen tool on 28 October 2026, inspected
for title/footer and recognisable architecture, and connected through the
`klut27:posters/klut27` model/item, atlas and voting display. The final prompt
is in `docs/poster-art.md`. The existing booth face placement is retained.

`scripts/configure_klut27.py` stages changed datapack entries plus original
hashes under `map-previewer/maps/klut27/patch`; it does not overwrite `mcm.zip`.
The task coordinator merges these entries with the gravity changes. The
original source world name remains unchanged.

## Backups and verification

All archives below are under `.minecraft/backups/klut27/`, created and checksum
verified before the first modification:

| Scope | Archive | SHA-256 |
|---|---|---|
| Original KLUT save | `20261028T070249643760Z-klut-original-12a495b8.zip` | `c7aa2a4c33dd211222ec992a6d2fa8d34c2138dbece054ad1edf79a84a5ea6e8` |
| Source main world | `20261028T070250074865Z-klut-source-before-8d764542.zip` | `fc1fd9985188125690f96cc612b0dcaf33cd2d517edad5a81ac5302bf5348110` |
| Installed main world | `20261028T070250677120Z-klut-live-before-46a96a7f.zip` | `914cfe599317f6fe4117864e74dd401de546dcf02f9b169f65376d6fd53ddeef` |

To restore, stop Minecraft, run the skill's `backup_world.py --verify` on the
archive, move the damaged save aside and extract the archived world folder
under its original parent. Preserve the backup. These are full save snapshots,
including regions, entities, POI, datapacks and metadata.

`tests/test_klut27.py` validates the actual imported blocks, all spawn routes,
all six gravity test contacts, irregular boundary exclusions, elevator
migration/scoping and lifecycle cleanup. Resource tests additionally traverse
the complete poster reference chain and check its face against every voting
booth. Static checks are not a Minecraft playtest; runtime elevator, selection,
poster, grace/round escape and reset evidence must be recorded by the task's
target-version test run before claiming full completion.

Static verification on 28 October 2026: `make test` passed all 61 tests,
including the five KLUT-27 tests. The resource-pack build succeeded with 252
files. The six new region/entity files were copied into the stopped Prism
main save and verified byte-for-byte, together with the merged datapack and
rebuilt resource pack. Runtime results are tracked separately by this task.


## Water surrounds and residents (28 October 2026)

Applied to the source main world, installed main world, and installed standalone
save. Full pre-edit snapshots are in `.minecraft/backups/klut27-decor/`.
The original downloaded map remains unchanged.

- Move the existing iron golem to the open main deck at standalone
  `(9.5, 15, 45.5)` / arena `(36873.5, 15, 36909.5)`.
- Anchor the original Pawn Shop resident at `(12.5, 15, 33.5)` / arena
  `(36876.5, 15, 36897.5)` with `NoAI`, zero velocity and persistence.
  Preserve UUID, trades and other resident data. The nearby named
  BubbleVehicles trader is a different entity and is unchanged.
- Replace 205 water-adjacent flammable full wood cubes with matching orange,
  red or brown terracotta, plain terracotta or smooth sandstone. Preserve
  water, glass, ironwork, shape and all unrelated materials.
- No replaced position is referenced by `restore_blocks.mcfunction`, so round
  reset cannot restore the former wood. No datapack modification is needed.

Exact positions and materials: `klut27-decor.json`. Repair utility:
`scripts/repair_klut27_decor.py`. The structure recipe and inspected full-map
and aquarium previews are in ignored `map-previewer/maps/klut27/decor/`.
The repair appends only changed Anvil chunks and preserves every unrelated
chunk and entity; each destination is patched independently, retaining saved
local gameplay changes. Source/live worlds need not have identical full files.

Verification: all 61 existing repository tests pass after this repair,
including saved-block spawn routes, containment, gravity contacts, elevators
and reset checks. This repair was visually inspected in the structure viewer;
no new in-game playtest was performed for these decoration edits.


## Standalone edits and ice-cream vending machine (28 October 2026)

Synchronized 59 saved block-state differences from the installed standalone
world into both main-world copies. These include scaffolding, birch doors,
mangrove trapdoors, copper weathering and redstone state changes. Compared
all 176,490 cells in the arena box: both destination block states match the
standalone source after translation. Entity, player and POI files are unchanged.
The mutable-block reset list now has 990 entries, including the added doors
and trapdoors. Exact differences are recorded in `klut27-sync.json`.

The oak button at standalone `(4, 15, 35)` / arena `(36868, 15, 36899)` uses
`minecraft:default_block_use` with an exact block location and dimension check.
Its reward function sends `SH*T！怎么坏了？` to `@s`, then is available for the
next interaction via advancement revocation. No nearest-player selector is
used. The old command block at `(4, 15, 34)` has its command disabled in all
three saves, so it cannot issue milk or duplicate/incorrect-recipient messages.
The standalone functionality is in `datapacks/klut27-vending.zip`; integrated
functionality uses the same `klut27_vending` namespace inside `mcm.zip`.

Pre-edit full save backups: `.minecraft/backups/klut27-sync/`.
All 61 repository checks pass. NeoForge integration tests exercise actual
Adventure-mode button interactions twice, place a non-clicking player closer
to the machine, and reject a nearby unrelated block interaction. See the
GravityChanger development project's `build/vending-green.log` and
`build/vending-standalone.log` for runtime results. No game mod rebuild is
required: this change uses datapack functions and advancements only.


## Spawn orientation and boundary audit (28 October 2026)

The 28 player/scrap markers retain DOWN gravity and strength 1. All now have
explicit cardinal yaw and zero pitch, selected using safe forward support,
clear body volume and continuation along the current saved walkable routes.
Marker 3 moves from standalone `(3.5,15,49.5)` to `(4.5,15,44.5)`;
marker 14 moves from `(10.5,15,49.5)` to `(12.5,15,47.5)`.
Both are inset from the southern unguarded edge. Player and scrap points move
together. Full positions, yaw/pitch and updated routes are in `klut27.json`.

The Overworld containment mask is rebuilt from current saved geometry as 239
layered boxes, retaining the existing three-block movement allowance. Its
outer extrema are X 36856..36892, Y -39..50, Z 36859..36918; these are NOT a
single rectangular playable region. Narrow layers follow the ship's actual
shape and exclude distant void and the detached lower antenna. Existing
behavior remains: waiting participants are tracked after entering the arena;
tracked waiting participants and active live participants die on leaving.
Lobby players, spectators and already-dead players retain their exemptions.
No physical terrain or barrier blocks were added or altered.

Source and installed main datapack entries are identical. Full backups are in
`.minecraft/backups/klut27-spawns/`. All 62 repository tests pass. The opt-in
NeoForge integration run passes (`build/klut-spawns-boundary.log` in the gravity
mod project), exercising all 28 actual spawn teleports and rotations, waiting
lobby exemption, waiting arena entry/exit, active exit, spectator exemption,
repeated activation and reset, plus the existing gravity/elevator/vending checks.
The standalone building save has no minigame spawn/death system and is unchanged.


## Airless cabins, elevators and role hooks (28 October 2026)

Three enclosed lower cabins use interior strips derived from their saved floor
silhouettes (floors Y=-36/-33/-27; ceilings Y=-33/-28/-22). Exact bounds are in
`klut27-features.json`. Exterior void, lower antenna and the Y=-20 deck are
excluded. After grace ends and roles are assigned, each live queued player
accumulates continuous exposure: a private warning at 40 ticks, normal game
elimination at 200 ticks. Leaving the volumes resets exposure immediately.
Spectators, dead players and lobby players are excluded. The existing death
function handles spectator transition, item drops and team bookkeeping.

Successful elevators now set a per-player cooldown of 30 ticks. The counter
is decremented before processing input, so exactly 30 ticks separate accepted
transfers. This update is also installed in the standalone save's elevator pack.

At map start all participants receive a gravity hook in hotbar slot zero,
before role loadouts. Hooks are non-droppable and excluded from death drops.
Innocents and gunners have a 200-tick release cooldown; murderers receive the
generic exemption tag after role assignment. Cooldown starts on retrieval or
detachment, as explicitly selected by the user. Death, leave, lobby inventory
and map reset clear hooks, cooldowns and exemption tags. The standard standalone
building save receives no role or suffocation mechanics.

Installed mod: `gravity-changer-neoforge-1.4.1-neoforge.4+mc1.21.4.jar`.
Source/live hashes and old JAR backup paths: `../klut27-features-installation.json`.
Save/JAR backups are under `.minecraft/backups/klut27-features/`.
Validation: 63 repository tests pass; ordinary and integrated NeoForge runs
pass all 41 registered tests (opt-in scenarios skipped when not selected).
`klut-features-integration.log` covers exact warning/death thresholds, leaving
and grace reset, private warning recipient, gun/murderer loadout preservation,
role exemption cleanup, and the full elevator lockout. Standalone elevator
and vending integration also passes (`klut-features-standalone.log`).
No manual multiplayer client playtest was performed.


## Current implementation: restored mod .3 (28 October 2026)

This supersedes the .4 installation/cooldown description above. At the user's
request, both source pack and live instance use the exact backed-up
`gravity-changer-neoforge-1.4.1-neoforge.3+mc1.21.4.jar`, SHA-256
`32e308ce51de825b11a0530677caeaaed1e4758143c7a950dbea0a075e1bb02a`.
The .4-specific runtime Java changes were reverted without reverting earlier
.3 work. Installation evidence: `../klut27-mod3-rollback.json`.

Cooldown now uses vanilla scoreboard, item-modifier and `execute on origin`
commands. The old hook implements TraceableEntity, so origin resolves the
actual owner even though ownership is not exposed in entity NBT. Each player's
active-to-absent transition starts 200 ticks for non-murderers. The hook becomes
a nonfunctional, same-model stick until expiry; all 36 inventory slots and
offhand are handled, preserving its current slot. Murderers skip the extra
200 ticks. The old mod's native 5-tick interaction debounce remains unchanged.

Because .3 does not expose its phase, the timer begins when the returning hook
entity disappears, rather than at the initial detachment moment. Cleanup uses
the same exact-owner relation and cannot remove another player's hook.
No .4 command or item cooldown parameter is required. Death/reset/lobby cleanup
also removes temporary placeholders. Airless cabins and 30-tick elevator
cooldown remain unchanged.

Validation: 63 repository tests; 40 registered NeoForge GameTests passed in
`build/klut-datapack-hooks.log` (standalone opt-in scenario skipped in this run).
Actual integration tests cover two simultaneous owners, exact 200-tick expiry,
slot changes during cooldown, murderer exemption, owner-isolated cleanup,
existing oxygen timing and elevator rules. Backups are in
`.minecraft/backups/klut27-datapack-cooldown/`.

## Resident homes and fire-safe scrap sites (28 October 2026)

All ordinary villagers now have individual homes, full standing headroom and
at least three blocks of separation from player starts. The standalone keeps
its 16 original villagers; both integrated saves retain their 19 originals
(three additional villagers were already present only in those saves).
Groups at the stern and market alternate with pairs and dispersed residents
in lower corridors/cabins. Normal AI and trades remain. Integrated activation
and round reset return survivors and respawn missing residents by exact UUID;
the standalone `/function klut27:fire/reset` also resets resident positions.

Player starts remain unchanged. Scrap markers are now separate: 28 player,
28 scrap and one spectator marker. Sixteen old scrap sites were replaced due
to fire/blast exposure or loss of guaranteed walking access after the fire.
Twenty of the 28 resulting sites are on/around the main deck; all use downward
gravity. Every scrap site has a validated post-fire walking route to the deck.

Coordinates, UUIDs, replaced indices and routes: `klut27-population.json`.
Installer: `scripts/arrange_klut27_population.py` (plan, then `--apply`).
Terrain is unchanged by this revision. Verified pre-change full-save backups
are in `.minecraft/backups/klut27-population/`; saved-entity and matching
integrated-datapack evidence is in `klut27-population-verification.json`.

Verification: 69 repository checks passed. Both isolated NeoForge 21.4.158
server runs passed all 40 registered tests (the opposite opt-in scenario is
inactive in each run). The new runtime checks move and damage every resident,
remove one, and run reset twice: all 16 standalone / 19 integrated villagers
return alive to the exact intended homes without duplication. Marker counts,
separation, downward gravity and existing complete-fire/reset checks pass.
Logs: `build/klut-population-integrated.log` and
`build/klut-population-standalone.log` in the Gravity Changer workspace.
Saved terrain matches the pre-change backups byte-for-byte; all entity UUIDs,
resident trades/traits and other entities are preserved. Installed mod .3 is
unchanged. These are automated server tests, not a multiplayer client playtest.
