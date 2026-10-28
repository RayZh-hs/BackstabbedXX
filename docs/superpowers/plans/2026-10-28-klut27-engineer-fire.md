# KLUT-27 engineer, NPC combat and scripted fire

## Scope
Retain mod .3. Update the standalone scene and both integrated worlds without touching unrelated arenas. Replace Pawn Shop resident with original engineer. Fixed-price fake gun and innocent-only base-hook upgrade (4s after return). Use actual projectile/attacker events for penalties. Script a 60-tick-per-block connected fire, remove supported decorations without drops, restore the scene each round. User approved the 3-block elevator overheat threshold.

## Implementation
1. Snapshot all three worlds; inspect actual blocks and entity UUIDs; preview hanging warning sign.
2. Add failing regression checks for upgraded cooldown retention, two native trade costs and exact NPC targeting.
3. Extend hook item modifiers with innocent/base and upgraded variants; grant role-specific base hook after role selection; preserve tier through cooldown.
4. Relocate original engineer, remove old resident, install identical offers, tag golem, wire projectile-specific villager punishment and golem attack elimination. Restore NPC health/position/offers each round.
5. Derive bounded fire graph from actual flammables; create per-cell ignition timers and decoration cleanup; no actual TNT or free-running fire. Add visible particles, explosion and radius checks; restore complete affected states/NBT on reset.
6. Run datapack parsing and real-server regression tests for trades, roles, combat, fire timing, explosion radius and reset; run repository suite. Verify all three save patches and mod hash; document limitations.

No commit or push requested.
