# Lobby Options Wall Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Put every setting available through `/trigger mcm_options` on the empty wall to the right of the existing upstairs lobby settings.

**Architecture:** Extend the existing text-display/interaction option system. New interactions resolve the actual clicking player's UUID and delegate to the existing options/change function. Render values from existing GameRules scores, including locked/dependent states. Install idempotently on load and rebuild, without editing terrain.

**Tech Stack:** Minecraft 1.21.4 datapack functions, existing NeoForge 21.4.158 test harness, Python overlay generator and geometry checks.

**Spec:** User request in this conversation; existing options/change actions 2–22, menu, and upstairs settings wall at X=27.9, ending at Z=108.5.

## Global Constraints

- All 14 setting categories and 21 actions must be accessible.
- Preserve current defaults, dependency normalization, 5–30 second knife timeout, existing mode/respawn choices and lobby lock rules.
- Use the existing right-hand blank wall, two rows at Z=112.5–136.5; keep the architecture and mods unchanged.
- Keep the chat menu functional and synchronized with the wall.
- Back up before installation; use the maintained Prism sync script with GameplayOnly after the game exits.

## Review Focus

- A nearby bystander must never receive another player's setting action.
- Locked/in-game/dependency-disabled interactions must not mutate settings.
- Repeated reloads/reset must not duplicate panels or reset user choices.
- Interaction hitboxes must be separate, reachable and in front of the existing wall.
- Chat-trigger changes, reset and lock/unlock must refresh wall labels.

## Task 1: Complete wall and existing-menu integration

Files: `scripts/lobby_options_wall.py`, `lobby-options-wall/datapack/`, canonical `mcm.zip`, `tests/test_lobby_options_wall.py`.

- [x] Add failing coverage/geometry/overlay tests against the existing archive.
- [x] Generate 14 panels, 21 interaction controls, titles and status callbacks using the existing lobby backend.
- [x] Add narrow load/rebuild/sync/click hooks; retain existing rule-changing code.
- [x] Verify action coverage, dependencies, idempotence and physical placement.

## Task 2: Runtime verification and installation

Files: `lobby-options-wall/tests/LobbyOptionsWallTests.java`, `docs/lobby-options-wall.md`.

- [x] Test actual installation, repeated installation, click ownership, all actions, locked/in-game states, dependencies, bounds and reset behavior in GameTest.
- [x] Compare the full Python suite with the known pre-existing failures.
- [x] Back up and sync the completed datapack/resource pack using the maintained script once the instance is stopped.
- [x] Verify installed hashes and report the wall location and supported controls.
