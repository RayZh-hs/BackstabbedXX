"""Bounded KLUT-27 merchant/NPC patch and deterministic, resettable fire.

Standalone coordinates throughout; translate only when emitting or applying.
Back up all three saves before --apply. No mod runtime changes are needed.
"""
import argparse, copy, json, math, zipfile
from klut27_fire_model import flammable, fire_distances, DIRS
from pathlib import Path
import nbtlib as nbt
from sync_klut27_standalone import ROOT, SOURCE, TARGETS, OFFSET, World, state_json, nbt_state, block_string, zip_bytes
from repair_klut27_decor import Region, translated_uuid

ENGINEER=[-82225078,680807956,-1400694282,-1054805724]
RESIDENT=[-887769658,-177321878,-1634696109,-940362132]
GOLEM=[-1320801167,-901363419,-1545393136,-561806550]
LEVER=(6,12,19)
SIGN=(6,13,19)
ELEVATOR=(8,15,20)
STAGE=ROOT/'map-previewer/maps/klut27/engineer-fire'
WOOD=('oak','spruce','birch','jungle','acacia','dark_oak','mangrove','cherry','pale_oak','bamboo')
DIRS=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))

def hook_data(upgraded=False):
 d={'klut27_hook':nbt.Byte(1),'NoDrop':nbt.Byte(1),'no_drop_on_death':nbt.Byte(1),'klut27_innocent':nbt.Byte(1)}
 if upgraded:d['klut27_upgraded']=nbt.Byte(1)
 return nbt.Compound(d)

def offers():
 def item(id,count=1,components=None):
  d=nbt.Compound({'id':nbt.String(id),'count':nbt.Int(count)})
  if components:d['components']=nbt.Compound(components)
  return d
 fake=item('minecraft:stick',components={'minecraft:item_model':nbt.String('minecraft:role_items/gun'),'minecraft:max_stack_size':nbt.Int(1),'minecraft:custom_data':nbt.Compound({'klut27_toy_gun':nbt.Byte(1)}),'minecraft:custom_name':nbt.String(json.dumps({'text':'玩具枪','italic':False},ensure_ascii=False))})
 base=item('gravity_changer:grappling_hook',components={'minecraft:custom_data':hook_data()})
 upgrade=item('gravity_changer:grappling_hook',components={'minecraft:custom_data':hook_data(True),'minecraft:custom_name':nbt.String(json.dumps({'text':'升级重力钩爪','color':'aqua','italic':False},ensure_ascii=False)),'minecraft:max_stack_size':nbt.Int(1),'minecraft:item_model':nbt.String('gravity_changer:grappling_hook')})
 result=[]
 for price,sell,buyB in [(4,fake,None),(5,upgrade,base)]:
  r=nbt.Compound({'buy':item('minecraft:netherite_scrap',price),'sell':sell,'uses':nbt.Int(0),'maxUses':nbt.Int(2147483647),'rewardExp':nbt.Byte(0),'xp':nbt.Int(0),'demand':nbt.Int(0),'specialPrice':nbt.Int(0),'priceMultiplier':nbt.Float(0)})
  if buyB:r['buyB']=buyB
  result.append(r)
 return result

def scene():
 w=World(SOURCE);blocks={}
 for y in range(-40,46):
  for z in range(-2,51):
   for x in range(-5,25):
    s=state_json(w.get((x,y,z)))
    if s['Name']!='minecraft:air':blocks[(x,y,z)]=s
 return blocks

def sign_nbt(pos):
 text=json.dumps({'text':'don’t switch！','color':'black'},ensure_ascii=False)
 # Ordinary hanging-sign width needs two lines to keep the warning legible.
 lines=[json.dumps({'text':'don’t'},ensure_ascii=False),json.dumps({'text':'switch！'},ensure_ascii=False),'""','""']
 face=nbt.Compound({'messages':nbt.List[nbt.String](lines),'color':nbt.String('black'),'has_glowing_text':nbt.Byte(0)})
 return nbt.Compound({'id':nbt.String('minecraft:hanging_sign'),'x':nbt.Int(pos[0]),'y':nbt.Int(pos[1]),'z':nbt.Int(pos[2]),'front_text':face,'back_text':copy.deepcopy(face),'is_waxed':nbt.Byte(1)})

