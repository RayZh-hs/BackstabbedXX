# Backstabbed++ arena editor

Edit one arena in Minecraft Java **1.21.4**, using your own instance and launch
command. The editor is a generated **datapack**: **1.21.4-Fabric** works without
an editor mod or Fabric API. Vanilla and other 1.21.4 loaders can also run it.
The interface uses a clickable written book, clickable chat controls,
right-clickable spawn labels, and a selected-box wireframe. It does not add a
custom inventory screen or mouse-drag gizmos.

Python extracts an arena from the shared save into a **persistent creative void
world** in your chosen instance. Edit player spawns, ammo (`ScrapSpawn`),
spectators, the return position, constraint boxes, and blocks. Your instance's
existing building mods can be used normally.

## Configure your instance

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run
from the repository root:

```sh
uv run arena-editor/editor.py init-config
```

Edit `arena-editor/config.local.json`. That exact filename is Git ignored;
[config.example.json](config.example.json) is the tracked template. For Prism:

```json
{
  "game_dir": "/path/to/PrismLauncher/instances/1.21.4-Fabric/.minecraft",
  "source_world": "../.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies",
  "launch_command": ["prismlauncher", "--launch", "1.21.4-Fabric"],
  "launch_cwd": "."
}
```

`game_dir` must be the directory this instance actually uses for `saves/`.
With HMCL/PCL version isolation this may be a version directory. Paths are
relative to the config file, support `~` and environment variables, and may
contain spaces. The editor does not rewrite your loader, mods, or settings.

`launch_command` is an argument array executed **without a shell**. Put pipelines
in your own script and use that script as the command. Arguments support literal
`{game_dir}`, `{world_dir}`, `{world_name}` and `{repo}` placeholders. The process
also receives `BBE_GAME_DIR`, `BBE_WORLD_DIR` and `BBE_WORLD_NAME` environment
variables. Your launcher owns authentication. If it supports forwarding
Minecraft's `--quickPlaySingleplayer`, use `{world_name}`; otherwise select the
editor world in Singleplayer. Use `--config /path/to/config.json` **before** a
subcommand for another instance; keep additional personal configs outside Git.

## Extract and open

Close the source world first. The normal workflow is:

```sh
make edit                 # List every arena; choose a name or number
make edit subway_station  # Choose directly
```

The command extracts a missing session or resumes an existing one, then runs your
local launch command. Edit the arena and choose **Save and Quit to Title**.
The terminal detects the world closing, exports the saved changes, displays the
replacement footprint and object-change counts, and asks:

```text
Write this edited arena back to the source world? [Y/n]
```

Press Enter or enter `y` or `yes` to write back **blocks, decorations, spawns and
editor-defined constraints** inside the original extracted footprint. It first
creates and verifies a full backup. Entering `n` or `no`, reaching EOF, or pressing
Ctrl-C leaves the source unchanged and retains the editor save/export. After a
successful write-back the session's baseline is updated, so
`make edit subway_station` resumes it next time.
Both worlds must remain closed during the review/confirmation step.

The game client can remain at its title screen: the command watches the world's
lock, rather than requiring the whole client to exit. For a launcher that exits
before Minecraft opens the save (including Windows HMCL launched from WSL),
the terminal keeps watching automatically. No extra Enter key is needed after
editing; confirmation is requested only when the export is ready to write back.
If you do not open the editor world, use Ctrl-C to cancel the waiting command.
The chosen save is passed to your launch command through `{world_name}`,
`{world_dir}` and the corresponding environment variables. Configure your
launcher's quick-play support to open it automatically; otherwise choose the
named editor save in Singleplayer.

When launching Windows HMCL/PCL from WSL with saves on a Windows drive (such as
`/mnt/d/...`), the editor also uses Windows PowerShell to hold/check the native
Windows file lock. Keep WSL Windows interoperability and `powershell.exe`
available: Linux file locks alone cannot detect a running Windows Minecraft.

For another local config:

```sh
make edit yacht EDIT_CONFIG=/absolute/path/to/another-local-config.json
```

The individual steps remain available for scripting and manual review:

```sh
uv run arena-editor/editor.py list
uv run arena-editor/editor.py prepare subway_station
uv run arena-editor/editor.py launch subway_station
```

