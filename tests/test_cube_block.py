"""Cube Block spawns and escape limits against the imported destination chunks."""
from collections import Counter
import json
import math
from pathlib import Path
import re
import unittest
from zipfile import ZipFile

from world_geometry import World, in_region

ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
from cube_geometry import FACES, face_surface, largest_surface, neighbours


class CubeBlockIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / 'docs/arenas/cube_block.json').read_text())
        cls.world = World(WORLD)
        with ZipFile(WORLD / 'datapacks/mcm.zip') as z:
            cls.functions = {name: z.read(name).decode() for name in z.namelist()
                             if name.startswith('data/cube_block/') or name in (
                                 'data/mcm/function/maps/tptospawn.mcfunction',
                                 'data/mcm/function/extensions/gravity/spawn_scrap.mcfunction')}
        cls.predicate = json.loads(cls.functions['data/cube_block/predicate/arena.json'])
        cls.spawns = cls.manifest['player_spawns']
        cls.clear = set(cls.manifest['spawn_validation']['clear_blocks'])
        cls.support = set(cls.manifest['spawn_validation']['support_blocks'])
        cls.contacts = cls.manifest['spawn_faces']

    def text(self, name):
        return self.functions[f'data/cube_block/function/{name}.mcfunction']

    def test_all_actual_spawns_have_full_support_clear_collision_and_region_membership(self):
        self.assertEqual(len(self.spawns), 32)
        self.assertEqual(len(self.spawns), len(set(map(tuple, self.spawns))))
        actual = [tuple(map(float, m)) for m in re.findall(
            r'summon marker ([\d.]+) ([\d.]+) ([\d.]+) \{Tags:\["PlayerSpawn"', self.text('activate'))]
        self.assertEqual(actual, list(map(tuple, self.spawns)))
        self.assertEqual(self.manifest['scrap_spawns'], self.spawns)
        self.assertEqual([r['position'] for r in self.contacts], self.spawns)
        directions = re.findall(r'gravity_direction:"(\w+)"', self.text('activate'))
        self.assertEqual(directions, [r['gravity_direction'] for r in self.contacts])
        expected = {'top': ('down', [0, 1, 0]), 'bottom': ('up', [0, -1, 0]),
                    'west': ('east', [-1, 0, 0]), 'east': ('west', [1, 0, 0]),
                    'north': ('south', [0, 0, -1]), 'south': ('north', [0, 0, 1])}
        for contact in self.contacts:
            point = contact['position']
            with self.subTest(point=point):
                self.assertEqual((contact['gravity_direction'], contact['normal']), expected[contact['face']])
                normal = contact['normal']
                axis = next(i for i, v in enumerate(normal) if v)
                support = [math.floor(v - n * .01) for v, n in zip(point, normal)]
                self.assertEqual(support, contact['support'])
                self.assertIn(self.world.block(*support)['Name'], self.support)
                state = self.world.block(*support)
                if state['Name'].endswith('_leaves'):
                    self.assertEqual(state['Properties']['persistent'], 'true')
                    self.assertEqual(state['Properties']['waterlogged'], 'false')
                # Enumerate every voxel intersecting the rotated 0.6 x 1.8
                # player body, with feet anchored at the support plane.
                bounds = []
                for i, v in enumerate(point):
                    lo, hi = sorted((v, v + 1.8 * normal[i])) if i == axis else (v - .3, v + .3)
                    bounds.append(range(math.floor(lo + 1e-6), math.floor(hi - 1e-6) + 1))
                for x in bounds[0]:
                    for y in bounds[1]:
                        for z in bounds[2]:
                            self.assertIn(self.world.block(x, y, z)['Name'], self.clear)
                self.assertTrue(in_region(self.predicate, point))

    def test_all_six_exterior_faces_have_spaced_spawns_and_routes_away(self):
        self.assertEqual(Counter(r['face'] for r in self.contacts),
                         {'top': 6, 'bottom': 6, 'west': 5, 'east': 5, 'north': 5, 'south': 5})
        for face, axis, sign, scan, tangents, _ in FACES:
            nodes = face_surface(self.world, axis, sign, scan, tangents)
            connected = largest_surface(self.world, nodes, axis, sign)
            self.assertGreater(len(connected), 150, face)
            for contact in self.contacts:
                if contact['face'] != face:
                    continue
                point = tuple(contact['support'])
                self.assertIn(point, connected, face)
                self.assertGreaterEqual(len(list(neighbours(self.world, point, connected, axis, sign))), 3)
        for i, point in enumerate(self.spawns):
            for other in self.spawns[i + 1:]:
                self.assertGreaterEqual(math.dist(point, other), 5)

    def test_player_and_scrap_use_the_selected_marker_gravity(self):
        spawn = self.text('spawn')
        self.assertIn('tag=!Occupied', spawn)
        gravity = spawn.index('arena_spawn_gravity ')
        teleport = spawn.index('tp @s ')
        self.assertLess(gravity, teleport, 'Apply gravity before teleport to avoid destination displacement')
        self.assertIn('tag=CubeBlockRuntime', spawn)
        self.assertIn('add Occupied', spawn)
        shared = self.functions['data/mcm/function/maps/tptospawn.mcfunction']
        self.assertIn('if score $selectedMap CmdData matches 23 run return run function cube_block:spawn', shared)
        scrap = self.functions['data/mcm/function/extensions/gravity/spawn_scrap.mcfunction']
        self.assertIn('gravity bridge marker @s @e[type=item,tag=McmNewScrap]', scrap)

    def test_outer_edges_vertical_limits_and_neighbouring_arenas(self):
        # The margin covers the cube's four faces, underside and grappler arcs.
        inside = (49200, 75, 49202)
        for axis, low, high in ((0, 49164, 49246), (1, 26, 126), (2, 49152, 49262)):
            for edge, direction in ((low, -1), (high, 1)):
                point = list(inside)
                point[axis] = edge
                self.assertTrue(in_region(self.predicate, point))
                point[axis] = edge + direction * .001
                self.assertFalse(in_region(self.predicate, point))
        for point in ((45080, 90, 45080), (24550, 64, 24550), (49200, 0, 49202)):
            self.assertFalse(in_region(self.predicate, point))
        target = re.search(r'tp @s ([\d.]+) ([\d.]+) ([\d.]+)', self.text('return_to_arena'))
        self.assertIn(list(map(float, target.groups())), self.spawns)

    def test_round_and_hook_cleanup_are_arena_and_live_player_scoped(self):
        tick = self.text('functionality')
        self.assertIn('$selectedMap CmdData matches 23', tick)
        self.assertIn('$gamestate CmdData matches 1', tick)
        self.assertIn('@a[tag=queued,tag=!spectating,gamemode=!spectator]', tick)
        self.assertIn('unless score @s dead matches 1.. unless predicate cube_block:arena', tick)
        self.assertIn('function cube_block:give_hook', self.text('start'))
        self.assertIn('gravity_changer:grappling_hook', self.text('give_hook'))
        self.assertIn('NoDrop:1b,no_drop_on_death:1b', self.text('give_hook'))
        self.assertIn('on origin if entity @s[type=player,tag=CubeBlockHookCleaning]', self.text('cleanup_player'))
        self.assertIn('schedule clear cube_block:activate', self.text('reset'))
        self.assertIn('kill @e[tag=CubeBlockRuntime]', self.text('reset'))
        self.assertIn('return run function cube_block:return_to_arena', self.text('fall'))
        self.assertIn('function mcm:game/playerdeath', self.text('fall'))

    def test_import_has_no_commands_and_spawners_cannot_emit_survival_mobs(self):
        count = 0
        for cx in range(3072, 3079):
            for cz in range(3072, 3079):
                chunk = self.world.chunk(cx, cz)
                self.assertEqual(chunk['DataVersion'], 4189)
                for entity in chunk.get('block_entities', []):
                    self.assertFalse(entity.get('Command'))
                    self.assertFalse(entity.get('Items'))
                    self.assertNotIn('LootTable', entity)
                    if entity['id'] == 'minecraft:mob_spawner':
                        self.assertEqual(entity['SpawnCount'], 0)
                        self.assertEqual(entity['RequiredPlayerRange'], 0)
                    count += 1
        self.assertEqual(count, len(self.manifest['block_entities']))

    def test_water_has_sealed_cut_faces_and_no_exterior_falling_columns(self):
        # The survival source had unsupported water on three cut faces. Merely
        # clearing fluid_ticks would only hide it until a neighbour update.
        low, high = (49181, 47, 49196), (49220, 86, 49235)
        def inside(p):
            return all(a <= v <= b for v, a, b in zip(p, low, high))

        water, seals = 0, set()
        for cx in range(3072, 3079):
            for cz in range(3072, 3079):
                for section in self.world.chunk(cx, cz).get('sections', []):
                    if not any(s['Name'] == 'minecraft:water' for s in
                               section.get('block_states', {}).get('palette', [])):
                        continue
                    for i in range(4096):
                        p = cx * 16 + i % 16, section['Y'] * 16 + i // 256, cz * 16 + i // 16 % 16
                        if self.world.block(*p)['Name'] != 'minecraft:water':
                            continue
                        water += 1
                        self.assertTrue(inside(p), f'Exterior waterfall: {p}')
                        for delta in ((-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 0, -1), (0, 0, 1)):
                            q = tuple(a + b for a, b in zip(p, delta))
                            if not inside(q):
                                name = self.world.block(*q)['Name']
                                self.assertIn(name, {'minecraft:barrier', 'minecraft:oak_planks',
                                                     'minecraft:spruce_planks'}, q)
                                if name == 'minecraft:barrier':
                                    seals.add(q)
        self.assertGreater(water, 2500, 'Keep the pool and interior water')
        self.assertEqual(len(seals), 857)
        self.assertEqual(self.world.block(49183, 86, 49235)['Name'], 'minecraft:water')
        self.assertEqual(self.world.block(49183, 86, 49236)['Name'], 'minecraft:barrier')
        self.assertEqual(self.world.block(49183, 85, 49236)['Name'], 'minecraft:barrier')
        self.assertEqual(self.world.block(49183, -64, 49236)['Name'], 'minecraft:air')


if __name__ == '__main__':
    unittest.main()
