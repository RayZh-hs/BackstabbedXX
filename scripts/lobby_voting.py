"""Maintained eight-candidate lobby voting overlay; preserves map-specific art/activation."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
P = 'data/mcm/function/'
V = P + 'lobby/voting/'
F = 'mcm:lobby/voting/'
SLOTS = [(i, z) for i,z in enumerate([90,95,100,106,111,116,121,126],1)]


def lines(text):
    return text.replace('\r\r\n','\n').replace('\r\n','\n')


def append(text, hook):
    text=lines(text)
    return text if hook in text else text.rstrip()+'\n'+hook+'\n'


def generated(members):
    out={}
    def put(name, text): out[name]=(text.strip()+'\n').encode()
    def read(name): return lines(members[name].decode())
    tags=[('random',-1,84)]+[(f'map{i}',i,z) for i,z in SLOTS]
    counts='\n'.join(f'scoreboard players set {tag} vote_count 0' for tag,_,_ in tags)
    tally=counts+'\n'+'\n'.join(f'execute as @a[scores={{vote_position={i}}}] run scoreboard players add {tag} vote_count 1' for tag,i,_ in tags)
    put(V+'clear_ballots.mcfunction', '''tag @a remove Voted
scoreboard players reset @a vote_position
scoreboard players reset @a vote_map_id
scoreboard players set @a current_vote 0
scoreboard players reset @a mapvote
scoreboard players set $countdown CmdData 20
scoreboard players set $countSec CmdData 0
'''+counts)
    setup=['kill @e[tag=MapVoteEntity]']
    displays=['kill @e[type=text_display,tag=VoteDisplay]']
    refresh=[]
    for tag,i,z in tags:
        x=27.8125 if i==-1 else 28.8125
        setup.append(f'summon interaction {x} 2 {z:.1f} {{width:2f,height:3f,Tags:["MapVoteEntity","vote_counter","{tag}"],response:1b}}')
        setup.append(f'scoreboard players set @e[type=interaction,tag=vote_counter,tag={tag}] vote_position {i}')
        dx=26.25 if i==-1 else 27.25
        displays.append(f'summon text_display {dx} 5.2 {z:.1f} {{billboard:"center",Tags:["{tag}","VoteDisplay","MapVoteEntity"],alignment:"center"}}')
        refresh.append(f'execute as @e[type=text_display,tag=VoteDisplay,tag={tag},tag=!disabled] run data merge entity @s {{text:\'{{"translate":"mcm.lobby.vote","with":[{{"score":{{"objective":"vote_count","name":"{tag}"}},"color":"#FFE700"}}]}}\'}}')
        if i>0:
            advancement={'criteria':{'click':{'trigger':'minecraft:player_interacted_with_entity','conditions':{'entity':{'type':'minecraft:interaction','nbt':f'{{Tags:["{tag}"],response:true}}'}}}},'rewards':{'function':F+'vote_slots/'+tag}}
            put(f'data/mcm/advancement/map_votes/{tag}.json',json.dumps(advancement,indent=2))
        put(V+'vote_slots/'+('random' if i==-1 else tag)+'.mcfunction',f'''advancement revoke @s only mcm:map_votes/{'map_random' if i==-1 else tag}
execute unless score $gamestate CmdData matches -1 run return fail
execute unless entity @e[type=interaction,tag=vote_counter,tag={tag},tag=!disabled,nbt={{response:1b}}] run return fail
scoreboard players set @s vote_position {i}
scoreboard players operation @s vote_map_id = @e[type=interaction,tag=vote_counter,tag={tag},limit=1] vote_map_id
function {F}player_vote''')
    # The random slot has a legacy map_random entity tag but a random score holder.
    setup=[s.replace('"random"','"map_random"').replace('tag=random','tag=map_random') for s in setup]
    displays=[s.replace('"random"','"map_random"') for s in displays]
    refresh=[s.replace('tag=random','tag=map_random') for s in refresh]
    out[V+'vote_slots/random.mcfunction']=out[V+'vote_slots/random.mcfunction'].replace(b'tag=random',b'tag=map_random')
    setup += ['function '+F+'vote_displays','function '+F+'ensure_reroll','team join posters @e[tag=MapVoteEntity]']
    put(P+'util/respawn_map_vote_entities.mcfunction','\n'.join(setup))
    put(V+'vote_displays.mcfunction','\n'.join(displays))
    put(V+'refresh_votes.mcfunction','\n'.join(refresh))
    # Keep every existing map-specific vote confirmation.
    old=read(V+'player_vote.mcfunction'); messages=old[old.index('tellraw @s'):]
    put(V+'player_vote.mcfunction','execute unless score $gamestate CmdData matches -1 run return fail\nplaysound block.note_block.bit master @s ~ ~ ~ 1 1.4\ntag @s add Voted\n'+tally+'\nfunction '+F+'refresh_votes\n'+messages)
    # Clean old poster generations before assigning any new candidate (including treehouse).
    poster_tags=sorted(set(re.findall(r'tag=([A-Za-z0-9]+Poster)',read(V+'set_maps.mcfunction'))))
    build=['function '+F+'clear_ballots','function mcm:lobby/options/sync_maps',
           'kill @e[type=item_display,tag=vote_display]']+[f'kill @e[tag={tag}]' for tag in poster_tags]
    build += ['function mcm:util/respawn_map_vote_entities',
              'tag @e[type=marker,tag=MapVote] remove selected',
              'scoreboard players set @e[type=interaction,tag=vote_counter] vote_map_id -2',
              'fill 27 1 88 27 5 129 crimson_trapdoor[open=true,facing=west] replace warped_trapdoor']
    for i,z in SLOTS:
        # Vec3 command arguments center bare integer X/Z; explicit decimals keep art in front of the wall.
        build.append(f'execute positioned 28.0 2.0 {z-1:.1f} as @e[type=marker,tag=MapVote,tag=!Random,tag=!disabled,tag=!selected,limit=1,sort=random] run function {F}map_position_id')
    build += [f'execute positioned 27.0 2.0 83.0 as @e[type=marker,tag=MapVote,tag=Random,limit=1] run function {F}map_position_id',
              'execute as @e[type=interaction,tag=vote_counter,scores={vote_map_id=-2}] at @s run function '+F+'disable_slot',
              'execute unless entity @e[type=interaction,tag=vote_counter,tag=!map_random,tag=!disabled] as @e[type=interaction,tag=map_random] at @s run function '+F+'disable_slot',
              'function '+F+'refresh_votes', 'function mcm:lobby/options/backend/update_displays']
    put(V+'set_maps.mcfunction','\n'.join(build))
    put(V+'disable_slot.mcfunction', '''tag @s add disabled
data merge entity @s {response:0b}
tag @e[type=text_display,tag=VoteDisplay,sort=nearest,limit=1] add disabled
data merge entity @e[type=text_display,tag=VoteDisplay,sort=nearest,limit=1] {text:'{"text":"未启用地图","color":"gray"}'}''')
    # Bind posters to vote interactions, never the nearby reroll/settings controls.
    mapping=read(V+'map_position_id.mcfunction').replace('@e[type=interaction,limit=1,sort=nearest]','@e[type=interaction,tag=vote_counter,limit=1,sort=nearest]')
    put(V+'map_position_id.mcfunction',mapping)
    put(V+'select_map.mcfunction', '''# One uniform random draw from valid highest-vote concrete slots.
tag @e[type=marker,tag=MapVote] remove SelectedMap
tag @e[type=interaction,tag=vote_counter] remove VoteEligible
tag @e[type=interaction,tag=vote_counter] remove VoteFinalist
scoreboard players reset $selectedMap CmdData
execute as @e[type=interaction,tag=vote_counter,tag=!map_random,tag=!disabled,scores={vote_map_id=1..}] run tag @s add VoteEligible
execute unless entity @e[type=interaction,tag=VoteEligible] run return fail
'''+ '\n'.join(f'scoreboard players operation @e[type=interaction,tag=vote_counter,tag=map{i}] vote_count = map{i} vote_count' for i,_ in SLOTS)+'''
scoreboard players set max_votes vote_count 0
scoreboard players operation max_votes vote_count > @e[type=interaction,tag=VoteEligible] vote_count
execute as @e[type=interaction,tag=VoteEligible] if score @s vote_count = max_votes vote_count run tag @s add VoteFinalist
# Random only expands the pool when strictly ahead, never when tied.
execute if score random vote_count > max_votes vote_count run tag @e[type=interaction,tag=VoteEligible] add VoteFinalist
scoreboard players operation $winner vote_map_id = @e[type=interaction,tag=VoteFinalist,sort=random,limit=1] vote_map_id
execute as @e[type=marker,tag=MapVote,tag=!Random] if score @s MapValues = $winner vote_map_id run tag @s add SelectedMap
execute unless entity @e[type=marker,tag=SelectedMap] run return fail
scoreboard players operation $selectedMap CmdData = $winner vote_map_id
execute as @e[type=interaction,tag=vote_counter] if score @s vote_map_id = $winner vote_map_id at @s run fill ~-1 ~-1 ~-2 ~-1 ~3 ~1 warped_trapdoor[open=true,facing=west] replace crimson_trapdoor
tag @e[type=interaction,tag=vote_counter] remove VoteEligible
tag @e[type=interaction,tag=vote_counter] remove VoteFinalist
return 1''')
    end=read(V+'end.mcfunction')
    original='function '+F+'select_map'
    guarded='execute store success score $vote_resolved temp run function '+F+'select_map\nexecute unless score $vote_resolved temp matches 1 run return run function '+F+'empty_pool'
    if guarded not in end:end=end.replace(original,guarded,1)
    finish='execute as @e[type=interaction,tag=vote_counter] if score @s vote_map_id = $selectedMap CmdData at @s run data merge entity @e[type=text_display,tag=VoteDisplay,sort=nearest,limit=1] {text:\'{"text":"已选中","color":"green","bold":true}\'}\nfunction mcm:lobby/options/backend/update_displays'
    put(V+'end.mcfunction',append(end,finish))
    put(V+'empty_pool.mcfunction', 'function '+F+'clear_ballots\nscoreboard players set $gamestate CmdData -1\ntellraw @a {"text":"没有可选地图，请先启用至少一张地图。","color":"yellow"}')
    # Cancel delayed activation before resetting an already selected pre-game map.
    activations=sorted(set(re.findall(r'run schedule function ([\w:/]+) ',end)))
    put(V+'cancel_preparation.mcfunction','\n'.join('schedule clear '+f for f in activations)+'''
function mcm:maps/reset
scoreboard players set $start CmdData 0
scoreboard players set $startcountdown CmdData 200
stopsound @a record minecraft:movie_start''')
    put(V+'enabled_changed.mcfunction', '''execute unless score $gamestate CmdData matches -1..0 run return fail
execute if data storage mcm:options init run return fail
execute if score $gamestate CmdData matches 0 run function mcm:lobby/voting/cancel_preparation
function mcm:lobby/voting/start
tellraw @a {"text":"候选地图已更新，请重新投票。","color":"yellow"}''')
    put(V+'reroll.mcfunction', '''execute unless score $gamestate CmdData matches -1..0 run return fail
execute if data storage mcm:options options{locked:1} run return fail
function mcm:lobby/voting/enabled_changed''')
    put(V+'reroll_enabled.mcfunction', '''execute unless score $gamestate CmdData matches -1..0 run return fail
execute if data storage mcm:options options{locked:1} run return fail
return 1''')
    put(V+'ensure_reroll.mcfunction', '''execute if entity @e[type=interaction,tag=VoteReroll,tag=VoteRerollLeft,nbt={Pos:[26.87d,2.85d,80.5d]}] run return 1
# Migrate the previous right-hand control and remove its callback passengers.
execute as @e[tag=VoteReroll] on passengers run kill @s
kill @e[tag=VoteReroll]
execute positioned 25.86 3.0 80.5 run function mcm:lobby/options/summon_updatable_text {data:{Tags:["VoteReroll","VoteRerollLeft"],Rotation:[90f,0f],line_width:112},extra:{},callback:"mcm:lobby/voting/reroll_text"}
execute positioned 26.87 2.85 80.5 run function mcm:lobby/options/summon_interaction {data:{Tags:["VoteReroll","VoteRerollLeft"],width:2f,height:0.9f,response:1b},extra:{enable_callback:"mcm:lobby/voting/reroll_enabled"},callback:"mcm:lobby/voting/reroll"}''')
    put(V+'reroll_text.mcfunction', '''data merge entity @s {text:'{"text":"[重新随机候选图]","color":"aqua","extra":[{"text":"\\\\n清空投票并重新抽取8张","color":"gray"}]}'}
execute if data storage mcm:options options{locked:1} run data merge entity @s {text:'{"text":"[重新随机候选图]","color":"gray","extra":[{"text":"\\\\n大厅设置已锁定","color":"gray"}]}'}
execute if score $gamestate CmdData matches 1.. run data merge entity @s {text:'{"text":"[重新随机候选图]","color":"gray","extra":[{"text":"\\\\n对局中不可修改","color":"gray"}]}'}''')
    for name in [P+'dev/shuffle_maps.mcfunction',P+'lobby/options/map_toggle/shuffle.mcfunction']:
        put(name,'function '+F+'reroll')
    for name in [P+'lobby/options/map_toggle/map_slot_interaction_inner.mcfunction',P+'lobby/options/reset_to_defaults.mcfunction']:
        put(name,append(read(name),'function '+F+'enabled_changed'))
    return out


def patched(members):
    result=dict(members)
    result.update(generated(members))
    return result
