import importlib.util
import json
from pathlib import Path
import re
import unittest
from zipfile import ZipFile
from world_geometry import World

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'data/mcm/function/lobby/options/ext_wall/'


class LobbyOptionsWallTests(unittest.TestCase):
    def test_all_trigger_actions_have_physical_controls(self):
        with ZipFile(next((ROOT / '.minecraft/saves').glob('*/datapacks/mcm.zip'))) as z:
            self.assertTrue(PREFIX + 'install.mcfunction' in z.namelist(), 'Physical options wall is missing')
            install = z.read(PREFIX + 'install.mcfunction').decode()
            actions = {int(v) for v in re.findall(r'action:(\d+)', install)}
            self.assertEqual(actions, set(range(2, 23)))
            self.assertIn('mcm:lobby/options/ext_wall/click', z.read('data/mcm/function/lobby/options/backend/click_interaction.mcfunction').decode())

    def test_overlay_is_narrow_idempotent_and_in_archive(self):
        path = ROOT / 'scripts/lobby_options_wall.py'
        self.assertTrue(path.exists(), 'Maintained wall overlay is missing')
        spec = importlib.util.spec_from_file_location('lobby_options_wall', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with ZipFile(next((ROOT / '.minecraft/saves').glob('*/datapacks/mcm.zip'))) as z:
            before = {n: z.read(n) for n in z.namelist()}
        after = module.patched(before)
        self.assertEqual(after, before)
        self.assertEqual(after, module.patched(after))
        old = {n: v for n, v in before.items() if not n.startswith(PREFIX)}
        for name, line in module.HOOKS.items():
            old[name] = old[name].decode().replace(line + '\n', '').encode()
        fixed = module.patched(old)
        self.assertEqual(fixed, before)
        self.assertEqual({n for n in old if old[n] != fixed[n]}, set(module.HOOKS))
        self.assertEqual(fixed['data/mcm/function/extensions/options/change.mcfunction'],
                         before['data/mcm/function/extensions/options/change.mcfunction'])

    def test_panels_fit_blank_wall_and_controls_do_not_overlap(self):
        path = ROOT / 'scripts/lobby_options_wall.py'
        self.assertTrue(path.exists())
        spec = importlib.util.spec_from_file_location('lobby_options_wall', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        world = World(next((ROOT / '.minecraft/saves').glob('Backstabbed ++!*')))
        controls = module.controls()
        self.assertEqual(len(module.PANELS), 14)
        self.assertEqual(len(controls), 21)
        for c in controls:
            mode = c['key'] == 'mode'
            self.assertGreater(c['z'] - c['width'] / 2, 83 if mode else 110)
            self.assertLess(c['z'] + c['width'] / 2, 86 if mode else 144)
            self.assertAlmostEqual(c['x'] - c['width'] / 2, 26.87 if mode else 27.87)
            wall_x = 27 if mode else 28
            self.assertEqual(world.block(wall_x, int(c['y']+c['height']/2), int(c['z']))['Name'], 'minecraft:light_gray_terracotta')
            self.assertNotEqual(world.block(wall_x-2, 7, int(c['z']))['Name'], 'minecraft:air')
            self.assertEqual(world.block(wall_x-2, 8, int(c['z']))['Name'], 'minecraft:air')
        for i, a in enumerate(controls):
            for b in controls[i+1:]:
                overlap_z = abs(a['z']-b['z']) < (a['width']+b['width'])/2
                overlap_y = a['y'] < b['y']+b['height'] and b['y'] < a['y']+a['height']
                self.assertFalse(overlap_z and overlap_y, (a, b))


if __name__ == '__main__':
    unittest.main()
