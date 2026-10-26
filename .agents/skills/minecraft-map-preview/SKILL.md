---
name: minecraft-map-preview
description: Preview downloaded Minecraft maps and structure NBT files with the repository's local 3D viewer, select arena bounds, and export scale measurements. Use for visual map selection and porting assessment in Backstabbed++; not for generating new builds or testing game logic.
---

# Minecraft Map Preview

Use the root-level `map-previewer/` tool. Resolve this skill's real directory
(following any installation symlink), then walk `../../..` to the repository
root, or use the working checkout; commands below run from that root.
See [the tool README](../../../map-previewer/README.md) for metadata fields,
controls, and limitations.

## Prepare and open a map

- Inspect the archive before extracting. A Java world has `level.dat` and
  `region/*.mca`; a vanilla structure has `size`, `palette`, and `blocks` NBT
  tags. Do not treat `.schem`, legacy `.schematic`, `.litematic`, or Bedrock
  `.mcworld` as vanilla structure NBT. Convert those with a tool that supports
  the actual source format/version first.
- Store downloads, extracted worlds, and generated previews in
  `map-previewer/maps/<map-name>/` (Git ignored). Preserve the source archive
  and source save. Check actual save/chunk metadata before inferring version
  compatibility from a download page.
- For an Anvil world using the Java 1.18+ chunk layout, export a finite preview:

  ```sh
  uv run --with nbtlib python map-previewer/export-java-world.py \
    'map-previewer/maps/example/world' \
    map-previewer/maps/example/example.nbt \
    --name 'Example' --creator 'Author' --source-url 'https://example.com/map'
  ```

  Choose `--min-y` / `--max-y` when the source includes large flat terrain or
  unrelated vertical space. Those limits change what the preview measures;
  report them. Unsupported chunk compression/layouts require another converter.
  This exporter makes a visual block structure, not a playable port.
- Run `npm --prefix map-previewer ci` if its local dependencies are missing.
  Then start the viewer, using the adjacent JSON metadata generated above:

  ```sh
  npm --prefix map-previewer run preview -- \
    --nbt "$PWD/map-previewer/maps/example/example.nbt" --open
  ```

  `--nbt` paths resolve from the caller's working directory. `--metadata FILE`
  overrides the adjacent JSON. The default port is 5189, localhost only; use
  `--port` for an additional viewer. Check an existing server before starting
  a duplicate, and only stop a process you started for this task.

## Measure a candidate arena

The initial box wraps the loaded structure. **Normal** mode takes two block
clicks as opposite corners of a new box. Dragging moves the camera and does not
select a point. **Extend** mode appends each clicked point to the displayed
list. The box is the union of all remaining points: clicking **×** beside a
point removes that point and recomputes the box. Removing a non-extreme point
may leave the dimensions unchanged. No points means the full structure bounds.
**Wrap all** restores the two original bounding corners.

Use the coordinate form for exact points, including points in empty space.
Coordinates shown in the list, copied bounds, and exported JSON are source-world
block coordinates. Dimensions include both endpoint cells (`max - min + 1`);
one block measures one metre. Report X × Y × Z, footprint, and the selected
min/max corners together so the proposed arena can be reproduced.

The green box and axis labels update without rebuilding the block mesh.
**Hide blocks outside this box** optionally applies the selection as a visual
mask. Turn it off to click additional points outside a cropped view. The
cutaway ceiling is a separate viewing aid and does not change the measurement
box. Use **Export selection** to hand the chosen points and bounds to a later
agent or to save them for porting work.

## Verify and report

Open the returned URL and check that the structure renders. When changing the
tool, run `npm --prefix map-previewer test`; exercise real clicks for two
corners, adding/removing extension points, dragging, and optional masking.
Keep simplified lighting and reduced resolution: dynamic point lights made
the station preview unusably slow. Lodestone is pinned because the adapter
uses its renderer internals for picking, overlays, and lighting control.

Preserve creator attribution and reuse terms alongside map provenance. Explain
that a preview does not validate collisions, commands, redstone, entities, or
target-version behavior. Importing into the game and adding arena gameplay are
separate tasks requiring their own implementation and in-game checks.
