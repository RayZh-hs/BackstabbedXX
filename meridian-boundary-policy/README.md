# Meridian Base — Yacht-style boundary timing (2026-11-03)

Meridian Base (map 17) reacted differently from Yacht. Applied now:

| Phase | Before | After |
| --- | --- | --- |
| Lobby / countdown (`gamestate=0`) | teleported to the return point | no arena-boundary action |
| Entered arena, preparation (`gamestate=1`, `graceperiod>0`) | ocean contact **eliminated**; leaving the scene teleported | both return to a valid arena spawn |
| Active round (`gamestate=1`, `graceperiod<=0`) | leaving the scene **teleported back** forever | existing elimination function |
| Spectator / dead / nonparticipant | excluded at the tick guard | unchanged |

That is Yacht's contract; the ocean is Meridian's equivalent of Yacht's death
line, and `meridian_base:scene` is its arena bound.

## Nothing about the boundaries changed

No predicate, block tag, coordinate box, spawn marker, scrap point, dispenser
pad or NPC was modified. `scene`, `arena`, `ocean_height`, `#meridian_base:ocean`
and all 825 `arena` boxes are byte-identical. The five ocean probe offsets
(`~±0.299 ~-0.01 ~±0.299`, plus the centre) are unchanged; only the reaction
they call was moved behind a phase decision.

Four functions change (`data/meridian_base/function/`):

* `check_player` — one game-state guard at the top, then the phase split for
  leaving the scene. The dispenser-pad block is copied through unchanged.
* `check_ocean` — the same five probes, now calling `ocean_contact`.
* `ocean_contact` — **new**: preparation returns, the active round eliminates.
* `return_player` — now prefers the nearest `PlayerSpawn` marker carrying
  `MeridianBaseRuntime` and satisfying `meridian_base:arena`; the previous fixed
  point `24582.5 -29 24576.5` stays as the fallback. All 24 spawn markers sit
  inside the `arena` predicate, so a qualifying marker normally exists.

## Install record

| World | Before | After |
| --- | --- | --- |
| project `.minecraft/saves/Backstabbed ++! …` | `A9F045F2…447BEE` | `9122E7BC…61A6` |
| Prism `Backstabbed ++! by NorbMinecraft…` | `A9F045F2…447BEE` | `9122E7BC…61A6` |
| Prism `Backstabbed ++! v1.1.1 Latest 2026-10-28 77e59f6` | `A9F045F2…447BEE` | `9122E7BC…61A6` |

Full API: `9122e7bc5cacdd2b35b1feaab3fe05a3dacb81792a3838c6fdcfac774fe761a6`.

The project world has a verified full-world backup plus `installation.json` at
`.minecraft/backups/meridian-boundary-policy/20261103T061436Z/`. The two Prism
worlds have verified `mcm.zip` backups at
`…/instances/Backstabbed++/.minecraft/backups/meridian-boundary-policy/20261103T141449Z/{main,latest}/`;
only `mcm.zip` differs in each save, and every other archive member was compared
before the swap.

`scripts/meridian_boundary_policy.py` stages with no arguments and installs with
`--install`; `--only 0,1` limits the install to selected worlds from
`stage.json`. On this machine the Python runtime cannot write under `%APPDATA%`,
so the two Prism worlds were written with the same verified copy step from
PowerShell. Re-run `stage` before `install` whenever the datapack moves on.

## Survey of the other arenas

Yacht-style (rescue in preparation, eliminate in the round): **Yacht**,
**Panda Village**, **KLUT-27**, **Underwater Base**, **Middle Ages**,
**Sworld Island**, **Cube Block**, **Airship**, **Riverboat**, **Train**,
**Sculk**, **Canyon**, and now **Meridian Base**.
`tests/test_boundary_policy_parity.py` pins this list.

Still different, deliberately not touched by this change:

| Arena | Difference |
| --- | --- |
| Bagger 288 (18) | eliminates during preparation; no rescue branch and no grace split |
| River Bank (14) | always returns an escaped participant; it never eliminates |
| Subway Station (16) | boundary handling is disabled by design |
| Launchpad (4) | only active-round kill zones; no preparation rescue |
| Library 2, Vineyard 2, Cyberpunk, Industry, Gumdrop | no out-of-bounds rule at all |
| Cabin (9) | no out-of-bounds rule (freezing mechanic instead) |

Bagger 288 is the one with the same defect this change fixed elsewhere: an
escaped participant is eliminated during the 15-second preparation instead of
being returned. Ask before changing it.
