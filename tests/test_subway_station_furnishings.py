"""Check installed upper-concourse furniture, walking routes and round resets."""
from collections import deque
import json
from pathlib import Path
import struct
import unittest
import zipfile
import zlib

from test_subway_station import StationBlocks, SHAPES
from test_yacht_spawns import Reader, WORLD, payload

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / 'docs/arenas/subway_station_furnishings.json').read_text())
FURNITURE_SHAPES = json.loads((ROOT / 'tests/fixtures/subway_station_furnishings_collision_shapes.json').read_text())['states']


def key(state):
    return state['Name'], dict(state.get('Properties', {}))


class FurnishedBlocks(StationBlocks):
    def shapes(self, x, y, z):
        state = self.state(x, y, z)
        name = state['Name'] + '[' + ','.join(f'{k}={v}' for k, v in sorted(state.get('Properties', {}).items())) + ']'
        return FURNITURE_SHAPES[name] if name in FURNITURE_SHAPES else SHAPES[name]


class SubwayStationFurnitureTests(unittest.TestCase):
    def test_every_saved_furnishing_matches_the_bounded_builder_patch(self):
        blocks = FurnishedBlocks()
        self.assertEqual(len(MANIFEST['placements']), MANIFEST['blocks'])
        self.assertEqual(len({tuple(p[:3]) for p in MANIFEST['placements']}), MANIFEST['blocks'])
        for x, y, z, state in MANIFEST['placements']:
            with self.subTest(position=(x, y, z)):
                self.assertEqual(key(blocks.state(x, y, z)), key(MANIFEST['palette'][state]))
                self.assertTrue(-48 <= y <= -43)
                self.assertTrue(20362 <= z <= 20386 or 20529 <= z <= 20552)
                if y == -48:
                    self.assertEqual(blocks.block(x, -49, z), 'cyan_terracotta')
        for x, y, z in MANIFEST['barrel_tables']:
            self.assertEqual(blocks.block(x, y, z), 'barrel')
            self.assertEqual(blocks.block(x, y + 1, z), 'air', 'Old tabletop remains above barrel')
            self.assertEqual(blocks.block(x, y + 2, z), 'air', 'Floating tabletop decoration remains')

    def test_upper_concourses_keep_central_and_stair_routes_connected(self):
        blocks = FurnishedBlocks()
        for side, route in MANIFEST['routes'].items():
            with self.subTest(concourse=side):
                zmin, zmax = route['z_range']
                walk = {(x, z) for x in range(20476, 20531) for z in range(zmin, zmax + 1)
                        if blocks.block(x, -49, z) == 'cyan_terracotta' and blocks.clear(x + .5, -48, z + .5)}
                start = (20502, zmin + 1)
                seen, pending = {start}, deque([start])
                while pending:
                    x, z = pending.popleft()
                    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        point = x + dx, z + dz
                        if point in walk and point not in seen:
                            seen.add(point)
                            pending.append(point)
                # The original two closed shop interiors are separate until their
                # doors open. New furniture must not create additional pockets.
                self.assertEqual(walk - seen, set(map(tuple, route['closed_booth_cells'])))
                self.assertGreater(len(seen), 1100)
                for x in range(20500, 20506):
                    for z in range(zmin, zmax + 1):
                        self.assertIn((x, z), seen, 'Six-block central aisle obstructed')
                for x in range(20476, 20531):
                    self.assertIn((x, route['cross_z']), seen, 'Cross-route to stairs obstructed')

    def test_round_reset_covers_furniture_and_information_signs_are_saved(self):
        with zipfile.ZipFile(WORLD / 'datapacks/mcm.zip') as archive:
            self.assertEqual(len(archive.namelist()), len(set(archive.namelist())))
            original = archive.read('data/subway_station/function/restore_blocks.mcfunction').decode()
            reset = archive.read('data/subway_station/function/furnishings/restore.mcfunction').decode()
        self.assertEqual(original.count('function subway_station:furnishings/restore'), 1)
        self.assertEqual(sum(line.startswith('setblock ') for line in reset.splitlines()), MANIFEST['interactive_reset_blocks'])
        for x, y, z in MANIFEST['barrel_tables']:
            self.assertIn(f'data modify block {x} {y} {z} Items set value []', reset)
        for x, y, z, index in MANIFEST['placements']:
            state = MANIFEST['palette'][index]
            if state['Name'].endswith(('_button', '_trapdoor', '_pressure_plate')):
                self.assertIn(f'setblock {x} {y} {z} {state["Name"]}', reset)
        blocks, tiles = FurnishedBlocks(), {}
        for cx, cz in {(x // 16, z // 16) for x, y, z in MANIFEST['signs']}:
            raw = blocks.region(cx // 32, cz // 32)
            slot = (cz % 32) * 32 + cx % 32
            offset = int.from_bytes(raw[slot * 4:slot * 4 + 3], 'big') * 4096
            length = struct.unpack_from('>I', raw, offset)[0]
            reader = Reader(zlib.decompress(raw[offset + 5:offset + 4 + length]))
            self.assertEqual(reader.number('B'), 10)
            reader.string()
            for tile in payload(reader, 10)['block_entities']:
                tiles[tuple(tile[k] for k in ('x', 'y', 'z'))] = tile
        for pos in MANIFEST['signs']:
            tile = tiles[tuple(pos)]
            self.assertEqual(tile['id'], 'minecraft:sign')
            self.assertEqual(tile['is_waxed'], 1)
            messages = [json.loads(line) for line in tile['front_text']['messages']]
            # Minecraft may save a simple text component as a JSON string.
            self.assertTrue(any(text if isinstance(text, str) else text.get('text') for text in messages))
