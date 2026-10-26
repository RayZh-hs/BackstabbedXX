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
| Subway Station | `/function subway_station:select` |
| Yacht | `/function yacht:select` |
| River Bank | `/function river_bank:select` |
| Panda Village | `/function panda_village:select` |

These commands select and load the arena through the normal game setup. Then
join the lobby queue and start the round normally; the normal start requires
at least four queued players. They do not start a solo round. If commands are
disabled in singleplayer, use **Esc → Open to LAN → Allow Commands: ON → Start
LAN World** for the current session.

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
map 16. Its original architecture is preserved; 24 connected central-platform
spawns, voting artwork and reset behavior are included. Automatic boundary
teleports are disabled. Inside each of the four six-carriage trains,
right-click **Previous carriage / Next carriage** on the end walls to travel
to the adjacent carriage. The labels also support Simplified Chinese.

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
`v1.1.1-alpha` is pushed. Tags with a prerelease suffix are published as GitHub
prereleases. The tagged commit must belong to `main`. The workflow runs `make test` and
`make release VERSION=<tag>`, checks the three ZIPs, generates SHA-256 checksums,
and uploads the modpack, standalone resource pack, separate map, and checksums
to a GitHub release.

Release notes are generated automatically from Git history. Every commit since
the previous version tag gets one concise entry, including changes made without
a pull request. The notes also link to the full comparison and explain which
downloads players and hosts need. To preview the notes for an existing tag:

```sh
python3 scripts/release_notes.py v1.1.1-alpha --repo RayZh-hs/BackstabbedXX
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
