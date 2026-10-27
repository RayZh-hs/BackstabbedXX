#!/usr/bin/env python3
"""Install the six builder-generated exit barriers and update fall behavior.

Default: prepare a read-only installation plan. --install requires a verified
full-save --backup matching the stopped save. Unrelated chunk bytes and ZIP
members are preserved. Requires nbtlib (uv run --with nbtlib==2.0.4).
"""
import argparse
from collections import defaultdict
import copy
import fcntl
from io import BytesIO
import json
from pathlib import Path
import struct
import zipfile
import zlib

import nbtlib as nbt

from arena_containment import configure_containment, EXIT_MANIFEST, ROOT, DESCRIPTIONS
from furnish_subway_station import (WORLD, unpack, repack, state_key, atomic_write, verify_backup)

WORK = ROOT / 'map-previewer/maps/containment-fix'


def prepare(world, patch):
    manifest = json.loads(EXIT_MANIFEST.read_text())
    structure = nbt.load(patch)
    assert int(structure['DataVersion']) == 4189
    assert list(map(int, structure['size'])) == manifest['size']
    entries = {tuple(int(b['pos'][i]) + manifest['origin'][i] for i in range(3)):
               structure['palette'][int(b['state'])] for b in structure['blocks']}
    assert len(structure['blocks']) == len(entries) == len(manifest['changes']) == 6
    assert set(entries) == {tuple(c['position']) for c in manifest['changes']}
    grouped = defaultdict(list)
    for cell in manifest['changes']:
        pos = tuple(cell['position'])
        assert state_key(entries[pos]) == state_key(cell['after'])
        grouped[pos[0]//16, pos[2]//16].append(cell)
    outputs, changed = {}, []
    for (cx, cz), cells in grouped.items():
        previous_changes = len(changed)
        path = world / f'region/r.{cx//32}.{cz//32}.mca'
        raw = outputs.get(path, path.read_bytes())
        slot = (cz % 32)*32 + cx % 32
        loc = int.from_bytes(raw[slot*4:slot*4+4], 'big')
        offset = (loc >> 8)*4096
        assert loc and raw[offset+4] == 2
        length = int.from_bytes(raw[offset:offset+4], 'big')
        chunk = nbt.File.parse(BytesIO(zlib.decompress(raw[offset+5:offset+4+length])))
        sections = {int(s['Y']): s for s in chunk['sections']}
        decoded = {}
        for cell in cells:
            x, y, z = pos = tuple(cell['position'])
            assert not any(tuple(int(t[k]) for k in 'xyz') == pos for t in chunk.get('block_entities', []))
            states = sections[y//16]['block_states']
            if y//16 not in decoded:
                decoded[y//16] = unpack(states)
            values = decoded[y//16]
            index = (y % 16)*256 + (z % 16)*16 + x % 16
            before = states['palette'][int(values[index])]
            if state_key(before) == state_key(cell['after']):
                continue
            if state_key(before) != state_key(cell['before']):
                raise ValueError(f'Unexpected original hatch at {pos}: {before}')
            state = entries[pos]
            target = next((i for i, v in enumerate(states['palette']) if state_key(v) == state_key(state)), None)
            if target is None:
                target = len(states['palette'])
                states['palette'].append(copy.deepcopy(state))
            values[index] = target
            changed.append(cell)
        if len(changed) == previous_changes:
            continue
        for sy, values in decoded.items():
            repack(sections[sy]['block_states'], values)
        sealed = {tuple(c['position']) for c in cells}
        for key in ('block_ticks', 'fluid_ticks'):
            if key in chunk:
                chunk[key] = nbt.List[nbt.Compound]([t for t in chunk[key]
                    if tuple(int(t[k]) for k in 'xyz') not in sealed])
        chunk['isLightOn'] = nbt.Byte(0)
        for section in chunk['sections']:
            section.pop('BlockLight', None)
            section.pop('SkyLight', None)
        stream = BytesIO()
        chunk.write(stream)
        compressed = zlib.compress(stream.getvalue())
        count = (len(compressed)+5+4095)//4096
        assert count <= 255
        result = bytearray(raw)
        result.extend(b'\0'*(-len(result) % 4096))
        struct.pack_into('>I', result, slot*4, (len(result)//4096) << 8 | count)
        result.extend((struct.pack('>I', len(compressed)+1)+b'\x02'+compressed).ljust(count*4096, b'\0'))
        outputs[path] = bytes(result)
    archive = world / 'datapacks/mcm.zip'
    with zipfile.ZipFile(archive) as saved:
        assert len(saved.namelist()) == len(set(saved.namelist()))
        infos = {info.filename: info for info in saved.infolist()}
        files = {name: saved.read(name) for name in saved.namelist()}
    configure_containment(files)
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as saved:
        for name, content in files.items():
            saved.writestr(infos.get(name, name), content)
    outputs[archive] = buffer.getvalue()
    return outputs, {'changed_blocks': len(changed), 'changed_chunks': len(grouped), 'changes': changed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--world', type=Path, default=WORLD)
    parser.add_argument('--patch', type=Path, default=WORK / 'underwater-exit-seals.nbt')
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    if args.install and not args.backup:
        parser.error('--install requires --backup')
    with (args.world / 'session.lock').open('a+b') as lock:
        fcntl.lockf(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        backup_sha = verify_backup(args.world, args.backup, allow_new_session_lock=True) if args.install else None
        outputs, report = prepare(args.world, args.patch)
        report.update(installed=args.install, backup=str(args.backup), backup_sha256=backup_sha,
                      files=[str(p.relative_to(args.world)) for p in outputs])
        if args.install:
            for path, contents in outputs.items():
                atomic_write(path, contents)
    WORK.mkdir(exist_ok=True, parents=True)
    (WORK / 'installation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'changes'}, indent=2))


if __name__ == '__main__':
    main()
