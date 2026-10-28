# KLUT-27 hazards and grappling loadout

User: lower enclosed rooms below Y=-20 kill after ten continuous seconds;
warn at two seconds. Elevators have 1.5-second cooldown. Every participant
starts with a gravity grappling hook in hotbar slot zero; innocents (including
gunner) have ten-second cooldown, murderers none. User explicitly selected
cooldown starting on retrieval/detachment, not launch.

1. Read saved cabin geometry; define three bounded interior volumes, excluding
   outside void and the floor at Y=-20. Run only after role assignment/grace.
   Add per-player 40/200 tick warning/death and reset on exit/death/round end.
   Use existing fake-death function to preserve team/win/drop bookkeeping.
2. Add opt-in item custom data `grappling_cooldown_ticks`, generic exemption
   tag `gravity_hook_no_cooldown`, and `/gravity grappling_hook clear <players>`.
   Unconfigured hooks keep existing behavior. Opt-in hooks allow manual recall,
   start a native item cooldown once on retrieval/removal, and enforce it server
   side. Clear active hook and cooldown during lifecycle cleanup.
3. Give hook before role loadouts to reserve slot zero; apply exemption only
   after murderer assignment. Prevent dropping/death loot using existing tags.
   Change successful elevator cooldown to 30 ticks; decrement before input
   checks so a fresh transfer retains all 30 ticks.
4. Write failing tests, implement, run saved-geometry and actual NeoForge
   timer/recipient/loadout/cooldown/teleport checks. Preserve other pending work.
5. Back up saves/JARs, build current mod, sync main source/live datapack and mod;
   standalone receives elevator cooldown only (no murder roles or game death).
   No automatic commit/push.


Superseded cooldown implementation: user requested restoring mod .3. The
current implementation is scripts/klut27_datapack_hook_cooldown.py, using
vanilla origin/scoreboard/item modifiers. See docs/arenas/klut27.md.
