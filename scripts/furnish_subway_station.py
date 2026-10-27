#!/usr/bin/env python3
"""Apply the sparse minecraft-builder-skill furniture structure to a stopped save.

Requires nbtlib: uv run --with nbtlib python scripts/furnish_subway_station.py
The default only prepares a plan; --install requires a verified full-save backup.
Unchanged chunks retain their exact stored bytes. Existing architecture and block
entities cannot be replaced. Furniture interaction states join the round reset.
"""
import argparse
from collections import defaultdict
import copy
import fcntl
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import struct
import tempfile
import zipfile
import zlib

import nbtlib as nbt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
WORLD = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
WORK = ROOT / 'map-previewer/maps/subway-station/furnishings'
ORIGIN = (20474, -48, 20362)
FUNCTION = 'data/subway_station/function/furnishings/restore.mcfunction'
HOOK = 'function subway_station:furnishings/restore'


def state_key(state):
    return (str(state['Name']), tuple(sorted((str(k), str(v)) for k, v in state.get('Properties', {}).items())))


def unpack(states):
    palette = states['palette']
    if len(palette) == 1:
        return np.zeros(4096, dtype=np.uint64)
    bits = max(4, (len(palette) - 1).bit_length())
    per = 64 // bits
    data = np.asarray(states['data'], dtype=np.int64).view(np.uint64)
    positions = np.arange(4096, dtype=np.uint64)
    return (data[(positions // per).astype(np.intp)] >> ((positions % per) * bits)) & ((1 << bits) - 1)


def repack(states, values):
    bits = max(4, (len(states['palette']) - 1).bit_length())
    per = 64 // bits
    data = np.zeros((4096 + per - 1) // per, dtype=np.uint64)
    for i, value in enumerate(values):
        data[i // per] |= np.uint64(value) << np.uint64((i % per) * bits)
    states['data'] = nbt.LongArray(data.view(np.int64))


def block_command(pos, state):
    name, props = state_key(state)
    suffix = '[' + ','.join(f'{k}={v}' for k, v in props) + ']' if props else ''
    return f'setblock {pos[0]} {pos[1]} {pos[2]} {name}{suffix}'


def patch_datapack(raw, entries):
    restore = ['# Second-floor furniture: reset all buttons and decorative trapdoors.']
    for pos, state, _ in entries:
        name = str(state['Name'])
        if name.endswith(('_button', '_trapdoor', '_pressure_plate')):
            restore.append(block_command(pos, state))
        elif name == 'minecraft:barrel':
            restore.append(block_command(pos, state))
            restore.append(f'data modify block {pos[0]} {pos[1]} {pos[2]} Items set value []')
    buffer = BytesIO()
    with zipfile.ZipFile(BytesIO(raw)) as original, zipfile.ZipFile(buffer, 'w') as output:
        names = original.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Existing datapack contains duplicate ZIP entries')
        for info in original.infolist():
            if info.filename == FUNCTION:
                continue
            data = original.read(info)
            if info.filename == 'data/subway_station/function/restore_blocks.mcfunction':
                text = data.decode()
                text = '\n'.join(line for line in text.splitlines() if line.strip() != HOOK)
                data = (text.rstrip() + '\n' + HOOK + '\n').encode()
            output.writestr(info, data)
        output.writestr(FUNCTION, '\n'.join(restore) + '\n', compress_type=zipfile.ZIP_DEFLATED)
    return buffer.getvalue(), sum(line.startswith('setblock ') for line in restore)


def prepare(world, patch, previous_manifest=None):
    structure = nbt.load(patch)
    if list(map(int, structure['size'])) != [58, 7, 191]:
        raise ValueError('Unexpected furniture patch dimensions')
    previous = {}
    if previous_manifest:
        previous_data = json.loads(Path(previous_manifest).read_text())
        previous = {tuple(p[:3]): previous_data['palette'][p[3]] for p in previous_data['placements']}
    entries, grouped = [], defaultdict(list)
    for block in structure['blocks']:
        pos = tuple(int(block['pos'][i]) + ORIGIN[i] for i in range(3))
        state = structure['palette'][int(block['state'])]
        if str(state['Name']) in ('minecraft:air', 'minecraft:barrier', 'minecraft:command_block'):
            raise ValueError('Unexpected removal, barrier or command block in furniture patch')
        if not (-48 <= pos[1] <= -42 and (20362 <= pos[2] <= 20386 or 20529 <= pos[2] <= 20552)):
            raise ValueError(f'Furniture outside second-floor concourses: {pos}')
        entries.append((pos, state, block.get('nbt')))
        grouped[pos[0] // 16, pos[2] // 16].append(entries[-1])
    # A revision may replace or remove only exact blocks owned by its earlier
    # manifest. It never grants permission to overwrite arbitrary station blocks.
    placed = {p for p, _, _ in entries}
    for pos in previous.keys() - placed:
        entries.append((pos, nbt.Compound({'Name': nbt.String('minecraft:air')}), None))
        grouped[pos[0] // 16, pos[2] // 16].append(entries[-1])
    if len({p for p, _, _ in entries}) != len(entries):
        raise ValueError('Duplicate furniture coordinates')
    files, changes, chunk_count = {}, [], 0
    region_groups = defaultdict(list)
    for (cx, cz), edits in grouped.items():
        region_groups[cx // 32, cz // 32].append((cx, cz, edits))
    for (rx, rz), chunks in region_groups.items():
        path = world / f'region/r.{rx}.{rz}.mca'
        raw = path.read_bytes()
        result = bytearray(raw)
        for cx, cz, edits in sorted(chunks):
            slot = (cz % 32) * 32 + cx % 32
            location = int.from_bytes(raw[slot * 4:slot * 4 + 4], 'big')
            offset = (location >> 8) * 4096
            if not location or raw[offset + 4] != 2:
                raise ValueError(f'Expected existing zlib chunk: {cx}, {cz}')
            length = int.from_bytes(raw[offset:offset + 4], 'big')
            chunk = nbt.File.parse(BytesIO(zlib.decompress(raw[offset + 5:offset + 4 + length])))
            chunk['block_entities'] = nbt.List[nbt.Compound](chunk.get('block_entities', []))
            sections = {int(s['Y']): s for s in chunk['sections']}
            decoded, changed = {}, False
            for pos, state, tile in edits:
                x, y, z = pos
                section = sections[y // 16]
                states = section['block_states']
                if y // 16 not in decoded:
                    decoded[y // 16] = unpack(states)
                values = decoded[y // 16]
                index = (y % 16) * 256 + (z % 16) * 16 + x % 16
                before = states['palette'][int(values[index])]
                same = state_key(before) == state_key(state)
                owned = pos in previous and state_key(before) == state_key(previous[pos])
                if not same and not owned and str(before['Name']) not in ('minecraft:air', 'minecraft:light', 'minecraft:cave_air'):
                    raise ValueError(f'Would replace original architecture at {pos}: {before}')
                existing = [t for t in chunk.get('block_entities', []) if tuple(int(t[k]) for k in ('x', 'y', 'z')) == pos]
                if existing and not same:
                    raise ValueError(f'Would replace existing block entity at {pos}')
                target = next((i for i, s in enumerate(states['palette']) if state_key(s) == state_key(state)), None)
                if target is None:
                    target = len(states['palette'])
                    states['palette'].append(copy.deepcopy(state))
                values[index] = target
                if tile is not None:
                    updated_tile = copy.deepcopy(tile)
                    for k, value in zip(('x', 'y', 'z'), pos):
                        updated_tile[k] = nbt.Int(value)
                    if existing:
                        # A geometry revision leaves saved sign text, container
                        # contents and game-added block-entity fields untouched.
                        if existing[0] != updated_tile and not (previous_manifest and same):
                            existing[0].clear()
                            existing[0].update(updated_tile)
                            changed = True
                    else:
                        chunk['block_entities'].append(updated_tile)
                        changed = True
                if not same:
                    changes.append({'position': list(pos), 'before': before.unpack(), 'after': state.unpack(),
                                    **({'nbt': tile.unpack()} if tile is not None else {})})
                    changed = True
            if not changed:
                continue
            for sy, values in decoded.items():
                repack(sections[sy]['block_states'], values)
            # Vanilla recomputes lighting. Roof heightmaps remain correct: every
            # addition is beneath the existing vaulted roof and floor envelope.
            chunk['isLightOn'] = nbt.Byte(0)
            for section in chunk['sections']:
                section.pop('BlockLight', None)
                section.pop('SkyLight', None)
            stream = BytesIO()
            chunk.write(stream)
            compressed = zlib.compress(stream.getvalue())
            count = (len(compressed) + 5 + 4095) // 4096
            if count > 255:
                raise ValueError('External chunks are not supported')
            result.extend(b'\0' * (-len(result) % 4096))
            offset = len(result) // 4096
            struct.pack_into('>I', result, slot * 4, offset << 8 | count)
            result.extend((struct.pack('>I', len(compressed) + 1) + b'\x02' + compressed).ljust(count * 4096, b'\0'))
            chunk_count += 1
        if bytes(result) != raw:
            files[path] = bytes(result)
    datapack = world / 'datapacks/mcm.zip'
    patched, reset_count = patch_datapack(datapack.read_bytes(), entries)
    files[datapack] = patched
    return files, {'origin': list(ORIGIN), 'blocks': len(structure['blocks']), 'changed_blocks': len(changes),
                   'changed_chunks': chunk_count, 'interactive_reset_blocks': reset_count,
                   'removed_blocks': sum(str(s['Name']) == 'minecraft:air' for _, s, _ in entries), 'changes': changes}


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    try:
        temporary.chmod(path.stat().st_mode & 0o777)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def verify_backup(world, backup, *, allow_new_session_lock=False):
    spec = importlib.util.spec_from_file_location('world_backup', ROOT / '.agents/skills/backstabbed-map-creator/scripts/backup_world.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    manifest = helper.verify_archive(backup)
    if Path(manifest['source_world']).resolve() != world.resolve():
        raise ValueError('Backup belongs to a different world')
    saved = {str(Path(f['path']).relative_to(manifest['world_folder'])): f for f in manifest['files']}
    current = helper.inventory(world)
    if allow_new_session_lock and 'session.lock' not in saved:
        # A save never opened by Minecraft may have no lock file. An installer
        # may create and lock an empty one after the backup, without changing data.
        lock = world / 'session.lock'
        if lock.is_file() and lock.stat().st_size == 0:
            current.pop('session.lock', None)
    if current.keys() != saved.keys():
        raise ValueError('Save file inventory changed since the backup')
    for relative in saved:
        if helper.digest_file(world / relative) != saved[relative]['sha256']:
            raise ValueError('Save changed since backup: ' + relative)
    return helper.digest_file(backup)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--world', type=Path, default=WORLD)
    parser.add_argument('--patch', type=Path, default=WORK / 'subway-station-second-floor-furnishings.nbt')
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--previous-manifest', type=Path, help='Exact prior furniture ownership for a bounded revision')
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--report', type=Path, default=WORK / 'installation-plan.json')
    args = parser.parse_args()
    if args.install and not args.backup:
        parser.error('--install requires --backup from the stopped current world')
    if args.install:
        # lockf uses the same OS record-lock mechanism as Java's FileLock.
        with (args.world / 'session.lock').open('r+b') as lock:
            fcntl.lockf(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            backup_sha = verify_backup(args.world, args.backup)
            files, report = prepare(args.world, args.patch, args.previous_manifest)
            report['backup'] = str(args.backup.resolve())
            report['backup_sha256'] = backup_sha
            for path, content in files.items():
                atomic_write(path, content)
            report['installed'] = True
    else:
        files, report = prepare(args.world, args.patch, args.previous_manifest)
        report['installed'] = False
    report['patch_sha256'] = hashlib.sha256(args.patch.read_bytes()).hexdigest()
    report['files'] = {str(p.relative_to(args.world)): hashlib.sha256(data).hexdigest() for p, data in files.items()}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'changes'}, indent=2))


if __name__ == '__main__':
    main()
