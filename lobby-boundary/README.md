# Lobby boundary timing fix — 2026-10-31

Affected arenas: Underwater Base (19), KLUT-27 (20), Middle Ages (22).

The editor-generated global boundary tick accepted game states `0..1`. State 0
is still lobby queueing/countdown, so queued players in the lobby were outside
the selected arena. The boundary's non-playing fallback consequently teleported
them to the arena's single return point before normal start.

Boundary ticks now require state 1. `mcm:maps/start` first distributes queued
players among unoccupied spawn markers and then sets state 1 synchronously.
The on-map grace period also uses state 1, so its existing boundary behavior is
preserved. Only the state guard changes; predicates, coordinates, spawn allocation,
elimination rules, map IDs and player exclusions are unchanged.

`arena-editor/editor.py` exports the corrected guard for future edits.
`scripts/lobby_boundary_gate.py` stages and installs the same narrow migration in
the project and Prism integrated worlds. `datapack/` contains the three changed
members. Standalone worlds have no lobby flow and require no change.

## Validation

- New Python regression tests failed on the original generator and all three
  original installed boundary gates before the fix.
- Real NeoForge GameTest reproduced premature teleportation on all three arenas
  at countdown values 199, 100 and 2.
- The fixed run passed 42/42 GameTests, including lobby/end/unselected-state
  exclusion, four distinct normal-start spawn allocations, in-bounds safety,
  active/grace-period boundary routing, and nonparticipant/spectator exclusions.
- The test drives the real boundary, start and spawn functions. Only the downstream
  elimination handler is replaced in the disposable test pack by a recorder,
  avoiding unrelated match UI dependencies. Automatic global load/tick tags are
  disabled while the test explicitly drives each phase.
- The editor's existing union/exclusion export test passes unchanged.

The reviewed GameTest source is `tests/LobbyBoundaryTests.java`; it is registered
in the sibling Gravity Changer development workspace's test loader and enabled
with `-PbackstabbedLobbyGate=true`. Runtime mod JARs are unchanged.

Local evidence: `dev/lobby-boundary/gametest-before.log` and
`dev/lobby-boundary/gametest-after.log`. Full verified save backups, archive
SHA-256 values and the exact installation report are under
`.minecraft/backups/lobby-boundary/20261031T034216Z/`. Archive 0 is the project,
archive 1 the Prism integrated save. To restore, stop Minecraft, verify the
archive hash in `installation.json`, move the affected save aside, and extract
the appropriate archive under its original saves parent.

No Git commit or push was performed. The previously reported unrelated test
failures were left alone as requested.
