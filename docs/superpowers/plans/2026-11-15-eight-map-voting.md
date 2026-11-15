# Eight-map voting implementation plan

> Use superpowers:executing-plans for inline implementation and one final independent review.

**Goal:** Eight distinct enabled candidate maps, fair highest-vote selection, live
enabled-map refresh and a physical reroll control, tested and synced to Prism.

**Architecture:** Extend the existing poster/interaction slots and advancement
callbacks. Replace the winner calculation with a filtered pool and one uniform
`sort=random,limit=1` choice. Keep arena activation and all gameplay/mods intact.

**Spec:** User request in this conversation, 2026-11-15. Random tied with concrete
maps must lose its special effect: choose only among highest-vote concrete maps.
Random alone winning chooses among all displayed enabled candidates.

**Implementation decisions:** Clearing/rebuilding candidates clears old ballots
and resets the 20-second timer. Enabled-map changes refresh before games, including
returning from preparation to voting; active games remain untouched. Manual reroll
obeys the lobby lock. Preserve the existing upstairs options wall.

**Tech:** Minecraft 1.21.4 functions/advancements, Python ZIP overlay, existing
NeoForge 21.4.158 GameTest harness. No production mod changes.

## Review focus

- No disabled/empty/random slot can become a concrete winner.
- Ties and random-only wins must reach every eligible candidate, including slots 7/8.
- Rebuilds must remove stale posters and votes, without duplicating entities.
- Enabled-map edits and reset defaults must refresh immediately; pagination must not.
- Returning from preparation must cancel pending old-map activation.

## Task 1 — voting overlay

- [x] Add failing archive coverage and physical placement checks.
- [x] Inspect free lobby space, add slots 7/8 and a reroll control without terrain edits.
- [x] Implement tallying, fair resolution, empty-pool guard and live refresh hooks.
- [x] Preserve prior wall changes and verify generated source/archive parity.

Files: `scripts/lobby_voting.py`, `lobby-voting/datapack/`,
`tests/test_lobby_voting.py`, canonical `datapacks/mcm.zip`.

## Task 2 — runtime verification and delivery

- [x] Test votes/change-votes, slots 7/8, tie/random distributions, disabled maps,
      reroll/reset/defaults, locks, preparation and game-state guards.
- [x] Review the whole change and resolve important findings.
- [x] Compare the full Python suite against six pre-existing failures.
- [x] Sync using the maintained Prism script; verify hashes and backup location.

Files: `lobby-voting/tests/LobbyVotingTests.java`, `docs/lobby-voting.md`.

## Execution ledger

- Base: 5285245 plus the completed, uncommitted upstairs options wall. Preserve it.
- Game is stopped at preflight. No commit/push was requested.

- Validation: 51 GameTests passed; 87 Python checks, same six pre-existing failures. Review locale finding fixed. Prism gameplay sync verified with backup.
