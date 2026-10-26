#!/usr/bin/env python3
"""Snapshot a stopped Minecraft save and verify every archived file by SHA-256.

This detects files changing during the snapshot; it does not stop Minecraft or
prove that a running game is idle. Close the world before calling this helper.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tempfile
import uuid
import zipfile


MANIFEST = 'backup-manifest.json'
CHUNK = 1024 * 1024


def signature(path):
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def inventory(world):
    result = {}
    for path in sorted(world.rglob('*')):
        if path.is_symlink():
            raise ValueError('Save contains a symlink; choose an explicit backup strategy: ' + str(path))
        if path.is_file():
            result[path.relative_to(world).as_posix()] = signature(path)
    return result


def digest_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(archive):
    with zipfile.ZipFile(archive) as saved:
        names = saved.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Backup contains duplicate ZIP members')
        manifest = json.loads(saved.read(MANIFEST))
        if manifest.get('format') != 'backstabbed-world-backup-v1':
            raise ValueError('Unrecognised backup manifest')
        expected = {MANIFEST}
        for entry in manifest['files']:
            name = entry['path']
            if PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts:
                raise ValueError('Invalid backup member path: ' + name)
            if name in expected:
                raise ValueError('Duplicate file in backup manifest: ' + name)
            expected.add(name)
            digest = hashlib.sha256()
            size = 0
            with saved.open(name) as stream:
                for chunk in iter(lambda: stream.read(CHUNK), b''):
                    digest.update(chunk)
                    size += len(chunk)
            if digest.hexdigest() != entry['sha256'] or size != entry['size']:
                raise ValueError('Backup content verification failed: ' + name)
        if set(names) != expected:
            raise ValueError('Backup contents differ from the manifest')
    return manifest


def backup_world(world, backup_dir, label='before-map-fix'):
    world, backup_dir = Path(world).resolve(), Path(backup_dir).resolve()
    if not world.is_dir() or not (world / 'level.dat').is_file():
        raise ValueError('Expected a Minecraft save directory containing level.dat: ' + str(world))
    try:
        backup_dir.relative_to(world)
    except ValueError:
        pass
    else:
        raise ValueError('Backup directory must be outside the source save')
    before = inventory(world)
    backup_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    label = re.sub(r'[^A-Za-z0-9_-]+', '-', label).strip('-') or 'before-map-fix'
    name = now.strftime('%Y%m%dT%H%M%S%fZ') + '-' + label + '-' + uuid.uuid4().hex[:8] + '.zip'
    final = backup_dir / name
    with tempfile.NamedTemporaryFile(dir=backup_dir, suffix='.partial', delete=False) as temporary:
        partial = Path(temporary.name)
    try:
        files = []
        with zipfile.ZipFile(partial, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as saved:
            for relative, original in before.items():
                source = world / relative
                if signature(source) != original:
                    raise ValueError('Save changed during backup; stop Minecraft and retry: ' + relative)
                member = world.name + '/' + relative
                digest, size = hashlib.sha256(), 0
                with source.open('rb') as incoming, saved.open(member, 'w', force_zip64=True) as outgoing:
                    for chunk in iter(lambda: incoming.read(CHUNK), b''):
                        outgoing.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
                if signature(source) != original:
                    raise ValueError('Save changed during backup; stop Minecraft and retry: ' + relative)
                files.append({'path': member, 'size': size, 'sha256': digest.hexdigest()})
            manifest = {
                'format': 'backstabbed-world-backup-v1',
                'created_utc': now.isoformat(), 'source_world': str(world),
                'world_folder': world.name, 'files': files,
            }
            saved.writestr(MANIFEST, json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
        verify_archive(partial)
        if inventory(world) != before:
            raise ValueError('Save changed during backup; stop Minecraft and retry')
        if final.exists():
            raise FileExistsError('Refusing to replace an existing backup: ' + str(final))
        partial.replace(final)
        return final
    finally:
        partial.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('world', nargs='?', type=Path)
    parser.add_argument('--backup-dir', type=Path)
    parser.add_argument('--label', default='before-map-fix')
    parser.add_argument('--verify', type=Path, metavar='ARCHIVE')
    args = parser.parse_args()
    if args.verify:
        if args.world or args.backup_dir:
            parser.error('--verify cannot be combined with a world or --backup-dir')
        archive = args.verify
    else:
        if not args.world or not args.backup_dir:
            parser.error('Provide WORLD and --backup-dir, or --verify ARCHIVE')
        archive = backup_world(args.world, args.backup_dir, args.label)
    manifest = verify_archive(archive)
    print('Verified backup:', archive.resolve())
    print('SHA256:', digest_file(archive))
    print('Files:', len(manifest['files']))
    print('Restore world folder:', manifest['world_folder'])


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        raise SystemExit('Backup failed: ' + str(error))
