"""KLUT-27 hook cooldown using vanilla datapack commands and mod .3 entities."""
import json,zipfile
from sync_klut27_standalone import TARGETS,zip_bytes,ROOT

def install():
 additions={}
 def fn(name,body):additions[f'data/klut27/function/{name}.mcfunction']=(body.strip()+'\n').encode('utf-8')
 fn('hook_tick','''execute unless score $selectedMap CmdData matches 20 run return 0
execute unless score $gamestate CmdData matches 1 run return 0
scoreboard players set @a[tag=Klut27Hook] kh_seen 0
execute as @e[type=gravity_changer:grappling_hook] on origin if entity @s[type=player,tag=Klut27Hook] run scoreboard players set @s kh_seen 1
execute as @a[tag=Klut27Hook,tag=queued,tag=!spectating,gamemode=!spectator] unless score @s dead matches 1.. run function klut27:hook_player_tick''')
 fn('hook_player_tick','''scoreboard players add @s kh_cd 0
execute if score @s kh_cd matches 1.. run scoreboard players remove @s kh_cd 1
execute if score @s kh_was matches 1 if score @s kh_seen matches 0 unless entity @s[tag=murderer] run function klut27:hook_start_cooldown
execute if entity @s[tag=murderer] run scoreboard players set @s kh_cd 0
execute if score @s kh_cd matches 1.. if items entity @s hotbar.* gravity_changer:grappling_hook[custom_data~{klut27_hook:1b}] run function klut27:hook_disable
execute if score @s kh_cd matches 1.. if items entity @s inventory.* gravity_changer:grappling_hook[custom_data~{klut27_hook:1b}] run function klut27:hook_disable
execute if score @s kh_cd matches 1.. if items entity @s weapon.offhand gravity_changer:grappling_hook[custom_data~{klut27_hook:1b}] run function klut27:hook_disable
execute if score @s kh_cd matches 0 if items entity @s hotbar.* minecraft:stick[custom_data~{klut27_cooling:1b}] run function klut27:hook_enable
execute if score @s kh_cd matches 0 if items entity @s inventory.* minecraft:stick[custom_data~{klut27_cooling:1b}] run function klut27:hook_enable
execute if score @s kh_cd matches 0 if items entity @s weapon.offhand minecraft:stick[custom_data~{klut27_cooling:1b}] run function klut27:hook_enable
scoreboard players operation @s kh_was = @s kh_seen''')
 slots=[f'hotbar.{i}' for i in range(9)]+[f'inventory.{i}' for i in range(27)]+['weapon.offhand']
 fn('hook_start_cooldown','scoreboard players set @s kh_cd 200\n'+'\n'.join(f'execute if items entity @s {group} gravity_changer:grappling_hook[custom_data~{{klut27_upgraded:1b}}] run scoreboard players set @s kh_cd 80' for group in ['hotbar.*','inventory.*','weapon.offhand']))
 for direction,item in [('disable','gravity_changer:grappling_hook'),('enable','minecraft:stick')]:
  marker='klut27_hook' if direction=='disable' else 'klut27_cooling'
  commands=[]
  for slot in slots:
   for variant,condition in [('upgraded',f'if items entity @s {slot} {item}[custom_data~{{klut27_upgraded:1b}}]'),('innocent',f'if items entity @s {slot} {item}[custom_data~{{klut27_innocent:1b}}] unless items entity @s {slot} {item}[custom_data~{{klut27_upgraded:1b}}]'),('',f'unless items entity @s {slot} {item}[custom_data~{{klut27_innocent:1b}}] unless items entity @s {slot} {item}[custom_data~{{klut27_upgraded:1b}}]')]:
    commands.append(f'execute if items entity @s {slot} {item}[custom_data~{{{marker}:1b}}] {condition} run item modify entity @s {slot} klut27:hook_{direction}'+('_'+variant if variant else ''))
  fn('hook_'+direction,'\n'.join(commands))
  disabled=direction=='disable'
  data={'klut27_hook':True,'NoDrop':True,'no_drop_on_death':True}
  if disabled:data['klut27_cooling']=True
  modifier=[{'function':'minecraft:set_item','item':'minecraft:stick' if disabled else 'gravity_changer:grappling_hook'},
   {'function':'minecraft:set_components','components':{'minecraft:custom_data':data,'minecraft:item_model':'gravity_changer:grappling_hook','minecraft:max_stack_size':1,
   'minecraft:custom_name':json.dumps({'text':'重力钩爪（冷却中）','color':'gray','italic':False} if disabled else {'translate':'item.gravity_changer.grappling_hook','italic':False},ensure_ascii=False)}}]
  additions[f'data/klut27/item_modifier/hook_{direction}.json']=(json.dumps(modifier,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
  import copy
  for variant in ['innocent','upgraded']:
   m=copy.deepcopy(modifier);components=m[1]['components'];components['minecraft:custom_data']['klut27_innocent']=True
   if variant=='upgraded':
    components['minecraft:custom_data']['klut27_upgraded']=True
    components['minecraft:custom_name']=json.dumps({'text':'升级重力钩爪'+('（冷却中）' if disabled else ''),'color':'gray' if disabled else 'aqua','italic':False},ensure_ascii=False)
   additions[f'data/klut27/item_modifier/hook_{direction}_{variant}.json']=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
  if direction=='enable':
   additions['data/klut27/item_modifier/hook_role_innocent.json']=json.dumps([{'function':'minecraft:set_custom_data','tag':'{klut27_innocent:1b}'}]).encode()
 fn('hook_mark_innocent','\n'.join(f'execute if items entity @s {slot} gravity_changer:grappling_hook[custom_data~{{klut27_hook:1b}}] run item modify entity @s {slot} klut27:hook_role_innocent' for slot in slots))
 fn('hook_cancel','''tag @s add Klut27HookCleaning
scoreboard players set @e[type=gravity_changer:grappling_hook] kh_owner 0
execute as @e[type=gravity_changer:grappling_hook] store success score @s kh_owner on origin if entity @s[type=player,tag=Klut27HookCleaning]
kill @e[type=gravity_changer:grappling_hook,scores={kh_owner=1}]
tag @s remove Klut27HookCleaning
scoreboard players set @s kh_seen 0
scoreboard players set @s kh_was 0
scoreboard players set @s kh_cd 0''')
 fn('give_hook','''execute unless score $selectedMap CmdData matches 20 run return 0
function klut27:hook_cancel
tag @s remove gravity_hook_no_cooldown
scoreboard players set @s klut_air 0
tag @s add Klut27Hook
item replace entity @s hotbar.0 with gravity_changer:grappling_hook[custom_data={klut27_hook:1b,NoDrop:1b,no_drop_on_death:1b}]''')
 fn('hook_roles','''execute unless score $selectedMap CmdData matches 20 run return 0
tag @a[tag=Klut27Hook] remove gravity_hook_no_cooldown
execute as @a[tag=Klut27Hook] run function klut27:hook_cancel
execute as @a[tag=Klut27Hook] run function klut27:hook_enable
execute as @a[tag=Klut27Hook,tag=innocent,tag=!murderer] run function klut27:hook_mark_innocent
scoreboard players set @a[tag=Klut27Hook] klut_air 0''')
 fn('cleanup_player','''execute unless entity @s[tag=Klut27Hook] run return 0
function klut27:hook_cancel
tag @s remove gravity_hook_no_cooldown
tag @s remove Klut27Hook
scoreboard players set @s klut_air 0
clear @s gravity_changer:grappling_hook[custom_data~{klut27_hook:1b}]
clear @s minecraft:stick[custom_data~{klut27_hook:1b}]''')
 for world in TARGETS:
  p=world/'datapacks/mcm.zip'
  with zipfile.ZipFile(p) as z:files={n:z.read(n) for n in z.namelist()}
  files.update(additions)
  name='data/mcm/function/load.mcfunction';t=files[name].decode().replace('\r','')
  for objective in ['kh_seen','kh_was','kh_cd','kh_owner']:
   line=f'scoreboard objectives add {objective} dummy'
   if line not in t:t=line+'\n'+t
  files[name]=t.encode()
  name='data/klut27/function/functionality.mcfunction';t=files[name].decode().replace('\r','')
  if 'function klut27:hook_tick' not in t:t=t.rstrip()+'\nfunction klut27:hook_tick\n'
  files[name]=t.encode()
  assert all(b'gravity grappling_hook clear' not in b for n,b in files.items() if n.endswith('.mcfunction'))
  temp=p.with_suffix('.zip.tmp');temp.write_bytes(zip_bytes(files));temp.replace(p)
 print('Installed .3-compatible per-owner datapack cooldown in both main saves.')

if __name__=='__main__':install()
