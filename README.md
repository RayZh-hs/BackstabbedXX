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
make resourcepack    # Rebuild only the resource pack, including the installed ZIP
make map             # Build only the map, using the latest Git version tag
make release VERSION=1.1.1  # Build all release assets for an explicit version
make test            # Check map metadata, archive separation, posters, and Yacht spawns
make clean           # Remove dist/; keep the installed resource-pack ZIP
```

Outputs:

- `dist/Backstabbed++.zip`: an importable Prism instance.
- `dist/backstabbed-resource.zip`: the standalone resource pack, with `pack.mcmeta`
  and `assets/` at the archive root.
- `dist/Backstabbed++-map-v<VERSION>.zip`: the separate host map, produced by
  `make map` or `make release`.

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
