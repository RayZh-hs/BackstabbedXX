"""Scene synchronization and scalable contact-triggered KLUT fire generation."""
import copy,json,uuid,zipfile
import nbtlib as nbt
from collections import defaultdict,deque
from klut27_engineer_fire import (ROOT,SOURCE,TARGETS,OFFSET,World,Region,STAGE,scene,
 state_json,nbt_state,block_string,coordinates,zip_bytes,translated_uuid,support_of,box_distance)
from klut27_fire_model import flammable,fire_distances,DIRS,touches

NEW_ELEVATOR=(8,15,20)
SEED=(5,11,19)
LEVER=(6,12,19)

def block_entity(world,p):
 _,_,c=world.chunk(p[0],p[2])
 return next((copy.deepcopy(e) for e in c['block_entities'] if tuple(int(e[a]) for a in ('x','y','z'))==p),None)

def synchronize():
 source=World(SOURCE);reference=World(TARGETS[0],OFFSET);changes=[]
 for y in range(-40,46):
  for z in range(-2,51):
   for x in range(-5,25):
    p=(x,y,z);a=state_json(source.get(p));b=state_json(reference.get(p))
    if a!=b:changes.append({'pos':list(p),'before':b,'after':a})
 elevator_state=state_json(source.get((8,10,20)));elevator_nbt=block_entity(source,(8,10,20))
 assert elevator_nbt is not None and 'lock' in elevator_nbt
 for world,offset in [(SOURCE,0)]+[(w,OFFSET) for w in TARGETS]:
  w=World(world,offset)
  for change in (changes if offset else [])+[{'pos':list(NEW_ELEVATOR),'after':elevator_state}]:
   p=tuple(change['pos']);w.set(p,nbt_state(change['after']));r,slot,c=w.chunk(p[0],p[2]);dst=(p[0]+offset,p[1],p[2]+offset)
   bes=c['block_entities'];bes[:]=[e for e in bes if tuple(int(e[a]) for a in ('x','y','z'))!=dst]
   be=copy.deepcopy(elevator_nbt) if p==NEW_ELEVATOR else block_entity(source,p)
   if be is not None:
    for a,v in zip(('x','y','z'),dst):be[a]=nbt.Int(v)
    bes.append(be)
   r.dirty.add(slot)
  for p,data in w.outputs().items():p.write_bytes(data)
  if offset:
   p=world/'datapacks/mcm.zip'
   with zipfile.ZipFile(p) as z:files={n:z.read(n)for n in z.namelist()}
   key='data/klut27/function/restore_blocks.mcfunction';lines=files[key].decode().splitlines()
   for change in changes:
    prefix='setblock '+coordinates(change['pos'],offset)+' '
    lines=[prefix+block_string(change['after']) if line.startswith(prefix) else line for line in lines]
   files[key]=('\n'.join(lines)+'\n').encode();p.write_bytes(zip_bytes(files))
 record=ROOT/'docs/arenas/klut27-large-fire-sync.json'
 if changes or not record.exists():record.write_text(json.dumps({'changes':changes,'new_elevator':NEW_ELEVATOR},indent=2)+'\n',encoding='utf-8')

def saved_entities():
 result=[]
 for p in (SOURCE/'entities').glob('r.*.mca'):
  if p.stat().st_size<8192:continue
  r=Region(p)
  for slot in range(1024):
   c=r.get(slot)
   if c:result.extend(copy.deepcopy(list(c.get('Entities',[]))))
 return result

def entity_uuid(e,offset):
 ints=translated_uuid(list(map(int,e['UUID'])),offset)
 return str(uuid.UUID(bytes=b''.join(v.to_bytes(4,'big',signed=True)for v in ints)))

