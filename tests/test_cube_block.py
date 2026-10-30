"""Cube Block spawns and escape limits against the imported destination chunks."""
from collections import deque
import json
from pathlib import Path
import re
import unittest
from zipfile import ZipFile

from world_geometry import World, in_region

ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'


class CubeBlockIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / 'docs/arenas/cube_block.json').read_text())
        cls.world = World(WORLD)
        with ZipFile(WORLD / 'datapacks/mcm.zip') as z:
            cls.functions = {name: z.read(name).decode() for name in z.namelist()
                             if name.startswith('data/cube_block/')}
        cls.predicate = json.loads(cls.functions['data/cube_block/predicate/arena.json'])
        cls.spawns = cls.manifest['player_spawns']
        cls.clear = set(cls.manifest['spawn_validation']['clear_blocks'])
        cls.support = set(cls.manifest['spawn_validation']['support_blocks'])

    def text(self, name):
        return self.functions[f'data/cube_block/function/{name}.mcfunction']

    def test_all_actual_spawns_have_full_support_clear_collision_and_region_membership(self):
        self.assertEqual(len(self.spawns), 32)
        self.assertEqual(len(self.spawns), len(set(map(tuple, self.spawns))))
        actual = [tuple(map(float, m)) for m in re.findall(
            r'summon marker ([\d.]+) ([\d.]+) ([\d.]+) \{Tags:\["PlayerSpawn"', self.text('activate'))]
        self.assertEqual(actual, list(map(tuple, self.spawns)))
        for point in self.spawns:
            with self.subTest(point=point):
                x, y, z = map(int, point)
                # All selected supports are full cubes. Partial snow, slabs,
                # stairs, tree canopy, liquids and closed doors are excluded.
                self.assertIn(self.world.block(x, y - 1, z)['Name'], self.support)
                self.assertIn(self.world.block(x, y, z)['Name'], self.clear)
                self.assertIn(self.world.block(x, y + 1, z)['Name'], self.clear)
                self.assertGreaterEqual(y, 86)
                self.assertTrue(in_region(self.predicate, point))

    def test_spawns_share_the_connected_top_ground_with_routes_away(self):
        nodes = set()
        for x in range(49176, 49234):
            for z in range(49164, 49250):
                for y in range(86, 100):
                    if (self.world.block(x, y - 1, z)['Name'] in self.support
                            and self.world.block(x, y, z)['Name'] in self.clear
                            and self.world.block(x, y + 1, z)['Name'] in self.clear):
                        nodes.add((x, y, z))

        def adjacent(p):
            x, y, z = p
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy, z + dz)
                    if q not in nodes:
                        continue
                    if dy > 0 and self.world.block(x, y + 2, z)['Name'] not in self.clear:
                        continue
                    if dy < 0 and self.world.block(q[0], y + 1, q[2])['Name'] not in self.clear:
                        continue
                    yield q

        points = [tuple(map(int, p)) for p in self.spawns]
        seen, pending = {points[0]}, deque([points[0]])
        while pending:
            for q in adjacent(pending.popleft()):
                if q not in seen:
                    seen.add(q)
                    pending.append(q)
        self.assertGreater(len(seen), 1200)
        self.assertTrue(set(points) <= seen)
        for point in points:
            self.assertGreaterEqual(len(list(adjacent(point))), 3, point)

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
