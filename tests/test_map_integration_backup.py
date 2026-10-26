"""Exercise the integration skill's recoverable world snapshots on temp saves."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile


SCRIPT = Path(__file__).resolve().parent.parent / '.agents/skills/backstabbed-map-creator/scripts/backup_world.py'
spec = importlib.util.spec_from_file_location('integration_backup', SCRIPT)
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class MapIntegrationBackupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.world = self.root / 'World 地图'
        self.output = self.root / 'backups'
        self.original = {
            'level.dat': b'world metadata', 'level.dat_old': b'previous metadata',
            'region/r.-1.0.mca': b'blocks\0\1\2', 'entities/r.-1.0.mca': b'entities',
            'poi/r.-1.0.mca': b'poi', 'datapacks/mcm.zip': b'datapack',
            'generated/test/structures/fix.nbt': b'structure',
        }
        for name, content in self.original.items():
            path = self.world / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

    def test_snapshot_verifies_and_restores_all_source_files_unchanged(self):
        archive = backup.backup_world(self.world, self.output, 'arena-before-fix')
        manifest = backup.verify_archive(archive)
        self.assertEqual(manifest['world_folder'], self.world.name)
        self.assertEqual(len(manifest['files']), len(self.original))
        with zipfile.ZipFile(archive) as saved:
            saved.extractall(self.root / 'restored')
        for name, content in self.original.items():
            self.assertEqual((self.world / name).read_bytes(), content)
            self.assertEqual((self.root / 'restored' / self.world.name / name).read_bytes(), content)
        another = backup.backup_world(self.world, self.output, 'arena-before-fix')
        self.assertNotEqual(archive, another)
        self.assertTrue(archive.is_file())
        self.assertFalse(list(self.output.glob('*.partial')))

    def test_invalid_source_and_recursive_backup_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'level.dat'):
            backup.backup_world(self.root / 'missing', self.output)
        with self.assertRaisesRegex(ValueError, 'outside'):
            backup.backup_world(self.world, self.world / 'backups')
        self.assertFalse((self.world / 'backups').exists())

    def test_source_change_prevents_publishing_a_backup(self):
        verify = backup.verify_archive
        def change_source_then_verify(archive):
            result = verify(archive)
            (self.world / 'level.dat').write_bytes(b'changed by a running game')
            return result
        with patch.object(backup, 'verify_archive', side_effect=change_source_then_verify):
            with self.assertRaisesRegex(ValueError, 'changed'):
                backup.backup_world(self.world, self.output)
        self.assertFalse(list(self.output.iterdir()))

    def test_corrupted_file_fails_verification(self):
        original = backup.backup_world(self.world, self.output)
        corrupt = self.output / 'corrupt.zip'
        with zipfile.ZipFile(original) as incoming, zipfile.ZipFile(corrupt, 'w') as outgoing:
            for entry in incoming.infolist():
                content = incoming.read(entry)
                if entry.filename.endswith('/level.dat'):
                    content = b'corrupted content'
                outgoing.writestr(entry, content)
        with self.assertRaisesRegex(ValueError, 'verification failed'):
            backup.verify_archive(corrupt)


if __name__ == '__main__':
    unittest.main()
