"""Generate/stage KLUT boots, elevator and shared HUD changes; install only after tests.

Needs nbtlib (same runtime as arena-editor). Never regenerate geometry or NPC positions.
"""
from pathlib import Path
from io import BytesIO
import argparse, copy, datetime, hashlib, json, sys, zipfile
import nbtlib as nbt

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'
SAVES=Path('C:/Users/dyf08/AppData/Roaming/PrismLauncher/instances/Backstabbed++/.minecraft/saves')
LIVE=SAVES/'Backstabbed ++! v1.1.1 Latest 2026-10-28 77e59f6'
STANDALONE=SAVES/'KLUT-27 - 1.21.4 Fixed'
STAGE=ROOT/'dev/klut27-mobility'
BOX='minecraft:white_shulker_box{lock:{components:{"minecraft:custom_name":"\\\"5567353566-5331\\\""}}}'
BOOTS='minecraft:leather_boots[custom_data~{klut27_boots:1b}]'
LIVE_PLAYER='@a[tag=queued,tag=!spectating,gamemode=!spectator]'

def readzip(p):
    with zipfile.ZipFile(p)as z:return {n:z.read(n)for n in z.namelist()}
def zipbytes(files):
    out=BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED)as z:
        for n,b in sorted(files.items()):z.writestr(n,b)
    return out.getvalue()

def offers():
    return nbt.parse_nbt('''{Recipes:[
{buy:{id:"minecraft:netherite_scrap",count:4},sell:{id:"minecraft:stick",count:1,components:{"minecraft:item_model":"minecraft:role_items/gun","minecraft:max_stack_size":1,"minecraft:custom_data":{klut27_toy_gun:1b},"minecraft:custom_name":'{"text":"玩具枪","italic":false}'}},maxUses:2147483647,uses:0,rewardExp:0b,xp:0,demand:0,specialPrice:0,priceMultiplier:0.0f},
{buy:{id:"minecraft:netherite_scrap",count:4},sell:{id:"minecraft:leather_boots",count:1,components:{"minecraft:item_model":"minecraft:leather_boots","minecraft:dyed_color":{rgb:3949738,show_in_tooltip:0b},"minecraft:custom_data":{klut27_boots:1b},"minecraft:custom_name":'{"text":"重力靴","color":"aqua","italic":false}'}},maxUses:2147483647,uses:0,rewardExp:0b,xp:0,demand:0,specialPrice:0,priceMultiplier:0.0f}]}''')

def update_engineer(e):
    e['CustomName']=nbt.String('{"text":"Engineer","italic":false}')
    e['CustomNameVisible']=nbt.Byte(1);e['Offers']=offers()
    tags=e.get('Tags',nbt.List[nbt.String]([]))
    if 'Klut27BootsVendor'not in tags:tags.append(nbt.String('Klut27BootsVendor'))
    e['Tags']=tags

