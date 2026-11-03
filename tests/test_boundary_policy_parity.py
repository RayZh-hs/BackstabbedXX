"""Executable survey of every arena's out-of-bounds policy.

Yacht's contract, which the shared policy work targets:

    lobby (gamestate 0)             -> no arena-boundary action
    preparation (graceperiod >= 1)  -> return a live participant to the arena
    active round (graceperiod <= 0) -> the existing elimination function

Arena styles that only eliminate, only teleport, or do nothing are listed in
``DOCUMENTED_GAPS`` with the reason, so the survey cannot silently drift.
"""
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DATAPACK = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/datapacks/mcm.zip'
RESCUE = ('return_player', 'return_to_arena', 'run tp', '/tp')

# Arena -> handler functions that implement the Yacht phase contract.
YACHT_STYLE = {
    'yacht': ['data/yacht/function/functionality.mcfunction'],
    'panda_village': ['data/panda_village/function/functionality.mcfunction'],
    'klut27': ['data/bbe_arena/function/klut27/kill.mcfunction'],
    'underwater_base': ['data/bbe_arena/function/underwater_base/kill.mcfunction'],
    'middle_ages': ['data/middle_ages/function/escape.mcfunction'],
    'sworld_island': ['data/sworld_island/function/escape.mcfunction'],
    'cube_block': ['data/cube_block/function/fall.mcfunction'],
    'meridian_base': ['data/meridian_base/function/check_player.mcfunction',
                      'data/meridian_base/function/ocean_contact.mcfunction'],
    'airship': ['data/mcm/function/maps/airship/functionality.mcfunction'],
    'riverboat': ['data/mcm/function/maps/riverboat/functionality.mcfunction'],
    'train': ['data/mcm/function/maps/train/functionality.mcfunction'],
    'sculk': ['data/mcm/function/maps/sculk/functionality.mcfunction'],
    'canyon': ['data/mcm/function/maps/canyon/functionality.mcfunction'],
}

# Arenas that still differ from Yacht, with the observed behavior.
DOCUMENTED_GAPS = {
    'bagger_288': 'eliminates during preparation; there is no rescue branch',
    'river_bank': 'always returns; it never eliminates an escaped participant',
    'subway_station': 'boundary handling is disabled by design',
    'library2': 'no out-of-bounds rule',
    'vineyard2': 'no out-of-bounds rule',
    'cyberpunk': 'no out-of-bounds rule',
    'industry': 'no out-of-bounds rule',
    'gumdrop': 'no out-of-bounds rule',
    'cabin': 'no out-of-bounds rule (freezing mechanic instead)',
}

# Arenas whose only rule is an active-round elimination, so preparation has no rescue.
ACTIVE_ONLY = ('launchpad',)


def datapack_files():
    with ZipFile(DATAPACK) as z:
        return {n: z.read(n).decode(errors='replace') for n in z.namelist() if n.endswith('.mcfunction')}


def code_lines(text):
    return [line.strip() for line in text.splitlines()
            if line.strip() and not line.strip().startswith('#')]


class BoundaryParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = datapack_files()

    def test_yacht_style_arenas_rescue_then_eliminate(self):
        for arena, handlers in YACHT_STYLE.items():
            eliminated = False
            for handler in handlers:
                self.assertIn(handler, self.files, f'{arena} is missing {handler}')
                lines = code_lines(self.files[handler])
                rescue = [l for l in lines if 'graceperiod CmdData matches 1..' in l]
                self.assertTrue(rescue, f'{arena}: {handler} has no preparation branch')
                self.assertTrue(any(any(token in l for token in RESCUE) for l in rescue),
                                f'{arena}: preparation must return the player to the arena, got {rescue}')
                eliminated = eliminated or any('mcm:game/playerdeath' in l for l in lines)
            self.assertTrue(eliminated, f'{arena}: the active round must eliminate')

    def test_meridian_excludes_the_lobby_and_keeps_its_bounds(self):
        check = self.files['data/meridian_base/function/check_player.mcfunction']
        lines = code_lines(check)
        self.assertEqual(lines[0], 'execute unless score $gamestate CmdData matches 1 run return 0',
                         'the lobby must be excluded before any boundary action')
        self.assertNotIn('matches 0', check, 'no lobby teleport may remain')

        contact = code_lines(self.files['data/meridian_base/function/ocean_contact.mcfunction'])
        self.assertTrue(contact[0].startswith('execute if score $graceperiod CmdData matches 1..'),
                        'ocean contact must rescue during preparation')
        self.assertIn('function mcm:game/playerdeath', contact)

        probes = [l for l in code_lines(self.files['data/meridian_base/function/check_ocean.mcfunction'])
                  if 'if block' in l]
        self.assertEqual(len(probes), 5, 'the five sampled ocean probes must be preserved')
        self.assertTrue(all('meridian_base:ocean_contact' in l for l in probes),
                        'every ocean probe must route through the phase decision')

    def test_meridian_return_prefers_a_valid_arena_spawn(self):
        lines = code_lines(self.files['data/meridian_base/function/return_player.mcfunction'])
        selector = ('@e[type=marker,tag=PlayerSpawn,tag=MeridianBaseRuntime,'
                    'predicate=meridian_base:arena,sort=nearest,limit=1]')
        self.assertTrue(any('unless entity ' + selector in l and '24582.5 -29 24576.5' in l for l in lines),
                        'the previous fixed point must remain the fallback')
        self.assertTrue(any('tp @s ' + selector in l for l in lines),
                        'a qualifying marker must win over the fixed point')
        self.assertTrue(any('effect clear @s minecraft:levitation' in l for l in lines),
                        'the lift effects must still be cleared on a rescue')

    def test_gap_list_still_describes_the_datapack(self):
        # bagger_288: an elimination with no grace branch at all.
        bagger = self.files['data/bagger_288/function/check_player.mcfunction']
        self.assertNotIn('graceperiod', bagger, DOCUMENTED_GAPS['bagger_288'])
        self.assertIn('bagger_288:fall', bagger)

        # river_bank: out-of-arena always teleports, never eliminates.
        river = code_lines(self.files['data/river_bank/function/functionality.mcfunction'])
        river_bounds = [l for l in river if '!river_bank:arena' in l]
        self.assertTrue(river_bounds and all('run tp @s' in l for l in river_bounds),
                        DOCUMENTED_GAPS['river_bank'])
        self.assertFalse(any('mcm:game/playerdeath' in l for l in river), DOCUMENTED_GAPS['river_bank'])

        # subway_station: intentional no-op.
        self.assertIn('disabled', self.files['data/subway_station/function/functionality.mcfunction'],
                      DOCUMENTED_GAPS['subway_station'])

        # Arenas without a boundary rule keep having none.
        for arena in ('library2', 'vineyard2', 'cyberpunk', 'industry', 'gumdrop'):
            handler = self.files.get(f'data/mcm/function/maps/{arena}/functionality.mcfunction', '')
            self.assertNotIn('mcm:game/playerdeath', handler, DOCUMENTED_GAPS[arena])

    def test_active_only_arenas_have_no_preparation_rescue(self):
        for arena in ACTIVE_ONLY:
            handler = self.files.get(f'data/mcm/function/maps/{arena}/functionality.mcfunction')
            self.assertIsNotNone(handler, arena)
            rescue = [l for l in code_lines(handler)
                      if 'graceperiod CmdData matches 1..' in l and any(t in l for t in RESCUE)]
            self.assertFalse(rescue, f'{arena} unexpectedly gained a preparation rescue; update the survey')


if __name__ == '__main__':
    unittest.main()
