#!/usr/bin/env python3
"""Install the maintained treehouse namespace and narrowly scoped shared lifecycle hooks."""
from pathlib import Path
import copy,hashlib,json,math,sys,zipfile
import nbtlib as n
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'arena-editor'))
from world import stopped
SAVE=ROOT/'.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
BASE=ROOT/'axolotl-treehouse';NS='axolotl_treehouse';TAG='AxolotlTreehouse';MID=25
m=json.loads((ROOT/'docs/arenas/axolotl_treehouse.json').read_text())
def write(rel,text):
 p=BASE/'datapack'/f'data/{NS}'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.rstrip()+'\n')
def fn(name,text):write('function/'+name+'.mcfunction',text)
def loc(position):return {'condition':'minecraft:location_check','predicate':{'dimension':'minecraft:overworld','position':position}}
def box(x1,y1,z1,x2,y2,z2):return loc({a:{'min':lo,'max':hi}for a,lo,hi in zip('xyz',[x1,y1,z1],[x2,y2,z2])})
center=m['center'][0];r=m['forceload'];rect=' '.join(map(str,r))
fn('register',f'execute unless entity @e[type=marker,tag=MapVote,tag={TAG}] run summon marker 0 -50 70 {{Tags:["MapVote","{TAG}"]}}\nscoreboard players set @e[type=marker,tag=MapVote,tag={TAG}] MapValues {MID}\nfunction mcm:lobby/options/map_toggle/init')
activate=[f'execute unless score $selectedMap CmdData matches {MID} run return 0','execute unless score $gamestate CmdData matches 0..1 run return 0',f'forceload add {rect}','kill @e[tag=MapEntity]',f'tag @a remove {TAG}Participant']
for x,y,z in m['spawns']:activate.append(f'summon marker {x} {y} {z} {{Tags:["MapEntity","{TAG}Runtime","PlayerSpawn","ScrapSpawn"]}}')
x,y,z=m['spectator'];activate+=[f'summon marker {x} {y} {z} {{Tags:["MapEntity","{TAG}Runtime","SpectatorSpawn"]}}',f'tellraw @a {{"translate":"{NS}.ready","color":"aqua"}}']
fn('activate','\n'.join(activate))
fn('functionality',f'execute unless score $selectedMap CmdData matches {MID} run return 0\nexecute unless score $gamestate CmdData matches 1 run return 0\nexecute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. run function {NS}:check_player')
fn('check_player',f'tag @s add {TAG}Participant\n# Falling to lake level outside the island is lethal from round start, including grace.\n# There is deliberately no water/fluid contact check. Island ponds and waterfalls are safe.\nexecute if predicate {NS}:lake_fall run return run function mcm:game/playerdeath\nexecute unless predicate {NS}:arena run return run function {NS}:escape')
fn('escape',f'execute if score $graceperiod CmdData matches 1.. run return run function {NS}:return_player\nfunction mcm:game/playerdeath')
x,y,z=m['safe_return'];fn('return_player',f'gravity bridge reset @s\nexecute in minecraft:overworld run tp @s {x} {y} {z}')
fn('waiting_tick',f'execute unless score $selectedMap CmdData matches {MID} run return 0\nexecute unless score $gamestate CmdData matches 0 run return 0\nexecute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s if predicate {NS}:arena run tag @s add {TAG}Participant\nexecute as @a[tag=queued,tag={TAG}Participant,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. if predicate {NS}:lake_fall run function {NS}:return_player\nexecute as @a[tag=queued,tag={TAG}Participant,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. unless predicate {NS}:arena run function {NS}:return_player')
fn('reset',f'kill @e[tag={TAG}Runtime]\nschedule clear {NS}:activate\nforceload remove {rect}\ntag @a remove {TAG}Participant')
# Derive membership from the actual terrain and dock boards, excluding canopies,
# plants and protruding branches. Preserve gaps as separate intervals in each row.
land=n.load(ROOT/'map-previewer/maps/axolotl-treehouse/build/treehouse-island.nbt')
ground={'stone','dirt','grass_block','coarse_dirt','dirt_path','gravel','andesite','cobblestone','mossy_cobblestone','spruce_planks','spruce_stairs','farmland'}
mask=set()
for b in land['blocks']:
 x,y,z=map(int,b['pos']);name=str(land['palette'][int(b['state'])]['Name']).split(':')[1]
 if y+48>=64 and name in ground:mask.add((x-64,z-64))
terms=[];rows=[]
for z in sorted({z for x,z in mask}):
 xs=sorted(x for x,zz in mask if zz==z);start=last=xs[0]
 for x in xs[1:]+[xs[-1]+2]:
  if x!=last+1:
   rows.append([center+start,center+z,center+last])
   terms.append(loc({'x':{'min':center+start,'max':center+last+.999999},'z':{'min':center+z,'max':center+z+.999999}}));start=x
  last=x
island={'condition':'minecraft:any_of','terms':terms}
lake={'condition':'minecraft:all_of','terms':[{'condition':'minecraft:inverted','term':island},loc({'y':{'max':64.0}})]}
arena=box(center-64,63,center-64,center+63.999999,150,center+63.999999)
for name,value in [('island',island),('lake_fall',lake),('arena',arena)]:write('predicate/'+name+'.json',json.dumps(value,separators=(',',':')))
pack=SAVE/'datapacks/mcm.zip'
with zipfile.ZipFile(pack)as z:
 entries={i.filename:(i,z.read(i))for i in z.infolist()}