def generate(standalone=False):
    files={}
    def fn(name,body,ns='klut27'):
        files[f'data/{ns}/function/{name}.mcfunction']=(body.strip()+'\n').encode('utf-8')
    def el(name,body):fn(name,body,'klut27_elevators')
    objectives=['kb_cd','kb_sec','kb_dec','kb_bar','kb_math','ke_dir','ke_up','ke_down','ke_scan','ke_here','ke_input','ke_move']
    if standalone:objectives+=['kh_owner','kh_cd','kh_seen','kh_was','klut_air']
    fn('mobility/load','\n'.join('scoreboard objectives add '+s+' dummy'for s in objectives)+'''
scoreboard players set $two kb_math 2
scoreboard players set $ten kb_math 10
scoreboard players set $three kb_math 3
scoreboard players set $thirty kb_math 30
kill @e[type=marker,tag=KlutBootsGravity]
execute as @a[tag=Klut27Hook] run function klut27:mobility/remove_hook
execute as @e[type=villager,tag=Klut27Engineer] run function klut27:mobility/merchant
''')
    vendor=nbt.Compound();update_engineer(vendor)
    # Do not replace other NPC tags when updating a loaded merchant.
    vendor.pop('Tags')
    fn('mobility/merchant','data merge entity @s '+vendor.snbt()+'\ntag @s add Klut27BootsVendor')
    fn('mobility/remove_hook','''execute if entity @s[tag=Klut27Hook] run function klut27:hook_cancel
clear @s gravity_changer:grappling_hook[custom_data~{klut27_hook:1b}]
clear @s minecraft:stick[custom_data~{klut27_hook:1b}]
tag @s remove gravity_hook_no_cooldown
tag @s remove Klut27Hook
''')
    fn('give_hook','function klut27:mobility/remove_hook')
    fn('hook_roles','execute as @a[tag=Klut27Hook] run function klut27:mobility/remove_hook')
    fn('mobility/release','''execute if entity @s[tag=KlutBootsEquipped] run gravity set_base_direction down @s
execute if entity @s[tag=KlutBootsEquipped] run effect clear @s minecraft:slow_falling
execute if entity @s[tag=KlutBootsEquipped] run effect clear @s minecraft:jump_boost
tag @s remove KlutBootsEquipped
tag @s remove KlutBootsUp
''')
    fn('mobility/cleanup','''function klut27:mobility/release
scoreboard players set @s kb_cd 0
scoreboard players set @s e.cooldown 0
scoreboard players set @s ke_scan 0
scoreboard players set @s ke_here 0
execute if entity @s[tag=KlutMobilityHud] run title @s actionbar ""
tag @s remove KlutMobilityHud
tag @s remove KlutMobility
''')
    fn('cleanup_player','''function klut27:mobility/remove_hook
function klut27:mobility/cleanup
scoreboard players set @s klut_air 0
''')
    for name,bound in [('low',{'max':-6}),('high',{'min':10})]:
        files[f'data/klut27/predicate/boots_{name}.json']=json.dumps({'condition':'minecraft:location_check','predicate':{'position':{'y':bound}}}).encode()
    fn('mobility/up','''gravity set_base_direction up @s
tag @s add KlutBootsUp
effect give @s minecraft:slow_falling infinite 0 true
effect give @s minecraft:jump_boost infinite 2 true
scoreboard players set @s kb_cd 300
''')
    fn('mobility/down','''gravity set_base_direction down @s
tag @s remove KlutBootsUp
effect clear @s minecraft:slow_falling
effect clear @s minecraft:jump_boost
scoreboard players set @s kb_cd 300
''')
    fn('mobility/player',f'''execute unless dimension minecraft:overworld run return 0
function klut27:mobility/remove_hook
scoreboard players add @s kb_cd 0
execute if score @s kb_cd matches 1.. run scoreboard players remove @s kb_cd 1
execute unless items entity @s armor.feet {BOOTS} run function klut27:mobility/release
execute unless items entity @s armor.feet {BOOTS} run return 0
tag @s add KlutMobility
tag @s add KlutBootsEquipped
execute if score @s kb_cd matches 0 unless entity @s[tag=KlutBootsUp] if predicate klut27:boots_low run function klut27:mobility/up
execute if score @s kb_cd matches 0 if entity @s[tag=KlutBootsUp] if predicate klut27:boots_high run function klut27:mobility/down
''')
    scope='@a[gamemode=!spectator]'if standalone else LIVE_PLAYER
    gate=''if standalone else '''execute unless score $selectedMap CmdData matches 20 run return 0
execute unless score $gamestate CmdData matches 0..1 run return 0
'''
    fn('mobility/tick',gate+f'''execute as {scope} at @s unless score @s dead matches 1.. run function klut27:mobility/player
function klut27_elevators:tick
execute as {scope} at @s unless score @s dead matches 1.. run function klut27:mobility/hud
''')
    global_body=''
    if not standalone:global_body+='''execute unless score $selectedMap CmdData matches 20 as @a[tag=KlutMobility] run function klut27:cleanup_player
execute unless score $gamestate CmdData matches 0..1 as @a[tag=KlutMobility] run function klut27:cleanup_player
execute as @a[tag=KlutMobility,tag=!queued] run function klut27:cleanup_player
execute as @a[tag=KlutMobility,tag=spectating] run function klut27:cleanup_player
'''
    global_body+='''execute as @a[tag=KlutMobility,gamemode=spectator] run function klut27:cleanup_player
execute as @a[tag=KlutMobility,scores={dead=1..}] run function klut27:cleanup_player
execute as @a[tag=KlutMobility,nbt={Health:0.0f}] run function klut27:cleanup_player
execute as @a[tag=KlutMobility] at @s unless dimension minecraft:overworld run function klut27:cleanup_player
'''
    fn('mobility/global_tick',global_body)
    # Elevator source position is the supporting shulker box, not the player's
    # eye position. Inverted feet sit against its bottom face.
    el('tick',f'''scoreboard players add {scope} e.cooldown 0
execute as {scope} if score @s e.cooldown matches 1.. run scoreboard players remove @s e.cooldown 1
execute as {scope} at @s unless score @s dead matches 1.. run function klut27_elevators:detect
scoreboard players set {scope} e.jumped 0
scoreboard players set {scope} e.sneakedTime 0
''')
    el('detect','scoreboard players set @s ke_here 0\nexecute unless dimension minecraft:overworld run return 0\n'+('execute unless predicate klut27:arena run return 0\n'if not standalone else '')+f'''
scoreboard players set @s ke_dir 0
execute store result score @s ke_dir run gravity bridge is_down @s
execute if entity @s[nbt={{"neoforge:attachments":{{"gravity_changer:gravity_data":{{currentGravityDirection:"up"}}}}}}] run scoreboard players set @s ke_dir -1
execute if score @s ke_dir matches 1 positioned ~ ~-1 ~ if block ~ ~ ~ {BOX} align xyz positioned ~0.5 ~ ~0.5 run function klut27_elevators:player
execute if score @s ke_dir matches -1 positioned ~ ~0.01 ~ if block ~ ~ ~ {BOX} align xyz positioned ~0.5 ~ ~0.5 run function klut27_elevators:player
execute if score @s ke_dir matches -1 unless score @s ke_here matches 1 positioned ~ ~1 ~ if block ~ ~ ~ {BOX} align xyz positioned ~0.5 ~ ~0.5 run function klut27_elevators:player
execute if score @s ke_here matches 0 run scoreboard players set @s ke_scan 0
''')
    el('player','''scoreboard players set @s ke_here 1
tag @s add KlutMobility
scoreboard players add @s ke_scan 0
scoreboard players remove @s ke_scan 1
scoreboard players set @s ke_input 0
execute if score @s e.cooldown matches 0 if score @s e.jumped matches 1.. run scoreboard players set @s ke_input 1
execute if score @s e.cooldown matches 0 if score @s e.sneakedTime matches 1.. run scoreboard players set @s ke_input -1
execute unless score @s ke_input matches 0 run scoreboard players set @s ke_scan 0
execute if score @s ke_scan matches ..0 run function klut27_elevators:probe
''')
    el('probe','''scoreboard players set @s ke_up 0
scoreboard players set @s ke_down 0
scoreboard players set @s ke_move 0
function klut27_elevators:find_upper
execute if score @s ke_move matches 0 run function klut27_elevators:find_lower
scoreboard players set @s ke_scan 5
''')
    for side,dy,flag,inp in [('upper',1,'ke_up',1),('lower',-1,'ke_down',-1)]:
        el('find_'+side,f'''kill @e[type=marker,tag=klut.e.search]
summon marker ~ ~ ~ {{Tags:["klut.e.search"]}}
execute if score @s ke_dir matches -1 run tag @e[type=marker,tag=klut.e.search] add klut.e.inverted
scoreboard players set @e[type=marker,tag=klut.e.search] e.steps 120
execute as @e[type=marker,tag=klut.e.search,limit=1] at @s run function klut27_elevators:search_{side}
execute store success score @s {flag} if entity @e[type=marker,tag=klut.e.found]
execute if score @s {flag} matches 1 if score @s ke_input matches {inp} if score @s e.cooldown matches 0 at @e[type=marker,tag=klut.e.found,limit=1] run function klut27_elevators:travel
kill @e[type=marker,tag=klut.e.search]
''')
        el('search_'+side,f'''tp @s ~ ~{dy} ~
execute at @s if block ~ ~ ~ {BOX} run function klut27_elevators:check_landing
scoreboard players remove @s e.steps 1
execute if score @s e.steps matches 1.. unless entity @s[tag=klut.e.found] at @s run function klut27_elevators:search_{side}
''')
    el('check_landing','''execute if entity @s[tag=klut.e.inverted] if block ~ ~-1 ~ #klut27_elevators:clear if block ~ ~-2 ~ #klut27_elevators:clear run tag @s add klut.e.found
execute if entity @s[tag=klut.e.inverted] run return 0
execute unless block ~ ~1 ~ #klut27_elevators:clear run return 0
execute if block ~ ~2 ~ #klut27_elevators:clear run tag @s add klut.e.found
execute if block ~ ~2 ~ #minecraft:trapdoors[half=top,open=false,waterlogged=false] run tag @s add klut.e.found
''')
    el('travel','''execute if score @s ke_dir matches 1 run tp @s ~ ~1 ~
execute if score @s ke_dir matches -1 run tp @s ~ ~-0.000002 ~
scoreboard players set @s e.cooldown 30
scoreboard players set @s ke_move 1
scoreboard players set @s ke_scan 0
''')
    fn('mobility/hud','''data modify storage klut27:hud line set value {hint:"",lift:"",boots:""}
execute if score @s ke_here matches 1 if score @s e.cooldown matches 0 if score @s ke_up matches 1 run data modify storage klut27:hud line.hint set value "JUMP to go UP"
execute if score @s ke_here matches 1 if score @s e.cooldown matches 0 if score @s ke_down matches 1 run data modify storage klut27:hud line.hint set value "SNEAK to go DOWN"
execute if score @s ke_here matches 1 if score @s e.cooldown matches 0 if score @s ke_up matches 1 if score @s ke_down matches 1 run data modify storage klut27:hud line.hint set value "JUMP to go UP | SNEAK to go DOWN"
execute if score @s e.cooldown matches 1.. run function klut27:mobility/hud_lift
execute if score @s kb_cd matches 1.. run function klut27:mobility/hud_boots
execute if data storage klut27:hud line{hint:"",lift:"",boots:""} run return run function klut27:mobility/hud_clear
tag @s add KlutMobilityHud
function klut27:mobility/hud_render with storage klut27:hud line
''')
    fn('mobility/hud_clear','''execute if entity @s[tag=KlutMobilityHud] run title @s actionbar ""
tag @s remove KlutMobilityHud
''')
    fn('mobility/hud_render','$title @s actionbar [{"text":"$(hint)","color":"aqua"},{"text":"$(lift)","color":"aqua","bold":true},{"text":"$(boots)","color":"yellow","bold":true}]')
    for kind,obj,unit,label in [('boots','kb_cd',30,'重力靴'),('lift','e.cooldown',3,'电梯')]:
        body=f'''scoreboard players operation @s kb_sec = @s {obj}
scoreboard players add @s kb_sec 1
scoreboard players operation @s kb_sec /= $two kb_math
scoreboard players operation @s kb_dec = @s kb_sec
scoreboard players operation @s kb_dec %= $ten kb_math
scoreboard players operation @s kb_sec /= $ten kb_math
execute store result storage klut27:hud line.sec int 1 run scoreboard players get @s kb_sec
execute store result storage klut27:hud line.dec int 1 run scoreboard players get @s kb_dec
'''
        for i in range(1,11):body+=f'execute if score @s {obj} matches {(i-1)*unit+1}..{i*unit} run data modify storage klut27:hud line.bar set value "'+('■'*i+'—'*(10-i))+'"\n'
        body+=f'function klut27:mobility/hud_{kind}_text with storage klut27:hud line'
        fn('mobility/hud_'+kind,body)
        fn('mobility/hud_'+kind+'_text',f'$data modify storage klut27:hud line.{kind} set value "  {label} | $(bar) | $(sec).$(dec)s"')
    if standalone:
        # Standalone has no Backstabbed death objective or match lifecycle.
        for path,raw in list(files.items()):
            if path.endswith('.mcfunction'):
                text=raw.decode().replace('unless score @s dead matches 1.. ', 'unless entity @s[nbt={Health:0.0f}] ')
                text='\n'.join(line for line in text.splitlines() if 'scores={dead=' not in line)+'\n'
                files[path]=text.encode()
    return files

