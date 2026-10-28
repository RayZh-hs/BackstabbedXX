"""Install scoped KLUT-27 airless cabins, hook loadout and elevator cooldown."""
import json,zipfile
from sync_klut27_standalone import ROOT,SOURCE,TARGETS,OFFSET,World,zip_bytes
from klut27_elevators import pack_files
from klut27_geometry import short

def main():
 world=World(TARGETS[0],OFFSET);terms=[];cabins=[]
 # Three sealed rooms below the Y=-20 deck. Floor silhouettes define their
 # interiors; exterior balconies/void and the antenna are never selected.
 for floor,ceiling in [(-36,-33),(-33,-28),(-27,-22)]:
  cells=[(x,z) for z in range(4,14) for x in range(4,13) if short(world.get((x,floor,z)))!='air']
  zmin=min(z for x,z in cells);zmax=max(z for x,z in cells);boxes=[]
  for z in range(zmin+1,zmax):
   xs=[x for x,zz in cells if zz==z]
   if not xs or max(xs)-min(xs)<2:continue
   box={'x':{'min':min(xs)+1+OFFSET,'max':max(xs)+OFFSET},'y':{'min':floor+1,'max':ceiling-0.000001},'z':{'min':z+OFFSET,'max':z+1+OFFSET}}
   boxes.append(box);terms.append({'condition':'minecraft:location_check','predicate':{'dimension':'minecraft:overworld','position':box}})
  cabins.append({'floor':floor,'ceiling':ceiling,'boxes':boxes})
 airless=json.dumps({'condition':'minecraft:any_of','terms':terms},separators=(',',':'))+'\n'
 additions={}
 def fn(name,text):additions[f'data/klut27/function/{name}.mcfunction']=(text.strip()+'\n').encode('utf-8')
 additions['data/klut27/predicate/airless.json']=airless.encode()
 fn('air_tick','''execute unless score $selectedMap CmdData matches 20 run return 0
execute unless score $gamestate CmdData matches 1 run return 0
execute if score $graceperiod CmdData matches 1.. run scoreboard players set @a klut_air 0
execute if score $graceperiod CmdData matches 1.. run return 0
execute unless score $pickedroles CmdData matches 1 run return 0
scoreboard players set @a[tag=!queued] klut_air 0
scoreboard players set @a[tag=spectating] klut_air 0
scoreboard players set @a[gamemode=spectator] klut_air 0
scoreboard players set @a[scores={dead=1..}] klut_air 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. unless predicate klut27:airless run scoreboard players set @s klut_air 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. if predicate klut27:airless run scoreboard players add @s klut_air 1
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] if score @s klut_air matches 40 run tellraw @s {"text":"警告：舱室缺氧！请在8秒内离开，否则将窒息死亡。","color":"red"}
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s if score @s klut_air matches 200.. run function klut27:suffocate''')
 fn('suffocate','''execute if score @s dead matches 1.. run return 0
execute unless entity @s[tag=queued,tag=!spectating,gamemode=!spectator] run return 0
tellraw @a [{"selector":"@s"},{"text":" 在 KLUT-27 的缺氧舱室中窒息身亡。","color":"gray"}]
function klut27:cleanup_player
function mcm:game/playerdeath
scoreboard players set @s klut_air 0''')
 fn('give_hook','''execute unless score $selectedMap CmdData matches 20 run return 0
function klut27:hook_cancel
tag @s remove gravity_hook_no_cooldown
scoreboard players set @s klut_air 0
tag @s add Klut27Hook
item replace entity @s hotbar.0 with gravity_changer:grappling_hook[custom_data={klut27_hook:1b,NoDrop:1b,no_drop_on_death:1b}]''')
 fn('hook_roles','''execute unless score $selectedMap CmdData matches 20 run return 0
tag @a[tag=Klut27Hook] remove gravity_hook_no_cooldown
execute as @a[tag=Klut27Hook] run function klut27:hook_cancel
scoreboard players set @a[tag=Klut27Hook] klut_air 0''')
 fn('cleanup_player','''execute unless entity @s[tag=Klut27Hook] run return 0
function klut27:hook_cancel
tag @s remove gravity_hook_no_cooldown
tag @s remove Klut27Hook
scoreboard players set @s klut_air 0
clear @s gravity_changer:grappling_hook[custom_data~{klut27_hook:1b}]''')
 outputs={}
 for target in TARGETS:
  p=target/'datapacks/mcm.zip'
  with zipfile.ZipFile(p) as z:files={n:z.read(n) for n in z.namelist()}
  files.update(additions)
  for n,b in pack_files('klut27_elevators',True).items():
   if n.startswith('data/klut27_elevators/'):files[n]=b
  def add(name,line,front=False):
   t=files[name].decode().replace('\r','')
   if line not in t:t=line+'\n'+t if front else t.rstrip()+'\n'+line+'\n'
   files[name]=t.encode('utf-8')
  add('data/mcm/function/load.mcfunction','scoreboard objectives add klut_air dummy',True)
  add('data/mcm/function/maps/start.mcfunction','execute if score $selectedMap CmdData matches 20 as @a[tag=queued,tag=!spectating] run function klut27:give_hook')
  add('data/mcm/function/game/pick_roles.mcfunction','execute if score $selectedMap CmdData matches 20 run function klut27:hook_roles')
  add('data/klut27/function/functionality.mcfunction','function klut27:air_tick')
  add('data/klut27/function/reset.mcfunction','execute as @a[tag=Klut27Hook] run function klut27:cleanup_player',True)
  add('data/klut27/function/activate.mcfunction','scoreboard players set @a klut_air 0')
  for name in ['data/mcm/function/lobby/give_lobby_items.mcfunction','data/mcm/function/player_leave.mcfunction']:
   add(name,'function klut27:cleanup_player',True)
  # Death cleanup runs after existing dead/queued guards, before any drops.
  name='data/mcm/function/game/playerdeath.mcfunction';t=files[name].decode().replace('\r','')
  if 'function klut27:cleanup_player' not in t:t=t.replace('clear @s netherite_scrap','function klut27:cleanup_player\nclear @s netherite_scrap',1)
  files[name]=t.encode();outputs[p]=zip_bytes(files)
 outputs[SOURCE/'datapacks/simpleelevators-1.21.4.zip']=zip_bytes(pack_files())
 for p,data in outputs.items():
  temp=p.with_suffix('.zip.tmp');temp.write_bytes(data);temp.replace(p)
 (ROOT/'docs/arenas/klut27-features.json').write_text(json.dumps({'airless_cabins':cabins,'warning_ticks':40,'death_ticks':200,'elevator_cooldown_ticks':30,'hook_cooldown_ticks':200,'hook_exempt_tag':'gravity_hook_no_cooldown','hook_slot':0},indent=2)+'\n')
 from klut27_datapack_hook_cooldown import install
 install()
 print('Installed feature datapacks;',len(terms),'interior strips; mod .3 compatibility applied')

if __name__=='__main__':main()
