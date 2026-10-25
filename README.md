# Backstabbed++

A fun Minecraft minigame with fast pace and killer combat.

## Getting Started

Build from a Git checkout with Make, Python 3.8 or newer, and Git installed:

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

The resource pack source is in in `.minecraft/resourcepacks/backstabbed-resource/`. The adjacent `backstabbed-resource.zip` is generated and ignored by Git. The source directory is excluded from Prism exports by `.packignore`.

