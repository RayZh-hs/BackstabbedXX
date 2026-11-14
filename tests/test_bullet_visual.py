import json
import importlib.util
from pathlib import Path
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


class BulletVisualTests(unittest.TestCase):
    def test_datapack_patch_is_narrow_and_repeatable(self):
        spec = importlib.util.spec_from_file_location('bullet_visual', ROOT / 'scripts/bullet_visual.py')
        patcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(patcher)
        path = next((ROOT / '.minecraft/saves').glob('*/datapacks/mcm.zip'))
        with ZipFile(path) as z:
            before = {n: z.read(n) for n in z.namelist()}
        after = patcher.patched(before)
        self.assertEqual(after, patcher.patched(after))
        self.assertLessEqual({n for n in after if before.get(n) != after[n]}, {patcher.TARGET, patcher.ALIGN, patcher.CAPTURE})
        self.assertEqual(after[patcher.TARGET].decode().count(patcher.CALL), 1)
        self.assertFalse(set(before) - set(after))

    def test_model_center_is_on_display_origin(self):
        model = json.loads((ROOT / '.minecraft/resourcepacks/backstabbed-resource/assets/minecraft/models/misc/bullet.json').read_text())
        # Item rendering subtracts (8, 8, 8). With a centered model, any
        # yaw/pitch/gravity rotation and the existing scale preserve the origin.
        for axis in range(3):
            low = min(e['from'][axis] for e in model['elements'])
            high = max(e['to'][axis] for e in model['elements'])
            self.assertAlmostEqual((low + high) / 2, 8, msg=f'axis {axis}')
        self.assertEqual(len(model['elements']), 31)


if __name__ == '__main__':
    unittest.main()
