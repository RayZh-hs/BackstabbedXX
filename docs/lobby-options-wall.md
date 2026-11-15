# Upstairs lobby options wall

The upstairs settings expose every setting from `/trigger mcm_options`.
The game-mode selector is centered at X=26.86, Z=84.5, on the negative-Z end wall
formerly occupied by the reset button. Its title/value start at Y=10.05, with
three choice buttons below. The physical reset button, label and callback marker
are removed on load and are no longer generated when rebuilding the options.
The remaining panels occupy X=27.86, Z=112.5–136.5,
with two rows above the existing floor. Right-click a panel to toggle/cycle it;
timeout, mode and respawn panels have individual choice buttons.

| Column | Upper panel | Lower panel |
| --- | --- | --- |
| 1 | First 10 scrap grants killer shield | Killer scrap reward |
| 2 | Gun carriers can hold scrap | Craft gun for 8 scrap |
| 3 | Scrap ammunition | Scrap spawn multiplier |
| 4 | Lost knife timeout enabled | Timeout seconds, 5–30 |
| 5 | Periodic global outline | First 30 seconds scrap boost |
| 6 | Killer teammate outline | Dropped gun outline |
| 7 | — (mode selection moved to the end wall) | Gunner respawn, 3/5/10/20/30 seconds |

## Behavior

- All 21 actions (trigger values 2–22) use the existing option-changing functions.
- The clicking player's full UUID is read from the interaction record. Nearby
  players and callback executors do not receive the action.
- Values remain synchronized with the chat menu, reset defaults and lock/unlock.
- Voting and lobby preparation allow changes. Active games and locked settings
  disable the controls. Game-state transitions refresh them automatically.
- Crafting retention and ammunition require gun-carrier scrap collection; disabled
  panels explain this prerequisite. Timeout buttons stop at 5 and 30 seconds.
- Loading installs the wall after 20 ticks; reinstalling replaces only entities
  tagged `McmOptionsWall` and their passenger markers. Settings are preserved.
- There are 26 text displays, 21 interactions and 45 passenger markers. No blocks,
  arena geometry or mod binaries are changed.

## Maintenance and verification

`scripts/lobby_options_wall.py` defines the layout and narrow archive hooks.
`lobby-options-wall/datapack/` contains the generated functions and static helpers.
The canonical integrated world's `datapacks/mcm.zip` contains the installed overlay.

Python checks cover action coverage, archive/source parity, idempotence, existing
wall/floor geometry and non-overlapping button bounds. The NeoForge test in
`lobby-options-wall/tests/LobbyOptionsWallTests.java` exercises the actual functions,
all choices, click ownership, prerequisites, limits, chat refresh, locks, game-state
transitions, defaults and repeated installation. Copy it into the existing test
harness's gameTest source set and use a disposable world with the candidate
datapack's automatic load/tick tags disabled.

The test explicitly enables entity tracking in the fixed lobby chunks: GameTest
uses a random remote origin, and its force-loaded chunks alone did not expose
entities to selectors. This fixture setup is confined to test code.

Validation on 2026-11-15: the three wall-specific Python checks pass; the full
83-test Python suite retains the same six pre-existing failures (Treehouse,
KLUT mobility, Merchants and Monolith). The NeoForge suite passes 50 tests,
including the complete wall scenario. No client screenshot verification is
included in this result.

Deploy through the maintained `sync-prism.cmd -GameplayOnly -ProjectPath <checkout>`
after exiting Minecraft. The script backs up and verifies the destination files.
