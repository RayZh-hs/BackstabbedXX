# KLUT-27 gravity controller and elevator HUD

Updated on 2026-11-03. Installed into the project world, Prism's integrated world
and `KLUT-27 - 1.21.4 Fixed`. Minecraft 1.21.4 / NeoForge 21.4.158 / Gravity
Changer `1.4.1-neoforge.3+mc1.21.4`; no runtime mod JAR changed.

## Behavior

- **Engineer sells the gravity controller for 4 scraps.** It is a
  `carrot_on_a_stick` carrying `item_model: minecraft:repeating_command_block`,
  so it renders with the repeating command block texture and stacks to one.
  The 4-scrap toy gun offer is unchanged.
- **Right click inverts your own gravity.** The function runs
  `gravity set_relative_base_direction up @s`, which resolves "local up" against
  the player's current gravity, so it flips to the exact opposite of any of the
  six directions. Using the mod's native player path keeps a clear body volume
  when flipping under a ceiling.
- **15 second cooldown.** A flip sets `kc_cd` to 300 ticks; a right click while
  it is positive is ignored. Carrying the controller without using it does
  nothing.
- **Cooldown HUD.** The shared actionbar shows the controller cooldown in bold
  yellow as `  重力控制器 | ■■■■■————— | 7.5s`, alongside the aqua elevator hints
  and lift cooldown. Ten remaining-time segments, tenths of a second.
- **Lifecycle.** Death, spectating, leaving the arena or resetting the match
  restores DOWN, clears the cooldown and empties the HUD line. The preparation
  rescue (`bbe_arena:klut27/tp`) already resets gravity.
- Map-issued hooks and their owned entities stay retired; guns and unrelated mod
  items are preserved. Elevators are unchanged: 30-tick cooldown, JUMP raises
  world Y and SNEAK lowers it under both DOWN and UP gravity.

## What was removed

The gravity boots are gone, not just un-traded: `mobility/up`, `mobility/down`,
`mobility/hud_boots`, `mobility/hud_boots_text`, `predicate/boots_low` and
`predicate/boots_high` are deleted from the datapack. The boots' automatic
height triggers (Y <= -6 / Y >= 10), slow-falling and jump-boost effects and the
`armor.feet` requirement no longer exist.

Two names are kept on purpose: the villager tag `Klut27BootsVendor` (renaming it
would need a full entity-data migration for no benefit) and the cleanup of
legacy `KlutBootsGravity` markers / `KlutBootsEquipped` tags so an old world
upgrades cleanly.

## Maintained files and reproduction

`scripts/klut27_mobility.py` regenerates every member and stages the integrated
ZIP plus the reviewable copies under `datapack/`; `--install` verifies full
backups, patches only authorized content and re-verifies writes. `--only` limits
an install to world indexes `0` (project), `1` (Prism integrated) and `2`
(standalone). `npc_reset` and the fire-revival snapshot carry the new offers.

## Verification

- Integrated NeoForge GameTest: **49/49 passed**, including the controller suite:
  trade item and model, four-scrap payment, inversion, 300-tick cooldown,
  cooldown blocking, HUD text/bar/colors from the real actionbar packet,
  collision-free ceiling flip, inert carrying, death cleanup.
- The same controller and elevator suites pass against the standalone pack
  (`-PbackstabbedBootsStandalone=true`, output `standalone=true`). That run
  reports 7 failures from suites that need the integrated `mcm:` datapack
  (spectator safety and round-item tests are not gated); the KLUT suites pass and
  no function fails to load. This is a pre-existing limitation of the standalone
  GameTest mode, not a defect of the standalone pack.
- Repository tests: 59 run, all pass except the two known CRLF source-hash
  mismatches in `test_merchants`.
- No client visual inspection was performed.

## Installed artifacts

| Target | Before | After |
| --- | --- | --- |
| project / Prism integrated `mcm.zip` | `9122E7BC…` | `392BD309F6F56CC7CB2BC3C5D7F3CD319875AA1834D67851B08C2D0CD5717040` |
| standalone `klut27-mobility.zip` | `20ECC910…` | `30133079A54DA3B50FA3B15D6E5437169A7D0BAF1B7980161238B57BD3FD2C35` |

Both integrated worlds are byte-identical. The project world's full backup and
`installation.json` are in `.minecraft/backups/klut27-mobility/20261103T062925Z/`;
the Prism and standalone prior files are in
`…/instances/Backstabbed++/.minecraft/backups/klut27-mobility-20261103T142938Z/`.
Detailed GameTest logs are in the Git-ignored `dev/` directory.

Note: `zipbytes` stamps each ZIP member with the current local time, so two
builds of identical content differ in archive hash. Compare member contents, not
archive hashes, when checking reproducibility.
