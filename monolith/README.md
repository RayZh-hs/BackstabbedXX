# Monolith

KAIZEN87's three overgrown monoliths, arranged as a triangle, form arena **24**, displayed as **Monolith**.
Use `/function monolith:select` while no round is active, or vote for its poster.
The source world remains `Backstabbed ++! by NorbMinecraft and Bagel Buddies`.

Persistent colored floor runes, upright circle outlines and enchanting-table
glyphs identify each altar. Entering the altar sends a chat hint to sneak;
beginning selection sends a second chat hint to look at another rune and release
sneak to travel. Hints trigger on entry/selection rather than every tick.

Stand on an existing summit platform inside the stone circle and hold sneak.
Darkness dims the scene and the other summits appear as colored luminous runes,
visible through the architecture only to the selecting player. Rune indicators
are projected along the actual destination sightlines so Darkness fog cannot hide them. Aim at a rune
(within 9 degrees) and release sneak to jump to its validated landing. A bright
arcing light trail connects the summits. Arrival faces the open triangular center
so the remaining two destinations are in view. Looking away or walking off the summit
cancels selection. A landing that has become obstructed rejects travel.

Every living participant receives a reusable **Potion of Floating** with the
normal role loadout at the end of the 15-second grace period. Drink it to gain
Levitation I for **100 ticks (5 seconds)**. Sneak while airborne to cancel the
float. Its **600-tick (30-second)** personal cooldown begins when floating starts;
cancelling preserves that deadline. The same potion returns after drinking.
Cooldown state follows the player across inventory slots, reconnects and reloads.
The server explicitly synchronizes the returned potion after drinking so vanilla
client prediction cannot leave an empty bottle displayed in its place.
Death, leaving the match, spectating, round end and reset remove arena equipment,
float state and private rune displays. Other maps and nonparticipants are excluded.

There are **36 distinct player/scrap spawns**, 12 per monolith, three summit
landings and one spectator marker. Containment follows the dilated build
footprints and includes the triangular airspace between islands for floating. Players who
fall below Y108, rise above Y210 or leave the allowed region return during waiting
and grace; after grace they are eliminated through the normal player-death path.
It does not impose a global world border or affect spectators.

The source is Java 1.21.8; the port targets Java 1.21.4 / NeoForge 21.4.158.
The imported architecture occupies X53201–53394, Y87–189, Z53213–53415.
Each island uses its own translated/rotated placement; exact pivots, quarter turns,
spawns and altar/rune positions are recorded in the arena manifest.
The showcase floor is not
part of the floating arena. All 189,368 selected block cells and 33 sign block
entities are retained. The approved compatibility patch replaces 193 newer
plants with ferns, pink petals and alliums. The 33 blank signs use 1.21.4 JSON
text encoding. No source commands, datapacks or entities were imported.

The [manifest](../docs/arenas/monolith.json) records exact spawns, altar positions,
boundary boxes, source/archive hashes, author, terms, poster prompt and asset hash.
[Source notices](../docs/arenas/monolith-source/) are preserved verbatim. The download
folder says “Vol 1”; the three nature-covered builds match the Vol. 2 listing.
Original archive, source world, previews and repair NBT are in the Git-ignored
`map-previewer/maps/monoliths/` directory. The bounded builder recipe and cell patch
are retained under `compatibility/`.

The poster was generated using OpenAI built-in imagegen, inspected and installed
at `assets/monolith/textures/posters/monolith.png`. Its item definition, model and
atlas entry use `monolith:posters/monolith`, with the established Z=8 model and
voting-display X offset -0.01.

The server-side implementation lives in
[`Monolith.java`](../merchant-bridge/src/backstabbed/merchants/Monolith.java) within
the existing shipped merchant bridge. No client mod protocol is introduced;
runes, particles, potion components and cooldown packets are vanilla. Rebuild Java
changes with `python merchant-bridge/build.py`, then run
`uv run --no-project --with nbtlib make test` and `make resourcepack`.
`datapack/` contains the installed arena namespace. Shared lifecycle hooks live in
the canonical `mcm.zip`, and existing maintained overlays remain synchronized.

The verified pre-import full-save backup is
`.minecraft/backups/map-integration/20261106T090753031548Z-monoliths-before-import-8885b4a3.zip`,
SHA-256 `c652297f7bd086ea48e159ddbac25f48a5984369270d093246ad989a0f323cd6`.
To restore, stop Minecraft, run the skill's `backup_world.py --verify` on that
archive, move the damaged save aside, then extract the archived world folder
under `.minecraft/saves`. Preserve the archive. All 963 pre-existing save files
other than the gameplay datapack are byte-identical to the backup.

`tests/test_monolith.py` checks actual saved support/headroom, boundaries, scene
exclusions, hooks, source/installed namespace agreement and the poster chain.
`tests/MonolithPlaytest.java` is a disposable NeoForge client test covering native
collisions, onward routes, a real four-player round, actual item consumption,
target selection, release travel, cancellation, independent cooldowns, expiry,
containment guards, reset and reactivation. Runtime evidence is recorded in the
arena verification manifest after the final run.

Run the disposable native checks with:

```sh
xvfb-run -a -s '-screen 0 1280x960x24' \
  uv run --no-project --with portablemc==4.4.1 python monolith/tests/run.py
```

Set `MONOLITH_VISUAL_ONLY=1` for a quick voting/rune screenshot pass.
The launcher uses a temporary full copy; the source save is never opened by the test.
Results, logs and screenshots are retained under `dev/monoliths/playtest/`.

The triangle-layout repair has a separate verified pre-change full-save backup:
`.minecraft/backups/map-integration/20261106T112407830555Z-monolith-before-triangle-8b1de0ca.zip`,
SHA-256 `b91bc6487ce539ab55f00f80e63779ddccf9f426be8f9db47571f7753a7f713d`.
External Java sources, the original bridge JAR and arena records are in
`.minecraft/backups/map-integration/monolith-before-triangle-external.zip`,
SHA-256 `e25a11ea9c2268e29ced2e02f9bd907d41df67206693ba09aab8b44e999a037a`.
The same stop/verify/move-aside/extract restore procedure applies. Restore the
external archive alongside the world archive when rolling back this repair.
The original voting poster is retained.
