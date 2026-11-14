"""Original build fidelity, actual island spawns, lake geometry, and shipped block assets."""
import gzip,hashlib,json,math
from pathlib import Path
import unittest
from zipfile import ZipFile
from world_geometry import World,in_region
ROOT=Path(__file__).resolve().parents[1]
SAVE=ROOT/'.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
BASE=ROOT/'axolotl-treehouse'

class TreehouseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads((ROOT/'docs/arenas/axolotl_treehouse.json').read_text());cls.w=World(SAVE)
  with ZipFile(SAVE/'datapacks/mcm.zip')as z:
   cls.files={f:z.read(f)for f in z.namelist()};assert len(cls.files)==len(z.namelist())
  cls.arena=json.loads(cls.files['data/axolotl_treehouse/predicate/arena.json'])
  cls.lake=json.loads(cls.files['data/axolotl_treehouse/predicate/lake_fall.json'])
  cls.island=json.loads(cls.files['data/axolotl_treehouse/predicate/island.json'])
 def test_every_original_source_block_is_preserved(self):
  expected=json.loads(gzip.decompress((BASE/'build/expected-source-blocks.json.gz').read_bytes()))
  self.assertEqual(len(expected),7745)
  for x,y,z,state in expected:self.assertEqual(self.w.block(x,y,z),state,(x,y,z))
 def test_spawn_safety_membership_and_distribution(self):
  points=self.m['spawns'];self.assertEqual(len(set(map(tuple,points))),32)
  full={'grass_block','dirt','coarse_dirt','spruce_planks','oak_planks','stripped_spruce_log','oak_wood','moss_block','smooth_sandstone'}
  clear={'air','short_grass','azure_bluet','oxeye_daisy','allium','pink_petals','fern','poppy','dandelion','cornflower','firefly_bush','cactus_flower'}
  for p in points:
   self.assertTrue(in_region(self.arena,p));self.assertTrue(in_region(self.island,p));self.assertFalse(in_region(self.lake,p))
   x,y,z=map(math.floor,p)
   self.assertIn(self.w.block(x,y-1,z)['Name'].split(':')[1],full)
   for dy in [0,1]:self.assertIn(self.w.block(x,y+dy,z)['Name'].split(':')[1],clear)
  self.assertGreaterEqual(len({p[1]for p in points}),5)
  self.assertTrue(in_region(self.island,self.m['spectator']))
 def test_surrounding_lake_and_mountains_are_saved_on_all_sides(self):
  c=57600
  for i in range(32):
   a=i*math.tau/32;water=[]
   for r in range(56,127):
    x,z=math.floor(c+math.cos(a)*r),math.floor(c+math.sin(a)*r)
    self.assertEqual(self.w.block(x,63,z)['Name'],'minecraft:water',(i,r))
    water.append((x,z))
   self.assertGreaterEqual(len(water),70)
   heights=[]
   for r in range(136,255,4):
    x,z=math.floor(c+math.cos(a)*r),math.floor(c+math.sin(a)*r)
    heights.extend(y for y in range(64,220)if self.w.block(x,y,z)['Name']in ['minecraft:stone','minecraft:grass_block','minecraft:dirt'])
   self.assertTrue(heights,(i,'missing shoreline'))
   self.assertGreater(max(heights),80,(i,'missing surrounding native terrain'))
   self.assertFalse(in_region(self.arena,(x,max(heights)+1,z)))
  self.assertEqual(self.m['terrain_sample']['chunk_count'],1024)
  self.assertEqual(self.m['terrain_sample']['seed'],69420018030897796)
 def test_distant_terrain_matches_the_native_minecraft_sample(self):
  reference=json.loads(gzip.decompress((BASE/'build/vanilla-surface-reference.json.gz').read_bytes()))
  self.assertGreater(len(reference),1000)
  for x,y,z,state in reference:self.assertEqual(self.w.block(x,y,z),state,(x,y,z))
 def test_native_forest_trees_keep_their_complete_unstretched_shape(self):
  trees=json.loads(gzip.decompress((BASE/'build/vanilla-tree-reference.json.gz').read_bytes()))
  self.assertEqual(len(trees),6)
  for tree in trees:
   self.assertNotEqual(tree['translation'][1],0)
   self.assertGreater(len(tree['blocks']),60)
   for x,y,z,state in tree['blocks']:self.assertEqual(self.w.block(x,y,z),state,(tree['root'],x,y,z))
 def test_lake_fall_is_position_based_and_island_water_is_harmless(self):
  c=57600
  self.assertTrue(in_region(self.lake,(c+58.5,63.9,c+.5)))
  self.assertFalse(in_region(self.lake,(c+58.5,64.1,c+.5)))
  waters=[]
  for x,y,z,state in json.loads(gzip.decompress((BASE/'build/expected-source-blocks.json.gz').read_bytes())):
   if state['Name']=='minecraft:water':waters.append((x+.5,y,z+.5))
  self.assertGreater(len(waters),50)
  for p in waters:self.assertFalse(in_region(self.lake,p));self.assertTrue(in_region(self.island,p))
  text=self.files['data/axolotl_treehouse/function/check_player.mcfunction'].decode()
  self.assertIn('if predicate axolotl_treehouse:lake_fall run return run function mcm:game/playerdeath',text)
  self.assertNotIn('if block',text);self.assertNotIn('graceperiod',text)
  function=self.files['data/axolotl_treehouse/function/functionality.mcfunction'].decode()
  for guard in ['matches 25','matches 1','tag=queued','tag=!spectating','gamemode=!spectator','dead matches 1..']:self.assertIn(guard,function)
 def test_maintained_namespace_and_lifecycle_hooks(self):
  for p in(BASE/'datapack').rglob('*'):
   if p.is_file():self.assertEqual(p.read_bytes(),self.files[p.relative_to(BASE/'datapack').as_posix()])
  for shared,hook in [('load','axolotl_treehouse:register'),('respawn_entities','axolotl_treehouse:register'),('lobby/voting/end','axolotl_treehouse:activate'),('maps/reset','axolotl_treehouse:reset'),('game/loops/ingame','axolotl_treehouse:functionality'),('everytick','axolotl_treehouse:waiting_tick')]:
   self.assertIn(hook,self.files['data/mcm/function/'+shared+'.mcfunction'].decode())
  self.assertEqual(self.files['data/axolotl_treehouse/function/activate.mcfunction'].decode().count('summon marker'),33)
 def test_visual_backport_and_poster_are_shipped(self):
  with ZipFile(ROOT/'.minecraft/mods/backstabbed-treehouse-1.0.0.jar')as z:
   meta=z.read('META-INF/neoforge.mods.toml').decode();self.assertIn('[1.21.4]',meta)
   provenance=json.loads(z.read('treehouse-build.json'))['assets']
   for name,digest in provenance['files'].items():self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),digest)
   for name in ['spruce_shelf','firefly_bush','cactus_flower']:
    self.assertIn('assets/minecraft/blockstates/'+name+'.json',z.namelist())
  assets=ROOT/'.minecraft/resourcepacks/backstabbed-resource/assets';ref='axolotl_treehouse:posters/axolotl_treehouse'
  model=json.loads((assets/'axolotl_treehouse/models/posters/axolotl_treehouse.json').read_text());self.assertEqual(model['textures']['poster'],ref)
  self.assertIn(ref,self.files['data/mcm/function/lobby/voting/map_position_id.mcfunction'].decode())
  self.assertIn(ref,{p.get('resource')for p in json.loads((assets/'minecraft/atlases/blocks.json').read_text())['sources']})

if __name__=='__main__':unittest.main()
