"""Voting references must resolve from registered maps through the real atlas."""
import json
from pathlib import Path
import struct
import unittest
from zipfile import ZipFile
import zlib

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / '.minecraft/resourcepacks/backstabbed-resource/assets'
SAVE = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
MAPS = [(21, 'sworld_island', 'SworldIsland'), (22, 'middle_ages', 'MiddleAges'), (23, 'cube_block', 'CubeBlock')]


class PortVotingResources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with ZipFile(SAVE / 'datapacks/mcm.zip') as z:
            cls.names = z.namelist()
            cls.members = {name: z.read(name) for name in cls.names}

    def text(self, name):
        return self.members['data/mcm/function/' + name + '.mcfunction'].decode()

    def test_registered_ids_have_complete_selection_and_round_lifecycle(self):
        self.assertEqual(len(self.names), len(set(self.names)))
        for mid, ns, tag in MAPS:
            with self.subTest(arena=ns):
                register = self.members[f'data/{ns}/function/register.mcfunction'].decode()
                self.assertTrue(f'data/{ns}/function/select.mcfunction' in self.members, ns)
                select = self.members[f'data/{ns}/function/select.mcfunction'].decode()
                self.assertIn('positioned 28.0 2.0 89.0 as', select)
                self.assertIn(f'MapValues {mid}', register)
                self.assertIn(f'function {ns}:register', self.text('respawn_entities'))
                self.assertIn(f'tag=SelectedMap,tag={tag}] run schedule function {ns}:activate', self.text('lobby/voting/end'))
                self.assertIn(f'matches {mid} run function {ns}:functionality', self.text('game/loops/ingame'))
                self.assertIn(f'matches {mid} run function {ns}:reset', self.text('maps/reset'))
                self.assertIn(f'{{name:{tag},translate:"{ns}.name"}}', self.text('lobby/options/map_toggle/init'))
                for lang in ['en_us', 'zh_cn']:
                    values = json.loads((ASSETS / ns / 'lang' / (lang + '.json')).read_text())
                    self.assertIn(ns + '.name', values)
                    self.assertIn(ns + '.voted', values)

    def test_voting_items_models_pngs_and_atlas_resolve(self):
        atlas = json.loads((ASSETS / 'minecraft/atlases/blocks.json').read_text())
        textures = {entry.get('resource') for entry in atlas['sources']}
        voting = self.text('lobby/voting/map_position_id')
        for mid, ns, tag in MAPS:
            ref = f'{ns}:posters/{ns}'
            with self.subTest(arena=ns):
                self.assertIn(f'matches {mid} positioned ~-0.01 ~1 ~1', voting)
                self.assertIn(f'"minecraft:item_model":"{ref}"', voting)
                item = json.loads((ASSETS / ns / 'items/posters' / (ns + '.json')).read_text())
                self.assertEqual(item['model'], {'type': 'minecraft:model', 'model': ref})
                model = json.loads((ASSETS / ns / 'models/posters' / (ns + '.json')).read_text())
                self.assertEqual(model['textures']['poster'], ref)
                self.assertEqual(model['elements'][0]['from'][2], 8)
                self.assertIn(ref, textures)
                raw = (ASSETS / ns / 'textures/posters' / (ns + '.png')).read_bytes()
                self.assertEqual(raw[:8], b'\x89PNG\r\n\x1a\n')
                width, height = struct.unpack('>II', raw[16:24])
                self.assertEqual((width, height), (1024, 1536))
                offset, pixels = 8, b''
                while offset < len(raw):
                    size = int.from_bytes(raw[offset:offset + 4], 'big')
                    name, data = raw[offset + 4:offset + 8], raw[offset + 8:offset + 8 + size]
                    self.assertEqual(zlib.crc32(name + data), int.from_bytes(raw[offset + 8 + size:offset + 12 + size], 'big'))
                    if name == b'IDAT': pixels += data
                    offset += size + 12
                self.assertGreater(len(zlib.decompress(pixels)), width * height * 3)
