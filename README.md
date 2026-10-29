# Backstabbed++

A fun Minecraft minigame with fast pace and killer combat.

## Getting Started

You can download a ready-to-use release or clone the repository and build it
locally.

### Download a release

1. Open the [latest release](https://github.com/RayZh-hs/BackstabbedXX/releases/latest).
2. Download `Backstabbed++.zip` from the release's **Assets** section.
3. In Prism Launcher, choose **Add Instance → Import**, then select the downloaded
   ZIP.

Clients need only `Backstabbed++.zip`, which includes the built resource pack
and contains no worlds. Each release also provides `backstabbed-resource.zip`
separately and a `SHA256SUMS` file for checking the downloads.

The map is a separate asset, `Backstabbed++-map-v<VERSION>.zip`, for the host.
Extract its world folder into the host's `.minecraft/saves/` directory, or use it
as the world for a dedicated server. Clients joining that host do not need to
download the map.

### Clone and build locally

Install Git, Make, and Python 3.8 or newer, then run:

```sh
git clone https://github.com/RayZh-hs/BackstabbedXX.git Backstabbed++
cd Backstabbed++
make
```

Import `dist/Backstabbed++.zip` into Prism Launcher using **Add Instance → Import**.
Other build commands:

```sh
make                 # Build the resource pack and the Prism instance ZIP
make launch          # Build, then launch the working copy (requires uv)
make launch -- --local  # Launch a fresh playtest world with idle players
make edit            # Choose an arena and open its persistent editor session
make edit yacht      # Edit an arena directly; confirm write-back after closing
make resourcepack    # Rebuild only the resource pack, including the installed ZIP
make map             # Build only the map, using the latest Git version tag
make release VERSION=1.1.1  # Build all release assets for an explicit version
make test            # Check map metadata, archives, posters, and arena spawns/boundaries
make clean           # Remove dist/; keep the installed resource-pack ZIP
```

Outputs:

- `dist/Backstabbed++.zip`: an importable Prism instance.
- `dist/backstabbed-resource.zip`: the standalone resource pack, with `pack.mcmeta`
  and `assets/` at the archive root.
- `dist/Backstabbed++-map-v<VERSION>.zip`: the separate host map, produced by
  `make map` or `make release`.

### Update an existing HMCL instance

Close Minecraft, update this checkout to the revision you want, then run:

```sh
python3 scripts/update_hmcl.py --dry-run  # Show the destination and planned changes
python3 scripts/update_hmcl.py            # Apply the update
```

The script requires only Python 3.8 or newer. In this directory layout it defaults
to `../../.minecraft/versions/1.21.4-BACKSTABBED`. For another HMCL installation,
pass its actual game directory, the folder containing `mods/`, `saves/` and
`hmclversion.cfg`:

```sh
python3 scripts/update_hmcl.py --instance "/path/to/.minecraft/versions/Backstabbed" --dry-run
python3 scripts/update_hmcl.py --instance "/path/to/.minecraft/versions/Backstabbed"
```

It replaces `mods/` with the checkout's complete mod set, replaces the existing
Backstabbed++ world including its datapacks, and rebuilds the resource pack from
source. Existing English/Chinese ZIP filenames and unpacked Backstabbed resource
packs are refreshed too. No build step or release download is needed; the current
checkout supplies all content. Extra or obsolete installed mods are moved into
the backup along with the previous mod set.

Your `config/`, `defaultconfigs/`, `options.txt` (including keybinds and pack
selection), HMCL settings, installed Minecraft/NeoForge, server lists and skins
are kept. The updated world's `serverconfig/` and `mcwifipnp.json` LAN settings
are also kept. Other worlds and resource packs are untouched. If the Backstabbed
resource pack was not enabled already, enable `backstabbed-resource.zip` in
Minecraft's Resource Packs menu.

**The world update replaces gameplay state, player data and local map edits
with the checkout's world.** It automatically selects the only save whose folder
starts with `Backstabbed ++`; if there are several, specify the exact folder with
`--world "Backstabbed ++! v1.0.0 by NorbMinecraft and Bagel Buddies"`. Its existing
folder name is reused. If no such save exists, a new unversioned world is installed.

Before replacement, the script stages all new content. It moves the original
components into `.minecraft/backups/instance-updates/<instance>/<UTC timestamp>/originals/`,
verifies installed SHA-256 hashes, and records them in `update-report.json` next
to `originals/`. Installation errors trigger an automatic rollback. For an
instance outside a `versions/` directory, backups go into the adjacent
`backstabbed-updates/<instance>/` directory. Keep Minecraft closed throughout.
To restore a successful update manually, move the replaced components listed in
the report out of the instance, then move the corresponding components from
`originals/` back to their original relative paths. Remove any paths listed under
`created` in the report, since those had no previous version.

### Launch the working copy

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
make launch
```

This rebuilds the resource pack and client ZIP, then uses
[PortableMC](https://pypi.org/project/portablemc/4.4.1/) to start the Minecraft and
NeoForge versions specified in `mmc-pack.json`. It uses this checkout's
`.minecraft/` folder, including its mods, resource packs and source save. The
newly built resource pack is enabled automatically, preserving other options.
The first launch downloads the launcher dependency, game, assets and Java runtime;
game downloads are cached in the ignored `dev/launcher/` directory. Set
`MINECRAFT_RUNTIME_DIR` to use another runtime cache. An installed Prism or HMCL
instance is not required.

By default, this starts a local development session named `BackstabbedDev` with
4 GiB of heap. Pass PortableMC start options with `LAUNCH_ARGS`, for example:

```sh
make launch LAUNCH_ARGS='--username Ray --resolution 1600x900'
make launch LAUNCH_ARGS='--login you@example.com'  # Microsoft account for online play
make launch LAUNCH_ARGS='--jvm-args=-Xmx8G'
```

The sign-in flow and session cache belong to PortableMC; it does not reuse your
Prism or HMCL login. Local launch files and authentication are ignored by Git
and excluded from client builds.

For solo level playtesting, run:

```sh
make launch -- --local
# Equivalent forms:
make launch LOCAL=1
make launch LAUNCH_ARGS='--local --resolution 1600x900'
```

GNU Make needs the extra `--` separator before custom flags; `make launch
--local` alone is rejected by Make before it reads the project. The launcher
itself accepts `--local`.

Local mode opens a fresh copy of the source world automatically and adds three
idle players named `PlaytestDummy1`–`PlaytestDummy3`. They count as real server
players, automatically queue each round, receive roles and spawn in the arena,
so you can meet the normal four-player minimum by joining the queue yourself.
Commands are enabled: select an arena with the commands below, then queue and
play normally. The dummies stand still; they do not fight or vote. Their packet
listeners discard outgoing packets before NeoForge's channel checks, so mods such
as MCM Highlight can send updates without requiring a dummy client handshake.

The world, settings and helper mod live in a temporary directory under `dev/`
and are removed when the game exits. Each local launch starts from the current
source world, so playtest changes are discarded. The helper is compiled using
PortableMC's Java 21 JDK and cached in `dev/local-playtest-helper/`. Normal
launches and release builds use the usual mods and world.

### Pick an arena

Open **Singleplayer** and load **Backstabbed ++! by NorbMinecraft and Bagel
Buddies**. All arenas live in this one world. In the lobby, vote at the map
posters; the options board's map toggles control which arenas appear. To make
one arena the only voting choice, disable the other maps on that board and
use **Shuffle** before anyone votes. The shuffle command is
`/function mcm:dev/shuffle_maps`; it only works during map voting while the
countdown is still at 20 seconds.

For a direct selection, enable commands (or use an operator account on a server)
and run one of these in chat while no round is active:

| Arena | Command |
| --- | --- |
| Sworld Island | `/function sworld_island:select` |
| Middle Ages Small Lobby | `/function middle_ages:select` |
| Cube Block | `/function cube_block:select` |
| Subway Station | `/function subway_station:select` |
| Meridian Base | `/function meridian_base:select` |
| Bagger 288 | `/function bagger_288:select` |
| Underwater Base | `/function underwater_base:select` |
| Yacht | `/function yacht:select` |
| River Bank | `/function river_bank:select` |
| Panda Village | `/function panda_village:select` |

These commands select and load the arena through the normal game setup. Then
join the lobby queue and start the round normally; the normal start requires
at least four queued players. They do not start a solo round. If commands are
disabled in singleplayer, use **Esc → Open to LAN → Allow Commands: ON → Start
LAN World** for the current session.

## Edit an arena in Minecraft

The [arena editor](arena-editor/README.md) extracts one arena into a persistent
creative void world in your chosen instance, including **1.21.4-Fabric**.
A generated datapack provides a clickable editor book and chat controls,
right-clickable player/ammo spawn labels, and editable keep-in/keep-out boxes
with teleport or kill responses. Your usual creative building tools can edit
the blocks too.

```sh
uv run arena-editor/editor.py init-config
# Edit arena-editor/config.local.json: instance game directory and launch command.
make edit                 # List arena names and choose one
make edit subway_station  # Open a specific arena directly
```

The local config is Git ignored. Sessions persist in the chosen instance.
After **Save and Quit**, the terminal presents an export and asks before writing
the edited blocks, decorations, spawns and constraints back into that arena's
source footprint. Press Enter to accept the default Yes. Confirmation creates a
verified full backup; declining keeps the source unchanged. Source conflicts are
refused, and successful write-back updates the session for the next `make edit`.
See the guide for boundary semantics, exact functions, launcher settings and
reset-script limitations.

## Map Source

For evaluating new maps, use the root-level [map previewer](map-previewer/README.md).
It provides a local 3D view, flight and cutaway controls, and a measured box
defined by an editable point list. Agent usage is documented in the
[map-preview skill](.agents/skills/minecraft-map-preview/SKILL.md).
For incorporating a chosen arena into the game, the
[map-creator skill](.agents/skills/backstabbed-map-creator/SKILL.md)
covers importing the build, generating its voting poster, validating spawns,
and containing players. It requires a user decision for map-design repairs,
followed by a verified backup and the Minecraft Builder workflow.
Both skills are vendored under `.agents/skills/`; their project instructions
and the previewer are included in a fresh checkout.

[Subway Station](docs/arenas/subway_station.md), by KnotXackly, is integrated as
map 16. Its original architecture is preserved; its 24 player/scrap spawns are
distributed evenly across the lower platform, upper concourse and train interiors.
Voting artwork and reset behavior are included. Automatic boundary
teleports are disabled. Inside each of the four six-carriage trains,
right-click **Previous carriage / Next carriage** on the end walls to travel
to the adjacent carriage. The labels also support Simplified Chinese.

KAIZEN87's [Meridian Base](docs/arenas/meridian_base.md),
[Bagger 288](docs/arenas/bagger_288.md), and
[Underwater Base](docs/arenas/underwater_base.md) are maps 17–19. Each includes
24 validated spawns, voting artwork adapted from its webpage imagery, reset
behavior and containment that follows the connected build. The original 1.21.8
builds are adapted to 1.21.4 with 112 user-approved decorative substitutions in
Meridian and Underwater Base. Their original archives, credits and license notices
are preserved; see the arena records for source links, terms and placement.

Meridian Base's exterior ocean is lethal during a round; indoor water and bubble
columns remain safe. Press the central shaft's lower buttons to reach the indoor
second-floor landing, and use its upper buttons to return. The plantation
occasionally drops **Delicious Food**, an edible potato granting Speed I and Jump
Boost I for 10 seconds. Stepping onto one of the seven locked outer-ring
dispensers randomly produces a swiftness potion or an airborne firework. Leave and
step on it again for a fresh roll. See the
[repair record](docs/arenas/meridian_base-repair.json) for controls and backup.

[Sworld Island](docs/arenas/sworld_island.json), by CloseeDBr, is map 21. Its
vine-covered giant sword and island ground have 32 validated player/scrap spawns;
touching the surrounding ocean eliminates active players. The original elevated
stream remains safe. [Middle Ages Small Lobby](docs/arenas/middle_ages.json), by
ElectronJoon and collaborators, is map 22: its original castle courtyard floats
in the void, with 32 validated spawns and fall elimination.
[Cube Block](docs/arenas/cube_block.md), by XxRexRaptorxX, is map 23. Its main cube
has 32 validated spawns, and live players receive the gravity grappler. The three
maps include new generated posters with varied layouts and restrained colors.
Their source downloads, credits and reuse notices are preserved in the arena
records; these local ports do not establish permission for public redistribution.

Underwater Base has a copper diving-suit zombie trader beside the hydroponics
counter: 4 scraps buy a drinkable 20-second invisibility potion. Panda Village's
toy merchant sells its existing non-firing toy gun for 4 scraps. Right-click
either NPC to use the normal trading screen during a round. The included
server-side NeoForge bridge and maintenance instructions are documented in
[Arena merchants](merchant-bridge/README.md).

The source save is
`.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/`.
Keep its folder name and Minecraft display name free of release versions.
The map build adds `v<VERSION>` to the archive's world folder and the display
names in `level.dat` and `level.dat_old`, preserving the source files.

Set `VERSION` explicitly, with or without the leading `v`, or let a local map
build use the latest reachable Git version tag. GitHub Actions always supplies
the tag being released. The client modpack build does not require the map source
and excludes all saves, independently of `.packignore`.

## Resource Pack

Edit the resource pack in `.minecraft/resourcepacks/backstabbed-resource/`.
The adjacent `backstabbed-resource.zip` is generated and ignored by Git. Running
`make` or `make resourcepack` rebuilds that ZIP and copies it into `dist/`.
The source directory is excluded from Prism exports by `.packignore`.

## Publishing a Release

[GitHub Actions](https://github.com/RayZh-hs/BackstabbedXX/actions/workflows/release.yml)
builds and publishes releases when a version tag such as `v1.1.0` or
`v1.1.1` is pushed. Tags with a prerelease suffix are published as GitHub
prereleases. The tagged commit must belong to `main`. The workflow runs `make test` and
`make release VERSION=<tag>`, checks the three ZIPs, generates SHA-256 checksums,
and uploads the modpack, standalone resource pack, separate map, and checksums
to a GitHub release.

Release notes are generated automatically from Git history. Every commit since
the previous version tag gets one concise entry, including changes made without
a pull request. The notes also link to the full comparison and explain which
downloads players and hosts need. To preview the notes for an existing tag:

```sh
python3 scripts/release_notes.py v1.1.1 --repo RayZh-hs/BackstabbedXX
```

After committing the next release's changes on `main`, tag that commit and push
the branch and tag together. For example, for the release after `1.1.0`:

```sh
git switch main
git tag -a v1.1.1 -m "Backstabbed++ 1.1.1"
git push --atomic origin main v1.1.1
```

An ordinary push to `main` without a new version tag does not publish a release.
If a tag push does not start a build, open the **Release** workflow in Actions,
choose **Run workflow**, and enter the existing version tag to publish it.