def text(path):return entries['data/mcm/function/'+path+'.mcfunction'][1].decode()
def update(path,value):
 key='data/mcm/function/'+path+'.mcfunction';entries[key]=(entries[key][0],value.encode())
def append(path,line):
 t=text(path)
 if line not in t:update(path,t.rstrip()+'\n\n'+line+'\n')
def before(path,anchor,line):
 t=text(path)
 if line not in t:
  assert anchor in t,(path,anchor);update(path,t.replace(anchor,line+'\n'+anchor,1))
for p in (BASE/'datapack').rglob('*'):
 if p.is_file():entries[p.relative_to(BASE/'datapack').as_posix()]=(None,p.read_bytes())
select=entries['data/monolith/function/select.mcfunction'][1].decode().replace('monolith',NS).replace('Monolith',TAG)
fn('select',select);entries[f'data/{NS}/function/select.mcfunction']=(None,select.encode())
append('respawn_entities',f'function {NS}:register')
before('load','execute unless score $gamestate CmdData matches ..0 run return 1',f'schedule function {NS}:register 1s')
append('lobby/voting/end',f'execute if entity @e[type=marker,tag=SelectedMap,tag={TAG}] run forceload add {rect}\nexecute if entity @e[type=marker,tag=SelectedMap,tag={TAG}] run schedule function {NS}:activate 1s replace')
append('game/loops/ingame',f'execute if score $selectedMap CmdData matches {MID} run function {NS}:functionality')
append('everytick',f'execute if score $gamestate CmdData matches 0 if score $selectedMap CmdData matches {MID} run function {NS}:waiting_tick')
append('maps/reset',f'execute if score $selectedMap CmdData matches {MID} run function {NS}:reset')
append('maps/start',f'execute if score $selectedMap CmdData matches {MID} run time set 6000')
append('lobby/voting/player_vote',f'tellraw @s[scores={{vote_map_id={MID}}}] {{"translate":"{NS}.voted","color":"green"}}')
append('lobby/voting/set_maps',f'kill @e[tag={TAG}Poster]')
before('lobby/options/map_toggle/init','execute store result score count temp',f'function mcm:lobby/options/map_toggle/add_map {{name:{TAG},translate:"{NS}.name"}}\n')
line=next(l for l in text('lobby/voting/map_position_id').splitlines()if 'matches 24 positioned'in l).replace('matches 24 ','matches 25 ').replace('monolith',NS).replace('Monolith',TAG)
append('lobby/voting/map_position_id',line)
assets=ROOT/'.minecraft/resourcepacks/backstabbed-resource/assets';ref=f'{NS}:posters/{NS}'
model=json.loads((assets/'monolith/models/posters/monolith.json').read_text());model['credit']='siyuan_日记; https://www.bilibili.com/video/BV1fDNJ6qEpx; voting artwork generated with OpenAI built-in imagegen.';model['textures']={'poster':ref,'particle':ref}
for rel,value in [('models/posters/'+NS+'.json',model),('items/posters/'+NS+'.json',{'model':{'type':'minecraft:model','model':ref}}),('lang/en_us.json',{NS+'.name':m['title'],NS+'.voted':'You voted for Axolotl Treehouse!',NS+'.ready':'Axolotl Treehouse ready'}),('lang/zh_cn.json',{NS+'.name':'水帘树洞',NS+'.voted':'你投票支持了水帘树洞！',NS+'.ready':'水帘树洞已就绪'})]:
 p=assets/NS/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
atlas=assets/'minecraft/atlases/blocks.json';a=json.loads(atlas.read_text())
if not any(v.get('resource')==ref for v in a['sources']):a['sources'].append({'type':'single','resource':ref})
atlas.write_text(json.dumps(a,indent=2)+'\n')
with stopped(SAVE):
 with zipfile.ZipFile(pack.with_suffix('.pending'),'w',compression=zipfile.ZIP_DEFLATED)as z:
  for key,(info,data)in entries.items():z.writestr(info or key,data)
 pack.with_suffix('.pending').replace(pack)
# These shared functions also have reviewed source overlays. Keep their newly
# added hooks synchronized so a later mobility/spectator rebuild preserves them.
for component in ['klut27-mobility','spectator-safety']:
 for p in(ROOT/component/'datapack/data/mcm/function').rglob('*.mcfunction'):
  key=p.relative_to(ROOT/component/'datapack').as_posix()
  if key in {'data/mcm/function/everytick.mcfunction','data/mcm/function/load.mcfunction','data/mcm/function/maps/start.mcfunction','data/mcm/function/game/loops/ingame.mcfunction'}:
   # Copy only the new arena hooks; preserve any unrelated overlay differences.
   old=p.read_text();canonical=entries[key][1].decode()
   for line in canonical.splitlines():
    if 'axolotl_treehouse:'in line and line not in old:old=old.rstrip()+'\n\n'+line+'\n'
   p.write_text(old)
m.update({'island_rows':rows,'poster':{'method':'OpenAI built-in imagegen','texture':str((assets/NS/f'textures/posters/{NS}.png').relative_to(ROOT)),'prompt_file':'axolotl-treehouse/poster-prompt.txt','sha256':hashlib.sha256((assets/NS/f'textures/posters/{NS}.png').read_bytes()).hexdigest()},'containment':'Lake-level fall outside the exact island footprint eliminates live queued players from round start, including grace. No fluid-contact rule. Waiting violations return safely; upper/horizontal escapes return during grace and eliminate afterward. Spectators/dead/unselected players are excluded.'})
(ROOT/'docs/arenas/axolotl_treehouse.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('Installed arena',MID,NS)
