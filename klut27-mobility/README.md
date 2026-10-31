# KLUT-27 gravity boots and elevator HUD

Installed on 2026-10-31 into the project world, Prism's integrated world and
`KLUT-27 - 1.21.4 Fixed`. Minecraft 1.21.4 / NeoForge 21.4.158 / Gravity Changer
`1.4.1-neoforge.3+mc1.21.4`; no runtime mod JAR changed.

## Behavior

- Map-issued hooks and their owned hook entities are retired. Guns and unrelated
  mod items are preserved. The obsolete hook upgrade trade is replaced.
- Engineer sells the existing toy gun for 4 scraps, and blue vanilla leather
  gravity boots for 4 scraps. NPC and fire restoration snapshots use these offers.
- Only equipped boots activate: Y <= -6 selects UP, slow falling I and jump
  boost III; Y >= 10 selects DOWN and removes those effects.
- Either automatic transition starts 300 ticks of cooldown. Unequipping restores
  DOWN and clears the effects while retaining the remaining cooldown. Death,
  spectating, leaving the arena's match or resetting the match clears mobility
  state. Standalone uses actual player health instead of Backstabbed scores.
- Player transitions use the mod's native `gravity set_base_direction` command.
  The next entity tick rotates around the body center, preserving a clear body
  volume under ceilings. The non-player `gravity bridge marker` command must not
  be used on players; `bridge reset` preserves feet position and is unsuitable
  for an in-place ceiling flip.
- Elevators retain their 30-tick cooldown. JUMP increases world Y and SNEAK
  decreases world Y under both DOWN and UP gravity. UP destinations require two
  clear blocks below the locked shulker platform; destroyed platforms are skipped.
- One actionbar combines available direction hints and the elevator cooldown in
  aqua, plus a bold yellow boots cooldown. Bars have ten remaining-time segments
  and tenths of a second. Unavailable directions do not appear.

## Maintained files and reproduction

`scripts/klut27_mobility.py` stages the integrated ZIP and the reviewable changed
members under `datapack/`. Its explicit `--install` mode locks all three saves,
verifies full backups, patches only authorized content, and verifies writes.
It is configured for the current local project/Prism paths. It does not copy
terrain from one save over another.

`tests/test_klut27_mobility.py` verifies the installed contracts. Run with UTF-8
mode on Windows:

```text
python -X utf8 -m unittest discover -s tests -p test_klut27_mobility.py -v
```

`tests/KlutMobilityTests.java` records the actual NeoForge GameTest used for this
change. In the sibling Gravity Changer development workspace it is registered
in `GravityGameTests`, with `backstabbed.boots` and `backstabbed.bootsStandalone`
system properties exposed by the Gradle GameTest run. Stage the disposable
`run-klut` datapack with `scripts/stage_klut_mobility_test.py`; its `--standalone`
option removes match infrastructure and installs only the standalone logic plus
a merchant test fixture. It disables automatic load/tick tags because the test
drives ticks explicitly and advances the real gravity component after commands.

```text
gradlew.bat runGameTestServer -PbackstabbedBoots=true -PintegrationRunDir=run-klut
gradlew.bat runGameTestServer -PbackstabbedBoots=true -PbackstabbedBootsStandalone=true -PintegrationRunDir=run-klut
```

## Verification and recovery

- Integrated GameTest run: 41/41 passed. Standalone run: 41/41 passed, with the
  Backstabbed `dead` objective explicitly absent.
- Covered actual trade payment, tagged equipment, exact height thresholds,
  300-tick timing, re-equip bypass prevention, independent players, death cleanup,
  actionbar packet content/colors, both elevator orientations, blocked/destroyed
  destinations, and ceiling collisions on expiry/unequip.
- Installed contract tests: 6/6 passed. No client visual inspection was performed.
- Repository regression run: 31 tests, with the same 3 failures and 3 errors
  observed before installation. Existing checks assume the old Middle Ages
  predicate/spawn format; merchant checks also report CRLF/source-hash mismatches.
  This change does not modify those unrelated maps or validation baselines.
- Verified 2,057 pre-existing files. Eight existing files changed and one
  standalone pack was added. Terrain, POI, mod JARs and existing editor changes
  are byte-identical. Entity-region comparison permits only Engineer's name,
  visible-name flag, offers and vendor tag; all positions and other NPCs match.

Full verified backups and SHA-256 records are in the Git-ignored directory
`.minecraft/backups/klut27-mobility/20261031T032620Z/`. Archives `0-world.zip`,
`1-world.zip`, `2-world.zip` correspond to project, Prism integrated and standalone
respectively. Stop Minecraft, verify `sha256.json`, move the affected save aside,
then extract that archive under its original saves parent to restore. Keep the
backup and moved save until the restored world has been checked.

Detailed before/after regression logs, GameTest logs and preservation manifests
are in the Git-ignored `dev/klut27-mobility/` directory. No Git commit or push was
performed.
