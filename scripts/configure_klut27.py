"""Stage KLUT-27 datapack changes; never concurrently overwrite mcm.zip.

Writes changed ZIP entries and an original-entry hash manifest under ignored
map-previewer/maps/klut27/patch. The coordinator merges these with other work.
"""
from collections import deque
import hashlib
import json
from pathlib import Path
import zipfile
from klut27_geometry import ROOT,OFFSET,analyze,short,solid
from klut27_elevators import pack_files
from import_klut27 import WORLD,SOURCE_URL

STAGE=ROOT/'map-previewer/maps/klut27/patch'

def main():
    with zipfile.ZipFile(WORLD/'datapacks/mcm.zip') as z: original={n:z.read(n) for n in z.namelist()}
    files=dict(original)
    def put(path,value):files['data/'+path]=(value.strip()+'\n').encode()
    def append(name,value):
        path='data/mcm/function/'+name+'.mcfunction'
        if value.strip() not in files[path].decode():files[path]=files[path].rstrip()+b'\n\n'+value.strip().encode()+b'\n'
    blocks,graph,components,columns=analyze()
    main_component=next(c for c in components if (8,16,15) in c)
    pool=sorted(p for p in main_component if len(graph[p])>=2 and short(blocks[(p[0],p[1]-1,p[2])])!='white_shulker_box')
    anchor=(9,16,15)
    chosen=[anchor]
    for _ in range(27):chosen.append(max((p for p in pool if p not in chosen),key=lambda p:min(sum((p[i]-q[i])**2 for i in range(3)) for q in chosen)))
    # Real traversable routes to the elevator-linked central deck are retained
    # as evidence and checked against the destination world by regression tests.
    parents={anchor:None};queue=deque([anchor])
    while queue:
        p=queue.popleft()
        for q in sorted(graph[p]):
            if q not in parents:parents[q]=p;queue.append(q)
    routes=[]
    for p in chosen:
        route=[]
        while p is not None:route.append(list(p));p=parents[p]
        routes.append(route)
    spawns=[[x+OFFSET+.5,y,z+OFFSET+.5] for x,y,z in chosen]
    activation=['execute unless score $selectedMap CmdData matches 20 run return 0','execute unless score $gamestate CmdData matches 0..1 run return 0','kill @e[tag=MapEntity]','tag @a remove Klut27Participant','function klut27:restore_blocks','gamerule doFireTick false']
    for x,y,z in spawns:
        activation.append(f'summon marker {x:g} {y:g} {z:g} {{Tags:["PlayerSpawn","ScrapSpawn","MapEntity","Klut27Runtime"],data:{{gravity_direction:"down",gravity_strength:1.0d}}}}')
    activation+=['summon marker 36873.5 18 36879.5 {Tags:["SpectatorSpawn","MapEntity","Klut27Runtime"]}','tellraw @a {"translate":"klut27.ready","fallback":"KLUT-27 ready","color":"aqua"}']
    put('klut27/function/activate.mcfunction','\n'.join(activation))
    register='execute unless entity @e[type=marker,tag=MapVote,tag=Klut27] run summon marker 0 -50 70 {Tags:["MapVote","Klut27"]}\nscoreboard players set @e[type=marker,tag=MapVote,tag=Klut27] MapValues 20'
    put('klut27/function/register.mcfunction',register+'\nfunction mcm:lobby/options/map_toggle/init')
    append('respawn_entities',register)
    from klut27_boundary import current_boxes
    boxes=current_boxes()
    predicate={'condition':'minecraft:any_of','terms':[{'condition':'minecraft:location_check','predicate':{'dimension':'minecraft:overworld','position':box}} for box in boxes]}
    put('klut27/predicate/arena.json',json.dumps(predicate,separators=(',',':')))
    for fn,state in [('functionality',1),('waiting_tick',0)]:
        participants='tag=Klut27Participant,' if state==0 else ''
        mark='execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s if predicate klut27:arena run tag @s add Klut27Participant\n' if state==0 else ''
        put(f'klut27/function/{fn}.mcfunction',f'''execute unless score $selectedMap CmdData matches 20 run return 0
execute unless score $gamestate CmdData matches {state} run return 0
function klut27_elevators:tick
{mark}execute as @a[tag=queued,{participants}tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. unless predicate klut27:arena run function klut27:fall''')
    put('klut27/function/fall.mcfunction','''execute unless score $selectedMap CmdData matches 20 run return 0
execute unless score $gamestate CmdData matches 0..1 run return 0
execute unless entity @s[tag=queued,tag=!spectating,gamemode=!spectator] run return 0
execute if score @s dead matches 1.. run return 0
tellraw @a {"translate":"klut27.death.fall","fallback":"%s drifted away from KLUT-27","with":[{"selector":"@s"}],"color":"gold"}
function mcm:game/playerdeath''')
    restore=[]
    for (x,y,z),state in sorted(blocks.items()):
        name=short(state)
        if name.endswith(('_door','_trapdoor','_button','_pressure_plate')) or name in ('lever','repeater'):
            props=','.join(f'{k}={v}' for k,v in state.get('Properties',{}).items())
            restore.append(f'setblock {x+OFFSET} {y} {z+OFFSET} minecraft:{name}[{props}]')
    put('klut27/function/restore_blocks.mcfunction','\n'.join(restore))
    put('klut27/function/reset.mcfunction','schedule clear klut27:activate\nkill @e[tag=Klut27Runtime]\nkill @e[tag=klut.e.search]\ntag @a remove Klut27Participant\nfunction klut27:restore_blocks')
    put('klut27/function/select.mcfunction',files['data/yacht/function/select.mcfunction'].decode().replace('Yacht','Klut27'))
    append('load','schedule function klut27:register 1s\nfunction klut27_elevators:load')
    # Reload cleanup runs before generic respawn and before the selection is reset.
    loadpath='data/mcm/function/load.mcfunction'
    cleanup='execute if score $selectedMap CmdData matches 20 run function klut27:reset\nexecute if score $selectedMap CmdData matches 20 run forceload remove 36848 36848 36895 36927\n'
    if cleanup not in files[loadpath].decode():
        files[loadpath]=files[loadpath].decode().replace('schedule function mcm:respawn_entities 1s',cleanup+'schedule function mcm:respawn_entities 1s').encode()
    append('maps/start','execute if score $selectedMap CmdData matches 20 run time set 18000')
    append('maps/reset',cleanup)
    append('everytick','execute if score $gamestate CmdData matches 0 if score $selectedMap CmdData matches 20 run function klut27:waiting_tick')
    append('game/loops/ingame','execute if score $selectedMap CmdData matches 20 run function klut27:functionality')
    append('lobby/voting/end','execute if entity @e[type=marker,tag=SelectedMap,tag=Klut27] run forceload add 36848 36848 36895 36927\nexecute if entity @e[type=marker,tag=SelectedMap,tag=Klut27] run schedule function klut27:activate 1s replace')
    append('lobby/voting/map_position_id','execute if score @s MapValues matches 20 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {Tags:["vote_display","Klut27Poster"],Rotation:[90f,0f],brightness:{block:15,sky:15},item_display:"fixed",item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"klut27:posters/klut27"}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}')
    setmaps='data/mcm/function/lobby/voting/set_maps.mcfunction'
    if 'kill @e[tag=Klut27Poster]' not in files[setmaps].decode():
        files[setmaps]=('kill @e[tag=Klut27Poster]\n'+files[setmaps].decode()).encode()
    append('lobby/voting/player_vote','tellraw @s[scores={vote_map_id=20}] {"translate":"klut27.voted","color":"green"}')
    option='data/mcm/function/lobby/options/map_toggle/init.mcfunction'
    if 'name:Klut27' not in files[option].decode():
        files[option]=files[option].decode().replace('execute store result score count temp','function mcm:lobby/options/map_toggle/add_map {name:Klut27,translate:"klut27.name"}\n\nexecute store result score count temp').encode()
    put('klut27/credits.txt',f'KLUT-27 by Bekulainen\n{SOURCE_URL}\nAuthor permission required before reuse/publication, plus attribution and original link.\nSimple Elevators by Supercam19; modernized for Java 1.21.4.\nVoting poster generated using OpenAI built-in imagegen on 28 October 2026.\nOriginal architecture preserved; source milk-give command disabled in integrated arena.')
    files.update({p:v for p,v in pack_files('klut27_elevators',True).items() if p!='pack.mcmeta'})
    changed={n:v for n,v in files.items() if original.get(n)!=v}
    STAGE.mkdir(parents=True,exist_ok=True)
    for n,v in changed.items():
        p=STAGE/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
    (STAGE/'manifest.json').write_text(json.dumps({n:hashlib.sha256(original[n]).hexdigest() if n in original else None for n in changed},indent=2))
    assets=ROOT/'.minecraft/resourcepacks/backstabbed-resource/assets'
    model=json.loads((assets/'subway_station/models/posters/subway_station.json').read_text())
    model['credit']='KLUT-27 by Bekulainen; '+SOURCE_URL+' Poster: OpenAI imagegen, 28 October 2026.'
    model['textures']={k:'klut27:posters/klut27' for k in model['textures']}
    for kind,value in [('models',model),('items',{'model':{'type':'minecraft:model','model':'klut27:posters/klut27'}})]:
        path=assets/f'klut27/{kind}/posters/klut27.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')
    atlaspath=assets/'minecraft/atlases/blocks.json';atlas=json.loads(atlaspath.read_text())
    entry={'type':'single','resource':'klut27:posters/klut27'}
    if entry not in atlas['sources']:atlas['sources'].append(entry)
    atlaspath.write_text(json.dumps(atlas,indent=2)+'\n')
    for language,values in {'en_us':{'name':'KLUT-27','ready':'KLUT-27 ready','voted':'| Voted: KLUT-27','death.fall':'%s drifted away from KLUT-27'},'zh_cn':{'name':'KLUT-27 太空船','ready':'KLUT-27 已就绪','voted':'| 已投票：KLUT-27','death.fall':'%s 飘离了 KLUT-27'}}.items():
        path=assets/f'klut27/lang/{language}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps({'klut27.'+k:v for k,v in values.items()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    gravity_tests={}
    for direction,vector in {'down':(0,-1,0),'up':(0,1,0),'north':(0,0,-1),'south':(0,0,1),'west':(-1,0,0),'east':(1,0,0)}.items():
        candidates=[]
        for p,s in blocks.items():
            if not solid(s) or short(s)=='white_shulker_box':continue
            if all(short(blocks.get(tuple(p[i]-d*vector[i] for i in range(3)),{}))=='air' for d in (1,2)):
                foot=[p[i]+(.5 if vector[i]==0 else (1 if vector[i]<0 else 0)) for i in range(3)]
                if -20<foot[1]<35:candidates.append((sum((foot[i]-[9.5,16,15.5][i])**2 for i in range(3)),p,foot))
        _,support,foot=min(candidates)
        # Positive-axis collision boxes shift 1e-6 toward gravity in the mod.
        # A 2e-6 gap preserves support contact without penetrating the cube.
        for axis in range(3):
            if vector[axis]>0:foot[axis]-=0.000002
        gravity_tests[direction]={'source_support':list(support),'destination_feet':[foot[0]+OFFSET,foot[1],foot[2]+OFFSET],'source_body_air_cells':[list(tuple(support[i]-d*vector[i] for i in range(3))) for d in (1,2)]}
    manifestpath=ROOT/'docs/arenas/klut27.json';manifest=json.loads(manifestpath.read_text())
    manifest.update({'source_player_spawns':[[x+.5,y,z+.5] for x,y,z in chosen],'destination_player_spawns':spawns,'spawn_routes_source':routes,'route_component_cells':len(main_component),'containment_boxes':boxes,'gravity_test_positions':gravity_tests,'elevator_columns':{f'{x},{z}':[p[1]-1 for p in values] for (x,z),values in columns.items()},'reset_commands':len(restore),'play_area':'Original ship cabins, terraces and parkour exterior; a single build-sized cuboid expanded 30 blocks on all six faces, including the lower antenna. Out-of-region live participants die through the existing game death path; spectators/dead/lobby players are exempt.','poster':'assets/klut27/textures/posters/klut27.png'})
    manifestpath.write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Staged {len(changed)} entries, {len(spawns)} spawns, {len(boxes)} boundary boxes, {len(restore)} state resets. ZIP unchanged.')
    print(json.dumps(gravity_tests,indent=2))

if __name__=='__main__':main()
