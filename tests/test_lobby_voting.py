import importlib.util
import json
from pathlib import Path
import unittest
from zipfile import ZipFile
from world_geometry import World

ROOT = Path(__file__).resolve().parents[1]
WORLD = next((ROOT / '.minecraft/saves').glob('Backstabbed ++!*'))


class LobbyVotingTests(unittest.TestCase):
    def test_all_vote_translations_display_the_count(self):
        for path in (ROOT/'.minecraft/resourcepacks/backstabbed-resource/assets/minecraft/lang').glob('*.json'):
            translations=json.loads(path.read_text(encoding='utf-8-sig'))
            if 'mcm.lobby.vote' in translations:
                self.assertEqual(translations['mcm.lobby.vote'].count('%s'),1,path.name)

    def test_eight_slots_and_advancements_are_installed(self):
        with ZipFile(WORLD / 'datapacks/mcm.zip') as z:
            for i in (7, 8):
                self.assertTrue(f'data/mcm/advancement/map_votes/map{i}.json' in z.namelist(), f'Missing vote slot {i}')
            self.assertTrue('data/mcm/function/lobby/voting/reroll.mcfunction' in z.namelist())

    def test_reviewed_overlay_is_installed_and_idempotent(self):
        script = ROOT / 'scripts/lobby_voting.py'
        self.assertTrue(script.exists(), 'Voting overlay generator missing')
        spec = importlib.util.spec_from_file_location('voting', script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        with ZipFile(WORLD / 'datapacks/mcm.zip') as z:
            current = {n:z.read(n) for n in z.namelist()}
        self.assertEqual(mod.patched(current), current)
        for n,b in mod.generated(current).items():
            self.assertEqual((ROOT/'lobby-voting/datapack'/n).read_bytes().replace(b'\r\n',b'\n'),b)

    def test_new_controls_have_clear_access_and_solid_wall(self):
        world = World(WORLD)
        for z in (121, 126):
            for y in (2,3,4):
                self.assertEqual(world.block(26,y,z)['Name'], 'minecraft:air')
                self.assertNotEqual(world.block(28,y,z)['Name'], 'minecraft:air')
            self.assertNotEqual(world.block(26,0,z)['Name'], 'minecraft:air')
        for z in (79,80,81):
            for y in (2,3,4):
                self.assertEqual(world.block(25,y,z)['Name'],'minecraft:air')
                self.assertNotEqual(world.block(26,y,z)['Name'],'minecraft:air')


if __name__ == '__main__': unittest.main()
