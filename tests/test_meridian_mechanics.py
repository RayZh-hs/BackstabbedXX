"""Meridian's saved dispenser pads, actual elevator landings and ocean boundary."""
import json
import math
from pathlib import Path
import unittest
from zipfile import ZipFile

from world_geometry import World, in_region

ROOT = Path(__file__).resolve().parents[1]
SAVE = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
PADS = [(24519, -30, 24583), (24538, -30, 24627), (24582, -30, 24520),
        (24626, -30, 24539), (24645, -30, 24583), (24626, -30, 24627),
        (24582, -30, 24646)]
LANDINGS = [(24569.5, -17, 24590.5), (24575.5, -10, 24594.5)]


class MeridianMechanics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = World(SAVE)
        with ZipFile(SAVE / 'datapacks/mcm.zip') as z:
            cls.data = {n: z.read(n) for n in z.namelist()}

    def text(self, path):
        return self.data[f'data/meridian_base/{path}'].decode()

    def predicate(self, name):
        return json.loads(self.text(f'predicate/{name}.json'))

    def test_saved_pads_are_locked_upward_dispensers(self):
        for index, (x, y, z) in enumerate(PADS, 1):
            with self.subTest(pad=index):
                block = self.world.block(x, y, z)
                self.assertEqual(block['Name'], 'minecraft:dispenser')
                self.assertEqual(block['Properties']['facing'], 'up')
                tile, = [t for t in self.world.chunk(x // 16, z // 16)['block_entities']
                         if (t['x'], t['y'], t['z']) == (x, y, z)]
                self.assertEqual(tile['id'], 'minecraft:dispenser')
                self.assertEqual(tile['Items'], [])
                self.assertEqual(tile['lock']['items'], 'minecraft:barrier')
                self.assertEqual(tile['lock']['components']['minecraft:custom_data'],
                                 {'meridian_dispenser_key': 170029})
                self.assertTrue(in_region(self.predicate(f'pad_{index}'), (x + .5, y + 1, z + .5)))
                self.assertFalse(in_region(self.predicate(f'pad_{index}'), (x + 1.1, y + 1, z + .5)))

    def test_elevator_support_headroom_connected_routes_and_buttons(self):
        for point in LANDINGS:
            x, y, z = map(math.floor, point)
            self.assertTrue(in_region(self.predicate('arena'), point))
            self.assertTrue(in_region(self.predicate('scene'), point))
            self.assertIn(self.world.block(x, y - 1, z)['Name'],
                          ('minecraft:light_gray_concrete', 'minecraft:polished_tuff_slab'))
            if 'slab' in self.world.block(x, y - 1, z)['Name']:
                self.assertEqual(self.world.block(x, y - 1, z)['Properties']['type'], 'double')
            # The west neighbour is a clear route, with at most a half-block
            # step down from the upper double-slab landing.
            self.assertIn(self.world.block(x - 1, y - 1, z)['Name'],
                          ('minecraft:light_gray_concrete', 'minecraft:polished_tuff_slab'))
            for dx, dz in [(0, 0), (-1, 0)]:
                for dy in [0, 1]:
                    self.assertIn(self.world.block(x + dx, y + dy, z + dz)['Name'],
                                  ('minecraft:air', 'minecraft:cave_air'))
        for name in ('up', 'down'):
            advancement = json.loads(self.text(f'advancement/lift_{name}.json'))
            self.assertEqual(advancement['criteria']['button']['trigger'], 'minecraft:default_block_use')
            terms = advancement['criteria']['button']['conditions']['location'][0]['terms']
            for term in terms:
                position = term['predicate']['position']
                xyz = [math.floor(position[a]['min']) for a in 'xyz']
                self.assertEqual(self.world.block(*xyz)['Name'], 'minecraft:polished_blackstone_button')

    def test_actual_ocean_water_is_fatal_height_and_indoor_fluids_are_excluded(self):
        ocean = (24576.5, -34, 24576.5)
        self.assertEqual(self.world.block(24576, -34, 24576)['Name'], 'minecraft:water')
        self.assertTrue(in_region(self.predicate('ocean_height'), ocean))
        self.assertTrue(in_region(self.predicate('scene'), ocean))
        self.assertFalse(in_region(self.predicate('arena'), ocean))
        for point in [(24591.5, -27, 24598.5), (24592.5, -13, 24600.5)]:
            self.assertEqual(self.world.block(*map(math.floor, point))['Name'], 'minecraft:bubble_column')
            self.assertFalse(in_region(self.predicate('ocean_height'), point))
        self.assertFalse(in_region(self.predicate('scene'), (24696.5, -29, 24576.5)))
        code = self.text('function/check_player.mcfunction')
        self.assertNotIn('#meridian_base:fluids', code)
        self.assertIn('unless predicate meridian_base:scene run return run function meridian_base:return_player', code)
        self.assertIn('matches 1 if predicate meridian_base:ocean_height', code)

    def test_potato_consumption_and_per_entry_reward_contract(self):
        line = self.text('function/plantation/spawn.mcfunction').strip()
        food = json.loads(line[line.index('{'):])['Item']
        self.assertEqual(food['id'], 'minecraft:potato')
        components = food['components']
        self.assertEqual(json.loads(components['minecraft:custom_name'])['text'], 'Delicious Food')
        self.assertTrue(components['minecraft:food']['can_always_eat'])
        effect, = components['minecraft:consumable']['on_consume_effects']
        self.assertEqual(effect['probability'], 1)
        self.assertEqual({e['id']: e['duration'] for e in effect['effects']},
                         {'minecraft:speed': 200, 'minecraft:jump_boost': 200})
        check = self.text('function/check_player.mcfunction')
        self.assertIn('unless score @s MeridianPad = @s MeridianLastPad', check)
        self.assertIn('scoreboard players operation @s MeridianLastPad = @s MeridianPad', check)
        self.assertIn('random value 0..1', self.text('function/dispenser/roll.mcfunction'))
        self.assertIn('LifeTime:18', self.text('function/dispenser/firework.mcfunction'))
        reset = self.text('function/reset.mcfunction')
        self.assertIn('kill @e[tag=MeridianBaseRuntime]', reset)
        self.assertIn('meridian_food:1b', reset)
        self.assertIn('function meridian_base:setup_mechanics', self.text('function/activate.mcfunction'))
        self.assertIn('function meridian_base:dispenser/restore', self.text('function/restore_blocks.mcfunction'))


if __name__ == '__main__':
    unittest.main()
