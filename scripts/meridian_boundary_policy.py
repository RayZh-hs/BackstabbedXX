"""Stage/install Yacht-style boundary timing for Meridian Base (map 17).

Meridian Base reacted differently from Yacht: the exterior ocean already
eliminated during preparation, leaving the scene always teleported back (even
in the active round), and the lobby teleported players. This applies Yacht's
phase contract to the same bounds:

    lobby (gamestate 0)            -> no arena-boundary action
    preparation (graceperiod >= 1) -> return to a valid arena spawn
    active round (graceperiod <= 0)-> the existing elimination function

No predicate, block tag, coordinate box, spawn marker or NPC is modified. The
reviewable result lives in ``meridian-boundary-policy/datapack``.
"""
import argparse
import datetime
import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lobby_boundary_gate import stopped

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'meridian-boundary-policy/datapack'
STAGE = ROOT / 'dev/meridian-boundary-policy'
SAVES = Path('C:/Users/dyf08/AppData/Roaming/PrismLauncher/instances/Backstabbed++/.minecraft/saves')
WORLDS = (
    ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies',
    SAVES / 'Backstabbed ++! by NorbMinecraft and Bagel Buddies',
    SAVES / 'Backstabbed ++! v1.1.1 Latest 2026-10-28 77e59f6',
)
EXPECTED = {
    'data/meridian_base/function/check_player.mcfunction',
    'data/meridian_base/function/check_ocean.mcfunction',
    'data/meridian_base/function/ocean_contact.mcfunction',
    'data/meridian_base/function/return_player.mcfunction',
}
# `ocean_contact` is new: the phase decision used to live inside `check_ocean`.
NEW = {'data/meridian_base/function/ocean_contact.mcfunction'}


def readzip(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def zipbytes(files):
    from io import BytesIO
    out = BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name in files:
            z.writestr(name, files[name])
    return out.getvalue()


def patched(files):
    result = dict(files)
    for path in SOURCE.rglob('*.mcfunction'):
        key = path.relative_to(SOURCE).as_posix()
        assert key in result or key in NEW, f'{key} is not present in the datapack'
        result[key] = path.read_bytes().replace(b'\r\n', b'\n')
    return result


def stage():
    STAGE.mkdir(parents=True, exist_ok=True)
    manifest = []
    for index, world in enumerate(WORLDS):
        path = world / 'datapacks/mcm.zip'
        before = readzip(path)
        after = patched(before)
        changes = sorted(n for n in after if after[n] != before.get(n))
        assert set(changes) == EXPECTED, changes
        (STAGE / f'{index}-mcm.zip').write_bytes(zipbytes(after))
        manifest.append({'world': str(world), 'before': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'changes': changes})
    (STAGE / 'stage.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Staged 4 functions for {len(manifest)} worlds; every boundary and spawn is unchanged.')


def install(only=None):
    records = json.loads((STAGE / 'stage.json').read_text())
    indexes = list(range(len(records))) if only is None else only
    records = [(index, records[index]) for index in indexes]
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = ROOT / '.minecraft/backups/meridian-boundary-policy' / stamp
    backup.mkdir(parents=True)
    from contextlib import ExitStack
    with ExitStack() as stack:
        for _, record in records:
            stack.enter_context(stopped(Path(record['world'])))
        for index, record in records:
            world = Path(record['world'])
            path = world / 'datapacks/mcm.zip'
            assert hashlib.sha256(path.read_bytes()).hexdigest() == record['before'], f'{world} changed since staging'
            archive = backup / f'{index}-world.zip'
            with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as z:
                for file in world.rglob('*'):
                    if file.is_file() and file.name != 'session.lock':
                        z.write(file, world.name + '/' + file.relative_to(world).as_posix())
            with zipfile.ZipFile(archive) as z:
                assert z.testzip() is None
            record['backup'] = str(archive)
            record['backup_sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()
            print('Verified full backup:', archive, flush=True)
        for index, record in records:
            world = Path(record['world'])
            path = world / 'datapacks/mcm.zip'
            assert hashlib.sha256(path.read_bytes()).hexdigest() == record['before']
            before = readzip(path)
            staged = readzip(STAGE / f'{index}-mcm.zip')
            assert set(before) <= set(staged) and set(staged) - set(before) == NEW
            assert sorted(n for n in staged if staged[n] != before.get(n)) == record['changes']
            raw = (STAGE / f'{index}-mcm.zip').read_bytes()
            pending = path.with_name('mcm.zip.policy-pending')
            pending.write_bytes(raw)
            pending.replace(path)
            assert path.read_bytes() == raw
            record['after'] = hashlib.sha256(raw).hexdigest()
            print(f"Installed {world.name}: {record['after'][:16]}")
    (backup / 'installation.json').write_text(json.dumps([r for _, r in records], indent=2) + '\n')
    (STAGE / 'installed.json').write_text(json.dumps([r for _, r in records], indent=2) + '\n')
    print('Installed the selected worlds. All other save files preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--only', help='comma-separated world indexes from stage.json')
    args = parser.parse_args()
    if args.install:
        install(None if not args.only else [int(i) for i in args.only.split(',')])
    else:
        stage()
