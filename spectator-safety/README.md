# Spectator isolation for knives and player trackers

The stuck-knife correction previously pulled an item toward its owner even when
that owner was spectating. It compared only the first integer of the UUID.
Classic and Killer trackers filtered the `spectating` tag but still selected
players switched directly to vanilla spectator mode.

The fix requires a queued, non-spectating, non-spectator player whose `dead`
score is not positive. An unset death score remains valid, matching the map's
round reset behavior. Stuck knives resolve their original owner's complete
UUID. Both tracker modes ignore inactive players and show a no-target message
when nobody eligible remains. Timeout recovery, explicit recall and throw
callbacks use the same eligibility guard. Recall's existing ownership and
generation cleanup is unchanged.

`scripts/spectator_safety.py` stages a new datapack ZIP without overwriting the
input world. The game-mode generator reapplies this transformation so rebuilding
modes cannot reintroduce the selectors. It preserves unrelated archive members.

Before installing a staged ZIP, stop Minecraft, acquire the save's session lock,
and make a verified full-save backup. Replace only `datapacks/mcm.zip`; this fix
does not require changing terrain, player data, configuration or runtime mods.

Verification:

- The original datapack failed both actual Minecraft regressions: native
  spectator knife attraction and nearest spectator tracker selection.
- `tests/SpectatorSafetyTests.java` runs under the existing NeoForge GameTest
  harness. It covers native/tagged/eliminated spectators, living players with
  unset death scores, UUID-prefix collisions, Classic/Killer tracker behavior,
  absent targets, timeout counters and explicit recall.
- `tests/test_spectator_safety.py` checks preservation, repeatability and
  game-mode regeneration using the committed datapack as its baseline.
