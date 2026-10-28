# KLUT-27 engineer, hooks and fire (2026-10-28)

## Installed scope
The standalone `KLUT-27 - 1.21.4 Fixed`, the PrismLauncher Backstabbed++ latest world, and the repository source world all contain the relocated original engineer and warning sign. Both integrated worlds have identical `mcm.zip` gameplay. Gravity Changer stays at exact version 1.4.1-neoforge.3+mc1.21.4 (SHA256 `32e308ce51de825b11a0530677caeaaed1e4758143c7a950dbea0a075e1bb02a`). No runtime mod changes were made.

Coordinates below are standalone coordinates. Integrated X/Z add 36864.

## Merchant and hooks
The original BubbleVehicles Trader keeps its UUID and name, moves to `(12.5,15,33.5)`, faces south, and has NoAI enabled. The old Pawn Shop resident is removed by exact UUID. Offers are unlimited for practical play and do not increase demand:
- 4 netherite scrap → a stick with the real gun item model; it has no `gun` flag and cannot fire.
- 5 netherite scrap + an innocent-role base grappling hook → upgraded hook.

After role selection, only innocent-team base hooks get the merchant eligibility component. The native merchant requires the exact base custom-data component, rejecting murderer hooks, cooling placeholders and already-upgraded hooks. Upgraded items retain their tier when swapped to/from the disabled placeholder. Normal cooldown is 200 ticks; upgraded cooldown is 80 ticks, starting after the owned hook entity disappears. Murderers continue to bypass the extra cooldown. Mod .3's short native debounce remains unchanged.

## NPC combat
A `GunShot` arrow hitting a villager in the active KLUT round invokes the existing innocent-shot penalty for an innocent gunner. Removing the gunner role also prevents repeated punishment from another already-flying bullet. Melee, ordinary arrows, murderers, spectators and other arenas do not invoke this penalty.

The tagged golem uses native retaliation AI, with follow range 64. Its physical hit uses a tiny positive damage value so the hurt event fires without killing a low-health player before the datapack can run normal minigame elimination. The exact broadcast is `<player>被铁哥一巴掌扇飞了！`. The standalone save uses ordinary death because it has no minigame role/death system. NPCs have protective health restored during ticks, and their round reset restores positions, health and trades.

## Fire (large-scene revision)
The latest standalone edits are authoritative: 45 block/state differences were copied into both integrated worlds, including 35 new wooden planks and five glass removals. A new locked Simple Elevators block replaces `(8,15,20)` with clear landing space above. It extends the X=8/Z=20 column from Y=6/10 to Y=6/10/15; there are now 19 elevator stops.

The lava lever `(6,12,19)` still starts a single scripted fire per round. Each burning fuel block lasts 60 game ticks before burning through and igniting face-adjacent fuel. The rebuilt connected graph has 679 candidate fuel blocks. Macro dispatch processes active cells rather than executing one selector for every candidate every tick. Waterlogged/Nether wood exclusions remain, and ordinary walls stop propagation.

The earlier 3-block overheat approximation is removed. A working elevator explodes immediately when a still-present burning block touches its face, edge or corner (26-neighbour shell). An unlit, burnt-out or removed block cannot trigger it; a one-block air gap is safe. Six elevator stops are reachable by this fire. Each explodes once, becomes black wool, removes radius-2 flammable block volumes, and ignites surviving adjacent fuel. Radius-3 live players and villagers die; iron golems are never explosion damage targets. The engineer's automatic healing excludes blasted villagers, so it cannot undo the death.

Flames and smoke are particles, not uncontrolled vanilla fire or TNT. Attached ladders, signs and two supported display frames are removed without drops; frame contents are restored with their original UUIDs. Container contents are cleared before scripted destruction. Prior block/entity/mob-loot gamerules are restored immediately. A few supported black carpets remain as ashes.

Round reset restores the new scene's block states, sign text, elevator locks, decorative entities and any original villagers killed by these explosions (17 villager snapshots). It clears all fire jobs and per-elevator blast flags. Standalone has the same fire; run `/function klut27:fire/reset` to reset it manually. Integrated reset runs before ordinary door/lever restoration. Old fire runtime state is migrated once when the new pack loads.

