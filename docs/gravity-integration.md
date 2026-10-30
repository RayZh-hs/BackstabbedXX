# Gravity integration (Minecraft 1.21.4 / NeoForge 21.4.158)

Requires Gravity Changer `1.4.1-neoforge.3+mc1.21.4` on host and clients. The gameplay datapack uses its bridge commands; older versions do not provide these commands.

## Gameplay behavior

- Guns remain no-gravity arrows: speed 7, existing eight-tick lifetime, ammo, cooldown, recoil, ownership and damage-event rules. The muzzle is local height 1.5 and aim follows the player's actual gravity frame. Bullet visuals retain the original model transformation.
- Thrown knives snapshot the player's applied gravity direction and strength before replacing the snowball with an arrow. Both arrow and cosmetic item retain owner UUID and generation tracking. Later player gravity changes do not steer an existing knife.
- Manual player drops snapshot applied gravity, retaining their world-space launch velocity. Scripted death inventory drops use the same snapshot and rotated local height 0.5.
- Scrap reads its selected marker's `data.gravity_direction` and `data.gravity_strength`. Missing fields mean `down` and `1.0`; strength is a local multiplier and still combines with dimension/global gravity. Spawn probability, timing and item count are unchanged.
- Entering a round, leaving a game, and receiving lobby items reset player base gravity. Other effects retain the mod's normal precedence.
- Cube Block (23) initializes players from the selected spawn marker after that reset. Its 32 shared player/scrap points cover all six faces with gravity pointing into each face. The bundled host bridge's `arena_spawn_gravity <marker>` applies player gravity synchronously before teleport; the Gravity Changer marker command supports non-player targets.

Example configured scrap marker:

```mcfunction
summon marker ~ ~ ~ {Tags:["ScrapSpawn","MapEntity"],data:{gravity_direction:"north",gravity_strength:1.0d}}
```

The six valid direction names are `down`, `up`, `north`, `south`, `west`, `east`. Set points deliberately beside their intended supported surface; changing a point's gravity does not relocate the point or modify architecture.

## Reusable mod commands

```mcfunction
# Execute as the shooter. Target is an existing arrow.
gravity bridge fire <arrow>
# Snapshot applied source gravity to supported non-player target(s).
gravity bridge inherit <source> <targets>
# Initialize from a marker's data, default down/base strength 1.
gravity bridge marker <marker> <targets>
# Snapshot source gravity and place drops at rotated local height 0.5.
gravity bridge drop <source> <targets>
# Synchronously reset base gravity before teleport (players supported).
gravity bridge reset <targets>
# Read-only result 1 for applied DOWN, otherwise 0.
gravity bridge is_down <source>
```

All commands require permission level 2. The bridge preserves target world velocity when changing its gravity; inheritance normalizes environmental strength so it is not multiplied twice. Invalid target/configuration is rejected before mutation.

## KLUT-27

Map ID 20, namespace `klut27`; see `docs/arenas/klut27.md` and `.json` for provenance, boundaries, elevator routes, spawn locations and six supported gravity test contacts. The standalone world has `doFireTick=false` and a converted Simple Elevators datapack. Integrated elevators are scoped to living participants in this arena with applied DOWN gravity. No architecture is changed to manufacture gravity test surfaces.

Development verification uses isolated `run-klut` and `run-standalone` world copies, never live saves. The ordinary GameTest suite omits opt-in map checks; run with `-PbackstabbedIntegration=true -PintegrationRunDir=run-klut` and `-PbackstabbedStandalone=true -PintegrationRunDir=run-standalone` respectively after preparing those copies. Do not treat an opt-in test's early return as evidence of map testing.

## Verification recorded 2026-10-28

- Repository suite: 61 tests passed.
- Original gameplay integration suite: 29 checks passed against the new canonical datapack and gravity mod (ammo, crafting, shield milestone/durability, gun pickup, knife ownership/paid recall/timeout, rewards, scrap rates/boost and highlights).
- NeoForge suite: 40 registered tests; ordinary run executes 38 mod tests and skips the two opt-in map cases. Separate KLUT and standalone runs each enable their respective case; both completed successfully.
- KLUT uses saved imported geometry: six actual body/support contacts, six-direction gun aim/speed/straight flag and exact -3 local pitch recoil, ammo/cooldown, two shooters, knife arrow/cosmetic gravity and full-owner recall, per-marker scrap, pickup reservations, activation/reset/containment, and all36 directional elevator routes plus real jump/sneak scoring and horizontal-gravity exclusion.
- Standalone: all18 original elevator stops tested upward/downward (36 paths), including trapdoor/sign headroom and no-op ends.
- Review fixes: synchronous reset prevents delayed destination displacement; cleared held anchors before lobby reset; shield incoming direction uses the same local frame as facing. Red regressions reproduced before green runs.
- These are real Minecraft1.21.4/NeoForge21.4.158 server tests, not a human multiplayer/client visual playthrough.
- Final installed artifact hashes and target folders: `gravity-installation-20261028.json`. Original/source/live full-world backups: `.minecraft/backups/klut27/`. No GitHub push performed.