Open **Arena Editor — Subway Station** in Singleplayer. The folder is
`<game_dir>/saves/Backstabbed-Editor-subway_station/`. First entry teleports you
to the return point, enables creative, and gives you the editor book. Right-click
the book, or use `/function bbe:menu`. Open chat with **T** to click chat controls.
Reopen the same session with `launch`; `prepare` refuses to overwrite it.

All 19 current voting-table arenas are discovered automatically: `library2`,
`airship`, `vineyard2`, `launchpad`, `cyberpunk`, `riverboat`, `industry`, `train`,
`cabin`, `gumdrop`, `canyon`, `sculk`, `panda_village`, `river_bank`, `yacht`,
`subway_station`, `meridian_base`, `bagger_288`, and `underwater_base`.
Separate/coincident ammo points and Canyon's conditional partition spawns are
preserved.

The footprint comes from recorded scene bounds or the voting forceload table.
To override it:

```sh
uv run arena-editor/editor.py prepare subway_station \
  --bounds 20464 20256 20543 20655
```

These are **inclusive MIN_X MIN_Z MAX_X MAX_Z** block coordinates, rounded
outward to whole chunks, with the full build height and original coordinates.
Block entities, inventories, signs, POI and decorations are preserved. Other
chunks/dimensions generate as void. Gameplay datapacks, saved round data and
runtime spawn entities are omitted. This is a chunk extraction, not a silhouette
crop or version converter. Newer-than-1.21.4 chunks and unsupported compression
are rejected. Preparing, exporting and applying check the world's Java-compatible
POSIX record lock. The filesystem helper currently requires Linux/POSIX `fcntl`;
Windows users can run it in WSL against a **closed** Windows instance.

Permanent display entities are part of the saved map. They are copied with their
positions, block/item data, and transformations, and their edits or deletions
are written back with `--blocks` (or the normal `make edit` confirmation).
Underwater Base's six exit trapdoor displays are saved decorations; activation
and reset do not recreate them. Their origins use exact block corners. When
adding a display with `/summon`, use decimal X/Z coordinates such as `32972.0`
and `32529.0`: integer command coordinates are centered by 0.5 blocks.

## Edit points

Labels show IDs and types. Particles distinguish player (cyan), ammo (orange),
and combined points (green). Labels appear as chunks load. Right-click a point's
invisible hitbox, choose **Select nearest** within eight blocks, or use the
paginated **List IDs**, including for unloaded objects.

| Control | Result |
| --- | --- |
| Add player / Ammo / Both / Spectator | Add at your feet, facing your direction |
| Return | Replace the single return destination with your position |
| Move here / Face my way | Move selected point, or update only its facing |
| Cycle spawn type | Player → ammo → combined → spectator → player |
| X± / Y± / Z± | Nudge by 0.5 blocks |
| Go to selected | Teleport to the point or box center |
| Delete | Remove selected object; the return point is protected |
| Undo / Redo | Restore the last metadata snapshot |
| Overlays on/off | Hide hitboxes/labels for unobstructed building |

Select directly with `/trigger bbe.pick set 12`. For exact coordinates:

```mcfunction
/function bbe:set_point {id:12,x:20500.5,y:-58,z:20470.5,yaw:90,pitch:0}
```

Normal Minecraft saving persists edits. **Save and Quit** before exporting.
Undo/redo holds one metadata snapshot; use your building mod's undo for blocks.
The intended workflow is one local editor: objects, corners, undo and wireframe
are shared; selection and boundary-test mode are per player.

## Edit constraints

Existing `arena.json` unions of location boxes become individually editable
boxes, preserving their limits. Subway Station's enforcement starts **off**, as
recorded in its integration. Original arenas with command-based boundaries have
no editable arena predicate; the tool reports this and retains their original
logic when applying. Add editor boxes for them as needed.

1. Capture **Corner A here** and **Corner B here** at opposite corners. Positions
   are your **feet**, including Y; you can fly to capture them.
2. Click **New box**. A keep-in box is created and its twelve edges appear in
   yellow. Corners normalize automatically.
3. Select any box's ID, capture new corners and choose **Resize selected box**.
   **Select containing box** chooses the first box containing your feet; use
   List IDs to distinguish overlaps. Chat shows its full coordinates/settings.
