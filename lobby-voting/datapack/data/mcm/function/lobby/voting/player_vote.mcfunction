execute unless score $gamestate CmdData matches -1 run return fail
playsound block.note_block.bit master @s ~ ~ ~ 1 1.4
tag @s add Voted
scoreboard players set random vote_count 0
scoreboard players set map1 vote_count 0
scoreboard players set map2 vote_count 0
scoreboard players set map3 vote_count 0
scoreboard players set map4 vote_count 0
scoreboard players set map5 vote_count 0
scoreboard players set map6 vote_count 0
scoreboard players set map7 vote_count 0
scoreboard players set map8 vote_count 0
execute as @a[scores={vote_position=-1}] run scoreboard players add random vote_count 1
execute as @a[scores={vote_position=1}] run scoreboard players add map1 vote_count 1
execute as @a[scores={vote_position=2}] run scoreboard players add map2 vote_count 1
execute as @a[scores={vote_position=3}] run scoreboard players add map3 vote_count 1
execute as @a[scores={vote_position=4}] run scoreboard players add map4 vote_count 1
execute as @a[scores={vote_position=5}] run scoreboard players add map5 vote_count 1
execute as @a[scores={vote_position=6}] run scoreboard players add map6 vote_count 1
execute as @a[scores={vote_position=7}] run scoreboard players add map7 vote_count 1
execute as @a[scores={vote_position=8}] run scoreboard players add map8 vote_count 1
function mcm:lobby/voting/refresh_votes
tellraw @s[scores={vote_map_id=-1}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.random.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=1}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.library.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=2}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.airship.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=3}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.vineyard.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=4}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.launchpad.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=5}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.cyberpunk.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=6}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.riverboat.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=7}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.industry.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=8}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.train.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=9}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.cabin.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=10}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.gumdrop.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=11}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.canyon.name", "color":"green"}]}]
tellraw @s[scores={vote_map_id=12}] [{"text":"| ","color":"gray","bold":true}, {"translate":"mcm.lobby.voted.for","color":"gray", "with": [{"translate":"mcm.sculk.name", "color":"green"}]}]

# Panda Village integration
tellraw @s[scores={vote_map_id=13}] [{"text":"| ","color":"gray","bold":true},{"translate":"mcm.lobby.voted.for","color":"gray","with":[{"text":"Panda Village","color":"green"}]}]

# River Bank integration
tellraw @s[scores={vote_map_id=14}] [{"text":"| 已投票：River Bank","color":"green"}]

# Yacht integration
tellraw @s[scores={vote_map_id=15}] [{"text":"| 已投票：Yacht","color":"green"}]

tellraw @s[scores={vote_map_id=16}] {"translate":"subway_station.voted","color":"green"}

tellraw @s[scores={vote_map_id=17}] {"translate":"meridian_base.voted","color":"green"}

tellraw @s[scores={vote_map_id=18}] {"translate":"bagger_288.voted","color":"green"}

tellraw @s[scores={vote_map_id=19}] {"translate":"underwater_base.voted","color":"green"}

tellraw @s[scores={vote_map_id=20}] {"translate":"klut27.voted","color":"green"}

tellraw @s[scores={vote_map_id=21}] {"translate":"sworld_island.voted","color":"green"}

tellraw @s[scores={vote_map_id=22}] {"translate":"middle_ages.voted","color":"green"}

tellraw @s[scores={vote_map_id=23}] {"translate":"cube_block.voted","color":"green"}

tellraw @s[scores={vote_map_id=24}] {"translate":"monolith.voted","color":"green"}

tellraw @s[scores={vote_map_id=25}] {"translate":"axolotl_treehouse.voted","color":"green"}
