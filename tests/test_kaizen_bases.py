"""Check the installed bases, actual collision states, containment and lifecycle."""
from collections import deque
from functools import lru_cache
import json
import math
from pathlib import Path
import re
import unittest
import zipfile

from test_subway_station import StationBlocks, inside
from test_yacht_spawns import WORLD

ROOT = Path(__file__).resolve().parent.parent
NAMES = ('meridian_base', 'bagger_288', 'underwater_base')
SHAPES = json.loads((ROOT / 'tests/fixtures/kaizen_collision_shapes.json').read_text())['states']


class BaseBlocks(StationBlocks):
    @lru_cache(None)
    def shapes(self, x, y, z):
        state = self.state(x, y, z)
        key = state['Name'] + '[' + ','.join(f'{k}={v}' for k, v in sorted(state.get('Properties', {}).items())) + ']'
        return SHAPES[key]


class KaizenBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blocks = BaseBlocks()
        cls.reports = {ns: json.loads((ROOT / f'docs/arenas/{ns}.json').read_text()) for ns in NAMES}
        with zipfile.ZipFile(WORLD / 'datapacks/mcm.zip') as z:
            cls.files = {n: z.read(n).decode() for n in z.namelist() if n.endswith(('.json', '.mcfunction', '.txt'))}

    def test_all_72_actual_spawn_volumes_support_and_local_routes(self):
        for ns, report in self.reports.items():
            predicate = json.loads(self.files[f'data/{ns}/predicate/arena.json'])
            activation = self.files[f'data/{ns}/function/activate.mcfunction']
            actual = [list(map(float, m)) for m in re.findall(r'^summon marker ([-\d.]+) ([-\d.]+) ([-\d.]+).*"PlayerSpawn"', activation, re.M)]
            self.assertEqual(actual, report['destination_player_spawns'])
            self.assertEqual(len(actual), 24)
            self.assertEqual(len(set(map(tuple, actual))), 24)
            for spawn in actual + [report['return_position']]:
                with self.subTest(arena=ns, spawn=spawn):
                    x, y, z = spawn
                    bx, by, bz = math.floor(x), math.floor(y-.00001), math.floor(z)
                    self.assertTrue(inside(predicate, spawn))
                    self.assertTrue(self.blocks.clear(*spawn), 'Actual saved collision volume is obstructed')
                    # Full player-footprint support at the exact fractional height.
                    self.assertTrue(any(s[0] <= .2 and s[2] <= .2 and s[3] >= .8 and s[5] >= .8 and
                                        abs(by+s[4]-y) < .00001 for s in self.blocks.shapes(bx, by, bz)))
                    for yy in range(by, math.floor(y+1.8)+1):
                        state = self.blocks.state(bx, yy, bz)
                        self.assertNotIn(state['Name'].split(':')[1], {'water', 'lava', 'fire', 'soul_fire', 'magma_block', 'cactus', 'powder_snow', 'sweet_berry_bush'})
                        self.assertNotEqual(state.get('Properties', {}).get('waterlogged'), 'true')
            for route in report['spawn_exit_checks']:
                self.assertGreaterEqual(len(route['exits']), 2)
                x, y, z = route['spawn']
                for qx, qy, qz in route['exits']:
                    self.assertEqual(qy, y)
                    self.assertEqual(abs(qx-x)+abs(qz-z), 1)
                    self.assertTrue(self.blocks.clear(qx, qy, qz))
                    self.assertTrue(self.blocks.clear((x+qx)/2, y, (z+qz)/2))

    def test_spawn_supports_belong_to_the_connected_build_not_surrounding_terrain(self):
        excluded = {'air', 'cave_air', 'void_air', 'water', 'lava', 'barrier', 'light', 'structure_void'}
        for ns, report in self.reports.items():
            omit = set(excluded)
            if ns == 'underwater_base':
                omit |= {'sand', 'sandstone', 'gravel', 'stone', 'dirt', 'clay', 'granite', 'diorite', 'andesite',
                         'seagrass', 'tall_seagrass', 'kelp', 'kelp_plant', 'sea_pickle', 'magma_block', 'mud', 'suspicious_sand'}
            offset = report['translation']
            lower = [report['build_min'][a]+offset[a] for a in range(3)]
            upper = [report['build_max'][a]+offset[a] for a in range(3)]
            supports = {(math.floor(x), math.floor(y-.00001), math.floor(z)) for x, y, z in report['destination_player_spawns']}
            seed = next(iter(supports))
            pending, seen = deque([seed]), {seed}
            while pending:
                x, y, z = pending.popleft()
                for dx, dy, dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
                    p = x+dx, y+dy, z+dz
                    if p in seen or not all(lower[a] <= p[a] <= upper[a] for a in range(3)):
                        continue
                    name = self.blocks.block(*p)
                    if name in omit or (ns == 'underwater_base' and ('coral' in name or name.endswith('_ore'))):
                        continue
                    seen.add(p)
                    pending.append(p)
            self.assertTrue(supports <= seen, (ns, supports-seen))
            self.assertGreater(len(seen), 10000)

    def test_region_masks_exclude_ground_ocean_exterior_and_other_dimensions(self):
        for ns, report in self.reports.items():
            predicate = json.loads(self.files[f'data/{ns}/predicate/arena.json'])
            self.assertEqual([t['predicate']['position'] for t in predicate['terms']], report['boundary_boxes'])
            self.assertGreater(len(predicate['terms']), 20)
            dx, _, dz = report['translation']
            outside = ((0,-34,0), (0,-53,40), (-5440,38,5873), (500,100,500))
            for p in outside:
                self.assertFalse(inside(predicate, [p[0]+dx, p[1], p[2]+dz]), (ns, p))
            self.assertFalse(inside(predicate, report['return_position'], 'minecraft:the_nether'))
            self.assertFalse(inside(predicate, report['return_position'], 'minecraft:the_end'))
            for term in predicate['terms']:
                axes = term['predicate']['position']
                centre = [(axes[a]['min']+axes[a]['max'])/2 for a in 'xyz']
                for index, axis in enumerate('xyz'):
                    for edge, step in [('min', -.001), ('max', .001)]:
                        p = centre.copy()
                        p[index] = axes[axis][edge]
                        self.assertTrue(inside(term, p))
                        p[index] += step
                        self.assertFalse(inside(term, p))

    def test_lifecycle_scopes_cleanup_waiting_reload_and_forceload_limits(self):
        for ns, report in self.reports.items():
            mid, tag = report['map_id'], report['tag']
            prefix = f'data/{ns}/function/'
            tick = self.files[prefix+'functionality.mcfunction']
            self.assertIn(f'$selectedMap CmdData matches {mid}', tick)
            self.assertIn('$gamestate CmdData matches 1', tick)
            self.assertIn('@a[tag=queued,tag=!spectating,gamemode=!spectator]', tick)
            self.assertIn('unless score @s dead matches 1..', tick)
            self.assertIn(f'unless predicate {ns}:arena', self.files[prefix+'check_player.mcfunction'])
            self.assertIn(f'if block ~ ~ ~ #{ns}:fluids', self.files[prefix+'check_player.mcfunction'])
            self.assertIn(f'#{ns}:waterloggable[waterlogged=true]', self.files[prefix+'check_player.mcfunction'])
            self.assertIn('minecraft:water', json.loads(self.files[f'data/{ns}/tags/block/fluids.json'])['values'])
            valid_blocks = {key.split('[')[0] for key in SHAPES}
            self.assertTrue(set(json.loads(self.files[f'data/{ns}/tags/block/waterloggable.json'])['values']) <= valid_blocks)
            waiting = self.files[prefix+'waiting_tick.mcfunction']
            self.assertIn(f'tag={tag}Participant', waiting)
            self.assertIn('$gamestate CmdData matches 0', waiting)
            reset = self.files[prefix+'reset.mcfunction']
            self.assertIn(f'schedule clear {ns}:activate', reset)
            self.assertIn(f'kill @e[tag={tag}Runtime]', reset)
            self.assertIn(f'tag @a remove {tag}Participant', reset)
            self.assertIn('kill @e[tag=MapEntity]', self.files[prefix+'activate.mcfunction'])
            for fn in ('maps/reset', 'load'):
                self.assertIn(f'function {ns}:reset', self.files[f'data/mcm/function/{fn}.mcfunction'])
            x0, z0, x1, z1 = report['forceload_bounds']
            self.assertLessEqual((x1//16-x0//16+1)*(z1//16-z0//16+1), 256)
            self.assertIn(f'schedule function {ns}:activate 1s replace', self.files['data/mcm/function/lobby/voting/end.mcfunction'])
            self.assertIn('execute unless entity', self.files[prefix+'register.mcfunction'])
            self.assertIn(f'MapValues {mid}', self.files[prefix+'register.mcfunction'])
            self.assertIn('KAIZEN87', self.files[f'data/{ns}/credits.txt'])

    def test_meridian_ocean_and_perimeter_eliminate_only_during_rounds(self):
        ocean = (24576.5, -34, 24576.5)
        self.assertEqual(self.blocks.state(*(math.floor(v) for v in ocean))['Name'], 'minecraft:water')
        self.assertFalse(inside(json.loads(self.files['data/meridian_base/predicate/arena.json']), ocean))
        check = self.files['data/meridian_base/function/check_player.mcfunction']
        # The ocean is outside the geometry mask; both paths must eliminate,
        # otherwise the perimeter check rescues a fall before the water check.
        self.assertEqual(check.count('function meridian_base:escape'), 5)
        self.assertNotIn('function meridian_base:return_player', check)
        escape = self.files['data/meridian_base/function/escape.mcfunction'].splitlines()
        self.assertEqual(escape, [
            'execute if score $gamestate CmdData matches 1 run return run function mcm:game/playerdeath',
            'function meridian_base:return_player',
        ])
        death = self.files['data/mcm/function/game/playerdeath.mcfunction']
        self.assertIn('scoreboard players set @s dead 1', death)
        self.assertIn('gamemode spectator @s', death)
        for ns in ('bagger_288', 'underwater_base'):
            self.assertEqual(self.files[f'data/{ns}/function/check_player.mcfunction']
                             .count(f'function {ns}:return_player'), 5)

    def test_authorized_compatibility_substitutions_are_exact_saved_states(self):
        changes = 0
        for ns in ('meridian_base', 'underwater_base'):
            report = self.reports[ns]
            manifest = json.loads((ROOT / f'docs/arenas/{ns}_compatibility.json').read_text())
            for change in manifest['changes']:
                p = [change['position'][a]+report['translation'][a] for a in range(3)]
                self.assertEqual(self.blocks.state(*p), change['after'])
                changes += 1
        self.assertEqual(changes, 112)

    def test_underwater_reset_removes_flooding_only_from_originally_dry_cells(self):
        source = self.files['data/underwater_base/function/restore_dry_cells.mcfunction']
        cells = set()
        for line in source.splitlines():
            match = re.fullmatch(r'fill ([-\d]+) ([-\d]+) ([-\d]+) ([-\d]+) ([-\d]+) ([-\d]+) minecraft:(air|cave_air) replace minecraft:water', line)
            self.assertIsNotNone(match, line)
            x0, y0, z0, x1, y1, z1 = map(int, match.groups()[:6])
            self.assertEqual((y0, z0), (y1, z1))
            for x in range(x0, x1+1):
                self.assertEqual(self.blocks.state(x, y0, z0)['Name'], 'minecraft:'+match[7])
                cells.add((x, y0, z0))
        self.assertGreater(len(cells), 1000)
        restore = '\n'.join(value for path, value in self.files.items()
                            if path.startswith('data/underwater_base/function/restore'))
        for x, y, z in self.reports['underwater_base']['destination_player_spawns']:
            for yy in (math.floor(y), math.floor(y+1)):
                p = (math.floor(x), yy, math.floor(z))
                name = self.blocks.state(*p)['Name']
                if name in ('minecraft:air', 'minecraft:cave_air'):
                    self.assertTrue(p in cells, f'Missing dry-cell reset at {p}')
                else:
                    command = f'setblock {p[0]} {p[1]} {p[2]} {name}'
                    self.assertTrue(command in restore, f'Missing original detail reset: {command}')


if __name__ == '__main__':
    unittest.main()
