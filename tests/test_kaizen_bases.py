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
        if state['Name'] == 'minecraft:barrier':
            return [[0, 0, 0, 1, 1, 1]]
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
            editor_spawns = f'data/bbe_arena/function/{ns}/spawns.mcfunction'
            if f'function bbe_arena:{ns}/spawns' in activation:
                activation += '\n' + self.files[editor_spawns]
            actual = [list(map(float, m)) for m in re.findall(r'^summon (?:minecraft:)?marker ([-\d.]+) ([-\d.]+) ([-\d.]+).*"PlayerSpawn"', activation, re.M)]
            if editor_spawns not in self.files:
                self.assertEqual(actual, report['destination_player_spawns'])
                self.assertEqual(len(actual), 24)
            else:
                edited = json.loads(self.files[f'data/bbe_arena/editor/{ns}.json'])
                state = edited.get('state', edited)
                expected = [[p[a] for a in 'xyz'] for p in state['objects']
                            if p['kind'] in ('both', 'player') and p.get('enabled', 1)]
                self.assertEqual(len(actual), len(expected))
                for p, q in zip(actual, expected):
                    for v, w in zip(p, q):
                        self.assertAlmostEqual(v, w, places=8)
                self.assertGreaterEqual(len(actual), 16)
            self.assertEqual(len(set(map(tuple, actual))), len(actual))
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
            self.assertEqual([t['predicate'].get('location', t['predicate'])['position'] for t in predicate['terms']], report['boundary_boxes'])
            self.assertGreater(len(predicate['terms']), 20)
            dx, _, dz = report['translation']
            outside = ((0,-34,0), (0,-53,40), (-5440,38,5873), (500,100,500))
            for p in outside:
                self.assertFalse(inside(predicate, [p[0]+dx, p[1], p[2]+dz]), (ns, p))
            self.assertFalse(inside(predicate, report['return_position'], 'minecraft:the_nether'))
            self.assertFalse(inside(predicate, report['return_position'], 'minecraft:the_end'))
            for term in predicate['terms']:
                axes = term['predicate'].get('location', term['predicate'])['position']
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
            if ns != 'underwater_base':
                self.assertIn(f'$selectedMap CmdData matches {mid}', tick)
                self.assertIn('$gamestate CmdData matches 1', tick)
                self.assertIn('@a[tag=queued,tag=!spectating,gamemode=!spectator]', tick)
                self.assertIn('unless score @s dead matches 1..', tick)
            if ns == 'underwater_base':
                self.assertNotIn(prefix+'check_player.mcfunction', self.files)
                self.assertNotIn('run function underwater_base:functionality', self.files['data/mcm/function/game/loops/ingame.mcfunction'])
            else:
                self.assertIn(f'unless predicate {ns}:arena', self.files[prefix+'check_player.mcfunction'])
                self.assertIn(f'if block ~ ~ ~ #{ns}:fluids', self.files[prefix+'check_player.mcfunction'])
                self.assertIn(f'#{ns}:waterloggable[waterlogged=true]', self.files[prefix+'check_player.mcfunction'])
            self.assertIn('minecraft:water', json.loads(self.files[f'data/{ns}/tags/block/fluids.json'])['values'])
            valid_blocks = {key.split('[')[0] for key in SHAPES}
            self.assertTrue(set(json.loads(self.files[f'data/{ns}/tags/block/waterloggable.json'])['values']) <= valid_blocks)
            waiting = self.files[prefix+'waiting_tick.mcfunction']
            if ns != 'underwater_base':
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
            self.assertNotIn(f'data/{ns}/function/return_player.mcfunction', self.files)

    def test_bagger_wheel_landings_and_falls_eliminate_before_boundary_checks(self):
        wheels = json.loads(self.files['data/bagger_288/predicate/wheels.json'])
        death_line = json.loads(self.files['data/bagger_288/predicate/below_death_line.json'])
        for p in self.reports['bagger_288']['destination_player_spawns']:
            self.assertFalse(inside(wheels, p))
            self.assertFalse(inside(death_line, p))
        # Exercise actual exposed surfaces of every wheel/tread column, including
        # outer edges which were included by the old arena mask and survived.
        surfaces = 0
        for x in range(28652, 28706):
            for z in range(28688, 28741):
                for y in range(-51, -46):
                    shapes = self.blocks.shapes(x, y, z)
                    if not shapes or self.blocks.shapes(x, y+1, z):
                        continue
                    top = max(s[4] for s in shapes)
                    p = (x+.5, y+top, z+.5)
                    self.assertTrue(inside(wheels, p), p)
                    surfaces += 1
        self.assertGreater(surfaces, 1000)
        check = self.files['data/bagger_288/function/check_player.mcfunction']
        self.assertLess(check.index('bagger_288:wheels'), check.index('bagger_288:below_death_line'))
        self.assertLess(check.index('bagger_288:wheels'), check.index('unless predicate bagger_288:arena'))
        for reason in ('squashed', 'fall'):
            function = self.files[f'data/bagger_288/function/{reason}.mcfunction']
            self.assertIn('function mcm:game/playerdeath', function)
            self.assertIn('unless entity @s[tag=queued,tag=!spectating,gamemode=!spectator]', function)
            self.assertIn('if score @s dead matches 1.. run return 0', function)
            self.assertNotIn(' tp ', function)
        self.assertIn('got squashed by giant wheels', self.files['data/bagger_288/function/squashed.mcfunction'])
        editor = 'data/bbe_arena/function/bagger_288/'
        if editor+'tick.mcfunction' in self.files:
            self.assertEqual(self.files[editor+'check_player.mcfunction'].strip(), 'function bagger_288:check_player')
            self.assertNotIn(editor+'tp.mcfunction', self.files.keys())
            tick = self.files[editor+'tick.mcfunction']
            self.assertIn('$gamestate CmdData matches 0 run function bagger_288:waiting_tick', tick)
            self.assertIn('$gamestate CmdData matches 1 run function bagger_288:functionality', tick)
            self.assertNotIn('as @a', tick)  # Waiting must use the entered-arena participant guard.

    def test_underwater_six_seals_displays_and_reset_never_reopen_hatches(self):
        manifest = json.loads((ROOT / 'docs/arenas/underwater_base_exits.json').read_text())
        self.assertEqual(len(manifest['changes']), 6)
        restore = '\n'.join(value for path, value in self.files.items()
                            if path.startswith('data/underwater_base/function/restore'))
        for cell in manifest['changes']:
            self.assertEqual(self.blocks.state(*cell['position']), cell['after'])
            coords = ' '.join(map(str, cell['position']))
            self.assertNotIn('setblock ' + coords + ' ' + cell['before']['Name'], restore)
            self.assertIn('setblock ' + coords + ' minecraft:barrier',
                          self.files['data/underwater_base/function/seal_exits.mcfunction'])
        displays = self.files['data/underwater_base/function/spawn_exit_displays.mcfunction'].splitlines()
        self.assertTrue(displays[0].startswith('kill @e[type=block_display,tag=UnderwaterBaseExitDisplay]'))
        self.assertEqual(len(displays[1:]), 6)
        for line, cell in zip(displays[1:], manifest['changes']):
            data = json.loads(line[line.index('{'):])
            self.assertEqual(data['block_state'], cell['before'])
            self.assertIn('MapEntity', data['Tags'])
            self.assertIn('UnderwaterBaseRuntime', data['Tags'])
        self.assertTrue(self.files['data/underwater_base/function/restore_blocks.mcfunction'].rstrip()
                        .endswith('function underwater_base:seal_exits'))
        self.assertIn('function underwater_base:spawn_exit_displays', self.files['data/underwater_base/function/activate.mcfunction'])
        for path, source in self.files.items():
            if path.startswith('data/underwater_base/function/'):
                self.assertNotRegex(source, r'\btp @s\b|function underwater_base:return_player')

    def test_underwater_openable_routes_cannot_reach_ocean_and_keep_bubble_lifts(self):
        report = self.reports['underwater_base']
        lower = [report['build_min'][a]+report['translation'][a] for a in range(3)]
        upper = [report['build_max'][a]+report['translation'][a] for a in range(3)]

        @lru_cache(None)
        def passable(p):
            if not all(lower[a] <= p[a] <= upper[a] for a in range(3)):
                return False
            state = self.blocks.state(*p)
            # Overapproximate every interactive door and hatch as removed, so
            # opening them (including crawling through hatches) cannot escape.
            if state['Name'].endswith(('_door', '_trapdoor', '_fence_gate')):
                return True
            return not any(all(.2 < s[a+3] and .8 > s[a] for a in range(3))
                           for s in self.blocks.shapes(*p))

        start = tuple(math.floor(v) for v in report['destination_player_spawns'][0])
        reached, pending = {start}, deque([start])
        while pending:
            p = pending.popleft()
            self.assertFalse(any(p[a] in (lower[a], upper[a]) for a in range(3)), p)
            self.assertNotEqual(self.blocks.block(*p), 'water', f'Ocean accessible through {p}')
            for delta in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
                q = tuple(p[a]+delta[a] for a in range(3))
                if q not in reached and passable(q):
                    reached.add(q)
                    pending.append(q)
        self.assertGreater(len(reached), 3000)
        self.assertTrue({tuple(math.floor(v) for v in p) for p in report['destination_player_spawns']} <= reached)
        for lift in ((32963, 49, 32497), (32965, 47, 32537)):
            self.assertIn(lift, reached)
            self.assertEqual(self.blocks.block(*lift), 'bubble_column')

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
