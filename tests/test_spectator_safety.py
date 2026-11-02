import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class SpectatorSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.safety = module('spectator_safety', 'scripts/spectator_safety.py')
        # Test the pure transformation on Windows; never invoke its Unix installer.
        with patch.dict(sys.modules, {'fcntl': Mock()}):
            cls.modes = module('mode_sync', 'game-modes/sync_datapack.py')
        raw = subprocess.check_output(['git', 'show', 'HEAD:.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/datapacks/mcm.zip'], cwd=ROOT)
        with ZipFile(io.BytesIO(raw)) as z:
            cls.original = {n: z.read(n) for n in z.namelist()}

    def test_patch_preserves_unrelated_members_and_is_repeatable(self):
        fixed = self.safety.patched(self.original)
        expected = {p.relative_to(ROOT / 'spectator-safety/datapack').as_posix()
                    for p in (ROOT / 'spectator-safety/datapack').rglob('*') if p.is_file()}
        self.assertFalse(set(self.original) - set(fixed))
        self.assertTrue({n for n in fixed if fixed[n] != self.original.get(n)} <= expected)
        self.assertEqual(fixed, self.safety.patched(fixed))

    def test_mode_rebuild_preserves_safety_and_single_tracker_tick(self):
        for source in (self.original, self.safety.patched(self.original)):
            rebuilt = self.modes.patched(source)
            self.assertEqual(rebuilt, self.modes.patched(rebuilt))
            self.assertEqual(rebuilt, self.safety.patched(rebuilt))
            ingame = rebuilt['data/mcm/function/game/loops/ingame.mcfunction'].decode()
            self.assertEqual(ingame.count('run function mcm:modes/tracker'), 1)

    def test_timeout_and_manual_callbacks_have_consistent_guards(self):
        fixed = self.safety.patched(self.original)
        for name in ('extensions/knife/recover', 'game/items/knife_retrieve', 'game/items/knife/throw'):
            self.assertTrue(fixed[f'data/mcm/function/{name}.mcfunction'].decode().startswith(self.safety.GUARD))
        tick = fixed['data/mcm/function/extensions/knife/tick.mcfunction'].decode()
        self.assertNotIn('@a[tag=queued,tag=murderer,tag=!spectating]', tick)


if __name__ == '__main__':
    unittest.main()
