# Minecraft map previewer

A local browser viewer for inspecting Minecraft builds before bringing them
into Backstabbed++. It supports vanilla Java structure NBT, camera flight,
cutaway views, and an editable measurement box. World files are read only.

## Start

Requires Node.js 20.19+ or 22.12+ (as required by Vite).
From the repository root:

```sh
npm --prefix map-previewer ci
npm --prefix map-previewer run preview -- --open
```

After installing dependencies, `make preview` is the root-level shortcut.

The default opens the locally prepared Subway Station preview, if present, at
http://127.0.0.1:5189/. Downloaded map assets are local and are not included in
the repository or game releases. To view a different structure:

```sh
npm --prefix map-previewer run preview -- \
  --nbt "$PWD/map-previewer/maps/example/example.nbt" --open
```

Paths passed to `--nbt` resolve from the caller's working directory. The server
binds to localhost. `--port 5190` starts an additional viewer; Ctrl+C stops it.
Use `?view=inside` on the viewer URL to start at the configured interior camera.
Restart the server after changing metadata or exporting a different crop so
the origin and camera entry match the updated structure.

Dependencies are pinned in `package-lock.json`. The viewer uses
[Lodestone](https://github.com/mattzh72/lodestone) and Three.js. It has its own
dependencies and does not depend on an agent skill's installation directory.

## Measurements and point lists

The initial green box wraps the entire loaded structure. Its edge labels and
sidebar show **X × Y × Z** in metres, with one block equal to one metre. The
sidebar also reports the horizontal footprint, box volume, and the number of
stored blocks inside the box. These are dimensions of the loaded preview:
terrain omitted when exporting a world is outside this measurement.

- **Normal:** click two blocks to choose opposite corners of a new box. The
  first click marks a pending corner; the second replaces the previous point
  list with the two corners. Esc cancels a pending corner.
- **Extend:** every block click appends a point to the list. The box contains
  every remaining point. Points inside the current box are retained even when
  they do not change its size.
- **× beside a point:** removes that point and recomputes the box. Removing a
  point that defines an outer edge shrinks the box. Removing an interior or
  redundant point may leave its size unchanged. A single remaining point is a
  1 × 1 × 1 box; no points falls back to wrapping the full structure.
- **Wrap all:** restores the two corners around the entire loaded structure.
- **Add a point by coordinates:** selects a point in the current mode. This
  also works for empty space and positions outside the loaded build.
- **Hide blocks outside this box:** applies the box as a visual mask. Disable
  it to click extension points outside the masked area. The point list and
  measurement box remain independent of the cutaway ceiling.
- **Copy bounds / Export selection:** copies or downloads JSON containing the
  points, inclusive min/max world block coordinates, dimensions, footprint,
  volume, and box diagonal. No map files are edited.

Dimensions include both corner cells: coordinates 10 through 19 span **10**
blocks, and two clicks on the same block measure **1 × 1 × 1**. Source-world
coordinates are preserved using metadata's `origin` offset.

## Camera and cutaway

Drag to orbit; right-drag or Shift-drag to pan; scroll to zoom. A drag does not
select a measurement point. **Inside** switches to flight: drag to look,
WASD to move, E/Q to rise/descend, Shift to move faster, and scroll to adjust
flight speed. **F** toggles fly/orbit. **Overview** frames the whole structure.

The ceiling slider hides blocks above a source-world Y coordinate. It does not
alter the measurement box. For Subway Station, Y −49 reveals the tracks.

Dynamic point lighting, shadows, and antialiasing are disabled. The canvas uses
reduced resolution, reduced further for software renderers. Flying draws nearby
chunks. Point selection uses voxel traversal instead of intersecting every
rendered triangle; the box itself uses twelve line segments. Geometry rebuilds
are only needed for cutaway or masking changes.

## Prepare a world

Keep the original archive and extracted save under `map-previewer/maps/`.
The included exporter reads the Java 1.18+ Anvil chunk layout and writes a
cropped, finite vanilla structure NBT plus JSON metadata:

```sh
uv run --with nbtlib python map-previewer/export-java-world.py \
  'map-previewer/maps/subway-station/world/Train Station' \
  map-previewer/maps/subway-station/subway-station.nbt \
  --min-y -60 --max-y -1 \
  --name 'Subway Station' --creator KnotXackly \
  --source-url 'https://www.minecraftmaps.com/51929-subway-station-original-build'
```

The exporter omits air, light/barrier/structure-void cells, and blocks outside
the chosen Y interval. It reports entities but does not export them. It
preserves block states and block-entity NBT. The preview does not simulate game
logic; sign text and special block effects may render differently. This is not
a world-version converter or a finished playable arena.

Legacy Java worlds, Bedrock worlds, Sponge `.schem`, MCEdit `.schematic`, and
Litematica `.litematic` files require conversion to vanilla structure NBT with
a tool that supports their actual source format/version. The exporter rejects
unsupported external chunk files and compression rather than interpreting
them as another format.

## Metadata

The viewer reads a JSON file beside the NBT with the same basename, or an
explicit `--metadata FILE`. Without metadata it uses local coordinates and the
NBT filename as the title. Fields used by the viewer:

```json
{
  "name": "Subway Station",
  "creator": "KnotXackly",
  "source_url": "https://www.minecraftmaps.com/51929-subway-station-original-build",
  "level_version": "1.20.4",
  "origin": [-12, -60, -214],
  "entry": [35.5, -56, -73.5]
}
```

`origin` is the source-world coordinate of local block `[0, 0, 0]`. `entry` is
the camera eye position in source-world coordinates. If omitted, **Inside**
starts at the structure centre. The exporter adds provenance, palette counts,
source command blocks, and version information to the same JSON.

## Local Subway Station assets

Creator: **KnotXackly**. Source:
https://www.minecraftmaps.com/51929-subway-station-original-build

The author allows reuse in builds/maps with credit to KnotXackly and a link to
the map post when publishing. Preserve that attribution when porting it.

The downloaded save and all 12,290 chunks report DataVersion 3700 / 1.20.4.
The prepared preview contains 98,245 visible block cells and measures
70 × 34 × 384 blocks, with the flat base and invisible blocks excluded. Source
commands include spawnpoint/worldspawn and teleport behavior; review those
when integrating into the game's datapacks.

## Agent skill and checks

Agent instructions are at
[`.agents/skills/minecraft-map-preview/SKILL.md`](../.agents/skills/minecraft-map-preview/SKILL.md).

```sh
npm --prefix map-previewer test
```

Unit checks cover inclusive dimensions, point-list unions/removal, negative
world offsets, voxel picking, and server arguments. Exercise real browser
clicks, camera drags, clipping, and selection exports when changing the UI.
