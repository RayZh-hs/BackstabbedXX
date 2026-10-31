# KLUT-27 gravity boots and elevator UI implementation plan

> Execute inline with superpowers:executing-plans; review the final patch separately.

**Goal:** Replace map-issued grappling hooks with purchasable gravity boots and add direction-aware elevator hints/cooldowns.

**Architecture:** Preserve the current dirty working map and arena-editor changes. Generate a narrowly scoped datapack overlay, patch merchant snapshots and existing lifecycle calls, then validate in a disposable NeoForge world before installing into the project and Prism worlds. Keep runtime mod .3 unchanged.

**Tech stack:** Minecraft 1.21.4 datapack format 61, NeoForge 21.4.158, Gravity Changer .3, Python/nbtlib and NeoForge GameTests.

**Spec:** User request and confirmed cooldown decision in this chat, 2026-10-31.

## Constraints and decisions
- Stop automatically issuing hooks and clear old map-tagged hooks/placeholders and owned hook entities; preserve guns/knives and unrelated mod items.
- Engineer retains the 4-scrap toy gun trade; replace the obsolete hook upgrade trade with 4 scraps for blue vanilla leather boots.
- Only equipped, tagged boots activate. Y <= -6 switches UP with slow falling I and jump boost III; Y >= 10 switches DOWN and clears those effects.
- Each automatic transition starts 300 ticks of cooldown, blocking both directions. Unequipping, death, leaving/reset immediately restores DOWN and removes effects. Unequipping does not erase a running cooldown, so re-equipping cannot bypass it.
- Existing elevators retain 30-tick cooldown. JUMP means increasing world Y, SNEAK means decreasing world Y even under UP gravity. UP landings need two clear blocks below the elevator and preserve UP gravity.
- A single actionbar combines light-blue available-direction hints/elevator cooldown and yellow bold boots cooldown, ten segments plus tenths of seconds. No unavailable-direction hint; no destination/no cooldown charge.
- Existing NPC locations, map geometry, fire restore baseline, airless-room rules, player/scrap spawns, unrelated arena/editor changes remain.
- Project + installed integrated saves receive gameplay; standalone receives the same merchant/boots/elevator interaction without match-role gates.

## Steps
- [x] Add failing assertions for boots item/trade, hook retirement, lifecycle and elevator/UI contracts.
- [x] Build the overlay and snapshot patcher; back up touched files, stage all changes without touching production saves.
- [x] Test actual boots transitions/thresholds, exact cooldown, unequip/re-equip, two players, cleanup and merchant purchase.
- [x] Test DOWN/UP elevator support, destination clearance, top/bottom hints, cooldown and combined actionbar.
- [x] Run repository regression checks and actual NeoForge tests; review and install verified overlay while worlds are closed.
- [x] Verify hashes and preserved terrain/entities, record backups and results; do not commit/push automatically.

## Review focus
Missing/removed equipment during cooldown; same-tick gravity and elevator changes; inverted feet/head clearance and jump detection; stale hook trades in fire/NPC reset snapshots; simultaneous cooldown HUD fields overwriting each other; unrequested dirty editor/terrain changes.