def patch_snapshots(files):
    for name,raw in list(files.items()):
        if not name.endswith('.mcfunction')or not name.startswith('data/klut27/'):continue
        body=raw.decode('utf-8');lines=[];changed=False
        for line in body.splitlines():
            if 'Klut27Engineer'in line and 'Offers:'in line and '{'in line:
                i=line.index('{');data=nbt.parse_nbt(line[i:]);update_engineer(data)
                line=line[:i]+data.snbt();changed=True
            lines.append(line)
        if changed:files[name]=('\n'.join(lines)+'\n').encode('utf-8')

def patch_pack(original):
    files=dict(original);files.update(generate())
    def edit(name,func):
        key='data/'+name;files[key]=func(files[key].decode('utf-8')).encode('utf-8')
    for name in ('functionality','waiting_tick'):
        edit(f'klut27/function/{name}.mcfunction',lambda s:s.replace('function klut27_elevators:tick','function klut27:mobility/tick').replace('function klut27:hook_tick\n',''))
    edit('mcm/function/maps/start.mcfunction',lambda s:'\n'.join(l for l in s.splitlines()if 'klut27:give_hook'not in l)+'\n')
    edit('mcm/function/game/pick_roles.mcfunction',lambda s:'\n'.join(l for l in s.splitlines()if 'klut27:hook_roles'not in l)+'\n')
    edit('klut27/function/reset.mcfunction',lambda s:s.replace('execute as @a[tag=Klut27Hook] run function klut27:cleanup_player','execute as @a[tag=KlutMobility] run function klut27:cleanup_player\nexecute as @a[tag=Klut27Hook] run function klut27:mobility/remove_hook'))
    for name,line in [('mcm/function/load.mcfunction','function klut27:mobility/load'),('mcm/function/everytick.mcfunction','function klut27:mobility/global_tick')]:
        edit(name,lambda s,line=line:s if line in s else s.rstrip()+'\n'+line+'\n')
    edit('klut27/function/npc_tick.mcfunction',lambda s:s if 'mobility/merchant'in s else s.rstrip()+'\nexecute as @e[type=villager,tag=Klut27Engineer,tag=!Klut27BootsVendor,tag=!Klut27Blasted] run function klut27:mobility/merchant\n')
    patch_snapshots(files)
    return files

