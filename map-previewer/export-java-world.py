#!/usr/bin/env python3
"""Read a Java 1.18+ world into a cropped, block-only preview structure.

Source files are opened read-only. Entities are reported but not exported;
this is a visual inspection tool, not a world/version converter.
Run with: uv run --with nbtlib export-java-world.py WORLD OUTPUT --min-y -60
"""
import argparse
from collections import Counter
from io import BytesIO
from pathlib import Path
import copy
import gzip
import json
import zlib

import nbtlib as nbt
import numpy as np


def chunks(folder):
    for file in sorted(folder.glob('*.mca')):
        data = file.read_bytes()
        for slot in range(1024):
            location = int.from_bytes(data[slot * 4:slot * 4 + 4], 'big')
            if not location:
                continue
            offset = (location >> 8) * 4096
            length = int.from_bytes(data[offset:offset + 4], 'big')
            compression = data[offset + 4]
            if compression & 128:
                raise ValueError('External chunk files are not supported')
            payload = data[offset + 5:offset + 4 + length]
            if compression == 1:
                payload = gzip.decompress(payload)
            elif compression == 2:
                payload = zlib.decompress(payload)
            elif compression != 3:
                raise ValueError(f'Unsupported chunk compression: {compression}')
            yield nbt.File.parse(BytesIO(payload))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('world', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--min-y', type=int, default=-64)
    parser.add_argument('--max-y', type=int, default=319)
    parser.add_argument('--name', help='Preview display name; defaults to the world name')
    parser.add_argument('--source-url', help='Original map post for attribution')
    parser.add_argument('--creator', help='Map author')
    args = parser.parse_args()
    if args.min_y > args.max_y:
        parser.error('--min-y must not exceed --max-y')
    level = nbt.load(args.world / 'level.dat')['Data']
    if int(level['DataVersion']) < 2860:
        parser.error('This preview exporter requires the Java 1.18+ chunk format')
    invisible = {'minecraft:' + b for b in
                 ('air', 'cave_air', 'void_air', 'light', 'barrier', 'structure_void')}
    palette, palette_ids, blocks, tiles = [], {}, [], {}
    versions, counts, ys, commands = Counter(), Counter(), Counter(), []
    for chunk in chunks(args.world / 'region'):
        versions[int(chunk['DataVersion'])] += 1
        for tile in chunk.get('block_entities', []):
            pos = tuple(int(tile[k]) for k in ('x', 'y', 'z'))
            tiles[pos] = tile
            if tile.get('Command'):
                commands.append({'position': pos, 'command': str(tile['Command'])})
        for section in chunk.get('sections', []):
            sy = int(section['Y']) * 16
            if sy > args.max_y or sy + 15 < args.min_y:
                continue
            states = section.get('block_states')
            if not states:
                continue
            local_palette = states['palette']
            if all(str(s['Name']) in invisible for s in local_palette):
                continue
            if len(local_palette) == 1:
                indexes = np.zeros(4096, dtype=np.uint64)
            else:
                bits = max(4, (len(local_palette) - 1).bit_length())
                per_long = 64 // bits
                packed = np.asarray(states['data'], dtype=np.int64).view(np.uint64)
                positions = np.arange(4096, dtype=np.uint64)
                indexes = (packed[(positions // per_long).astype(np.intp)] >>
                           ((positions % per_long) * bits)) & ((1 << bits) - 1)
                if int(indexes.max()) >= len(local_palette):
                    raise ValueError('Invalid block palette index')
            for i, state in enumerate(local_palette):
                name = str(state['Name'])
                if name in invisible:
                    continue
                positions = np.flatnonzero(indexes == i)
                y = (positions >> 8) + sy
                positions = positions[(y >= args.min_y) & (y <= args.max_y)]
                if not len(positions):
                    continue
                key = (name, tuple(sorted((str(k), str(v)) for k, v in
                                         state.get('Properties', {}).items())))
                if key not in palette_ids:
                    palette_ids[key] = len(palette)
                    palette.append(state)
                state_id = palette_ids[key]
                cx, cz = int(chunk['xPos']) * 16, int(chunk['zPos']) * 16
                for p in positions.tolist():
                    pos = (cx + (p & 15), sy + (p >> 8), cz + ((p >> 4) & 15))
                    blocks.append((pos, state_id))
                    ys[pos[1]] += 1
                counts[name] += len(positions)
    if not blocks:
        raise ValueError('No visible blocks in selection')
    origin = [min(p[a] for p, _ in blocks) for a in range(3)]
    upper = [max(p[a] for p, _ in blocks) for a in range(3)]
    size = [upper[a] - origin[a] + 1 for a in range(3)]
    nbt_blocks = []
    for pos, state in blocks:
        item = nbt.Compound({'pos': nbt.List[nbt.Int](
            [pos[a] - origin[a] for a in range(3)]), 'state': nbt.Int(state)})
        if pos in tiles:
            tile = copy.deepcopy(tiles[pos])
            for axis in ('x', 'y', 'z'):
                tile.pop(axis, None)
            item['nbt'] = tile
        nbt_blocks.append(item)
    result = nbt.File({
        'DataVersion': nbt.Int(max(versions)),
        'size': nbt.List[nbt.Int](size),
        'palette': nbt.List[nbt.Compound](palette),
        'blocks': nbt.List[nbt.Compound](nbt_blocks),
        'entities': nbt.List[nbt.Compound]([]),
    }, gzipped=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output)
    entity_types = Counter()
    for chunk in chunks(args.world / 'entities'):
        for entity in chunk.get('Entities', []):
            entity_types[str(entity['id'])] += 1
    report = {
        'name': args.name or str(level.get('LevelName', args.world.name)),
        'source_url': args.source_url,
        'creator': args.creator,
        'source_world': str(args.world),
        'level_version': str(level['Version']['Name']),
        'level_data_version': int(level['DataVersion']),
        'chunk_data_versions': dict(versions),
        'origin': origin, 'upper': upper, 'size': size,
        'visible_blocks': len(blocks), 'palette_states': len(palette),
        'block_types': dict(counts.most_common()),
        'blocks_by_y': dict(sorted(ys.items())),
        'source_entities_not_exported': dict(entity_types),
        'source_commands': commands,
        'omitted': sorted(invisible),
        'note': 'Block-only visual preview; source world is unchanged. Not a version conversion.',
    }
    player_pos = level.get('Player', {}).get('Pos')
    if player_pos is not None and len(player_pos) == 3:
        entry = [float(value) for value in player_pos]
        entry[1] += 1.62
        if all(origin[axis] <= entry[axis] < upper[axis] + 1 for axis in range(3)):
            report['entry'] = entry
    args.output.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in (
        'level_version', 'chunk_data_versions', 'origin', 'upper', 'size',
        'visible_blocks', 'palette_states', 'source_entities_not_exported')}, indent=2))
    print('Blocks by Y:', dict(sorted(ys.items())))
    print('Commands:', json.dumps(commands, indent=2))
    print('Wrote', args.output)


if __name__ == '__main__':
    main()
