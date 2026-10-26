#!/usr/bin/env python3
"""Import the preserved Subway Station chunks into an unused arena region.

Run with ``uv run --with nbtlib python scripts/import_subway_station.py``.
Requires a stopped source save and the original download under map-previewer/maps/.
Refuses to replace existing destination regions. No downloaded level/datapack is
installed. Commands in command-block NBT are disabled without replacing blocks.
"""

from collections import Counter, defaultdict
from io import BytesIO
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import zlib

import nbtlib as nbt


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'map-previewer/maps/subway-station/world/Train Station'
WORLD = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
OFFSET = (20480, 0, 20480)
CHUNKS = (-1, 3, -14, 10)


def write_regions(folder, chunks):
    regions = defaultdict(list)
    for cx, cz, chunk in chunks:
        regions[cx // 32, cz // 32].append((cx, cz, chunk))
    outputs = {}
    for (rx, rz), entries in regions.items():
        path = folder / f'r.{rx}.{rz}.mca'
        if path.exists():
            raise ValueError(f'Destination already exists: {path}')
        header, sectors, sector = bytearray(8192), [], 2
        for cx, cz, chunk in sorted(entries):
            stream = BytesIO()
            chunk.write(stream)
            data = zlib.compress(stream.getvalue())
            size = (len(data) + 5 + 4095) // 4096
            if size > 255:
                raise ValueError('External chunks are not supported')
            slot = (cz % 32) * 32 + cx % 32
            struct.pack_into('>I', header, slot * 4, sector << 8 | size)
            sectors.append((struct.pack('>I', len(data) + 1) + b'\x02' + data).ljust(size * 4096, b'\0'))
            sector += size
        outputs[path] = bytes(header) + b''.join(sectors)
    return outputs


def main():
    spec = importlib.util.spec_from_file_location('preview_export', ROOT / 'map-previewer/export-java-world.py')
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    dx, _, dz = OFFSET
    chunks, tiles, disabled = [], Counter(), []
    for original in exporter.chunks(SOURCE / 'region'):
        sx, sz = int(original['xPos']), int(original['zPos'])
        if not (CHUNKS[0] <= sx <= CHUNKS[1] and CHUNKS[2] <= sz <= CHUNKS[3]):
            continue
        chunk = copy.deepcopy(original)
        cx, cz = sx + dx // 16, sz + dz // 16
        chunk['xPos'], chunk['zPos'] = nbt.Int(cx), nbt.Int(cz)
        for tile in chunk.get('block_entities', []):
            tiles[str(tile['id'])] += 1
            if str(tile['id']) == 'minecraft:command_block':
                if tile.get('Command'):
                    disabled.append({'source': [int(tile[k]) for k in ('x', 'y', 'z')], 'command': str(tile['Command'])})
                tile['Command'] = nbt.String('')
                tile['auto'] = nbt.Byte(0)
                tile['powered'] = nbt.Byte(0)
                tile['SuccessCount'] = nbt.Int(0)
                tile.pop('LastOutput', None)
            tile['x'], tile['z'] = nbt.Int(int(tile['x']) + dx), nbt.Int(int(tile['z']) + dz)
        for key in ('block_ticks', 'fluid_ticks'):
            for tick in chunk.get(key, []):
                tick['x'] = nbt.Int(int(tick['x']) + dx)
                tick['z'] = nbt.Int(int(tick['z']) + dz)
        structures = chunk.get('structures', {})
        if any(structures.get(k) for k in ('starts', 'References')):
            raise ValueError('Source has structure references requiring explicit translation')
        chunks.append((cx, cz, chunk))
    if len(chunks) != 125:
        raise ValueError(f'Expected 125 complete source chunks, got {len(chunks)}')
    # The original has no decorative entities; fail rather than silently omit any.
    for entity_chunk in exporter.chunks(SOURCE / 'entities'):
        for entity in entity_chunk.get('Entities', []):
            x, _, z = map(float, entity['Pos'])
            if -16 <= x < 64 and -224 <= z < 176:
                raise ValueError(f'Entity needs translation: {entity}')
    outputs = write_regions(WORLD / 'region', chunks)
    # Check every output before performing the first mutation.
    for path in outputs:
        if path.exists():
            raise ValueError(f'Occupied destination: {path}')
    for path, data in outputs.items():
        path.write_bytes(data)
    report = {
        'source_url': 'https://www.minecraftmaps.com/51929-subway-station-original-build',
        'creator': 'KnotXackly', 'title': 'Subway Station', 'namespace': 'subway_station', 'map_id': 16,
        'reuse_terms': 'Reuse in builds/maps with credit to KnotXackly and a link to the original map post when publishing (recorded during source preview).',
        'source_archive_sha256': hashlib.sha256((ROOT / 'map-previewer/maps/subway-station/source.zip').read_bytes()).hexdigest(),
        'source_data_version': 3700, 'source_version': '1.20.4', 'target_version': '1.21.4',
        'transform': {'translation': list(OFFSET), 'rotation_degrees': 0},
        'source_visible_bounds': {'min': [-12, -60, -214], 'max': [57, -27, 169]},
        'destination_visible_bounds': {'min': [20468, -60, 20266], 'max': [20537, -27, 20649]},
        'imported_chunk_bounds': {'min': [20464, -64, 20256], 'max': [20543, 319, 20655]},
        'imported_chunks': len(chunks), 'block_entities': dict(tiles), 'decorative_entities': 0,
        'disabled_source_commands': disabled,
        'regions': {str(p.relative_to(ROOT)): hashlib.sha256(d).hexdigest() for p, d in outputs.items()},
        'play_area': 'Main station platforms, trains, tracks and vaulted hall. Tunnel extensions and exterior terrain are excluded by a tapered vertical predicate.',
    }
    output = ROOT / 'docs/arenas/subway_station.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