def stage():
    STAGE.mkdir(parents=True,exist_ok=True)
    before=readzip(PROJECT/'datapacks/mcm.zip');after=patch_pack(before)
    (STAGE/'mcm.zip').write_bytes(zipbytes(after))
    overlay=ROOT/'klut27-mobility/datapack'
    for n,b in after.items():
        if before.get(n)!=b:
            p=overlay/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    report={'base_sha256':hashlib.sha256((PROJECT/'datapacks/mcm.zip').read_bytes()).hexdigest(),'changed_members':[n for n in after if before.get(n)!=after[n]]}
    (STAGE/'stage.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Staged',len(report['changed_members']),'datapack members:',STAGE/'mcm.zip')

def standalone_pack(project_files):
    files=generate(True)
    for n in ['data/klut27_elevators/function/load.mcfunction','data/klut27_elevators/tags/block/clear.json','data/klut27/function/hook_cancel.mcfunction']:
        files[n]=project_files[n]
    files['data/elevators/function/tick.mcfunction']=b'# Replaced by direction-aware klut27:mobility/tick.\n'
    files['pack.mcmeta']=json.dumps({'pack':{'pack_format':61,'description':'KLUT-27 boots and direction-aware elevator HUD'}}).encode()
    files['data/minecraft/tags/function/load.json']=b'{"values":["klut27_elevators:load","klut27:mobility/load"]}'
    files['data/minecraft/tags/function/tick.json']=b'{"values":["klut27:mobility/global_tick","klut27:mobility/tick"]}'
    return files

