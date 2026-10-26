---
name: backstabbed-map-creator
description: Integrate a requested Minecraft arena into Backstabbed++, including the imported build, an imagegen voting poster, validated player spawns, and enforced play-area boundaries. Use for adding or porting maps and repairing an integration; not for preview-only requests.
---

# Backstabbed Map Creator

Complete all four parts of an integration: **build, poster, suitable spawns,
and player containment**. A pasted build or a selectable voting entry alone
does not finish the task.

Resolve this skill's real directory, following any installation symlink, then
walk `../../..` to the repository root. Read
[the repository integration contracts](references/repository-contracts.md)
before changing the world or resource pack; verify those paths and contracts
against the current checkout.

## Establish the intended arena

Use the vendored
[`$minecraft-map-preview`](../minecraft-map-preview/SKILL.md) to inspect the
source and the main playable object. Read that repository-local skill directly
if it is absent from the available skill catalog. Its viewer, exporter, tests,
and pinned dependencies live in the root-level `map-previewer/` directory.
Preserve the original download, author, source URL, version metadata,
and reuse terms. Check the target game version in `mmc-pack.json` rather than
assuming the download page's version is accurate.

Record the source selection, destination placement, coordinate transform,
main playable region, map namespace/ID, and any user-designated spawn areas.
Treat the user's indicated points, decks, rooms, or surfaces as constraints.
A measurement box's corners are not spawn points unless the user says so.
Carry source coordinates through translation/rotation into the destination
world and validate the destination result.

## Incorporate the build

Import the requested architecture into an unused, non-overlapping region of
the game's source world. Include the build's needed block states, block
entities, and decorative entities; a block-only preview export may omit them.
Preserve the source world and unrelated arenas. Inspect imported command blocks
and datapacks: source spawn, teleport, ticking, or world-changing commands must
not take control of Backstabbed++.

Implement the complete arena lifecycle using the current datapack conventions:
registration, unique map ID, voting/selecting, activation, player/spectator
spawns, per-round functionality, cleanup/reset, and needed chunk loading.
Update applicable map labels and options. Repeated activation, reload, and reset
must not leave duplicate markers, stale boundaries, scheduled work, or entities.

Routine import, registration, poster wiring, spawn selection, and containment
logic are part of the requested integration. If they reveal a problem whose
solution requires changing the map's design or geometry, follow the decision
and repair rule below.

## Generate and install the voting poster

**Use the `$imagegen` skill for every newly integrated map's poster.** Read and
follow that skill; use its built-in image-generation path by default. Generate
art from the actual arena's theme and recognisable features, with the correct
map title and the resource pack's established poster style and proportions.
Inspect the output for misleading content, illegible text, and visual defects.
An unrelated image, screenshot placeholder, or renamed existing poster does
not satisfy this step.

Save the chosen PNG in the resource pack and wire its item definition, model,
texture, atlas entry, and voting display. Verify the whole reference chain;
creating a PNG alone is insufficient. Record the final prompt, generation
method, asset path, and creator/map attribution in the project conventions.
If image generation is unavailable, report the blocker and follow the imagegen
skill's fallback rules; do not claim the integration is complete without it.

## Generate and validate spawn points

Generate enough distinct spawns for the intended player count, distributed
across the intended playable surfaces. Check **each actual destination spawn**
against the saved blocks and the arena region:

- Its standing surface and player collision volume are safe: solid support,
  clear feet/head space, and no suffocation, immediate fall, fluid, or damage
  hazard. Account for partial blocks and block states if used.
- It belongs to the intended main object or user-designated area. For a ship,
  use its playable hull/decks, not nearby islands, ocean, or ground underneath.
  Do not accept a coordinate merely because it is inside a large bounding box.
- It is not buried under the arena, in an accidental cave, or in an inaccessible
  pocket. Deliberate underground arena content must be part of the intended
  play area; do not silently substitute an underground level for a requested
  surface or deck.
- Players can move away into legitimate routes; the spawn is not outside the
  containment region, trapped in decoration, or dependent on a closed/reset
  door's transient state. Respect user-indicated locations and avoid duplicate
  or needlessly clustered positions.