def prepare():
 blocks=scene();blocks[SIGN]={'Name':'minecraft:oak_hanging_sign','Properties':{'attached':'false','rotation':'12','waterlogged':'false'}}
 seeds=[(5,11,19)];dist=fire_distances(blocks,seeds)
 STAGE.mkdir(parents=True,exist_ok=True)
 rows=[[[p[0]+5,p[1]+40,p[2]+2],block_string(s)] for p,s in blocks.items()]
 (STAGE/'blocks.json').write_text(json.dumps(rows),encoding='utf-8')
 (STAGE/'preview.mjs').write_text("import fs from 'node:fs'; export default function(api){const s=api.createStructure([30,86,53]);for(const [p,b] of JSON.parse(fs.readFileSync(new URL('./blocks.json',import.meta.url),'utf8')))api.setBlock(s,p,b);return {structure:s,metadata:{name:'klut27-engineer-fire'}};}",encoding='utf-8')
 print('Connected flammable cells:',len(dist),'max steps:',max(dist.values(),default=0))
 print('Closest cells to elevator:', sorted([(sum((p[i]-ELEVATOR[i])**2 for i in range(3))**.5,p,d) for p,d in dist.items()])[:10])
 return blocks,dist

def patch_entities(world,offset):
 regions={};found={};ids={name:translated_uuid(value,offset) for name,value in [('engineer',ENGINEER),('resident',RESIDENT),('golem',GOLEM)]}
 for path in (world/'entities').glob('r.*.mca'):
  # Scan only the imported arena's entity regions.
  rx,rz=map(int,path.stem.split('.')[1:]);base=offset//512
  if rx not in (base-1,base) or rz not in (base-1,base):continue
  r=Region(path);regions[path]=r
  for slot in range(1024):
   c=r.get(slot)
   if c is None:continue
   for e in list(c.get('Entities',[])):
    for name,uid in ids.items():
     if list(e.get('UUID',[]))==uid:
      assert name not in found,('duplicate',name)
      found[name]=(r,slot,e)
 assert 'engineer' in found and 'golem' in found,found.keys()
 if 'resident' in found:
  r,slot,e=found['resident'];r.get(slot)['Entities'].remove(e);r.dirty.add(slot)
 r,slot,e=found['engineer'];r.get(slot)['Entities'].remove(e);r.dirty.add(slot)
 e['Pos']=nbt.List[nbt.Double]([offset+12.5,15,offset+33.5]);e['Rotation']=nbt.List[nbt.Float]([180,0]);e['Motion']=nbt.List[nbt.Double]([0,0,0]);e['NoAI']=nbt.Byte(1);e['PersistenceRequired']=nbt.Byte(1);e['Invulnerable']=nbt.Byte(0)
 e['Offers']=nbt.Compound({'Recipes':nbt.List[nbt.Compound](offers())});e['Health']=nbt.Float(1000)
 e['attributes']=nbt.List[nbt.Compound]([nbt.Compound({'id':nbt.String('minecraft:max_health'),'base':nbt.Double(1000)})])
 tags=list(map(str,e.get('Tags',[])));e['Tags']=nbt.List[nbt.String](tags+([] if 'Klut27Engineer' in tags else ['Klut27Engineer']))
 cx,cz=(offset+12)//16,(offset+33)//16;path=world/'entities'/f'r.{cx//32}.{cz//32}.mca';dest=regions[path];target=(cz%32)*32+cx%32
 dest.get(target)['Entities'].append(e);dest.dirty.add(target)
 gr,gs,g=found['golem'];g['PlayerCreated']=nbt.Byte(0);g['Invulnerable']=nbt.Byte(0);g['PersistenceRequired']=nbt.Byte(1)
 # Let the hurt advancement perform minigame elimination before vanilla health
 # damage can send a low-health player to a death screen.
 g['Health']=nbt.Float(1000);g['attributes']=nbt.List[nbt.Compound]([nbt.Compound({'id':nbt.String('minecraft:max_health'),'base':nbt.Double(1000)}),nbt.Compound({'id':nbt.String('minecraft:attack_damage'),'base':nbt.Double(0.000001)}),nbt.Compound({'id':nbt.String('minecraft:follow_range'),'base':nbt.Double(64)})])
 gt=list(map(str,g.get('Tags',[])));g['Tags']=nbt.List[nbt.String](gt+([] if 'Klut27Golem' in gt else ['Klut27Golem']));gr.dirty.add(gs)
 for p,r in regions.items():
  if r.dirty:p.write_bytes(r.encoded())
 return copy.deepcopy(e),copy.deepcopy(g)

