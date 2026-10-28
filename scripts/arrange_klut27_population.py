"""Separate scrap markers from player starts and assign resident home positions."""
import argparse,copy,json,math,re,uuid,zipfile
from collections import deque
import nbtlib as nbt
import klut27_geometry as geom
from klut27_engineer_fire import ROOT,SOURCE,TARGETS,OFFSET,World,Region,scene,coordinates,zip_bytes,enable_pack
from rebuild_klut27_fire import saved_entities,entity_uuid
from repair_klut27_decor import translated_uuid

MANIFEST=ROOT/'docs/arenas/klut27-population.json'
STAGE=ROOT/'map-previewer/maps/klut27/population'
# Groups at the stern and market; smaller groups/single residents in cabins.
HOMES=[(3,15,49),(5,15,49),(7,15,49),(9,15,48),
 (5,15,27),(7,15,27),(8,15,29),(6,15,33),
 (6,11,23),(8,11,27),(6,11,33),(10,11,37),
 (7,7,21),(9,7,23),(7,-12,13),(9,-12,7)]
GROUPS=['stern']*4+['market']*3+['pawn-shop']+['lower-walkway']*4+['lower-hall']*2+['lower-cabins']*2

def center(p):return [p[0]+.5,p[1],p[2]+.5]
def analyze(blocks):
 original=geom.read_blocks
 try:geom.read_blocks=lambda:blocks;return geom.analyze()
 finally:geom.read_blocks=original