Use object membership/connectivity and walkable-route checks where appropriate,
then inspect the spawns in a preview and in Minecraft. A name-only palette
check or a screenshot is not proof of collision safety. Reject unsafe points
and choose other valid points within the user's constraints. If valid spawns
require rebuilding, moving the chosen play area, or relaxing the user's
constraints, ask the user rather than silently doing so.

## Ensure players cannot escape the main region

Define and enforce the arena's actual playable footprint, vertical limits,
dimension, and exclusions. Use unions, per-slice masks, or other suitable
geometry for irregular shapes; a coarse box may include forbidden islands,
outside terrain, or spaces below the main object. Check all legal spawns are
inside the final region.

Connect containment to the game's active-round tick path and existing return
or elimination rules. Scope it to the selected arena and live participating
players, respecting spectators, dead players, lobby players, and reset states.
Do not apply a global world border across unrelated arenas. Avoid return loops
by using only validated safe return positions.

Exercise the perimeter and plausible escape routes: doors, gaps, roof edges,
jumps, water, vertical drops/climbs, and movement/teleport mechanics actually
available in the game. Check containment across activation, grace period,
round play, reload, and reset as applicable. If closing an escape requires
adding physical barriers, sealing passages, or altering terrain, ask before
editing those blocks. A preview measurement mask is not in-game containment.

## User decisions, backups, and authorized repairs

**If a problem needs a map-design or geometry change, query the user before
applying it.** Explain the issue, affected coordinates/area, gameplay impact,
and a concrete proposed fix (or a small set of options). Continue independent
integration work while waiting, but do not implement the dependent alteration.
If the user already explicitly requested the same fix, that authorization is
sufficient; ask again only when a materially different repair is needed.

**Before the first write of an authorized repair, back up the affected map.**
Ensure the save is not being written by Minecraft. Snapshot the full affected
save, including region/entity/POI data, generated structures, datapacks, and
level metadata. Preserve the original source download, and include any other
affected working save or external assets in the recovery plan. An unsaved Git
diff or the preview NBT alone is not a map backup.

Use [scripts/backup_world.py](scripts/backup_world.py) for a timestamped,
checksum-verified full-save archive, outside the save being backed up:

```sh
python .agents/skills/backstabbed-map-creator/scripts/backup_world.py \
  '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies' \
  --backup-dir .minecraft/backups/map-integration --label '<arena>-before-fix'
```

Do not edit until the archive verifies. Record its path, SHA-256, and restore
procedure. A failure or concurrent-write warning blocks the repair until a
valid snapshot exists. Restoring means stopping Minecraft, verifying the
archive, moving the damaged save aside, and extracting the archived world
folder back under its parent; preserve the backup throughout.

To recheck a backup before restoring it:

```sh
python .agents/skills/backstabbed-map-creator/scripts/backup_world.py \
  --verify '<path-to-backup.zip>'
```

**Use `$minecraft-builder-skill` for the user-authorized map repair.** Read the
installed skill and use its recipes/structure-NBT workflow to produce the
bounded repair, then inspect it in the interactive browser preview before
importing it into the working save. The skill is available online at
[mattzh72/minecraft-builder-skill](https://github.com/mattzh72/minecraft-builder-skill).
Use that upstream when locating the skill or consulting its online instructions;
do not substitute an unrelated builder. Preserve unaffected blocks, block
entities, and states when applying a patch. If the skill cannot express or
apply the required change, explain the limitation and ask before using another
repair method.

After the repair, revalidate affected spawns, routes, containment, reset, and
unrelated neighbouring content. Keep the backup and a record of what changed.

## Completion evidence

Run `make test` and the focused checks needed for the new map. Add meaningful
regression coverage for spawn validity and boundary membership/escape behavior;
use the actual destination geometry and predicates. Build the resource pack
and appropriate release assets to verify packaging. Test selection/poster
display, spawning, a round, escape handling, and reset in the target Minecraft
version. Report any unavailable in-game verification explicitly; do not present
static checks as a playtest or mark unresolved requirements complete.

The handoff should identify the source/credits, placement and region, poster
paths/prompt, spawn count and validation, containment behavior, checks run,
remaining user decisions, and backup/repair details when applicable.