def combat_files():
 files={}
 def fn(name,body):files[f'data/klut27/function/{name}.mcfunction']=(body.strip()+'\n').encode('utf-8')
 shot={'direct_entity':{'type':'minecraft:arrow','nbt':'{Tags:["GunShot"]}'}}
 for name,trigger,conditions,body in [
  ('villager_shot','minecraft:player_hurt_entity',{'entity':{'type':'minecraft:villager'},'damage':{'type':shot}},'''execute unless entity @s[tag=innocent,tag=gunner,tag=queued,tag=!spectating,tag=!murderer] run return 0
execute if score @s dead matches 1.. run return 0
function mcm:game/innocentshot'''),
  ('golem_hit','minecraft:entity_hurt_player',{'damage':{'type':{'direct_entity':{'type':'minecraft:iron_golem','nbt':'{Tags:["Klut27Golem"]}'}}}},'''execute unless entity @s[tag=queued,tag=!spectating,gamemode=!spectator] run return 0
execute if score @s dead matches 1.. run return 0
tellraw @a [{"selector":"@s"},{"text":"被铁哥一巴掌扇飞了！","color":"red"}]
function mcm:game/playerdeath''')]:
  adv={'criteria':{'hit':{'trigger':trigger,'conditions':conditions}},'rewards':{'function':'klut27:'+name}}
  files[f'data/klut27/advancement/{name}.json']=(json.dumps(adv,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
  fn(name,f'''advancement revoke @s only klut27:{name}
execute unless score $selectedMap CmdData matches 20 run return 0
execute unless score $gamestate CmdData matches 1 run return 0
execute unless score $pickedroles CmdData matches 1 run return 0
execute if score $graceperiod CmdData matches 1.. run return 0
'''+body)
 fn('npc_tick','''execute as @e[type=villager,tag=Klut27Engineer,tag=!Klut27Blasted] run data merge entity @s {Health:1000.0f,Gossips:[]}
execute as @e[type=iron_golem,tag=Klut27Golem] run data merge entity @s {Health:1000.0f}''')
 return files

def coordinates(p,offset,center=False):
 return ' '.join(str(p[i]+(offset if i!=1 else 0)+(.5 if center else 0)) for i in range(3))

def patch_sign(world,offset):
 w=World(world,offset);w.set(SIGN,nbt_state({'Name':'minecraft:oak_hanging_sign','Properties':{'attached':'false','rotation':'12','waterlogged':'false'}}))
 r,slot,c=w.chunk(SIGN[0],SIGN[2]);pos=(SIGN[0]+offset,SIGN[1],SIGN[2]+offset)
 bes=c['block_entities'];bes[:]=[e for e in bes if tuple(int(e[a]) for a in ('x','y','z'))!=pos];bes.append(sign_nbt(pos));r.dirty.add(slot)
 for p,data in w.outputs().items():p.write_bytes(data)

def support_of(p,s):
 """Fragile decoration support; used before removing wood, not a radius wipe."""
 name=s['Name'].split(':')[-1];props=s.get('Properties',{})
 directions={'north':(0,0,-1),'south':(0,0,1),'east':(1,0,0),'west':(-1,0,0)}
 def shift(d):return tuple(p[i]+d[i] for i in range(3))
 if '_wall_' in name or name in ('ladder','tripwire_hook') or (name.endswith(('_button','lever')) and props.get('face')=='wall'):
  d=directions.get(props.get('facing'))
  return shift(tuple(-v for v in d)) if d else None
 if name.endswith('_hanging_sign') or (name in ('lantern','soul_lantern') and props.get('hanging')=='true') or props.get('face')=='ceiling':return shift((0,1,0))
 if name.endswith('_door') and props.get('half')=='lower':return shift((0,-1,0))
 if name.endswith(('_carpet','_banner','_sign','_pressure_plate','_button')) or name in ('lever','torch','redstone_torch','flower_pot','lantern','soul_lantern') or name.startswith('potted_'):return shift((0,-1,0))
 return None

def removals(blocks,seeds):
 result=set(seeds)
 while True:
  extra={p for p,s in blocks.items() if support_of(p,s) in result}-result
  # Paired doors are removed together, including the upper half.
  for p in list(result):
   s=blocks.get(p,{})
   if s.get('Name','').endswith('_door'):
    dy=1 if s.get('Properties',{}).get('half')=='lower' else -1
    n=(p[0],p[1]+dy,p[2])
    if blocks.get(n,{}).get('Name')==s['Name'] and n not in result:extra.add(n)
  if not extra:return result
  result|=extra

def box_distance(p,q):
 # Distance from block p's volume to the centre of block q.
 return math.sqrt(sum(max(abs(p[i]-q[i])-.5,0)**2 for i in range(3)))

def fire_files(offset):
 from rebuild_klut27_fire import generate
 return generate(offset)

def install_fire():
 for world,offset in [(SOURCE,0)]+[(w,OFFSET) for w in TARGETS]:
  additions,manifest=fire_files(offset)
  if offset:
   p=world/'datapacks/mcm.zip'
   with zipfile.ZipFile(p) as z:files={n:z.read(n) for n in z.namelist()}
   for name,line in [('load','function klut27:fire/load'),('functionality','function klut27:fire/tick'),('reset','function klut27:fire/reset'),('activate','function klut27:fire/reset')]:
    key=f'data/{"mcm" if name=="load" else "klut27"}/function/{name}.mcfunction';body=files[key].decode()
    if name in ('reset','activate'):
     body=body.replace(line+'\n','')
     body=body.replace('function klut27:restore_blocks',line+'\nfunction klut27:restore_blocks')
     files[key]=body.encode()
    elif line not in body:files[key]=(body.rstrip()+'\n'+line+'\n').encode()
  else:
   p=world/'datapacks/klut27-fire.zip';files={'pack.mcmeta':json.dumps({'pack':{'pack_format':61,'description':'KLUT-27 scripted fire'}}).encode(),'data/minecraft/tags/function/load.json':b'{"values":["klut27:fire/load"]}','data/minecraft/tags/function/tick.json':b'{"values":["klut27:fire/tick"]}'}
  files={n:b for n,b in files.items() if not n.startswith('data/klut27/function/fire/')}
  files.update(additions)
  if not offset and (world/'datapacks/klut27-residents.zip').exists():
   files['data/klut27/function/fire/reset.mcfunction']+=b'function klut27:residents/reset\n'
  key='data/klut27/function/npc_tick.mcfunction'
  if key in files:files[key]=files[key].replace(b'tag=Klut27Engineer]',b'tag=Klut27Engineer,tag=!Klut27Blasted]')
  p.write_bytes(zip_bytes(files))
  if not offset:enable_pack(world,'klut27-fire.zip')
 (ROOT/'docs/arenas/klut27-fire.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')

def install_npcs():
 import klut27_datapack_hook_cooldown
 klut27_datapack_hook_cooldown.install()
 for world,offset in [(SOURCE,0)]+[(w,OFFSET) for w in TARGETS]:
  patch_sign(world,offset);engineer,golem=patch_entities(world,offset)
  reset=[]
  for e,tag,position in [(engineer,'Klut27Engineer',(12.5,15,33.5)),(golem,'Klut27Golem',(9.5,15,45.5))]:
   e['Pos']=nbt.List[nbt.Double]([position[0]+offset,position[1],position[2]+offset]);e['Motion']=nbt.List[nbt.Double]([0,0,0]);e['AngerTime']=nbt.Int(0)
   for key in ['AngryAt','Brain','HurtByTimestamp','DeathTime','HurtTime']:e.pop(key,None)
   summon=copy.deepcopy(e);id=str(summon.pop('id'));summon.pop('Pos',None)
   merge=copy.deepcopy(e)
   for key in ['UUID','id']:merge.pop(key,None)
   reset += [f'execute unless entity @e[tag={tag}] run summon {id} {coordinates(position,offset)} {summon.snbt()}',f'execute as @e[tag={tag}] run data remove entity @s AngryAt',f'execute as @e[tag={tag}] run data merge entity @s {merge.snbt()}']
  additions=combat_files();additions['data/klut27/function/npc_reset.mcfunction']=('\n'.join(reset)+'\n').encode('utf-8')
  if offset:
   p=world/'datapacks/mcm.zip'
   with zipfile.ZipFile(p) as z:files={n:z.read(n) for n in z.namelist()}
   files.update(additions)
   for name,line in [('functionality','function klut27:npc_tick'),('reset','function klut27:npc_reset'),('activate','function klut27:npc_reset')]:
    key=f'data/klut27/function/{name}.mcfunction';body=files[key].decode()
    if line not in body:files[key]=(body.rstrip()+'\n'+line+'\n').encode()
   p.write_bytes(zip_bytes(files))
  else:
   # No minigame roles in the standalone building save; keep scene and trades.
   additions={n:b for n,b in additions.items() if 'npc_' in n}
   additions['data/klut27/advancement/golem_hit.json']=combat_files()['data/klut27/advancement/golem_hit.json']
   additions['data/klut27/function/golem_hit.mcfunction']='advancement revoke @s only klut27:golem_hit\nexecute if entity @s[gamemode=spectator] run return 0\ntellraw @a [{"selector":"@s"},{"text":"被铁哥一巴掌扇飞了！","color":"red"}]\nkill @s\n'.encode('utf-8')
   additions['pack.mcmeta']=json.dumps({'pack':{'pack_format':61,'description':'KLUT-27 engineer scene'}}).encode()
   additions['data/minecraft/tags/function/tick.json']=b'{"values":["klut27:npc_tick"]}'
   (world/'datapacks/klut27-engineer.zip').write_bytes(zip_bytes(additions))
   enable_pack(world,'klut27-engineer.zip')

def enable_pack(world,name):
 level=nbt.load(world/'level.dat');data=level['Data']['DataPacks'];key='file/'+name
 if key not in data['Enabled']:data['Enabled'].append(nbt.String(key))
 data['Disabled']=nbt.List[nbt.String]([v for v in data.get('Disabled',[]) if str(v)!=key]);level.save(world/'level.dat')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--npcs',action='store_true');parser.add_argument('--fire',action='store_true');args=parser.parse_args()
 if args.npcs:install_npcs()
 elif args.fire:install_fire()
 else:prepare()