def install():
    from contextlib import ExitStack,contextmanager
    import msvcrt,importlib.util
    spec=importlib.util.spec_from_file_location('klut_world_io',ROOT/'arena-editor/world.py')
    io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
    @contextmanager
    def locked(world):
        # Git source worlds intentionally omit this runtime-only file.
        with (world/'session.lock').open('a+b')as f:
            f.seek(0)
            msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
            try:yield
            finally:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    info=json.loads((STAGE/'stage.json').read_text())
    assert digest(PROJECT/'datapacks/mcm.zip')==info['base_sha256'],'Project changed since staging; regenerate/retest before installing.'
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup=ROOT/'.minecraft/backups/klut27-mobility'/stamp;backup.mkdir(parents=True)
    jobs=[];worlds=[PROJECT,LIVE,STANDALONE]
    with ExitStack()as stack:
        for w in worlds:stack.enter_context(locked(w))
        for index,w in enumerate(worlds):
            archive=backup/f'{index}-world.zip'
            with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1)as z:
                for p in w.rglob('*'):
                    if p.is_file()and p.name!='session.lock':z.write(p,w.name+'/'+p.relative_to(w).as_posix())
            with zipfile.ZipFile(archive)as z:assert z.testzip()is None
            print('Verified full backup',archive,flush=True)
            if w!=STANDALONE:
                p=w/'datapacks/mcm.zip';data=(STAGE/'mcm.zip').read_bytes()if w==PROJECT else zipbytes(patch_pack(readzip(p)))
                jobs.append((p,p.read_bytes(),data))
            else:
                # Update all original engineer snapshots, including fire revival.
                for p in (w/'datapacks').glob('*.zip'):
                    original=p.read_bytes();files=readzip(p);before=dict(files);patch_snapshots(files)
                    if files!=before:jobs.append((p,original,zipbytes(files)))
                p=w/'datapacks/klut27-mobility.zip';jobs.append((p,p.read_bytes()if p.exists()else None,zipbytes(standalone_pack(readzip(STAGE/'mcm.zip')))))
                p=w/'level.dat';level=nbt.load(p);entry='file/klut27-mobility.zip'
                enabled=level['Data']['DataPacks']['Enabled'];disabled=level['Data']['DataPacks']['Disabled']
                if entry not in enabled:enabled.append(nbt.String(entry))
                if entry in disabled:disabled.remove(entry)
                tmp=STAGE/'standalone-level.dat';level.save(tmp);jobs.append((p,p.read_bytes(),tmp.read_bytes()))
            count=0;base=0 if w==STANDALONE else 72
            for p in (w/'entities').glob('r.*.mca'):
                rx,rz=map(int,p.stem.split('.')[1:])
                if rx not in (base-1,base)or rz not in(base-1,base):continue
                chunks=io.read_region(p);dirty=False
                for slot,(timestamp,payload)in list(chunks.items()):
                    chunk=nbt.File.parse(BytesIO(payload));changed=False
                    for entity in chunk.get('Entities',[]):
                        if 'Klut27Engineer'in entity.get('Tags',[]):update_engineer(entity);count+=1;changed=True
                    if changed:chunks[slot]=(timestamp,io.encode(chunk));dirty=True
                if dirty:
                    tmp=STAGE/f'{index}-{p.name}';io.write_region(tmp,chunks);jobs.append((p,p.read_bytes(),tmp.read_bytes()))
            assert count==1,(w,'Engineer count',count)
        # Stage every mutation before touching any original file.
        for p,old,new in jobs:assert (p.read_bytes()if p.exists()else None)==old,p
        for p,old,new in jobs:
            temp=p.with_name(p.name+'.mobility-pending');temp.write_bytes(new);temp.replace(p)
            assert p.read_bytes()==new,p
    report={'backup':str(backup),'files':[{'path':str(p),'before':hashlib.sha256(old).hexdigest()if old is not None else None,'after':hashlib.sha256(new).hexdigest()}for p,old,new in jobs]}
    (backup/'installation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Installed and verified',len(jobs),'files; report',backup/'installation.json')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--install',action='store_true');args=parser.parse_args()
    if args.install:install()
    else:stage()
