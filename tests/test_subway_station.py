"""Check destination blocks, collision shapes, routes, and the live predicate."""

from collections import deque
from functools import lru_cache
import json
import math
from pathlib import Path
import re
import unittest
import zipfile

from test_yacht_spawns import WorldBlocks, WORLD
from subway_station_carriages import links, patch_datapack


ROOT = Path(__file__).resolve().parent.parent
SHAPES = json.loads((ROOT / 'tests/fixtures/subway_station_collision_shapes.json').read_text())['states']
REPORT = json.loads((ROOT / 'docs/arenas/subway_station.json').read_text())


class StationBlocks(WorldBlocks):
    @lru_cache(None)
    def state(self, x, y, z):
        states = self.chunk(x // 16, z // 16).get(y // 16, {})
        palette = states.get('palette', [{'Name': 'minecraft:air'}])
        index = 0
        if len(palette) > 1:
            bits = max(4, (len(palette) - 1).bit_length())
            count = 64 // bits
            position = (y % 16) * 256 + (z % 16) * 16 + x % 16
            index = (states['data'][position // count] >> ((position % count) * bits)) & ((1 << bits) - 1)
        return palette[index]

    @lru_cache(None)
    def shapes(self, x, y, z):
        state = self.state(x, y, z)
        key = state['Name'] + '[' + ','.join(f'{k}={v}' for k, v in sorted(state.get('Properties', {}).items())) + ']'
        return SHAPES[key]  # Unknown states fail instead of assuming passability.

    def clear(self, x, y, z, radius=.3, height=1.8):
        lo, hi = (x-radius, y+.00001, z-radius), (x+radius, y+height-.00001, z+radius)
        # Include walls/fences that project above their own voxel.
        for bx in range(math.floor(lo[0]), math.floor(hi[0])+1):
            for by in range(math.floor(lo[1])-1, math.floor(hi[1])+1):
                for bz in range(math.floor(lo[2]), math.floor(hi[2])+1):
                    for shape in self.shapes(bx, by, bz):
                        offset = bx, by, bz
                        if all(lo[a] < shape[a+3]+offset[a]-1e-7 and hi[a] > shape[a]+offset[a]+1e-7 for a in range(3)):
                            return False
        return True


def inside(predicate, point, dimension='minecraft:overworld'):
    if predicate['condition'] == 'minecraft:any_of':
        return any(inside(term, point, dimension) for term in predicate['terms'])
    location = predicate['predicate']
    return location['dimension'] == dimension and all(
        location['position'][axis]['min'] <= value <= location['position'][axis]['max']
        for axis, value in zip('xyz', point))


class SubwayStationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(WORLD / 'datapacks/mcm.zip') as archive:
            cls.files = {n: archive.read(n).decode() for n in archive.namelist() if n.endswith(('.mcfunction', '.json'))}
        cls.activate = cls.files['data/subway_station/function/activate.mcfunction']
        cls.predicate = json.loads(cls.files['data/subway_station/predicate/arena.json'])
        cls.spawns = [tuple(map(float, m)) for m in re.findall(r'^summon marker ([-\d.]+) ([-\d.]+) ([-\d.]+).*"PlayerSpawn"', cls.activate, re.M)]
        cls.blocks = StationBlocks()

    def test_spawn_collision_support_platform_membership_and_escape_routes(self):
        self.assertEqual(len(self.spawns), 24)
        self.assertEqual(len(set(self.spawns)), 24)
        self.assertEqual(self.spawns, list(map(tuple, REPORT['destination_player_spawns'])))
        for spawn in self.spawns + [tuple(REPORT['return_position'])]:
            with self.subTest(spawn=spawn):
                x, y, z = spawn
                bx, by, bz = map(math.floor, spawn)
                self.assertTrue(inside(self.predicate, spawn))
                self.assertTrue(self.blocks.clear(*spawn), 'Player collision volume intersects the saved station')
                self.assertEqual(self.blocks.shapes(bx, by-1, bz), [[0, 0, 0, 1, 1, 1]])
                self.assertIn(self.blocks.block(bx, by-1, bz), {'granite', 'polished_granite', 'bricks', 'coarse_dirt'})
                # Main platforms, not track tunnels, exterior base, train roof or caves.
                self.assertEqual(y, -58)
                self.assertTrue(14 < x-20480 < 31)
                self.assertTrue(20356 < z < 20556)
                exits = sum(self.blocks.clear(x+dx, y, z+dz) and
                            self.blocks.shapes(bx+dx, by-1, bz+dz) == [[0, 0, 0, 1, 1, 1]]
                            for dx, dz in ((1,0),(-1,0),(0,1),(0,-1)))
                self.assertGreaterEqual(exits, 2, 'Spawn cannot leave decoration safely')

    def test_all_spawns_share_the_connected_central_platform(self):
        # Conservative 0.6 x 1.8 player clearance on the saved flat platform.
        # Closed/reset doors are obstacles; no spawn depends on opening one.
        for xmin, xmax in ((20495, 20510),):
            starts = [(math.floor(x), math.floor(z)) for x, y, z in self.spawns if xmin <= x <= xmax+1]
            self.assertEqual(len(starts), 24)

            @lru_cache(None)
            def walkable(x, z):
                return (xmin <= x <= xmax and 20357 <= z <= 20555 and
                        self.blocks.shapes(x, -59, z) == [[0, 0, 0, 1, 1, 1]] and
                        self.blocks.clear(x+.5, -58, z+.5))

            seen, pending = {starts[0]}, deque([starts[0]])
            while pending:
                x, z = pending.popleft()
                for dx, dz in ((1,0),(-1,0),(0,1),(0,-1)):
                    q = x+dx, z+dz
                    if q not in seen and walkable(*q):
                        seen.add(q)
                        pending.append(q)
            self.assertTrue(set(starts) <= seen, f'Disconnected spawns on platform {xmin}: {set(starts)-seen}')
            self.assertGreater(len(seen), 700)

    def test_recorded_station_footprint_excludes_tunnels_exterior_and_wrong_dimension(self):
        for point in ((20502.5,-58,20356.4), (20502.5,-58,20555.6),
                      (20470.4,-58,20400), (20535.6,-58,20400), (20502.5,-29,20400)):
            self.assertTrue(inside(self.predicate, point), point)
        for point in ((20502.5,-58,20356.2), (20502.5,-58,20555.8),
                      (20470.2,-58,20400), (20535.8,-58,20400),
                      (20487,-59,20280), (20519,-59,20630),
                      (20502.5,-59.1,20400), (20502.5,-27.9,20400),
                      (20471,-29,20400), (20535,-29,20400), (20465,-58,20400)):
            self.assertFalse(inside(self.predicate, point), point)
        self.assertFalse(inside(self.predicate, self.spawns[0], 'minecraft:the_nether'))
        for term in self.predicate['terms']:
            axes = term['predicate']['position']
            middle = [(axes[a]['min']+axes[a]['max'])/2 for a in 'xyz']
            for index, axis in enumerate('xyz'):
                for edge in ('min', 'max'):
                    point = middle.copy()
                    point[index] = axes[axis][edge]
                    self.assertTrue(inside(term, point))
                    point[index] += -.001 if edge == 'min' else .001
                    self.assertFalse(inside(term, point))

    def test_tick_lifecycle_registration_and_cleanup(self):
        prefix = 'data/subway_station/function/'
        tick = self.files[prefix+'functionality.mcfunction']
        self.assertNotIn('tp ', tick)
        self.assertNotIn('return_player', tick)
        self.assertNotIn(prefix+'return_player.mcfunction', self.files)
        self.assertFalse(any('unless predicate subway_station:arena' in text for text in self.files.values()))
        self.assertIn('function subway_station:functionality', self.files['data/mcm/function/game/loops/ingame.mcfunction'])
        reset = self.files[prefix+'reset.mcfunction']
        self.assertIn('schedule clear subway_station:activate', reset)
        self.assertIn('kill @e[tag=SubwayStationRuntime]', reset)
        self.assertTrue(self.activate.startswith('kill @e[tag=MapEntity]'))
        self.assertIn('function subway_station:carriages/spawn', self.activate)
        for path in ('maps/reset', 'load'):
            self.assertIn('forceload remove 20464 20256 20543 20655', self.files[f'data/mcm/function/{path}.mcfunction'])
        self.assertIn('schedule function subway_station:activate 1s replace', self.files['data/mcm/function/lobby/voting/end.mcfunction'])

    def test_carriage_links_are_bidirectional_adjacent_and_land_on_actual_train_floors(self):
        routes = list(links())
        self.assertEqual(len(routes), 40)
        self.assertEqual(json.loads((ROOT / 'docs/arenas/subway_station_carriages.json').read_text()), routes)
        directed = {(r['train'], r['carriage'], r['target_carriage']) for r in routes}
        self.assertEqual(len(directed), 40)
        for route in routes:
            with self.subTest(link=route['id']):
                self.assertEqual(abs(route['target_carriage']-route['carriage']), 1)
                self.assertIn((route['train'], route['target_carriage'], route['carriage']), directed)
                x, y, z = route['destination']
                self.assertTrue(self.blocks.clear(x, y, z), 'Destination intersects the saved train')
                bx, by, bz = map(math.floor, (x, y, z))
                self.assertEqual(self.blocks.block(bx, by, bz), 'iron_trapdoor')
                self.assertTrue(any(abs(shape[4]+by-y) < 1e-6 for shape in self.blocks.shapes(bx, by, bz)))
                # The destination must also allow a step down the carriage aisle.
                step = -1 if route['direction'] == 'previous' else 1
                self.assertTrue(self.blocks.clear(x, y, z+step))

    def test_clicks_target_the_actual_player_and_are_scoped_to_local_live_participants(self):
        spawn = self.files['data/subway_station/function/carriages/spawn.mcfunction']
        self.assertEqual(spawn.count('summon text_display '), 40)
        self.assertEqual(spawn.count('summon interaction '), 40)
        self.assertEqual(spawn.count('SubwayStationRuntime'), 80)
        self.assertTrue(spawn.splitlines()[1].startswith('kill @e[tag=SubwayStationCarriageLink]'))
        for route in links():
            name = route['id']
            advancement = json.loads(self.files[f'data/subway_station/advancement/carriages/{name}.json'])
            self.assertEqual(advancement['criteria']['use']['trigger'], 'minecraft:player_interacted_with_entity')
            self.assertIn('SubwayStationLink_'+name, advancement['criteria']['use']['conditions']['entity']['nbt'])
            self.assertEqual(advancement['rewards']['function'], f'subway_station:carriages/{name}')
            function = self.files[f'data/subway_station/function/carriages/{name}.mcfunction']
            self.assertIn(f'advancement revoke @s only subway_station:carriages/{name}', function)
            for guard in ('$selectedMap CmdData matches 16', '$gamestate CmdData matches 0..1',
                          'dimension minecraft:overworld', 'tag=queued,tag=!spectating,gamemode=!spectator',
                          'if score @s dead matches 1..', 'distance=..4.5'):
                self.assertIn(guard, function)
            self.assertEqual(function.count('run tp @s '), 1)
            self.assertNotIn('tp @p', function)
        load = self.files['data/mcm/function/load.mcfunction']
        self.assertLess(load.index('run function subway_station:carriages/spawn'),
                        load.index('execute unless score $gamestate CmdData matches ..0 run return 1'))

    def test_patching_is_idempotent_and_preserves_other_maps_and_spawn_points(self):
        files = {path: text.encode() for path, text in self.files.items()}
        original = files.copy()
        patch_datapack(files)
        once = files.copy()
        patch_datapack(files)
        self.assertEqual(files, once)
        for path in original:
            if not path.startswith('data/subway_station/') and path != 'data/mcm/function/load.mcfunction':
                self.assertEqual(files[path], original[path], path)
        self.assertEqual(files['data/subway_station/function/activate.mcfunction'],
                         original['data/subway_station/function/activate.mcfunction'])

    def test_voting_poster_is_created_after_cleanup_and_in_front_of_booth(self):
        commands = self.files['data/mcm/function/lobby/voting/set_maps.mcfunction']
        self.assertLess(commands.index('kill @e[tag=SubwayStationPoster]'), commands.index('run function mcm:lobby/voting/map_position_id'))
        poster = self.files['data/mcm/function/lobby/voting/map_position_id.mcfunction']
        stations = [line for line in poster.splitlines() if line.startswith('execute if score @s MapValues matches 16 ')]
        self.assertEqual(len(stations), 1)
        station = stations[0]
        self.assertIn('positioned ~-0.01 ~1 ~1', station)
        self.assertIn('subway_station:posters/subway_station', station)
        # The backing block is X=28; the flat north-facing model rotated by 90
        # degrees must sit at X=27.99, outside the block's western face.
        self.assertEqual(self.blocks.block(28, 3, 90), 'light_gray_terracotta')
        self.assertEqual(self.blocks.block(27, 3, 90), 'air')

    def test_downloaded_commands_cannot_take_control(self):
        # Decode actual destination command-block entities, not the preview NBT.
        import struct
        import zlib
        from nbt import Reader
        from test_yacht_spawns import payload
        commands = []
        for path in (WORLD / 'region').glob('r.*.mca'):
            if path.name not in {'r.39.39.mca', 'r.39.40.mca', 'r.40.39.mca', 'r.40.40.mca'}:
                continue
            data = path.read_bytes()
            for slot in range(1024):
                offset = int.from_bytes(data[slot*4:slot*4+3], 'big')*4096
                if not offset:
                    continue
                size = struct.unpack_from('>I', data, offset)[0]
                reader = Reader(zlib.decompress(data[offset+5:offset+4+size]))
                self.assertEqual(reader.number('B'), 10)
                reader.string()
                chunk = payload(reader, 10)
                for tile in chunk.get('block_entities', []):
                    if tile['id'] == 'minecraft:command_block':
                        commands.append(tile)
        self.assertEqual(len(commands), 22)
        for tile in commands:
            self.assertEqual(tile['Command'], '')
            self.assertEqual(tile['auto'], 0)


if __name__ == '__main__':
    unittest.main()
