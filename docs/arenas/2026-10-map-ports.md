# October 2026 arena ports and repairs

The canonical world remains
`.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies`.
All content targets Minecraft Java 1.21.4 with NeoForge 21.4.158 and the installed
Gravity Changer mod. Source downloads and conversion copies remain under the
Git-ignored `map-previewer/maps/` directory.

| Arena | ID | Placement / transform | Player and scrap spawns |
| --- | --- | --- | --- |
| Sworld Island | 21 | Original source + `[40224,0,40592]`; imported X40864–41055, Z40912–41023 | 32 across connected island ground, Y64–87 |
| Middle Ages Small Lobby | 22 | Original source + `[45056,96,45056]`; architecture X45026–45087, Y92–128, Z45026–45086 | 32 in the original courtyard, Y96 |
| Cube Block | 23 | Original source + `[49136,0,49408]`; main cube X49176–49233, Y0–102, Z49164–49249 | 32 on connected upper ground, Y86+ |
| Subway Station update | 16 | Existing architecture unchanged | 8 lower platform, 8 upper concourse, 8 train interiors |

Sworld Island is by CloseeDBr, from
<https://www.minecraftmaps.com/44852-sworld-island>. Its 1.16.1 save was upgraded
through vanilla Minecraft's converter before importing selected chunks. Ocean
contact is lethal after the grace period, including passengers of an ocean boat;
air above the shoreline and the original elevated stream remain safe.

Middle Ages Small Lobby is by ElectronJoon and collaborators, from
<https://www.minecraftmaps.com/51285-middle-ages-small-lobby>. Its 1.21.7 structure
was checked against the 1.21.4 registry and re-encoded into new target chunks.
All 70 block entities are retained. The original castle is surrounded by void;
falling below Y90 or leaving the arena eliminates active players after grace.

Cube Block is by XxRexRaptorxX, from
<https://www.curseforge.com/minecraft/worlds/cube-block>. The normal v5.4 save
actually uses 1.12.2 data; a copy was converted with vanilla 1.21.4. The main cube
is the selected arena. Living participants receive `gravity_changer:grappling_hook`;
ownership cleanup removes only the departing participant's arena equipment and
projectiles. The playable volume includes the cube's faces and underside.

Original archives, credits, terms, conversion details, exact boundary predicates
and spawn/route data are recorded in `sworld_island.json`, `middle_ages.json` and
`cube_block.json`. No public redistribution permission is asserted by this local
integration. Cube's listing states All Rights Reserved and its archive includes
additional reuse restrictions. Neither of the other two downloads supplied an
explicit reuse grant. Source notices remain alongside the integration records.

Each new map is wired through registration, voting, map toggles, selection,
activation, waiting and active ticks, player/scrap/spectator spawns, reset and
chunk unloading. Direct selection commands are `/function sworld_island:select`,
`/function middle_ages:select` and `/function cube_block:select`.

The three voting posters were generated using built-in OpenAI imagegen, inspected
and installed at `assets/<namespace>/textures/posters/<namespace>.png` in the
resource pack. The user requested varied compositions and restrained saturation:
Sworld uses a lower title, Middle Ages a mid-left title, and Cube a lower-right
title. Final prompts, hashes and attribution are in
`2026-10-map-port-posters.json`; each has a complete item/model/texture/atlas chain.

Meridian Base retains its original geometry except for seven expressly requested
outer-ring dropper-to-dispenser replacements. The installed builder skill produced
the bounded NBT repair, which was rendered and inspected before import. Actual
ocean contact is lethal during play; indoor water and bubble columns are safe.
The existing central shaft buttons teleport their actual presser between indoor
landings, with labels for both directions. The plantation generates always-edible
potatoes named Delicious Food every 10–25 seconds, granting Speed I and Jump Boost I
for 200 ticks. A fresh step on a dispenser rerolls potion versus airborne firework;
standing still does not repeat, inventories stay locked and empty, and rewards
cannot deplete. `meridian_base-repair.json` records coordinates and components.

The full source save was stopped and backed up before any repair/import write:

```text
.minecraft/backups/map-integration/20261028T165526428350Z-five-arenas-before-port-and-fixes-872b9d08.zip
SHA-256: 2ac52afaaa9f04dbf92a4e16776ddae221d656516709e477986b300fa5083f5e
```

To restore, stop Minecraft, verify the archive with the skill's
`backup_world.py --verify <archive>`, move the current save aside, and extract the
archived world folder back under `.minecraft/saves/`. Keep the archive. The new
poster namespaces can be removed separately, restoring the pre-change atlas from
Git if rolling back the resource pack.

Static regression tests read the actual destination regions, block states,
collision shapes, routes, bounds and voting assets. Target-version runtime checks
use a fresh disposable full-world copy with an actual NeoForge client/server and
three idle players. Runtime sources, detailed assertions, logs and screenshots
are retained under `dev/map-ports/playtest/`. The consolidated verification record
is `2026-10-map-port-verification.json`; automated checks do not constitute a
human multiplayer playthrough.
