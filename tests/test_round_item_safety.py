import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
LOADOUT = ROOT / 'game-modes/datapack'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def function(members, name):
    return members[f'data/mcm/function/{name}.mcfunction'].decode()


class RoundItemSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = module('round_item_safety', 'scripts/round_item_safety.py')
        cls.safety = module('spectator_safety', 'scripts/spectator_safety.py')
        # Test the pure transformation on Windows; never invoke its Unix installer.
        with patch.dict(sys.modules, {'fcntl': Mock()}):
            cls.modes = module('mode_sync', 'game-modes/sync_datapack.py')
        raw = subprocess.check_output(
            ['git', 'show', 'HEAD:.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/datapacks/mcm.zip'],
            cwd=ROOT)
        with ZipFile(io.BytesIO(raw)) as z:
            cls.original = {n: z.read(n) for n in z.namelist()}

    def test_patch_preserves_unrelated_members_and_is_repeatable(self):
        fixed = self.items.patched(self.original)
        self.assertFalse(set(self.original) - set(fixed))
        changed = {n for n in fixed if fixed[n] != self.original.get(n)}
        # Once the fix is in HEAD the base is already correct, so the delta is
        # empty; what must never happen is rewriting some other member.
        self.assertLessEqual(changed, {
            'data/mcm/function/items/loadouts/murderer.mcfunction',
            'data/mcm/function/extensions/knife/recover.mcfunction',
            'data/mcm/function/extensions/gun/setspeed.mcfunction',
            'data/mcm/function/game/items/gun/shoot.mcfunction',
        })
        self.assertEqual(fixed, self.items.patched(fixed))

    def test_killer_loadout_cannot_grant_two_knives(self):
        loadout = function(self.items.patched(self.original), 'items/loadouts/murderer')
        # Every kit slot is written in place; `/give` would pick whatever slot is free.
        for slot in (1, 2, 3, 4):
            self.assertIn(f'{{slot:{slot},replace:1b,nbt:{{murderer:1b}}}}', loadout)
        self.assertIn('clear @s snowball[custom_data~{knife:1b}]', loadout)
        self.assertLess(loadout.index('clear @s snowball'), loadout.index('{item:knife}'),
                        'the stale knife must be cleared before the new one is handed out')

    def test_timeout_recovery_never_grants_a_second_knife(self):
        recover = function(self.items.patched(self.original), 'extensions/knife/recover')
        self.assertTrue(recover.startswith(self.safety.GUARD),
                        'the spectator guard must still be the first command')
        guard_at = recover.index('Never hand out a replacement')
        for check in ('if items entity @s container.* snowball[custom_data~{knife:1b}]',
                      'if items entity @s weapon.* snowball[custom_data~{knife:1b}]'):
            self.assertIn(f'execute {check} run return 0', recover.split('# Invalidate')[0])
        self.assertLess(guard_at, recover.index('# Invalidate'),
                        'the ownership check must run before the knife is invalidated and reissued')

    def test_bullet_arrows_stay_unpickable(self):
        fixed = self.items.patched(self.original)
        self.assertIn('data merge entity @s {pickup:0b}', function(fixed, 'extensions/gun/setspeed'))
        tick = function(fixed, 'game/items/gun/shoot')
        self.assertIn('execute as @e[type=arrow,tag=GunShot] run data merge entity @s {pickup:0b}', tick)

    def test_mode_rebuild_keeps_item_guards(self):
        for source in (self.original, self.safety.patched(self.original)):
            rebuilt = self.modes.patched(source)
            self.assertEqual(rebuilt, self.modes.patched(rebuilt))
            self.assertEqual(rebuilt, self.items.patched(rebuilt))
            self.assertIn('clear @s snowball[custom_data~{knife:1b}]', function(rebuilt, 'items/loadouts/murderer'))
            self.assertIn('run return 0', function(rebuilt, 'extensions/knife/recover'))
            self.assertIn('{pickup:0b}', function(rebuilt, 'extensions/gun/setspeed'))


if __name__ == '__main__':
    unittest.main()
