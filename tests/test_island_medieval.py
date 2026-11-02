"""Verify both new arenas against their actual saved geometry and live predicates."""
from collections import defaultdict, deque
import json
import math
from pathlib import Path
import re
import unittest
from zipfile import ZipFile

from world_geometry import World, in_region

ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'


class IslandMedievalGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = World(WORLD)
        cls.shapes = json.loads((ROOT / 'docs/arenas/island-medieval-collision-shapes.json').read_text())['shapes']
        cls.reports = {ns: json.loads((ROOT / f'docs/arenas/{ns}.json').read_text())
                       for ns in ['sworld_island', 'middle_ages']}
        with ZipFile(WORLD / 'datapacks/mcm.zip') as archive:
            cls.files = {name: archive.read(name) for name in archive.namelist()}

    def block_shapes(self, x, y, z):
        state = self.world.block(x, y, z)
        if state['Name'] in ['minecraft:air', 'minecraft:cave_air', 'minecraft:void_air']:
            return []
        key = state['Name'] + '[' + ','.join(f'{k}={v}' for k, v in sorted(state.get('Properties', {}).items())) + ']'
        if key not in self.shapes:
            self.fail(f'Unreviewed block state at {(x, y, z)}: {key}')
        return self.shapes[key]

    def clear_player(self, x, y, z):
        # Editor spawns can have fractional coordinates and straddle block columns.
        for bx in range(math.floor(x - .3 + 1e-5), math.floor(x + .3 - 1e-5) + 1):
            for bz in range(math.floor(z - .3 + 1e-5), math.floor(z + .3 - 1e-5) + 1):
                for by in range(math.floor(y), math.floor(y + 1.8 - 1e-5) + 1):
                    state = self.world.block(bx, by, bz)
                    self.assertNotIn(state['Name'], ['minecraft:water', 'minecraft:lava', 'minecraft:cobweb',
                                                    'minecraft:sweet_berry_bush', 'minecraft:fire', 'minecraft:campfire'])
                    for shape in self.block_shapes(bx, by, bz):
                        overlaps = (bx + shape[0] < x + .3 - 1e-5 and bx + shape[3] > x - .3 + 1e-5
                                    and bz + shape[2] < z + .3 - 1e-5 and bz + shape[5] > z - .3 + 1e-5
                                    and by + shape[1] < y + 1.8 - 1e-5 and by + shape[4] > y + 1e-5)
                        self.assertFalse(overlaps, f'Player collision at {(x, y, z)} with {(bx, by, bz, shape)}')

    def spawn_commands(self, ns):
        text = self.files[f'data/{ns}/function/activate.mcfunction'].decode()
        if f'function bbe_arena:{ns}/spawns' in text:
            text = self.files[f'data/bbe_arena/function/{ns}/spawns.mcfunction'].decode()
        return [match for match in re.findall(
            r'^summon (?:minecraft:)?marker ([\d.-]+) ([\d.-]+) ([\d.-]+) (.*)$', text, re.MULTILINE)
            if '"PlayerSpawn"' in match[3]]

    def spawns(self, ns):
        return [tuple(map(float, command[:3])) for command in self.spawn_commands(ns)]

    def predicate(self, ns):
        return json.loads(self.files[f'data/{ns}/predicate/arena.json'])

    def test_all_64_spawns_have_full_support_and_clear_player_aabb(self):
        for ns, report in self.reports.items():
            with self.subTest(arena=ns):
                points = self.spawns(ns)
                self.assertEqual(len(points), 32)
                self.assertEqual(len({tuple(p) for p in points}), 32)
                for x, y, z in points:
                    self.assertEqual(y, int(y))
                    for bx in range(math.floor(x - .3), math.floor(x + .3) + 1):
                        for bz in range(math.floor(z - .3), math.floor(z + .3) + 1):
                            self.assertIn([0, 0, 0, 1, 1, 1], self.block_shapes(bx, int(y) - 1, bz))
                    self.clear_player(x, y, z)
                    self.assertTrue(in_region(self.predicate(ns), [x, y, z]))
                    self.assertEqual(self.world.chunk(math.floor(x) // 16, math.floor(z) // 16)['DataVersion'], 4189)

    def test_every_spawn_has_a_connected_walkable_route_in_saved_blocks(self):
        for ns, report in self.reports.items():
            with self.subTest(arena=ns):
                routes = {tuple(p) for p in report['validated_routes']}
                spawn_cells = {(math.floor(x), y, math.floor(z)) for x, y, z in self.spawns(ns)}
                routes.update(spawn_cells)
                by_column = defaultdict(list)
                for x, y, z in routes:
                    by_column[x, z].append((x, y, z))
                seed = min(spawn_cells)
                parents, todo = {seed: None}, deque([seed])
                while todo:
                    x, y, z = todo.popleft()
                    for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        for other in by_column[x + dx, z + dz]:
                            if abs(y - other[1]) <= 1.001 and other not in parents:
                                parents[other] = (x, y, z)
                                todo.append(other)
                self.assertTrue(spawn_cells <= parents.keys())
                # Editor moves can leave unused historical endpoints inside new
                # decorations. Validate the paths joining the current spawns.
                paths = set()
                for point in spawn_cells:
                    while point is not None and point not in paths:
                        paths.add(point)
                        point = parents[point]
                for x, y, z in paths:
                    self.clear_player(x + .5, y, z + .5)
                    self.assertTrue(any(abs(by + shape[4] - y) < 1e-4
                                        and shape[0] < .8 and shape[3] > .2
                                        and shape[2] < .8 and shape[5] > .2
                                        for by in range(math.floor(y) - 2, math.floor(y) + 1)
                                        for shape in self.block_shapes(x, by, z)), f'Unsupported route: {(x, y, z)}')
                    self.assertTrue(in_region(self.predicate(ns), [x + .5, y, z + .5]))
                    other = parents[x, y, z]
                    if other is not None:
                        self.clear_player(x + .5, max(y, other[1]), z + .5)
                        self.clear_player(other[0] + .5, max(y, other[1]), other[2] + .5)

    def test_real_ocean_stream_and_void_positions(self):
        self.assertEqual(self.world.block(40870, 62, 40970)['Name'], 'minecraft:water')
        self.assertEqual(self.world.block(40870, 66, 40970)['Name'], 'minecraft:air')
        self.assertEqual(self.world.block(40950, 70, 40943)['Name'], 'minecraft:water')
        contact = json.loads(self.files['data/sworld_island/predicate/ocean_contact.json'])['predicate']
        self.assertEqual(contact['position']['y']['max'], 63)
        self.assertEqual(contact['fluid']['fluids'], 'minecraft:water')
        vehicle = json.loads(self.files['data/sworld_island/predicate/vehicle_in_ocean.json'])['predicate']['vehicle']['location']
        self.assertEqual(vehicle['fluid']['fluids'], 'minecraft:water')
        self.assertEqual(vehicle['position']['y']['max'], 63)
        self.assertTrue(in_region(self.predicate('sworld_island'), [40870.5, 66, 40970.5]))
        self.assertTrue(in_region(self.predicate('sworld_island'), [40950.5, 70, 40943.5]))
        self.assertEqual(self.world.block(45056, 89, 45056)['Name'], 'minecraft:air')
        self.assertFalse(in_region(self.predicate('middle_ages'), [45056.5, 89, 45056.5]))
        for ns, report in self.reports.items():
            low, high = report['arena'][:3], report['arena'][3:]
            center = [(a + b) / 2 for a, b in zip(low, high)]
            for axis in range(3):
                for boundary in [low[axis] - .01, high[axis] + .01]:
                    point = center.copy()
                    point[axis] = boundary
                    self.assertFalse(in_region(self.predicate(ns), point))

    def test_scoped_lifecycle_uses_final_spawn_geometry_and_waiting_rescue(self):
        for ns, report in self.reports.items():
            text = self.files[f'data/{ns}/function/activate.mcfunction'].decode()
            commands = self.spawn_commands(ns)
            self.assertEqual(len(commands), 32)
            self.assertIn('kill @e[tag=MapEntity]', text)
            for *_, tags in commands:
                self.assertIn('"ScrapSpawn"', tags)
                self.assertIn('"MapEntity"', tags)
                self.assertIn(f'"{report["tag"]}Runtime"', tags)
            functionality = self.files[f'data/{ns}/function/functionality.mcfunction'].decode()
            self.assertIn(f'$selectedMap CmdData matches {report["map_id"]}', functionality)
            self.assertIn('$gamestate CmdData matches 1', functionality)
            self.assertIn('tag=queued,tag=!spectating,gamemode=!spectator', functionality)
            self.assertIn('unless score @s dead matches 1..', functionality)
            escape = self.files[f'data/{ns}/function/escape.mcfunction'].decode()
            self.assertIn('unless score $gamestate CmdData matches 1', escape)
            self.assertIn('if score $graceperiod CmdData matches 1..', escape)
            waiting = self.files[f'data/{ns}/function/waiting_tick.mcfunction'].decode()
            self.assertIn(f'tag={report["tag"]}Participant', waiting)
            reset = self.files[f'data/{ns}/function/reset.mcfunction'].decode()
            self.assertIn(f'kill @e[tag={report["tag"]}Runtime]', reset)
            for line in reset.splitlines():
                if line.startswith('forceload remove '):
                    self.assertEqual(len(line.split()), 6)
                    for arg in line.split()[2:]:
                        int(arg)