def plan():
 blocks=scene();_,graph,components,columns=analyze(blocks)
 old=json.loads((ROOT/'docs/arenas/klut27.json').read_text());players=old['source_player_spawns']
 fire=json.loads((ROOT/'docs/arenas/klut27-fire.json').read_text());affected={tuple(p)for p in fire['affected_cells']}
 after={p:s for p,s in blocks.items()if p not in affected}
 for p in fire['elevators']:after[tuple(p)]={'Name':'minecraft:black_wool'}
 _,post,post_components,_=analyze(after);anchor=(9,15,45);connected=next(c for c in post_components if anchor in c)
 villagers=sorted([e for e in saved_entities()if str(e['id'])=='minecraft:villager' and 'Klut27Engineer'not in e.get('Tags',[])],key=lambda e:entity_uuid(e,0))
 assert len(villagers)==len(HOMES)==16
 rows=[]
 for e,p,group in zip(villagers,HOMES,GROUPS):
  assert p in components[0] and len(graph[p])>=2,p
  assert geom.safe(blocks,p) and geom.short(blocks.get((p[0],p[1]+1,p[2]),{}))=='air',p
  distance=min(math.dist(center(p),q)for q in players);assert distance>=3,(p,distance)
  directions=[]
  for dx,dz,yaw in [(0,1,0),(-1,0,90),(0,-1,-180),(1,0,-90)]:
   run=0
   for i in range(1,5):
    q=(p[0]+dx*i,p[1],p[2]+dz*i)
    if not geom.safe(blocks,q):break
    run=i
   directions.append((run,yaw))
  rows.append({'source_uuid':entity_uuid(e,0),'integrated_uuid':entity_uuid(e,OFFSET),'uuid_ints':list(map(int,e['UUID'])),'position':center(p),'yaw':max(directions)[1],'group':group,'distance_to_player_spawn':distance})
 def fire_safe(p):
  x,y,z=p
  return p in connected and not {(x,y-1,z),p,(x,y+1,z)}&affected and all(math.dist(center(p),[v+.5 for v in e])>3.5 for e in fire['elevators'])
 original=[tuple(map(math.floor,p))for p in players];kept=[p for p in original if fire_safe(p)];chosen=kept.copy()
 candidates={p for p in connected if fire_safe(p) and geom.safe(blocks,p) and len(post[p])>=2 and p[1]in(15,16) and min(math.dist(center(p),r['position'])for r in rows)>=1.5}
 while len(chosen)<28:
  available=[p for p in candidates-set(chosen)if min(math.dist(p,q)for q in chosen)>=2]
  assert available,('Insufficient spaced scrap sites',len(chosen))
  def rank(p):
   distance=min(math.dist(p,q)for q in chosen)
   return (min(distance,5)+(1.5 if p[2]>=35 else 0),len(post[p]),-abs(p[0]-8),p)
  chosen.append(max(available,key=rank))
 # Preserve source ordering and only replace invalid sites.
 replacements=iter(chosen[len(kept):]);scraps=[p if p in kept else next(replacements)for p in original]
 parents={anchor:None};q=deque([anchor])
 while q:
  parent=q.popleft()
  for p in sorted(post[parent]):
   if p not in parents:parents[p]=parent;q.append(p)
 routes=[]
 for p in scraps:
  route=[];node=p
  while node is not None:route.append(list(node));node=parents[node]
  routes.append(route)
 data={'villagers':rows,'player_spawns_source':players,'scrap_spawns_source':[center(p)for p in scraps],
  'scrap_routes_after_fire':routes,'relocated_scrap_indices':[i+1 for i,(a,b)in enumerate(zip(original,scraps))if a!=b],
  'scrap_gravity':'down','player_spawns_unchanged':True,'elevator_columns':{f'{x},{z}':[p[1]-1 for p in v]for (x,z),v in columns.items()}}
 # The integrated scene has three additional original residents. Preserve them
 # without inventing matching villagers in the separately edited standalone save.
 common={r['integrated_uuid']for r in rows};extras=[]
 for path in (TARGETS[0]/'entities').glob('r.*.mca'):
  rx,rz=map(int,path.stem.split('.')[1:]);base=OFFSET//512
  if rx not in (base-1,base)or rz not in (base-1,base)or path.stat().st_size<8192:continue
  region=Region(path)
  for slot in range(1024):
   chunk=region.get(slot)
   if not chunk:continue
   for e in chunk.get('Entities',[]):
    if str(e['id'])!='minecraft:villager'or 'Klut27Engineer'in e.get('Tags',[]):continue
    uid=entity_uuid(e,0)
    if uid not in common:extras.append(e)
 assert len(extras)==3,len(extras)
 data['integrated_only_villagers']=[]
 for e,p in zip(sorted(extras,key=lambda e:entity_uuid(e,0)),[(7,11,20),(7,11,30),(6,11,37)]):
  distance=min(math.dist(center(p),q)for q in players)
  assert p in components[0]and geom.safe(blocks,p)and distance>=3
  assert geom.short(blocks.get((p[0],p[1]+1,p[2]),{}))=='air'
  data['integrated_only_villagers'].append({'integrated_uuid':entity_uuid(e,0),'integrated_uuid_ints':list(map(int,e['UUID'])),'position':center(p),'yaw':0,'group':'lower-walkway','distance_to_player_spawn':distance})
 MANIFEST.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
 STAGE.mkdir(parents=True,exist_ok=True)
 from sync_klut27_standalone import block_string
 overlay={p:s for p,s in blocks.items()}
 for p in scraps:overlay[p]={'Name':'minecraft:lime_stained_glass'}
 for p in HOMES:overlay[p]={'Name':'minecraft:yellow_stained_glass'}
 (STAGE/'blocks.json').write_text(json.dumps([[[p[0]+5,p[1]+40,p[2]+2],block_string(s)]for p,s in overlay.items()]),encoding='utf-8')
 (STAGE/'preview.mjs').write_text("import fs from 'node:fs';export default function(api){const s=api.createStructure([30,86,53]);for(const[p,b]of JSON.parse(fs.readFileSync(new URL('./blocks.json',import.meta.url),'utf8')))api.setBlock(s,p,b);return{structure:s,metadata:{name:'klut27-population'}};}",encoding='utf-8')
 print('Relocated scrap indices:',data['relocated_scrap_indices']);print('Deck scraps:',sum(p[2]>=35 for p in scraps));print('Resident minimum player distance:',min(r['distance_to_player_spawn']for r in rows))
 return data

