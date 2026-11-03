"""The Meridian Base policy must change reactions only, never boundaries."""
import importlib.util
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DATAPACK = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/datapacks/mcm.zip'
CHANGED = {
    'data/meridian_base/function/check_ocean.mcfunction',
    'data/meridian_base/function/check_player.mcfunction',
    'data/meridian_base/function/ocean_contact.mcfunction',
    'data/meridian_base/function/return_player.mcfunction',
}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class MeridianBoundaryPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = module('meridian_boundary_policy', 'scripts/meridian_boundary_policy.py')
        with ZipFile(DATAPACK) as z:
            cls.installed = {n: z.read(n) for n in z.namelist()}

    def test_the_installed_datapack_matches_the_reviewed_source(self):
        rebuilt = self.policy.patched(self.installed)
        for name in CHANGED:
            self.assertEqual(rebuilt[name], self.installed[name],
                             f'{name} is installed differently from meridian-boundary-policy/datapack')
        self.assertEqual(rebuilt, self.installed, 'the policy is already applied and must be idempotent')

    def test_only_the_reaction_changed(self):
        source = self.policy.SOURCE
        names = {p.relative_to(source).as_posix() for p in source.rglob('*.mcfunction')}
        self.assertEqual(names, CHANGED)
        # Predicates, block tags, spawn markers and every other function stay untouched.
        for name in self.installed:
            if name.startswith('data/meridian_base/predicate/') or name.startswith('data/meridian_base/tags/'):
                self.assertNotIn(name, CHANGED)

    def test_preparation_rescues_and_the_active_round_eliminates(self):
        check = self.installed['data/meridian_base/function/check_player.mcfunction'].decode()
        self.assertTrue(check.startswith('#> Yacht-style boundary timing'))
        self.assertIn(
            'execute if score $graceperiod CmdData matches 1.. unless predicate meridian_base:scene '
            'run return run function meridian_base:return_player', check)
        self.assertIn(
            'execute if score $graceperiod CmdData matches ..0 unless predicate meridian_base:scene '
            'run return run function mcm:game/playerdeath', check)

        contact = self.installed['data/meridian_base/function/ocean_contact.mcfunction'].decode()
        self.assertIn('execute if score $graceperiod CmdData matches 1.. run return run function meridian_base:return_player', contact)
        self.assertIn('\nfunction mcm:game/playerdeath', contact)

    def test_return_keeps_the_old_fallback(self):
        body = self.installed['data/meridian_base/function/return_player.mcfunction'].decode()
        self.assertIn('run tp @s 24582.5 -29 24576.5', body)
        self.assertIn('tag=MeridianBaseRuntime', body)
        self.assertIn('predicate=meridian_base:arena', body)


if __name__ == '__main__':
    unittest.main()
