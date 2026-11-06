"""Monolith's actual destination blocks, footprint, lifecycle, and poster chain."""
import hashlib
import json
import math
from pathlib import Path
import struct
import unittest
from zipfile import ZipFile
from world_geometry import World, in_region

ROOT = Path(__file__).resolve().parents[1]
SAVE = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
ASSETS = ROOT / '.minecraft/resourcepacks/backstabbed-resource/assets'

class MonolithTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / 'docs/arenas/monolith.json').read_text())
        cls.world = World(SAVE)
        with ZipFile(SAVE / 'datapacks/mcm.zip') as z:
            cls.files = {name: z.read(name) for name in z.namelist()}
            assert len(z.namelist()) == len(cls.files)
        cls.region = json.loads(cls.files['data/monolith/predicate/arena.json'])

    def text(self, path):
        path = path.replace('monolith/', 'monolith/function/', 1) if path.startswith('monolith/') else path
        return self.files['data/' + path + '.mcfunction'].decode()

    def test_actual_spawns_and_summit_landings(self):
        points = self.manifest['spawns'] + self.manifest['altars']
        self.assertEqual(len(set(map(tuple, self.manifest['spawns']))), 36)
        safe_full = {'polished_tuff','tuff','stone','andesite','stone_bricks','moss_block',
                     'podzol','dirt','rooted_dirt','deepslate_tiles','deepslate_bricks',
                     'cyan_terracotta','gray_concrete','cobbled_deepslate','light_gray_wool'}
        passable = {'air','cave_air','void_air','short_grass','fern','pink_petals','allium',
                    'dandelion','poppy','brown_mushroom','red_mushroom','large_fern','tall_grass'}
        for point in points:
            with self.subTest(point=point):
                self.assertTrue(in_region(self.region, point))
                x, y, z = map(math.floor, point)
                self.assertIn(self.world.block(x, y-1, z)['Name'].split(':')[1], safe_full)
                for dy in [0, 1]:
                    state = self.world.block(x, y+dy, z)
                    if state['Name'] == 'minecraft:spruce_trapdoor':
                        self.assertEqual(state['Properties']['open'], 'true')
                        self.assertIn(state['Properties']['facing'], ['north','east','south','west'])
                    else:
                        self.assertIn(state['Name'].split(':')[1], passable)
        for island in self.manifest['islands']:
            lo, hi = island['bounds']
            self.assertEqual(sum(all(lo[i] <= q[i] < hi[i]+1 for i in range(3))
                                 for q in self.manifest['spawns']), 12)

    def test_triangle_has_separated_destinations_and_inward_facing_circles(self):
        altars = self.manifest['altars']
        a,b,c = altars
        area2 = abs((b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0]))
        self.assertGreater(area2, 10000)
        for i, island in enumerate(self.manifest['islands']):
            origin = altars[i]
            vectors = [(p[0]-origin[0], p[2]-origin[2]) for j,p in enumerate(altars) if i != j]
            dot = sum(x*y for x,y in zip(*vectors)) / math.prod(math.hypot(*v) for v in vectors)
            angle = math.degrees(math.acos(dot))
            self.assertGreater(angle, 50)
            self.assertLess(angle, 70)
            front = (island['inward_normal'][0],island['inward_normal'][2])
            self.assertTrue(all(sum(x*y for x,y in zip(front,v)) > 0 for v in vectors))
            self.assertEqual(self.world.block(*map(math.floor, (origin[0], origin[1]-1, origin[2])))['Name'].split(':')[0], 'minecraft')

    def test_boundary_membership_escape_and_flight_corridors(self):
        for point in self.manifest['spawns'] + self.manifest['altars'] + [self.manifest['safe_return']]:
            self.assertTrue(in_region(self.region, point))
        for point in [(53230,107.99,53350),(53230,210.01,53350),(53100,150,53350),
                      (53450,150,53350),(53230,150,53200),(53230,150,53500),
                      (0,1,70),(49190,100,49190),(53230,68,53350)]:
            self.assertFalse(in_region(self.region, point), point)
        for z in [53309,53320,53375,53390,53340.9995,53341.0,53341.0005]:
            self.assertTrue(in_region(self.region, (53240,155,z)), z)
        code=self.text('monolith/functionality')
        for guard in ['matches 24','matches 1','tag=queued','tag=!spectating','gamemode=!spectator','dead matches 1..']:
            self.assertIn(guard, code)
        self.assertIn('mcm:game/playerdeath', self.text('monolith/escape'))
        self.assertIn('matches 1..', self.text('monolith/escape'))
        self.assertIn('monolith:return_player', self.text('monolith/waiting_tick'))

    def test_old_linear_tail_has_no_leftover_architecture(self):
        # This old southern tail lies beyond every island's final triangle bounds.
        # Clearing the old placement matters as much as copying the new one.
        for cx in range(53200//16, 53295//16+1):
            for cz in range(53424//16, 53455//16+1):
                for section in self.world.chunk(cx, cz).get('sections', []):
                    names = {s['Name'] for s in section.get('block_states', {}).get('palette', [])}
                    self.assertLessEqual(names, {'minecraft:air','minecraft:cave_air','minecraft:void_air'})

    def test_registration_full_lifecycle_and_maintained_source(self):
        for path in (ROOT/'monolith/datapack').rglob('*'):
            if path.is_file():
                self.assertEqual(path.read_bytes(),self.files[path.relative_to(ROOT/'monolith/datapack').as_posix()])
        for shared, hook in [('respawn_entities','monolith:register'),('lobby/voting/end','monolith:activate'),
                             ('game/loops/ingame','monolith:functionality'),('maps/reset','monolith:reset'),
                             ('everytick','monolith tick'),('load','monolith:register')]:
            self.assertIn(hook,self.text('mcm/function/'+shared))
        reset=self.text('monolith/reset')
        for code in ['monolith cleanup','kill @e[tag=MonolithRuntime]','schedule clear monolith:activate','forceload remove']:
            self.assertIn(code,reset)
        self.assertEqual(self.text('monolith/activate').count('summon marker'),40)

    def test_poster_chain_and_title(self):
        ref='monolith:posters/monolith'
        self.assertIn('"minecraft:item_model":"'+ref+'"',self.text('mcm/function/lobby/voting/map_position_id'))
        self.assertEqual(json.loads((ASSETS/'monolith/items/posters/monolith.json').read_text())['model']['model'],ref)
        model=json.loads((ASSETS/'monolith/models/posters/monolith.json').read_text())
        self.assertEqual(model['textures']['poster'],ref)
        self.assertEqual(model['elements'][0]['from'][2],8)
        raw=(ASSETS/'monolith/textures/posters/monolith.png').read_bytes()
        self.assertEqual(raw[:8],b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>II',raw[16:24]),(1024,1536))
        self.assertIn(ref,{s.get('resource')for s in json.loads((ASSETS/'minecraft/atlases/blocks.json').read_text())['sources']})
        self.assertEqual(json.loads((ASSETS/'monolith/lang/en_us.json').read_text())['monolith.name'],'Monolith')

    def test_no_imported_commands_or_unsupported_plant_blocks(self):
        for cx in range(self.manifest['forceload'][0]//16,self.manifest['forceload'][2]//16+1):
            for cz in range(self.manifest['forceload'][1]//16,self.manifest['forceload'][3]//16+1):
                chunk=self.world.chunk(cx,cz)
                for tile in chunk.get('block_entities',[]):
                    self.assertNotIn('command_block',tile['id'])
                for section in chunk.get('sections',[]):
                    for state in section.get('block_states',{}).get('palette',[]):
                        self.assertNotIn(state['Name'],{'minecraft:bush','minecraft:wildflowers','minecraft:cactus_flower'})

if __name__=='__main__':unittest.main()