def relocate(world,offset,data):
 regions={};found={};wanted={tuple(translated_uuid(r['uuid_ints'],offset)):r for r in data['villagers']}
 if offset:wanted.update({tuple(r['integrated_uuid_ints']):r for r in data.get('integrated_only_villagers',[])})
 base=offset//512
 for path in (world/'entities').glob('r.*.mca'):
  rx,rz=map(int,path.stem.split('.')[1:])
  if rx not in (base-1,base)or rz not in (base-1,base)or path.stat().st_size<8192:continue
  r=Region(path);regions[path]=r
  for slot in range(1024):
   chunk=r.get(slot)
   if not chunk:continue
   for e in list(chunk.get('Entities',[])):
    key=tuple(map(int,e.get('UUID',[])))
    if key in wanted:
     assert key not in found,('Duplicate resident',key)
     found[key]=e;chunk['Entities'].remove(e);r.dirty.add(slot)
 assert set(found)==set(wanted),('Missing ordinary villagers',set(wanted)-set(found))
 functions=[]
 for key,row in wanted.items():
  e=found[key];p=row['position'];position=[p[0]+offset,p[1],p[2]+offset]
  e['Pos']=nbt.List[nbt.Double](position);e['Motion']=nbt.List[nbt.Double]([0,0,0]);e['Rotation']=nbt.List[nbt.Float]([row['yaw'],0])
  tags=[str(t)for t in e.get('Tags',[])if str(t)!='Klut27Blasted']
  if 'Klut27Resident'not in tags:tags.append('Klut27Resident')
  e['Tags']=nbt.List[nbt.String](tags);e['Health']=nbt.Float(20);e['DeathTime']=nbt.Short(0);e['HurtTime']=nbt.Short(0);e['Fire']=nbt.Short(-1);e['FallDistance']=nbt.Float(0);e['PersistenceRequired']=nbt.Byte(1)
  cx,cz=math.floor(position[0])//16,math.floor(position[2])//16;path=world/'entities'/f'r.{cx//32}.{cz//32}.mca';r=regions[path];slot=cz%32*32+cx%32
  c=r.get(slot)
  if c is None:c=nbt.File({'DataVersion':nbt.Int(4189),'Position':nbt.IntArray([cx,cz]),'Entities':nbt.List[nbt.Compound]([])});r.loaded[slot]=c
  c['Entities'].append(e);r.dirty.add(slot)
  uid=row['integrated_uuid']if offset else row['source_uuid'];template=copy.deepcopy(e);template.pop('id',None)
  fields=['Pos','Motion','Rotation','Health','DeathTime','HurtTime','Fire','FallDistance','PersistenceRequired','Tags']
  state=nbt.Compound({k:copy.deepcopy(e[k])for k in fields})
  functions += [f'execute unless entity {uid} run summon villager {coordinates(p,offset)} {template.snbt()}',f'execute as {uid} run data merge entity @s {state.snbt()}']
 for path,r in regions.items():
  if r.dirty:path.write_bytes(r.encoded())
 return ('\n'.join(functions)+'\n').encode('utf-8')

def apply(data):
 for world,offset in [(SOURCE,0)]+[(w,OFFSET)for w in TARGETS]:
  reset=relocate(world,offset,data)
  if offset:
   path=world/'datapacks/mcm.zip'
   with zipfile.ZipFile(path)as z:files={n:z.read(n)for n in z.namelist()}
   key='data/klut27/function/activate.mcfunction';lines=files[key].decode().splitlines();output=[]
   for line in lines:
    if line.startswith('summon marker')and '"ScrapSpawn"'in line:
     if '"PlayerSpawn"'not in line:continue
     line=line.replace(',"ScrapSpawn"','').replace('"ScrapSpawn",','')
    output.append(line)
   for p in data['scrap_spawns_source']:output.append(f'summon marker {coordinates(p,offset)} {{Tags:["ScrapSpawn","MapEntity","Klut27Runtime"],data:{{gravity_direction:"down",gravity_strength:1.0d}}}}')
   files[key]=('\n'.join(output)+'\n').encode()
   for name in ('activate','reset'):
    key=f'data/klut27/function/{name}.mcfunction';line='function klut27:residents/reset'
    if line not in files[key].decode():files[key]=files[key].rstrip()+b'\n'+line.encode()+b'\n'
   files['data/klut27/function/residents/reset.mcfunction']=reset;path.write_bytes(zip_bytes(files))
  else:
   files={'pack.mcmeta':json.dumps({'pack':{'pack_format':61,'description':'KLUT-27 ordinary resident spawn/reset positions'}}).encode(),'data/klut27/function/residents/reset.mcfunction':reset}
   (world/'datapacks/klut27-residents.zip').write_bytes(zip_bytes(files));enable_pack(world,'klut27-residents.zip')
 # Refresh fire's snapshots from the newly assigned resident positions.
 from klut27_engineer_fire import install_fire
 install_fire()
 # Deterministically share identical payloads despite ZIP timestamp boundaries.
 a,b=[w/'datapacks/mcm.zip'for w in TARGETS]
 with zipfile.ZipFile(a)as z:fa={n:z.read(n)for n in z.namelist()}
 with zipfile.ZipFile(b)as z:fb={n:z.read(n)for n in z.namelist()}
 assert fa==fb;b.write_bytes(a.read_bytes())
 p=ROOT/'docs/arenas/klut27.json';m=json.loads(p.read_text());m['elevator_columns']=data['elevator_columns'];m['source_scrap_spawns']=data['scrap_spawns_source'];m['destination_scrap_spawns']=[[p[0]+OFFSET,p[1],p[2]+OFFSET]for p in data['scrap_spawns_source']];p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
 if args.apply:apply(json.loads(MANIFEST.read_text()))
 else:plan()
