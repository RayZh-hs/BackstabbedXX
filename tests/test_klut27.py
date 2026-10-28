"""KLUT-27 destination collision, routes, irregular boundary and lifecycle."""
import json
import math
from pathlib import Path
import re
import tempfile
import unittest
import zipfile
from test_yacht_spawns import WorldBlocks, WORLD

ROOT=Path(__file__).resolve().parent.parent
OFFSET=36864

class SavedBlocks(WorldBlocks):
    def state(self,x,y,z):
        states=self.chunk(x//16,z//16).get(y//16,{})
        palette=states.get('palette',[{'Name':'minecraft:air'}]);index=0
        if len(palette)>1:
            bits=max(4,(len(palette)-1).bit_length());per=64//bits
            p=(y%16)*256+(z%16)*16+x%16
            index=(states['data'][p//per]>>((p%per)*bits))&((1<<bits)-1)
        return palette[index]

class Klut27Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((ROOT/'docs/arenas/klut27.json').read_text())
        cls.blocks=SavedBlocks()
        with zipfile.ZipFile(WORLD/'datapacks/mcm.zip') as z:cls.files={n:z.read(n) for n in z.namelist()}
        cls.arena=json.loads(cls.files['data/klut27/predicate/arena.json'])

    def inside(self,p,dimension='minecraft:overworld'):
        return any(t['predicate']['dimension']==dimension and all(r['min']<=p[i]<=r['max'] for i,a in enumerate(('x','y','z')) for r in [t['predicate']['position'][a]]) for t in self.arena['terms'])

    def check_safe(self,p):
        x,y,z=p
        support=self.blocks.block(x,y-1,z)
        # Explicit cube material classes: no partial slabs/stairs/fences, fluids,
        # gravity blocks, damage sources or doors are accepted as spawn support.
        self.assertTrue(support in {'iron_block','polished_blackstone','oxidized_copper','terracotta','sea_lantern','weathered_copper','exposed_copper','gold_block','prismarine_bricks','glass','blackstone','diorite','polished_diorite','diamond_block','oxidized_cut_copper','chiseled_stone_bricks','crafting_table','target','white_shulker_box'} or support.endswith(('_concrete','_terracotta','_planks','_wood','_log','_stem','_hyphae','_froglight','_stained_glass')),(p,support))
        self.assertEqual(self.blocks.block(x,y,z),'air',p)
        head=self.blocks.state(x,y+1,z);name=head['Name'].split(':')[-1];props=head.get('Properties',{})
        self.assertTrue(name=='air' or name.endswith('_wall_sign') or (name.endswith('_trapdoor') and props.get('half')=='top' and props.get('open')=='false' and props.get('waterlogged')=='false'),(p,head))
        self.assertTrue(self.inside((x+.5,y,z+.5)),p)

    def test_spawns_match_destination_and_have_real_departure_routes(self):
        text=self.files['data/klut27/function/activate.mcfunction'].decode()
        points=[tuple(map(float,m)) for m in re.findall(r'^summon marker ([\d.]+) (-?[\d.]+) ([\d.]+).*"PlayerSpawn"',text,re.M)]
        self.assertEqual(len(points),28);self.assertEqual(len(set(points)),28)
        self.assertEqual(points,[tuple(p) for p in self.manifest['destination_player_spawns']])
        self.assertEqual(sum('gravity_direction:"down",gravity_strength:1.0d' in line for line in text.splitlines() if '"PlayerSpawn"' in line),28)
        for index,spawn in enumerate(points):
            self.check_safe(tuple(map(math.floor,spawn)))
            route=self.manifest['spawn_routes_source'][index]
            self.assertEqual(route[0],[math.floor(spawn[0])-OFFSET,math.floor(spawn[1]),math.floor(spawn[2])-OFFSET])
            self.assertEqual(route[-1],[9,16,15])
            if index:self.assertGreater(len(route),1)
            for x,y,z in route:self.check_safe((x+OFFSET,y,z+OFFSET))
            for a,b in zip(route,route[1:]):
                horizontal=abs(a[0]-b[0])+abs(a[2]-b[2])
                if horizontal==0 and abs(a[1]-b[1])>1:
                    for p in (a,b):self.assertEqual(self.blocks.block(p[0]+OFFSET,p[1]-1,p[2]+OFFSET),'white_shulker_box')
                    # Every intermediate elevator is represented, not a route
                    # that assumes skipping a physically present landing.
                    for y in range(min(a[1],b[1]),max(a[1],b[1])-1):
                        self.assertNotEqual(self.blocks.block(a[0]+OFFSET,y,a[2]+OFFSET),'white_shulker_box')
                else:self.assertEqual(horizontal,1);self.assertLessEqual(abs(a[1]-b[1]),1)

    def test_spawn_rotations_face_walkable_routes_and_edge_points_are_inset(self):
        text=self.files['data/klut27/function/activate.mcfunction'].decode()
        lines=[line for line in text.splitlines() if line.startswith('summon marker') and '"PlayerSpawn"' in line]
        self.assertEqual(len(lines),28)
        self.assertEqual(self.manifest['source_player_spawns'][2],[4.5,15,44.5])
        self.assertEqual(self.manifest['source_player_spawns'][13],[12.5,15,47.5])
        for line,point in zip(lines,self.manifest['destination_player_spawns']):
            rotation=re.search(r'Rotation:\[(-?[\d.]+)f,0\.0f\]',line)
            self.assertIsNotNone(rotation,line)
            yaw=float(rotation.group(1));self.assertIn(yaw,(-180,-90,0,90))
            dx,dz={-180:(0,-1),-90:(1,0),0:(0,1),90:(-1,0)}[yaw]
            x,y,z=map(math.floor,point)
            # First forward step must have full support and clear body volume.
            self.check_safe((x+dx,y,z+dz))

    def test_hazard_timing_and_per_map_hook_wiring(self):
        air=self.files['data/klut27/function/air_tick.mcfunction'].decode()
        self.assertIn('matches 40 run',air)
        self.assertIn('matches 200.. run',air)
        self.assertIn('unless predicate klut27:airless',air)
        self.assertIn('$graceperiod CmdData matches 1..',air)
        give=self.files['data/klut27/function/give_hook.mcfunction'].decode()
        self.assertIn('hotbar.0 with gravity_changer:grappling_hook',give)
        self.assertNotIn('grappling_cooldown_ticks',give)
        self.assertIn('no_drop_on_death:1b',give)
        cooldown=self.files['data/klut27/function/hook_tick.mcfunction'].decode()
        self.assertIn('on origin',cooldown)
        self.assertNotIn('sort=nearest',cooldown)
        self.assertNotIn('gravity grappling_hook clear','\n'.join(self.files[n].decode() for n in self.files if n.startswith('data/klut27/') and n.endswith('.mcfunction')))
        for side in ('upper','lower'):
            self.assertIn('e.cooldown 30',self.files[f'data/klut27_elevators/function/find_{side}.mcfunction'].decode())

    def test_irregular_boundary_excludes_void_and_antenna(self):
        self.assertGreater(len(self.arena['terms']),1)
        for p in self.manifest['destination_player_spawns']:self.assertTrue(self.inside(p))
        for p in [(36873.5,-45,36873.5),(36800,16,36879),(36950,16,36879),(36873,80,36879),(36873,16,37000)]:self.assertFalse(self.inside(p),p)
        self.assertFalse(self.inside((36873.5,16,36879.5),'minecraft:the_nether'))
        # Probe just outside the union's extrema, not only arbitrary distant points.
        for axis in range(3):
            key=('x','y','z')[axis]
            minimum=min(t['predicate']['position'][key]['min'] for t in self.arena['terms'])
            maximum=max(t['predicate']['position'][key]['max'] for t in self.arena['terms'])
            for edge in (minimum-.01,maximum+.01):
                p=[36873.5,16,36879.5];p[axis]=edge;self.assertFalse(self.inside(p))
        tick=self.files['data/klut27/function/functionality.mcfunction'].decode()
        self.assertIn('$selectedMap CmdData matches 20',tick)
        self.assertIn('tag=queued,tag=!spectating,gamemode=!spectator',tick)
        self.assertIn('unless score @s dead matches 1.. unless predicate klut27:arena',tick)
        self.assertIn('function mcm:game/playerdeath',self.files['data/klut27/function/fall.mcfunction'].decode())
        waiting=self.files['data/klut27/function/waiting_tick.mcfunction'].decode()
        self.assertIn('if predicate klut27:arena run tag @s add Klut27Participant',waiting)
        self.assertIn('tag=queued,tag=Klut27Participant,tag=!spectating',waiting)
        for name in ('activate','reset'):
            self.assertIn('tag @a remove Klut27Participant',self.files[f'data/klut27/function/{name}.mcfunction'].decode())

    def test_all_six_gravity_test_contacts_are_saved_full_cube_faces(self):
        self.assertEqual(set(self.manifest['gravity_test_positions']),{'up','down','north','south','east','west'})
        for data in self.manifest['gravity_test_positions'].values():
            x,y,z=data['source_support'];self.assertNotEqual(self.blocks.block(x+OFFSET,y,z+OFFSET),'air')
            for x,y,z in data['source_body_air_cells']:self.assertEqual(self.blocks.block(x+OFFSET,y,z+OFFSET),'air')
            self.assertTrue(self.inside(data['destination_feet']))

    def test_elevators_migrated_and_scoped_and_reset_is_idempotent(self):
        self.assertEqual(sum(map(len,self.manifest['elevator_columns'].values())),19)
        for column,levels in self.manifest['elevator_columns'].items():
            x,z=map(int,column.split(','))
            for y in levels:self.check_safe((x+OFFSET,y+1,z+OFFSET))
        prefix='data/klut27_elevators/'
        names=[n for n in self.files if n.startswith(prefix)]
        self.assertTrue(names)
        self.assertFalse(any('/functions/' in n or '/recipes/' in n or '/advancements/' in n for n in names))
        commands='\n'.join(self.files[n].decode() for n in names if n.endswith('.mcfunction'))
        self.assertNotIn('{Lock:',commands);self.assertNotIn('BlockEntityTag',commands)
        tick=self.files[prefix+'function/tick.mcfunction'].decode()
        self.assertIn('gravity bridge is_down @s',tick)
        self.assertIn('if predicate klut27:arena unless score @s dead matches 1.. if score @s klut27_gravity matches 1',tick)
        for direction in ('upper','lower'):
            find=self.files[prefix+f'function/find_{direction}.mcfunction'].decode()
            self.assertIn('run tp @s ~ ~1 ~',find)
            self.assertNotIn('Rotation',find)
        reset=self.files['data/klut27/function/reset.mcfunction'].decode()
        self.assertIn('schedule clear klut27:activate',reset);self.assertIn('kill @e[tag=Klut27Runtime]',reset)
        self.assertIn('forceload remove 36848 36848 36895 36927',self.files['data/mcm/function/maps/reset.mcfunction'].decode())

    def test_standalone_pack_metadata_targets_1214_and_preserves_bukkit_description(self):
        from klut27_elevators import pack_files, modernize_empty_bukkit
        self.assertEqual(json.loads(pack_files()['pack.mcmeta'])['pack']['pack_format'],61)
        with tempfile.TemporaryDirectory() as directory:
            world=Path(directory)
            path=world/'datapacks/bukkit/pack.mcmeta'
            path.parent.mkdir(parents=True)
            description='Data pack for resources provided by Bukkit plugins'
            path.write_text(json.dumps({'pack':{'pack_format':26,'description':description}}))
            modernize_empty_bukkit(world)
            self.assertEqual(json.loads(path.read_text()),{'pack':{'pack_format':61,'description':description}})

if __name__=='__main__':unittest.main()
