#!/usr/bin/env python3
"""Import the three preserved KAIZEN87 builds into unused region files.

Run with uv run --with nbtlib python scripts/import_kaizen_bases.py --install.
Original archives/worlds remain read-only. Requires a stopped host save and the
checksum-verified full backup. The default writes an import plan only.
"""
import argparse
from collections import Counter
import copy
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path

import nbtlib as nbt
import numpy as np

from furnish_subway_station import unpack, repack, state_key
from import_subway_station import ROOT, WORLD, write_regions

WORK = ROOT / 'map-previewer/maps/kaizen-bases'
MAPS = (
    dict(namespace='meridian_base', title='Meridian Base', tag='MeridianBase', map_id=17,
         slug='52535-meridian-base', translation=[24576, 0, 24576], chunks=[-7, 7, -6, 7],
         build_min=[-97, -33, -84], build_max=[109, 18, 116]),
    dict(namespace='bagger_288', title='Bagger 288', tag='Bagger288', map_id=18,
         slug='52537-bagger-288-survival-base', translation=[28672, 0, 28672], chunks=[-6, 5, 0, 5],
         build_min=[-87, -51, 16], build_max=[81, 42, 76]),
    dict(namespace='underwater_base', title='Underwater Base', tag='UnderwaterBase', map_id=19,
         slug='52536-underwater-base', translation=[38400, 0, 26624], chunks=[-343, -336, 363, 371],
         build_min=[-5455, 36, 5825], build_max=[-5393, 62, 5920]),
)
BACKUP = ROOT / '.minecraft/backups/map-integration/20261026T165452608726Z-kaizen-bases-before-import-7d3cd058.zip'
BACKUP_SHA256 = '2f87de1dd768d4277bb17d5642ac9f164f757bdcbec657be7e0bbcac75c96dbd'


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [plain(v) for v in value]
    if isinstance(value, (nbt.String, str)):
        return str(value)
    if isinstance(value, (float, np.floating)):
        return float(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    return value


def downgrade_text(data):
    """1.21.5+ stores text as NBT components; 1.21.4 expects JSON strings."""
    if not isinstance(data, nbt.Compound):
        return
    for key in list(data):
        value = data[key]
        if key in ('CustomName', 'minecraft:custom_name', 'minecraft:item_name'):
            data[key] = nbt.String(json.dumps(plain(value), ensure_ascii=False))
        elif key in ('messages', 'filtered_messages', 'minecraft:lore'):
            data[key] = nbt.List[nbt.String]([json.dumps(plain(v), ensure_ascii=False) for v in value])
        elif isinstance(value, nbt.Compound):
            downgrade_text(value)
        elif isinstance(value, nbt.List):
            for item in value:
                downgrade_text(item)


def compatibility(spec):
    path = ROOT / f"docs/arenas/{spec['namespace']}_compatibility.json"
    if not path.exists():
        return {}
    manifest = json.loads(path.read_text())
    patch = nbt.load(WORK / 'repairs' / (spec['namespace'].replace('_', '-') + '-compatibility.nbt'))
    origin = manifest['origin']
    entries = {tuple(int(b['pos'][a]) + origin[a] for a in range(3)): patch['palette'][int(b['state'])] for b in patch['blocks']}
    assert set(entries) == {tuple(b['position']) for b in manifest['changes']}
    for b in manifest['changes']:
        assert state_key(entries[tuple(b['position'])]) == state_key(b['after'])
    return {tuple(b['position']): (b['before'], entries[tuple(b['position'])]) for b in manifest['changes']}


def prepare(spec):
    source = ROOT / 'map-previewer/maps' / spec['slug']
    world = next((source / 'world').iterdir())
    selection = source / 'selected-world'
    exporter_spec = importlib.util.spec_from_file_location('world_export', ROOT / 'map-previewer/export-java-world.py')
    exporter = importlib.util.module_from_spec(exporter_spec)
    exporter_spec.loader.exec_module(exporter)
    repair = compatibility(spec)
    dx, _, dz = spec['translation']
    blocks, tiles, disabled, repaired = [], Counter(), [], []
    for original in exporter.chunks(selection / 'region'):
        c = copy.deepcopy(original)
        sx, sz = int(c['xPos']), int(c['zPos'])
        for section in c.get('sections', []):
            sy = int(section['Y']) * 16
            entries = [(pos, before, after) for pos, (before, after) in repair.items()
                       if pos[0] // 16 == sx and pos[2] // 16 == sz and pos[1] // 16 == sy // 16]
            if not entries:
                continue
            states = section['block_states']
            values = unpack(states)
            for (x, y, z), before, after in entries:
                index = (y % 16) * 256 + (z % 16) * 16 + x % 16
                assert state_key(states['palette'][int(values[index])]) == state_key(before)
                # Replacing a palette entry also removes unsupported unused states.
                old_index = int(values[index])
                if np.count_nonzero(values == old_index) == 1:
                    states['palette'][old_index] = copy.deepcopy(after)
                else:
                    states['palette'].append(copy.deepcopy(after))
                    values[index] = len(states['palette']) - 1
                repaired.append([x, y, z])
            # Eliminate unused palette entries; target-version validation covers all.
            used = sorted(set(map(int, values)))
            remap = {v: i for i, v in enumerate(used)}
            states['palette'] = nbt.List[nbt.Compound]([states['palette'][i] for i in used])
            values = np.array([remap[int(v)] for v in values], dtype=np.uint64)
            repack(states, values)
        c['xPos'], c['zPos'], c['DataVersion'] = nbt.Int(sx + dx // 16), nbt.Int(sz + dz // 16), nbt.Int(4189)
        # Natural structure metadata refers to the source world, not the build.
        c['structures'] = nbt.Compound({'starts': nbt.Compound(), 'References': nbt.Compound()})
        for tile in c.get('block_entities', []):
            tiles[str(tile['id'])] += 1
            if str(tile['id']) == 'minecraft:command_block':
                if tile.get('Command'):
                    disabled.append({'source': [int(tile[k]) for k in 'xyz'], 'command': str(tile['Command'])})
                tile['Command'], tile['auto'], tile['powered'] = nbt.String(''), nbt.Byte(0), nbt.Byte(0)
                tile['SuccessCount'] = nbt.Int(0)
                tile.pop('LastOutput', None)
            downgrade_text(tile)
            tile['x'], tile['z'] = nbt.Int(int(tile['x']) + dx), nbt.Int(int(tile['z']) + dz)
        for key in ('block_ticks', 'fluid_ticks'):
            for tick in c.get(key, []):
                tick['x'], tick['z'] = nbt.Int(int(tick['x']) + dx), nbt.Int(int(tick['z']) + dz)
        blocks.append((int(c['xPos']), int(c['zPos']), c))
    assert len(repaired) == len(repair)
    known_states = json.loads((WORK / 'collision-audit.json').read_text())['states']
    for _, _, c in blocks:
        for section in c.get('sections', []):
            for state in section.get('block_states', {}).get('palette', []):
                name, properties = state_key(state)
                key = name + '[' + ','.join(f'{k}={v}' for k, v in properties) + ']'
                if key not in known_states:
                    raise ValueError('State unsupported by Java 1.21.4: ' + key)
    # The skeleton-skull replacement adds its vanilla block entity.
    for pos, (_, after) in repair.items():
        if str(after['Name']) != 'minecraft:skeleton_skull':
            continue
        x, y, z = pos
        c = next(c for cx, cz, c in blocks if cx == (x + dx) // 16 and cz == (z + dz) // 16)
        c['block_entities'].append(nbt.Compound({'id': nbt.String('minecraft:skull'),
            'x': nbt.Int(x + dx), 'y': nbt.Int(y), 'z': nbt.Int(z + dz)}))
        tiles['minecraft:skull'] += 1
    output = write_regions(WORLD / 'region', blocks)
    # No decorative entity is silently dropped. Natural mobs/minecarts in terrain
    # do not belong to these builds; preserve all actual decorative entities.
    decorations = Counter()
    envelope = spec['chunks']
    for original in exporter.chunks(world / 'entities'):
        entities = []
        for entity in original.get('Entities', []):
            x, _, z = map(float, entity['Pos'])
            if not (envelope[0] <= x // 16 <= envelope[1] and envelope[2] <= z // 16 <= envelope[3]):
                continue
            if str(entity['id']) not in ('minecraft:painting', 'minecraft:item_frame', 'minecraft:glow_item_frame',
                                         'minecraft:armor_stand', 'minecraft:text_display', 'minecraft:item_display', 'minecraft:block_display'):
                continue
            raise ValueError('Decorative entity requires an explicit translation: ' + entity.snbt())
    hashes = {str(p.relative_to(WORLD)): hashlib.sha256(b).hexdigest() for p, b in output.items()}
    report = {**spec, 'source_url': 'https://www.minecraftmaps.com/' + spec['slug'], 'creator': 'KAIZEN87',
              'source_world': str(world.relative_to(ROOT)), 'source_archive_sha256': hashlib.sha256((source / 'source.zip').read_bytes()).hexdigest(),
              'source_version': '1.21.8', 'source_data_version': 4440, 'target_version': '1.21.4', 'target_data_version': 4189,
              'imported_chunks': len(blocks), 'regions': hashes, 'block_entities': dict(tiles),
              'decorative_entities': dict(decorations), 'disabled_source_commands': disabled, 'compatibility_changes': len(repaired),
              'backup': str(BACKUP.relative_to(ROOT)), 'backup_sha256': BACKUP_SHA256,
              'reuse_terms': 'All rights reserved. Personal use only; see source License & Usage Terms.txt and https://www.patreon.com/posts/license-usage-70505678 . Original notices preserved.',
              'version_conversion': 'All saved palette states validated against Java 1.21.4. Text components converted from 1.21.8 NBT to JSON strings. Unrelated source level metadata, datapacks, POIs and natural structure references not installed.'}
    return output, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    outputs, reports = {}, []
    for spec in MAPS:
        out, report = prepare(spec)
        assert not (set(outputs) & set(out))
        outputs.update(out)
        reports.append(report)
    WORK.mkdir(exist_ok=True, parents=True)
    (WORK / 'import-plan.json').write_text(json.dumps(reports, indent=2) + '\n')
    if args.install:
        if hashlib.sha256(BACKUP.read_bytes()).hexdigest() != BACKUP_SHA256:
            raise ValueError('Missing or invalid full-save backup')
        with (WORLD / 'session.lock').open('a+b') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            for path in outputs:
                if path.exists():
                    raise ValueError('Occupied destination: ' + str(path))
            for path, content in outputs.items():
                path.write_bytes(content)
            for report in reports:
                (ROOT / f"docs/arenas/{report['namespace']}.json").write_text(json.dumps(report, indent=2) + '\n')
    print(f"{'Installed' if args.install else 'Planned'} {len(reports)} arenas, {sum(r['imported_chunks'] for r in reports)} chunks, {len(outputs)} unused regions")


if __name__ == '__main__':
    main()