The subsequent resident-placement revision adds an unconditional ordinary
villager reset after restoration: 16 residents in standalone, 19 in integrated
saves. Survivors return to their individual homes and missing residents are
respawned with their original UUIDs. Integrated activation also runs it.
This supplements the fire-specific snapshots, including three villagers that
exist only in the integrated scene. See `klut27-population.json` and `klut27.md`.

The manifest `klut27-fire.json` records fuel cells, six exposed elevators, the full restoration footprint and blast sets. `klut27-large-fire-sync.json` records the standalone changes and added elevator.

## Maintenance
`klut27_engineer_fire.py --npcs` installs the entity/trade/combat changes and the current hook generator. `--fire` generates fire from the pristine standalone scene and installs both integrated copies and its standalone pack. Run only with Minecraft exited and verified backups; do not regenerate the restoration baseline from an already-burnt scene. `rebuild_klut27_fire.py` checks/synchronizes fresh standalone block differences and replaces the new elevator, then installs the fire; no ignored staging files are required. `klut27_fire_model.py` holds dependency-free connectivity/contact rules.

## Backups
Full verified archives are under `.minecraft/backups/klut27-engineer-fire/`:
- standalone: `20261028T104325786563Z-before-engineer-fire-0-b7efadff.zip`, SHA256 `529ee7295cb3f928b0b0a605acf2fd6a50c85f6ec52fb30940557b6e3309fb05`
- repository: `20261028T104326661282Z-before-engineer-fire-1-f656fd82.zip`, SHA256 `1d89d778c8262eabc531ef32d97ecad359a7d87fec0e8df6e101498d697378a0`
- live integrated: `20261028T104333156114Z-before-engineer-fire-2-dc229688.zip`, SHA256 `32da5205fb7a257369ed98e232598a686157c5ac455387d6c5e11bfbddb1db9b`

To restore, stop Minecraft, verify the chosen archive with the project backup tool, move the affected save aside, then extract the archived world folder under its original saves parent. Keep the archive and moved save.

## Verification
- `make test PYTHON=C:/Python314/python.exe`: 66 checks passed, including all arena spawn/boundary regressions and native saved merchant data.
- NeoForge integrated GameTest run: all 40 registered tests passed (includes the inactive standalone opt-in case). New coverage exercises native merchant validation/consumption, two upgraded cooldown cycles, real villager damage, native golem AI retaliation, native golem melee at one health, blast distance boundary, complete fire progression, whole-room state restoration and sign text restoration.
- Standalone GameTest run: all 40 registered tests passed (includes the inactive integrated opt-in case), with new scene/datapacks loaded and existing elevator/button checks.
- Resource pack build succeeded (252 files). No new runtime mod artifact was built or installed.
- All three saved scenes contain one original engineer at the target, no old resident, one tagged original golem, and the ceiling-supported sign. Integrated gameplay ZIPs match byte-for-byte.
- Existing integrated-map disabled vanilla advancement-parent warnings remain; there are no new KLUT function/advancement parsing errors.

Server logs are in the mod workspace `build/klut-large-fire-clean-world.log` and `build/klut-large-fire-standalone.log`. These are automated server tests, not a manual multiplayer client playthrough.

### Large-fire verification and recovery
The integrated server test burns the complete scene: 717 changed blocks were observed, then every block state in the affected room volume was verified after reset. It checks corner contact, an intervening gap, inactive/burnt-out markers, engineer death without automatic revival, unchanged golem health, player radius boundary, original display-frame UUIDs/items, sign text, and all 19 elevator stops. Standalone exercises the same 19 stops in both directions.

Fresh full backups before this revision are in `.minecraft/backups/klut27-large-fire/`:
- `20261028T113941283120Z-before-large-fire-0-47e0ebba.zip`: `2312db3306dab925b38bd67da56d35f7bc35a2f8dd5d4be927bdc5bdb0e86e42`
- `20261028T113942150055Z-before-large-fire-1-1cf92745.zip`: `93248cf09ed995b49d5889ed8aac6f310dc28c1b18db2cf5e349c885d7b75a23`
- `20261028T113948856169Z-before-large-fire-2-2d299e1a.zip`: `d07251e4d32ef33092c1c819d5048ca4fae514627f37ec194ba932192c329f9e`