def translated(e,offset):
 e=copy.deepcopy(e);e['UUID']=nbt.IntArray(translated_uuid(list(map(int,e['UUID'])),offset))
 e['Pos'][0]+=offset;e['Pos'][2]+=offset
 if offset:
  tags=list(map(str,e.get('Tags',[])))
  if 'Klut27Decoration' not in tags:tags.append('Klut27Decoration')
  e['Tags']=nbt.List[nbt.String](tags)
 for key in ('TileX','TileZ'):
  if key in e:e[key]=nbt.Int(int(e[key])+offset)
 e['DeathTime']=nbt.Short(0);e['HurtTime']=nbt.Short(0)
 if str(e['id'])=='minecraft:villager':e['Health']=nbt.Float(max(20,float(e.get('Health',20))))
 return e

def generate(offset):
 blocks=scene();world=World(SOURCE);dist=fire_distances(blocks,[SEED]);points=sorted(dist);ids={p:i for i,p in enumerate(points)}
 elevators=sorted(p for p,s in blocks.items() if s['Name']=='minecraft:white_shulker_box' and block_entity(world,p) is not None and 'lock' in block_entity(world,p))
 vulnerable=[p for p in elevators if any(touches(p,q)for q in points)]
 blast={e:{p for p,s in blocks.items()if flammable(s)and box_distance(p,e)<=2}for e in vulnerable}
 dependencies=defaultdict(set)
 for p,s in blocks.items():
  support=support_of(p,s)
  if support:dependencies[support].add(p)
  if s['Name'].endswith('_door') and s.get('Properties',{}).get('half')=='upper':dependencies[(p[0],p[1]-1,p[2])].add(p)
 def removed(cells):
  result=set(cells);q=deque(result)
  while q:
   for p in dependencies[q.popleft()]-result:result.add(p);q.append(p)
  return result
 affected=removed(set(points)|set().union(*blast.values()))|set(vulnerable)|{LEVER}
 entities=saved_entities();decor=[];villagers=[]
 for e in entities:
  if str(e['id'])=='minecraft:villager':villagers.append(e)
  if str(e['id'])in('minecraft:item_frame','minecraft:glow_item_frame','minecraft:painting') and all(k in e for k in ('TileX','TileY','TileZ')):
   p=tuple(int(e[k])for k in ('TileX','TileY','TileZ'));face=int(e.get('Facing',e.get('facing',0)))
   d=((0,-1,0),(0,1,0),(0,0,-1),(0,0,1),(-1,0,0),(1,0,0))[face];support=tuple(p[i]-d[i]for i in range(3))
   if support in affected:decor.append((support,e))
 files={}
 def fn(name,lines):files[f'data/klut27/function/fire/{name}.mcfunction']=('\n'.join(lines)+'\n').encode('utf-8')
 def pos(p,center=False):return coordinates(p,offset,center)
 before=['execute store result score $tile kf run gamerule doTileDrops','execute store result score $entity kf run gamerule doEntityDrops','execute store result score $mob kf run gamerule doMobLoot','gamerule doTileDrops false','gamerule doEntityDrops false','gamerule doMobLoot false']
 after=['execute if score $tile kf matches 1 run gamerule doTileDrops true','execute if score $entity kf matches 1 run gamerule doEntityDrops true','execute if score $mob kf matches 1 run gamerule doMobLoot true']
 def erase(cells):
  allcells=removed(cells)
  lines=[f'kill {entity_uuid(e,offset)}'for support,e in decor if support in allcells]
  for p in sorted(allcells,key=lambda p:-p[1]):
   if block_entity(world,p) is not None:lines.append(f'data remove block {pos(p)} Items')
   lines.append(f'setblock {pos(p)} air')
   if p in ids:lines.append(f'scoreboard players set @e[tag=Klut27Fire{ids[p]}] kf_age -1')
  return lines
 flags=[f'scoreboard players set $boom{i} kf 0'for i in range(len(vulnerable))]
 flags += [f'scoreboard players set $villager{i} kf 0'for i in range(len(villagers))]
 fn('migrate',['kill @e[type=marker,tag=Klut27Fire]','scoreboard players set $state kf 0','scoreboard players set $version kf 2']+flags)
 fn('load',['scoreboard objectives add kf dummy','scoreboard objectives add kf_age dummy','execute unless score $version kf matches 2 run function klut27:fire/migrate'])
 gates=['execute unless score $selectedMap CmdData matches 20 run return 0','execute unless score $gamestate CmdData matches 1 run return 0','execute unless score $pickedroles CmdData matches 1 run return 0','execute if score $graceperiod CmdData matches 1.. run return 0']if offset else []
 fn('tick',gates+['execute if score $state kf matches 1 run function klut27:fire/advance',f'execute if score $state kf matches 0 if block {pos(LEVER)} lever[powered=true] run function klut27:fire/start'])
 fn('start',['execute unless score $state kf matches 0 run return 0','scoreboard players set $state kf 1','kill @e[type=marker,tag=Klut27Fire]']+flags+
  [f'summon marker {pos(p,True)} {{Tags:["Klut27Fire","Klut27Fire{i}"],data:{{cell:{i}}}}}'for p,i in ids.items()]+
  ['scoreboard players set @e[tag=Klut27Fire] kf_age 0',f'scoreboard players set @e[tag=Klut27Fire{ids[SEED]}] kf_age 1','function klut27:fire/check_elevators'])
 fn('dispatch',['$function klut27:fire/cell/$(cell)'])
 fn('skip',['scoreboard players set @s kf_age -1'])
 fn('finish',['scoreboard players set $state kf 2','kill @e[type=marker,tag=Klut27Fire]'])
 fn('advance',['scoreboard players add @e[tag=Klut27Fire,scores={kf_age=1..60}] kf_age 1',
  'execute as @e[tag=Klut27Fire,scores={kf_age=1..60}] at @s run particle flame ~ ~0.3 ~ 0.3 0.35 0.3 0.01 2 force',
  'execute as @e[tag=Klut27Fire,scores={kf_age=1..60}] at @s run particle smoke ~ ~0.5 ~ 0.2 0.3 0.2 0.01 1 force',
  'execute as @e[tag=Klut27Fire,scores={kf_age=61}] at @s run function klut27:fire/dispatch with entity @s data',
  'function klut27:fire/check_elevators','execute unless entity @e[tag=Klut27Fire,scores={kf_age=1..60}] run function klut27:fire/finish'])
 def ignite_neighbors(cells,excluded=set()):
  candidates={tuple(p[i]+d[i]for i in range(3))for p in cells for d in DIRS}-excluded
  return [f'execute if block {pos(n)} {blocks[n]["Name"]} run scoreboard players set @e[tag=Klut27Fire{ids[n]},scores={{kf_age=0}}] kf_age 1'for n in sorted(candidates)if n in ids]
 ashes={p for p in points if p[1]==11 and p[2]%2==0 and blocks.get((p[0],p[1]-1,p[2]),{}).get('Name','').endswith('terracotta')}
 for p,i in ids.items():
  fn(f'cell/{i}',[f'execute unless block {pos(p)} {blocks[p]["Name"]} run return run function klut27:fire/skip','scoreboard players set @s kf_age -1']+before+erase({p})+after+
   ([f'setblock {pos(p)} black_carpet']if p in ashes else [])+ignite_neighbors({p}))
 files['data/klut27/tags/block/fire_fuel.json']=json.dumps({'values':sorted({blocks[p]['Name']for p in points})}).encode()
 checks=['execute as @e[tag=Klut27Fire,scores={kf_age=1..60}] at @s unless block ~ ~ ~ #klut27:fire_fuel run scoreboard players set @s kf_age -1']
 for i,e in enumerate(vulnerable):
  x,y,z=e
  checks.append(f'execute unless score $boom{i} kf matches 1 if block {pos(e)} white_shulker_box if entity @e[type=marker,tag=Klut27Fire,x={x+offset-1},y={y-1},z={z+offset-1},dx=2,dy=2,dz=2,scores={{kf_age=1..60}}] run function klut27:fire/explode/{i}')
  lines=[f'execute if score $boom{i} kf matches 1 run return 0',f'scoreboard players set $boom{i} kf 1']+before+erase(blast[e])+[f'data remove block {pos(e)} Items',f'setblock {pos(e)} black_wool']
  for j,v in enumerate(villagers):
   uid=translated(v,offset)['UUID'].snbt()
   lines.append(f'execute positioned {pos(e,True)} if entity @e[type=villager,nbt={{UUID:{uid}}},distance=..3] run scoreboard players set $villager{j} kf 1')
  lines += [f'execute positioned {pos(e,True)} run tag @e[type=villager,distance=..3] add Klut27Blasted',f'execute positioned {pos(e,True)} run kill @e[type=villager,distance=..3]']+after+ignite_neighbors(blast[e],removed(blast[e]))
  lines += [f'particle explosion_emitter {pos(e,True)} 0 0 0 0 1 force',f'playsound entity.generic.explode master @a {pos(e,True)} 1 1']
  if offset:lines += [f'execute positioned {pos(e,True)} as @a[tag=queued,tag=!spectating,gamemode=!spectator,distance=..3] at @s unless score @s dead matches 1.. run function klut27:fire/death']
  else:lines += [f'execute positioned {pos(e,True)} run kill @a[gamemode=!creative,gamemode=!spectator,distance=..3]']
  fn(f'explode/{i}',lines)
 fn('check_elevators',checks)
 fn('death',['tellraw @a [{"selector":"@s"},{"text":"被电梯爆炸炸飞了！","color":"red"}]','function mcm:game/playerdeath']if offset else [])
 reset=['kill @e[type=marker,tag=Klut27Fire]','scoreboard players set $state kf 0']+before
 for p in sorted(affected,key=lambda p:(support_of(p,blocks.get(p,{'Name':'minecraft:air'}))is not None,p[1],p[0],p[2])):
  reset += [f'data remove block {pos(p)} Items',f'setblock {pos(p)} {block_string(blocks.get(p,{"Name":"minecraft:air"}))}']
  be=block_entity(world,p)
  if be is not None:
   for a in ('x','y','z'):be.pop(a,None)
   reset.append(f'data merge block {pos(p)} {be.snbt()}')
 def restore_entity(e,condition=''):
  e=translated(e,offset);uid=str(uuid.UUID(bytes=b''.join(int(v).to_bytes(4,'big',signed=True)for v in e['UUID'])))
  original_pos=e['Pos'];position=' '.join(str(float(v))for v in original_pos);kind=str(e.pop('id'))
  summon=f'execute {condition}unless entity {uid} run summon {kind} {position} {e.snbt()}'
  e.pop('UUID',None);e['Pos']=original_pos
  return [summon,f'execute {condition}as {uid} if entity @s[tag=Klut27Blasted] run data merge entity @s {e.snbt()}',f'execute {condition}as {uid} run tag @s remove Klut27Blasted']
 for _,e in decor:reset+=restore_entity(e)
 for i,e in enumerate(villagers):reset+=restore_entity(e,f'if score $villager{i} kf matches 1 ')
 reset+=after+flags;fn('reset',reset)
 manifest={'trigger':'26-neighbour burning-block contact','seconds_per_block':3,'seed':SEED,'fire_cells':points,'elevators':vulnerable,'all_elevators':elevators,'affected_cells':sorted(affected),'blast_cells':{str(e):sorted(v)for e,v in blast.items()},'decor_entities':len(decor),'villager_snapshots':len(villagers),'ashes':sorted(ashes),'max_distance_steps':max(dist.values())}
 return files,manifest

if __name__=='__main__':
 synchronize()
 from klut27_engineer_fire import install_fire
 install_fire()