4. Toggle **Keep in / keep out**, **Box kill / TP**, and **Box enabled**.
5. Set **Boundaries on/off** and **Outside kill / TP**, then enable **Test on/off**
   to try them on yourself. Enforcement is otherwise off during editing.

Enabled **keep-in** boxes form a **union**. Leaving the union invokes the global
outside action. With no enabled keep-in boxes, there is no outside restriction.
Entering a **keep-out** box invokes that box's action, with priority over keep-in
rules. The box action is used for keep-out; use the global outside action for
keep-in. Teleports use the Return point, which should be inside the playable area.
Keep-in checks reject other dimensions.

Tests run every five ticks and only affect editors who enable them. A kill ends
your test automatically; datapack reload also resets tests. Large masks show one
selected wireframe at a time. Nudging/corner normalization uses 0.001-block
scoreboard arithmetic suitable for this project's coordinates; original bounds
retain their precision until resized.

The isolated editor models spatial boxes. It does not simulate fluid checks,
death-plane predicates, dynamic gates, jump pads, redstone or other scripted
mechanics. Applying metadata retains these mechanics. Disabling editor-defined
boundaries does not disable an unrelated original hazard.

## Export and apply

After saving and closing the editor world:

```sh
uv run arena-editor/editor.py export subway_station --output dev/my-station-edit
# Omit --output for a timestamped directory under dev/arena-editor/exports/.
```

Review `arena.json` (metadata/source manifest), `datapack/` (spawn functions,
predicates and game hooks), and `world/` (edited chunks with overlays removed).
Then apply to the original save:

```sh
uv run arena-editor/editor.py apply dev/my-station-edit
# Include your creative block and decoration edits as well:
uv run arena-editor/editor.py apply dev/my-station-edit --blocks
```

Apply rejects changed source region files/datapacks. It creates a **full backup
ZIP**, verifies every file against its SHA-256, stages replacements and restores
affected files if a write fails. Backups normally live under Git-ignored
`dev/arena-editor/backups/`. Metadata-only apply leaves source chunk files intact.
`--blocks` replaces only the extracted footprint, retaining neighboring chunks
even within the same region. Blocks built outside that footprint are excluded.

Integration replaces recognized activation spawn commands while retaining other
activation/reset behavior. Exported constraints affect only the selected map's
queued, living participants in waiting/active game states; spectators/lobby
players are excluded. Game kills use the game's death function; waiting players
return to the arena. Replaced `arena` checks use the new rules; other mechanics
are retained. Applied definitions are stored in the gameplay pack so a new
session reimports your edits.

After a **manual** `apply`, move the old editor save aside or use another
instance/config, then prepare again. The `make edit` workflow updates its own
session automatically after confirmation. Exports retain their original baseline and cannot overwrite a
changed source repeatedly. This editor does not regenerate `docs/arenas/` reports
or geometry-specific reset snapshots. If you change reset-controlled furniture,
doors or containers, update that arena's reset script/snapshot and playtest a full
round. The exported pack contains callable definitions; `apply` wires them into
the game. Do not enable the editor pack itself in the shared gameplay save.

## Validation

```sh
make test-editor
make test
```

The optional [runtime test](tests/runtime.cjs) uses a real 1.21.4 protocol client
and RCON against a **disposable extracted world** on a local vanilla/Fabric
server. It checks books, labels, real right-clicks, point edits, undo/redo,
wireframes, dimensional escapes, teleports and kills; starting metadata is
restored in `finally`.

```sh
npm install --prefix dev/arena-editor/runtime mineflayer@4.39.0 rcon-client@4.2.5
BBE_RUNTIME_TEST=1 \
BBE_NODE_MODULES="$PWD/dev/arena-editor/runtime/node_modules" \
BBE_SERVER_PORT=25691 BBE_RCON_PORT=25692 \
BBE_RCON_PASSWORD='your-local-test-password' \
node arena-editor/tests/runtime.cjs
```

Use the extracted save on the test server, offline auth for the client, and
loopback-only listeners. The report goes to ignored
`dev/arena-editor/runtime-results.json` (`BBE_TEST_REPORT` overrides it).
Normal editor use requires neither a dedicated server nor Node dependencies.
The official release notes document [1.21.4 data pack format
61](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-4) and
[function macros](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-20-2).
