"""Contracts for KLUT merchant and scripted hazard generation."""
import sys
import unittest
import zlib
import struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import klut27_fire_model as feature
from test_yacht_spawns import Reader, payload, WORLD

class EngineerFireTests(unittest.TestCase):
    def test_elevator_contact_includes_edges_corners_but_no_gap(self):
        e=(8,15,20)
        for x in (-1,0,1):
            for y in (-1,0,1):
                for z in (-1,0,1):
                    self.assertEqual(feature.touches((8+x,15+y,20+z),e),bool(x or y or z))
        self.assertFalse(feature.touches((10,15,20),e))

    def test_trade_requires_exact_innocent_base_hook(self):
        entities=[]
        data=(WORLD/'entities/r.72.72.mca').read_bytes()
        for slot in range(1024):
            offset=int.from_bytes(data[slot*4:slot*4+3],'big')*4096
            if not offset:continue
            length=struct.unpack_from('>I',data,offset)[0]
            reader=Reader(zlib.decompress(data[offset+5:offset+4+length]))
            self.assertEqual(reader.number('B'),10);reader.string()
            entities.extend(payload(reader,10).get('Entities',[]))
        engineers=[e for e in entities if 'Klut27Engineer' in e.get('Tags',[])]
        self.assertEqual(len(engineers),1)
        self.assertEqual(engineers[0]['Pos'],[36876.5,15,36897.5])
        self.assertEqual(engineers[0]['NoAI'],1)
        offers = engineers[0]['Offers']['Recipes']
        self.assertEqual(len(offers), 2)
        self.assertEqual(offers[0]['buy']['count'], 4)
        self.assertEqual(offers[0]['sell']['id'], 'minecraft:stick')
        self.assertNotIn('gun', offers[0]['sell']['components']['minecraft:custom_data'])
        upgrade = offers[1]
        self.assertEqual(upgrade['buy']['count'], 5)
        self.assertEqual(upgrade['buyB']['components']['minecraft:custom_data']['klut27_innocent'], 1)
        self.assertEqual(upgrade['sell']['components']['minecraft:custom_data']['klut27_upgraded'], 1)
        self.assertNotIn('klut27_upgraded', upgrade['buyB']['components']['minecraft:custom_data'])

    def test_fire_does_not_cross_nonflammable_barrier(self):
        wood={'Name':'minecraft:oak_planks'}
        stone={'Name':'minecraft:stone'}
        blocks={(0,0,0):wood,(1,0,0):wood,(2,0,0):stone,(3,0,0):wood}
        self.assertEqual(feature.fire_distances(blocks, [(0,0,0)]), {(0,0,0):0,(1,0,0):1})
        self.assertFalse(feature.flammable({'Name':'minecraft:crimson_planks'}))
        self.assertFalse(feature.flammable({'Name':'minecraft:oak_stairs','Properties':{'waterlogged':'true'}}))

if __name__ == '__main__': unittest.main()
