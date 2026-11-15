# Eight-candidate lobby voting

The first-floor poster wall offers eight distinct enabled maps plus Random.
New slots are centered at Z=121 and Z=126; the reroll control is at
approximately (25.86, 3, 80.5), on the wall left of Random. Existing poster models are reused.
There are no terrain or mod changes.

## Voting rules

- Each player has one replaceable vote. Slots 7 and 8 use the same advancement
  interaction flow as the original slots.
- A unique concrete leader wins. Concrete ties use one uniform random draw
  among the tied leaders.
- Random tied with concrete leaders is ignored: only the highest-vote concrete
  maps enter the draw. Random strictly ahead selects uniformly from all displayed
  enabled candidates, not from the entire map registry.
- An empty pool leaves voting open and cannot activate an old selected map.
- Fewer than eight enabled maps leave the remaining slots disabled. Random is
  also disabled when there is no concrete candidate.

## Refreshing candidates

Changing an enabled-map toggle or resetting lobby defaults immediately rebuilds
the candidates before a game. The physical first-floor reroll, existing upstairs
shuffle control and developer shuffle function use the same reroll path.
Map-option pagination does not rebuild or clear votes.

Every rebuild clears ballots and restarts the nominal 20-second voting timer,
which waits for a vote as before. Rebuilding during preparation cancels pending
arena activation, resets the old selected arena and returns to voting. Active
games reject reroll/refresh; manual reroll also respects the lobby settings lock.

## Maintained implementation

- `scripts/lobby_voting.py`: deterministic ZIP overlay and eight-slot definitions.
- `lobby-voting/datapack/`: reviewable generated functions and advancements.
- The canonical integrated world's `datapacks/mcm.zip` contains the overlay.
- Four existing locale strings now include the vote-count placeholder, consistent
  with the other supported languages.

## Verification (2026-11-15)

- Four Python tests cover slot registration, generated-source/archive parity,
  idempotence, wall access and all locale count placeholders.
- NeoForge 21.4.158 runs 51 tests successfully, including the upstairs settings
  wall and the new voting scenario. Voting checks include 688 selections across
  tie/random/disabled pools, real toggle callbacks, pagination, ballot clearing,
  pending-activation cancellation, lock guards and repeat rebuilds.
- Tests run in a disposable world. Entity tracking is explicitly enabled for the
  fixed lobby fixture, away from GameTest's random origin. A fresh run directory
  avoids stale temporary entities left by earlier failed test experiments.
- The full Python suite retains six pre-existing failures; this work adds none.
- A subsequent regression test checks the exact poster plane and reroll position.
  Vec3 command arguments use explicit decimal X/Z coordinates: bare integers
  silently center the coordinate by 0.5 blocks and put the poster behind the wall.
  Existing right-hand reroll entities and their callback passengers are migrated
  automatically to the left-hand location.
- Client verification after the coordinate fix confirmed visible original and
  newly added posters (including slots 7/8), and the reroll button on the wall
  to the left of the Random poster. The world was saved after verification.

Deploy with the maintained `sync-prism.cmd -GameplayOnly -ProjectPath <checkout>`
while Minecraft is stopped. This backs up the instance and verifies the installed
datapack and rebuilt resource pack.
