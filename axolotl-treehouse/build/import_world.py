#!/usr/bin/env python3
"""Import the original schematic and generated surroundings into an unused region.

Run after the builder recipes, with nbtlib/numpy. The original palette is retained.
Refuses to overwrite any existing destination region.
"""
from pathlib import Path
import collections,copy,gzip,hashlib,json,math,sys,time,uuid
import nbtlib as n
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'arena-editor'))
from world import encode,stopped,write_region,read_region
BASE=ROOT/'map-previewer/maps/axolotl-treehouse'
SAVE=ROOT/'.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
CENTER=57600
SIDE=512
HEIGHT=272
ORIGIN=[CENTER-SIDE//2,48,CENTER-SIDE//2]
prior_manifest=ROOT/'docs/arenas/axolotl_treehouse.json'
prior=json.loads(prior_manifest.read_text()) if prior_manifest.exists() else None
SOURCE_ORIGIN=[CENTER-17,73,CENTER-18]
native=np.load(BASE/'vanilla-sample/scene.npz')
grid=native['grid'].copy()
palette=[]
for state in json.loads(str(native['palette'])):
 p=n.Compound({'Name':n.String(state['Name'])})
 if 'Properties'in state:p['Properties']=n.Compound({k:n.String(v)for k,v in state['Properties'].items()})
 palette.append(p)
ids={p.snbt():i for i,p in enumerate(palette)}
tiles={};entities={};expected=[]
def insert(path,origin,original=False):
 s=n.load(path);indices=[]
 for p in s['palette']:
  key=p.snbt()
  if key not in ids:ids[key]=len(palette);palette.append(copy.deepcopy(p))
  indices.append(ids[key])
 for b in s['blocks']:
  pos=[int(b['pos'][i])+origin[i]for i in range(3)]
  x,y,z=[pos[i]-ORIGIN[i]for i in range(3)]
  index=indices[int(b['state'])];grid[y,z,x]=index
  if original:expected.append([*pos,palette[index].unpack()])
  if 'nbt'in b:
   tile=copy.deepcopy(b['nbt'])
   if str(tile.get('id',''))=='minecraft:shelf':
    assert not len(tile.get('Items',[])), 'The visual backport only supports empty shelves.'
    continue
   tile.update({a:n.Int(pos[i])for i,a in enumerate('xyz')});tiles.setdefault((pos[0]//16,pos[2]//16),[]).append(tile)
 for ent in s.get('entities',[]):
  e=copy.deepcopy(ent['nbt']);pos=[float(ent['pos'][i])+origin[i]for i in range(3)];e['Pos']=n.List[n.Double](pos)
  for i,a in enumerate('XYZ'):
   if 'Tile'+a in e:e['Tile'+a]=n.Int(int(e['Tile'+a])+origin[i])
  if 'block_pos'in e:e['block_pos']=n.IntArray([int(ent['blockPos'][i])+origin[i]for i in range(3)])
  e['UUID']=n.IntArray(np.frombuffer(uuid.uuid4().bytes,dtype='>i4').astype('int32'))
  e.pop('LastEntityID',None);e['Motion']=n.List[n.Double]([0,0,0]);e['Invulnerable']=n.Byte(1)
  e['Tags']=n.List[n.String](['AxolotlTreehouseDecor'])
  if str(e['id'])=='minecraft:axolotl':e['PersistenceRequired']=n.Byte(1);e['FromBucket']=n.Byte(1)
  if str(e['id'])=='minecraft:hopper_minecart':e['Enabled']=n.Byte(0);e['NoGravity']=n.Byte(1)
  entities.setdefault((math.floor(pos[0]/16),math.floor(pos[2]/16)),[]).append(e)
 return s

insert(BASE/'build/treehouse-island.nbt',[CENTER-64,48,CENTER-64])
source=insert(BASE/'original-treehouse.nbt',SOURCE_ORIGIN,True)
def block(x,y,z):
 if not(0<=x-ORIGIN[0]<SIDE and 0<=y-48<HEIGHT and 0<=z-ORIGIN[2]<SIDE):return 'minecraft:air'
 return str(palette[int(grid[y-48,z-ORIGIN[2],x-ORIGIN[0]])]['Name'])
# Spawn candidates use full support and genuinely empty or non-colliding flora cells.
support={'minecraft:'+v for v in ['grass_block','dirt','coarse_dirt','spruce_planks','oak_planks','stripped_spruce_log','oak_wood','moss_block','smooth_sandstone']}
passable={'minecraft:'+v for v in ['air','short_grass','azure_bluet','oxeye_daisy','allium','pink_petals','fern','poppy','dandelion','cornflower','firefly_bush','cactus_flower']}
candidates=set()
for x in range(CENTER-40,CENTER+41):
 for z in range(CENTER-40,CENTER+41):
  if math.hypot(x-CENTER,z-CENTER)>41:continue
  for y in range(74,90):
   # Surface candidates must be exposed to the sky or belong to the source house.
   # This excludes accidental pockets below the generated hillside and paths.
   inside_source=(SOURCE_ORIGIN[0]<=x<SOURCE_ORIGIN[0]+34 and SOURCE_ORIGIN[2]<=z<SOURCE_ORIGIN[2]+37)
   exposed=all(block(x,yy,z)=='minecraft:air' for yy in range(y+2,120))
   if (inside_source or exposed) and block(x,y-1,z)in support and all(block(x,y+dy,z)in passable for dy in [0,1]):candidates.add((x,y,z))
routes={p for p in candidates if sum(any((p[0]+dx,p[1]+dy,p[2]+dz)in candidates for dy in [-1,0,1])for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)])>=2}
def choose(points,amount):
 points=set(points);assert len(points)>=amount,(len(points),amount)
 chosen=[min(points,key=lambda p:abs(p[0]-CENTER)+abs(p[2]-CENTER))]
 while len(chosen)<amount:chosen.append(max(points-set(chosen),key=lambda p:(min((p[0]-q[0])**2+(p[2]-q[2])**2+2*(p[1]-q[1])**2 for q in chosen),p)))
 return chosen
lawn={p for p in routes if 22<math.hypot(p[0]-CENTER,p[2]-CENTER)<40 and p[1]==74}
inside={p for p in routes if CENTER-17<=p[0]<CENTER+17 and CENTER-18<=p[2]<CENTER+19}
spawns=choose(lawn,16)+choose(inside,16)
assert len(set(spawns))==32
paths={};now=int(time.time())
for iz in range(SIDE//16):
 for ix in range(SIDE//16):
  cx=ORIGIN[0]//16+ix;cz=ORIGIN[2]//16+iz;sections=[]
  for sy in range(3,20):
   start=sy*16-48;data=grid[start:start+16,iz*16:iz*16+16,ix*16:ix*16+16].reshape(-1)
   if not np.any(data):continue
   unique,local=np.unique(data,return_inverse=True);pal=n.List[n.Compound]([palette[int(i)]for i in unique]);bs=n.Compound({'palette':pal})
   if len(pal)>1:
    bits=max(4,(len(pal)-1).bit_length());per=64//bits;packed=np.zeros(math.ceil(4096/per),dtype=np.uint64)
    for i in range(per):
     values=local[i::per].astype(np.uint64);packed[:len(values)]|=values<<np.uint64(i*bits)
    bs['data']=n.LongArray(packed.view(np.int64))
   sections.append(n.Compound({'Y':n.Byte(sy),'block_states':bs,'biomes':n.Compound({'palette':n.List[n.String](['minecraft:forest'])})}))
  chunk=n.File({'DataVersion':n.Int(4189),'xPos':n.Int(cx),'yPos':n.Int(-4),'zPos':n.Int(cz),'Status':n.String('minecraft:full'),'LastUpdate':n.Long(0),'InhabitedTime':n.Long(0),'isLightOn':n.Byte(0),'sections':n.List[n.Compound](sections),'block_entities':n.List[n.Compound](tiles.get((cx,cz),[])),'block_ticks':n.List[n.Compound]([]),'fluid_ticks':n.List[n.Compound]([]),'structures':n.Compound({'starts':n.Compound(),'References':n.Compound()}),'PostProcessing':n.List[n.List[n.Short]]([n.List[n.Short]([])for _ in range(24)])})
  paths.setdefault(('region',f'r.{cx//32}.{cz//32}.mca'),{})[cx%32+32*(cz%32)]=(now,encode(chunk))
for (cx,cz),es in entities.items():
 chunk=n.File({'DataVersion':n.Int(4189),'Position':n.IntArray([cx,cz]),'Entities':n.List[n.Compound](es)})
 paths.setdefault(('entities',f'r.{cx//32}.{cz//32}.mca'),{})[cx%32+32*(cz%32)]=(now,encode(chunk))
if '--preview-only' not in sys.argv:
 with stopped(SAVE):
  for(folder,file),chunks in paths.items():
   target=SAVE/folder/file
   if target.exists():
    assert '--replace-own-scene' in sys.argv,f'Occupied destination: {folder}/{file}'
    old=set(read_region(target));expected_slots=set(chunks)
    if folder=='region'and prior:
     lo,hi=prior['scene_bounds'];expected_slots={(x%32)+32*(z%32)for x in range(lo[0]//16,hi[0]//16+1)for z in range(lo[2]//16,hi[2]//16+1)}
    assert old==expected_slots,f'Destination includes non-arena chunks: {target}'
  for(folder,file),chunks in paths.items():write_region(SAVE/folder/file,chunks)

# A compact reproducible source contract checks every original block against the saved world.
out=ROOT/'axolotl-treehouse/build/expected-source-blocks.json.gz'
out.write_bytes(gzip.compress(json.dumps(expected,separators=(',',':')).encode(),mtime=0))
report=json.loads((BASE/'original-treehouse.json').read_text());report['terrain_sample']=json.loads((BASE/'vanilla-sample/provenance.json').read_text());report.update({'namespace':'axolotl_treehouse','title':'Axolotl Treehouse','map_id':25,'tag':'AxolotlTreehouse','source_origin':SOURCE_ORIGIN,'destination_build_bounds':[SOURCE_ORIGIN,[SOURCE_ORIGIN[i]+int(source['size'][i])-1 for i in range(3)]],'scene_bounds':[ORIGIN,[ORIGIN[0]+SIDE-1,319,ORIGIN[2]+SIDE-1]],'center':[CENTER,CENTER],'spawns':[[x+.5,y,z+.5]for x,y,z in spawns],'spawn_count':32,'safe_return':[spawns[0][0]+.5,spawns[0][1],spawns[0][2]+.5],'spectator':[CENTER+.5,115,CENTER+.5],'forceload':[CENTER-64,CENTER-64,CENTER+63,CENTER+63],'source_preserved_blocks':len(expected),'block_entities_preserved':sum(map(len,tiles.values())),'empty_shelf_block_entities_omitted':98,'entities_preserved':sum(map(len,entities.values())),'region_files':[f'{folder}/{file}'for folder,file in paths],'compatibility':'Three visual-only blocks registered with their original minecraft: IDs by backstabbed-treehouse-1.0.0.jar; all source block states and coordinates preserved. Empty shelf inventories are omitted; all other block entities retained.','lake_surface_y':63,'lake_death_y':64.0,'backup':{'path':'.minecraft/backups/map-integration/20261109T150803338789Z-axolotl-treehouse-before-import-71435139.zip','sha256':'672245cbfd57c5977c2834e2c3a557c61c66d5b8e2f6af42fb17e03f36a3c82c'},'reuse_terms':'Author supplied the schematic publicly in the pinned tutorial comment. No explicit license was supplied; preserve attribution without asserting a broader reuse grant.'})
report['landscape_reference']={'screenshot':'map-previewer/maps/axolotl-treehouse/reference-video.png','screenshot_sha256':'d4caa4d802c5bfc47aeb64e6e291e7ce229b23accbeb57b509cea14e76ed73da','island_recipe':'axolotl-treehouse/build/island.mjs','tree_template':'axolotl-treehouse/build/central-tree-reference.json','tree_template_blocks':501,'sampled_island_trees':6}
report['repair_backups']=[{'path':'.minecraft/backups/map-integration/20261109T160006889268Z-treehouse-before-island-redesign-034646ff.zip','sha256':'747b57db40c89644780a5b82b45f18963022c9d6852be20230da53832b041f58'},{'path':'.minecraft/backups/map-integration/20261109T161916700927Z-treehouse-before-vanilla-terrain-rebuild-6cbc708a.zip','sha256':'f89345069a75232308cdc095fe3a7927eda0f8c91b9267a44cfdda4fb0562376'}]
manifest_output=BASE/'proposed-manifest.json' if '--preview-only' in sys.argv else ROOT/'docs/arenas/axolotl_treehouse.json'
manifest_output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Preview the island with the imported original, omitting the distant scenic shell.
preview=n.File({'DataVersion':n.Int(4189),'size':n.List[n.Int]([128,112,128]),'palette':n.List[n.Compound](palette),'blocks':n.List[n.Compound]([]),'entities':n.List[n.Compound]([])},gzipped=True)
for y,z,x in zip(*np.nonzero(grid[:112,SIDE//2-64:SIDE//2+64,SIDE//2-64:SIDE//2+64])):
 preview['blocks'].append(n.Compound({'pos':n.List[n.Int]([int(x),int(y),int(z)]),'state':n.Int(int(grid[y,z+SIDE//2-64,x+SIDE//2-64]))}))
preview.save(BASE/'island-preview.nbt');(BASE/'island-preview.json').write_text(json.dumps({'name':'Axolotl Treehouse island','creator':'siyuan_日记; surroundings by Backstabbed++','source_url':report['source_url'],'origin':[CENTER-64,48,CENTER-64]}))
if '--scene-preview' in sys.argv:
 air=np.asarray([str(p['Name'])in {'minecraft:air','minecraft:cave_air','minecraft:void_air'}for p in palette])[grid]
 exposed=np.zeros_like(air)
 for axis in range(3):
  exposed|=np.roll(air,1,axis=axis);exposed|=np.roll(air,-1,axis=axis)
 exposed&=~air
 scene=n.File({'DataVersion':n.Int(4189),'size':n.List[n.Int]([SIDE,HEIGHT,SIDE]),'palette':n.List[n.Compound](palette),'blocks':n.List[n.Compound]([]),'entities':n.List[n.Compound]([])},gzipped=True)
 for y,z,x in zip(*np.nonzero(exposed)):
  scene['blocks'].append(n.Compound({'pos':n.List[n.Int]([int(x),int(y),int(z)]),'state':n.Int(int(grid[y,z,x]))}))
 scene.save(BASE/'scene-preview.nbt');(BASE/'scene-preview.json').write_text(json.dumps({'name':'Treehouse in sampled vanilla mountain basin','creator':'siyuan_日记; native Minecraft 1.21.4 terrain','origin':ORIGIN,'source_url':report['source_url']}))
print('Prepared preview of' if '--preview-only' in sys.argv else 'Imported',len(expected),'original blocks;',report['block_entities_preserved'],'block entities;',report['entities_preserved'],'entities; spawns',len(spawns))
