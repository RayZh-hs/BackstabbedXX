# Yacht-style boundary policy for three edited arenas

Underwater Base (19), KLUT-27 (20) and Middle Ages (22) now use Yacht's timing:

| Phase | Out-of-bounds behavior |
| --- | --- |
| Lobby / countdown (`gamestate=0`) | No arena-boundary action |
| Entered arena, preparation (`gamestate=1`, `graceperiod>0`) | Return to the nearest valid current-arena player spawn |
| Active round (`gamestate=1`, `graceperiod<=0`) | Existing player-elimination function |
| End / unselected arena / spectator / nonparticipant / dead player | Excluded by existing tick guards |

The return selector requires `PlayerSpawn`, the current arena's runtime tag and
its complete allowed-area predicate. Missing markers use the previous fixed
fallback coordinates. All return teleports target the Overworld and reset player
gravity before moving. KLUT additionally releases gravity-boot effects/tags while
preserving the remaining boots cooldown. Automatic low-altitude activation can
resume normally after a rescue.

No arena footprint, height limit, spawn marker, scrap point, block or NPC changes.
KLUT retains its existing active-round fall announcement. Its separate `fall`
path also respects preparation and refuses lobby state, preventing an early
elimination before the editor boundary tick runs.

`arena-editor/editor.py` regenerates the same policy for these three arena names.
Other editor arenas keep their existing action semantics. The existing lobby
state guard remains in place. `scripts/yacht_boundary_policy.py` stages or installs
exactly seven functions: three `kill`, three `tp`, and KLUT's `fall`.

Validation on 2026-10-31: the new contract checks first failed against the old
behavior; the staged bundle then passed 19 focused checks. NeoForge 21.4.158 passed
42/42 GameTests with both mobility and boundary suites enabled. The maintained
test source is `../lobby-boundary/tests/LobbyBoundaryTests.java`. It covers the
last preparation tick, exact expiry, valid nearest-spawn selection, exclusion of
wrong-map/out-of-bounds markers, missing-marker fallback, normal start, lobby and
spectator exclusions, the legacy KLUT path, and inverted-boots rescue. The isolated
server records calls to the actual elimination route rather than running the
unrelated full match UI.

Installed into project and Prism integrated saves. Full verified backups and
SHA-256 records: `.minecraft/backups/yacht-boundary-policy/20261031T044545Z/`.
Archive 0 is the project, archive 1 Prism. Stop Minecraft and verify the archive
hash from `installation.json` before restoring an archive under its original
saves parent, keeping the current save aside. Logs/manifests are retained under
`dev/yacht-boundary-policy/`. Runtime mod files are unchanged.
