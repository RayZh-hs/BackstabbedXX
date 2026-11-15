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
        self.assertLessEqual({n for n in after if before.get(n) != after[n]},
                             {patcher.TARGET, patcher.ALIGN, patcher.SYNC, patcher.SHOOT, patcher.SPAWN, patcher.TRY_FIRE})
        self.assertEqual(after[patcher.TARGET].decode().count(patcher.CALL), 1)
        self.assertLessEqual(set(before) - set(after), {patcher.CAPTURE})
        self.assertEqual(after, before, 'Canonical archive must contain the maintained overlay')

    def test_migration_preserves_projectile_rules_and_replaces_nearest_cleanup(self):
        spec = importlib.util.spec_from_file_location('bullet_visual', ROOT / 'scripts/bullet_visual.py')
        patcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(patcher)
        original_setup = 'tag @s remove NewGunShot\ntag @s add Fired\ndata merge entity @s {pickup:0b}\n'
        original_rules = 'scoreboard players add @e[type=arrow,tag=GunShot] gundelay 1\nkill @e[type=arrow,scores={gundelay=8..}]\n'
        old_summon = 'summon arrow ~ ~ ~ {NoGravity:1b,Tags:["GunShot","NewGunShot"],Passengers:[{id:"minecraft:item_display",Tags:["BulletDeco","NewBullet"],' + patcher.VISIBLE_ITEM + 'interpolation_duration:8}]}\n'
        before = {
            patcher.TARGET: (original_setup + patcher.OLD_CALL + '\n').encode(),
            patcher.SHOOT: (patcher.OLD_ORPHAN + '\n' + patcher.OLD_NEAREST + '\n' + original_rules).encode(),
            patcher.TRY_FIRE: ('# Ammo remains unchanged\n' + old_summon + 'gravity bridge fire @e[type=arrow,tag=NewGunShot,limit=1]\n').encode(),
            patcher.CAPTURE: b'obsolete seat helper',
            'unrelated': b'untouched',
        }
        after = patcher.patched(before)
        self.assertEqual(after, patcher.patched(after))
        self.assertEqual(after['unrelated'], before['unrelated'])
        self.assertNotIn(patcher.CAPTURE, after)
        setup = after[patcher.TARGET].decode()
        shoot = after[patcher.SHOOT].decode()
        self.assertTrue(setup.startswith(original_setup))
        self.assertLess(setup.index(patcher.SAVE_UUID), setup.index(patcher.CALL))
        self.assertTrue(shoot.startswith(original_rules))
        self.assertEqual(shoot.count(patcher.TICK), 1)
        self.assertNotIn('sort=nearest', shoot)
        fire = after[patcher.TRY_FIRE].decode()
        self.assertIn('BulletTemplate', fire)
        self.assertNotIn('item:', fire)
        self.assertTrue(fire.startswith('# Ammo remains unchanged\n'))
        self.assertTrue(fire.endswith('gravity bridge fire @e[type=arrow,tag=NewGunShot,limit=1]\n'))

    def test_display_uses_full_uuid_and_no_passenger_or_velocity_prediction(self):
        root = ROOT / 'bullet-visual/datapack/data/mcm/function/extensions/gun'
        setup = (root / 'align_visual.mcfunction').read_text()
        sync = (root / 'sync_visual.mcfunction').read_text()
        spawn = (root / 'spawn_visual.mcfunction').read_text()
        self.assertNotIn('ride @s dismount', setup)
        self.assertIn('kill @s', setup)
        self.assertIn('teleport_duration:1', spawn)
        self.assertIn('run summon item_display ~ ~ ~', spawn)
        self.assertNotIn('Passengers:', spawn)
        self.assertIn('Rotation:$(rotation)', spawn)
        self.assertIn('transformation.translation set value [0.0f,0.0f,0.0f]', setup)
        self.assertIn('UUID:$(arrow_uuid)', sync)
        self.assertIn('return run kill @s', sync)
        self.assertNotIn('sort=nearest', sync)

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
