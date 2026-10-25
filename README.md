# Backstabbed++

A fun Minecraft minigame with fast pace and killer combat.

## Getting Started

You can download a ready-to-use release or clone the repository and build it
locally.

### Download a release

1. Open the [latest release](https://github.com/RayZh-hs/Backstabbed-/releases/latest).
2. Download `Backstabbed++.zip` from the release's **Assets** section.
3. In Prism Launcher, choose **Add Instance → Import**, then select the downloaded
   ZIP.

The modpack includes the built resource pack. Each release also provides
`backstabbed-resource.zip` separately and a `SHA256SUMS` file for checking the
downloads.

### Clone and build locally

Install Git, Make, and Python 3.8 or newer, then run:

```sh
git clone https://github.com/RayZh-hs/Backstabbed-.git Backstabbed++
cd Backstabbed++
make
```

Import `dist/Backstabbed++.zip` into Prism Launcher using **Add Instance → Import**.
Other build commands:

```sh
make                 # Build the resource pack and the Prism instance ZIP
make resourcepack    # Rebuild only the resource pack, including the installed ZIP
make clean           # Remove dist/; keep the installed resource-pack ZIP
```

Outputs:

- `dist/Backstabbed++.zip`: an importable Prism instance.
- `dist/backstabbed-resource.zip`: the standalone resource pack, with `pack.mcmeta`
  and `assets/` at the archive root.

## Resource Pack

Edit the resource pack in `.minecraft/resourcepacks/backstabbed-resource/`.
The adjacent `backstabbed-resource.zip` is generated and ignored by Git. Running
`make` or `make resourcepack` rebuilds that ZIP and copies it into `dist/`.
The source directory is excluded from Prism exports by `.packignore`.

## Publishing a Release

[GitHub Actions](https://github.com/RayZh-hs/Backstabbed-/actions/workflows/release.yml)
builds and publishes releases when a version tag such as `v1.1.0` is pushed. The
tagged commit must belong to `main`. The workflow builds both ZIPs with `make`,
checks their integrity, generates SHA-256 checksums, and uploads all three files
to a GitHub release.

After committing the next release's changes on `main`, tag that commit and push
the branch and tag together. For example, for the release after `1.1.0`:

```sh
git switch main
git tag -a v1.1.1 -m "Backstabbed++ 1.1.1"
git push --atomic origin main v1.1.1
```

An ordinary push to `main` without a new version tag does not publish a release.
