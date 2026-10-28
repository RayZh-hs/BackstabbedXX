"""Validate resident separation and post-fire scrap routes against saved blocks."""
import json,math,re,unittest,zipfile
from pathlib import Path
from test_klut27 import SavedBlocks
from test_yacht_spawns import WORLD
ROOT=Path(__file__).resolve().parents[1]
class PopulationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/'docs/arenas/klut27-population.json').read_text())
  cls.fire=json.loads((ROOT/'docs/arenas/klut27-fire.json').read_text())
  cls.blocks=SavedBlocks()
  with zipfile.ZipFile(WORLD/'datapacks/mcm.zip')as z:cls.files={n:z.read(n)for n in z.namelist()}
 def test_residents_have_clear_heads_and_player_separation(self):
  rows=self.data['villagers']+self.data['integrated_only_villagers'];self.assertEqual(len(rows),19)
  self.assertEqual(len({tuple(r['position'])for r in rows}),19)
  players=self.data['player_spawns_source']
  for r in rows:
   p=r['position'];self.assertGreaterEqual(min(math.dist(p,q)for q in players),3)
   x,y,z=map(math.floor,p)
   for yy in [y,y+1]:self.assertEqual(self.blocks.block(x+36864,yy,z+36864),'air')
  nearest=[min(math.dist(r['position'],q['position'])for q in rows if q!=r)for r in rows]
  self.assertGreaterEqual(sum(v<=3 for v in nearest),6)
  self.assertGreaterEqual(sum(v>=4 for v in nearest),2)
 def test_scraps_are_separate_safe_and_connected_after_fire(self):
  text=self.files['data/klut27/function/activate.mcfunction'].decode()
  player=[l for l in text.splitlines()if l.startswith('summon marker')and '"PlayerSpawn"'in l]
  scrap=[l for l in text.splitlines()if l.startswith('summon marker')and '"ScrapSpawn"'in l]
  self.assertEqual(len(player),28);self.assertEqual(len(scrap),28)
  self.assertTrue(all('"ScrapSpawn"'not in l for l in player))
  self.assertTrue(all('gravity_direction:"down"'in l for l in scrap))
  affected={tuple(p)for p in self.fire['affected_cells']}
  points=self.data['scrap_spawns_source'];self.assertEqual(len({tuple(p)for p in points}),28)
  for p,route in zip(points,self.data['scrap_routes_after_fire']):
   x,y,z=map(math.floor,p)
   self.assertFalse({(x,y-1,z),(x,y,z),(x,y+1,z)}&affected)
   self.assertTrue(all(math.dist(p,[v+.5 for v in e])>3 for e in self.fire['elevators']))
   self.assertEqual(route[0],[x,y,z]);self.assertEqual(route[-1],[9,15,45])
   for q in route:
    self.assertNotIn((q[0],q[1]-1,q[2]),affected)
   for a,b in zip(route,route[1:]):
    self.assertEqual(abs(a[0]-b[0])+abs(a[2]-b[2]),1)
    self.assertLessEqual(abs(a[1]-b[1]),1)
  self.assertGreaterEqual(sum(p[2]>=35 for p in points),16)
 def test_reset_wires_all_residents(self):
  for name in ('activate','reset'):
   self.assertIn('function klut27:residents/reset',self.files[f'data/klut27/function/{name}.mcfunction'].decode())
  reset=self.files['data/klut27/function/residents/reset.mcfunction'].decode()
  for row in self.data['villagers']+self.data['integrated_only_villagers']:self.assertIn(row['integrated_uuid'],reset)

if __name__=='__main__':unittest.main()
