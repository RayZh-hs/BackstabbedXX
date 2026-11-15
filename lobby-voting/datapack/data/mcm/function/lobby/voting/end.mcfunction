#> Sounds
execute as @a at @s run playsound minecraft:block.note_block.snare master @s ~ ~ ~ 1 1.2
execute as @a at @s run playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 0.7
execute as @a at @s run playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 0

#> Finish vote
#scoreboard players add @e[type=marker,tag=MapVote] CmdData 1
#execute if entity @e[type=marker,tag=MapVote,scores={CmdData=1..}] run function mcm:lobby/map_poggercalculation
#tag @e[type=marker,tag=MapVote,scores={CmdData=0},sort=random,limit=1] add SelectedMap
#execute if entity @e[type=marker,tag=SelectedMap,tag=Random] run tag @e[type=marker,tag=MapVote,tag=!SelectedMap,tag=selected,limit=1,sort=random] add SelectedMap
#execute as @e[type=marker,tag=SelectedMap,tag=Random] run tag @s remove SelectedMap
#scoreboard players operation $selectedMap CmdData = @e[type=marker,tag=SelectedMap] MapValues

execute store success score $vote_resolved temp run function mcm:lobby/voting/select_map
execute unless score $vote_resolved temp matches 1 run return run function mcm:lobby/voting/empty_pool

#> Teardown interaction entities
execute as @e[type=minecraft:interaction,tag=MapVoteEntity] run data merge entity @s {response:false}
#> Hide vote counts
execute as @e[type=text_display,tag=VoteDisplay] run data remove entity @s text

tag @e[type=text_display,tag=VoteDisplay] remove disabled

#> Load correct map
# Library
#execute if entity @e[type=marker,tag=SelectedMap,tag=Library] run forceload add 1023 960 912 1039
#execute if entity @e[type=marker,tag=SelectedMap,tag=Library] run forceload add 1023 960 1108 1039
execute if entity @e[type=marker,tag=SelectedMap,tag=Library] run forceload add 1028 1040 890 1155
# Airship
execute if entity @e[type=marker,tag=SelectedMap,tag=Airship] run forceload add -555 -56 -744 77
# Vineyard
#execute if entity @e[type=marker,tag=SelectedMap,tag=Vineyard] run forceload add 2111 2095 1937 1911
execute if entity @e[type=marker,tag=SelectedMap,tag=Vineyard] run forceload add 1675 2155 1780 2020
# Launch Complex
execute if entity @e[type=marker,tag=SelectedMap,tag=Launchpad] run forceload add -860 -1100 -1170 -1280
execute if entity @e[type=marker,tag=SelectedMap,tag=Launchpad] run forceload add -860 -1100 -1128 -997
execute if entity @e[type=marker,tag=SelectedMap,tag=Launchpad] run forceload add -961 -881 -1136 -976
# Color Filth
execute if entity @e[type=marker,tag=SelectedMap,tag=Cyberpunk] run forceload add -2178 1968 -1969 2135
# Riverboat
execute if entity @e[type=marker,tag=SelectedMap,tag=Riverboat] run forceload add 2130 -2015 2000 -1975
# Industry
execute if entity @e[type=marker,tag=SelectedMap,tag=Industry] run forceload add -1926 -2938 -2067 -3063
# Train
execute if entity @e[type=marker,tag=SelectedMap,tag=Train] run forceload add 2000 3040 1585 2945
# Cabin
execute if entity @e[type=marker,tag=SelectedMap,tag=Cabin] run forceload add -1938 3000 -2030 3048
# Gumdrop Plains
execute if entity @e[type=marker,tag=SelectedMap,tag=Gumdrop] run forceload add 994 -3072 1194 -2795
execute if entity @e[type=marker,tag=SelectedMap,tag=Gumdrop] run forceload add 832 -3152 1055 -2929
#Canyon
execute if entity @e[type=marker,tag=SelectedMap,tag=Canyon] run forceload add 2885 2899 3084 3085
# Stagnant Sanctuary (Sculk)
execute if entity @e[type=marker,tag=SelectedMap,tag=Sculk] run forceload add 2920 870 3090 1065

# Panda Village: 16 x 16 chunks, within the per-command limit.
execute if entity @e[type=marker,tag=SelectedMap,tag=PandaVillage] run forceload add 8192 8192 8447 8447

execute if entity @e[type=marker,tag=SelectedMap,tag=RiverBank] run forceload add 12304 12304 12543 12559

execute if entity @e[type=marker,tag=SelectedMap,tag=Yacht] run forceload add 16384 16384 16559 16591

#> Map specific activation
#Library
#execute if entity @e[type=marker,tag=SelectedMap,tag=Library] run schedule function mcm:maps/library/activate 1s
execute if entity @e[type=marker,tag=SelectedMap,tag=Library] run schedule function mcm:maps/library2/activate 1s
#Airship
execute if entity @e[type=marker,tag=SelectedMap,tag=Airship] run schedule function mcm:maps/airship/activate 1s
#Vineyard
#execute if entity @e[type=marker,tag=SelectedMap,tag=Vineyard] run schedule function mcm:maps/vineyard/activate 1s
execute if entity @e[type=marker,tag=SelectedMap,tag=Vineyard] run schedule function mcm:maps/vineyard2/activate 1s
#Launch Complex
execute if entity @e[type=marker,tag=SelectedMap,tag=Launchpad] run schedule function mcm:maps/launchpad/activate 1s
#Color Filth
execute if entity @e[type=marker,tag=SelectedMap,tag=Cyberpunk] run schedule function mcm:maps/cyberpunk/activate 1s
#Riverboat
execute if entity @e[type=marker,tag=SelectedMap,tag=Riverboat] run schedule function mcm:maps/riverboat/activate 1s
# Industry
execute if entity @e[type=marker,tag=SelectedMap,tag=Industry] run schedule function mcm:maps/industry/activate 1s
# Train
execute if entity @e[type=marker,tag=SelectedMap,tag=Train] run schedule function mcm:maps/train/activate 1s
# Cabin
execute if entity @e[type=marker,tag=SelectedMap,tag=Cabin] run schedule function mcm:maps/cabin/activate 1s
#Gumdrop Plains
execute if entity @e[type=marker,tag=SelectedMap,tag=Gumdrop] run schedule function mcm:maps/gumdrop/activate 1s
#Canyon
execute if entity @e[type=marker,tag=SelectedMap,tag=Canyon] run schedule function mcm:maps/canyon/activate 1s
#Stagnant Sanctuary (Sculk)
execute if entity @e[type=marker,tag=SelectedMap,tag=Sculk] run schedule function mcm:maps/sculk/activate 1s

execute if entity @e[type=marker,tag=SelectedMap,tag=PandaVillage] run schedule function panda_village:activate 1s

execute if entity @e[type=marker,tag=SelectedMap,tag=RiverBank] run schedule function river_bank:activate 1s

execute if entity @e[type=marker,tag=SelectedMap,tag=Yacht] run schedule function yacht:activate 1s

#> Change gamestate to 0 (Players can now join, game has not started yet)
bossbar remove lobbybar
scoreboard players set $gamestate CmdData 0

scoreboard players set @a current_vote 0

kill @e[type=text_display,tag=game_summary]

# Subway Station: 5 x 25 chunks, below the per-command 256 chunk limit.
execute if entity @e[type=marker,tag=SelectedMap,tag=SubwayStation] run forceload add 20464 20256 20543 20655
execute if entity @e[type=marker,tag=SelectedMap,tag=SubwayStation] run schedule function subway_station:activate 1s replace

execute if entity @e[type=marker,tag=SelectedMap,tag=MeridianBase] run forceload add 24464 24480 24703 24703
execute if entity @e[type=marker,tag=SelectedMap,tag=MeridianBase] run schedule function meridian_base:activate 1s replace

execute if entity @e[type=marker,tag=SelectedMap,tag=Bagger288] run forceload add 28576 28672 28767 28767
execute if entity @e[type=marker,tag=SelectedMap,tag=Bagger288] run schedule function bagger_288:activate 1s replace

execute if entity @e[type=marker,tag=SelectedMap,tag=UnderwaterBase] run forceload add 32912 32432 33039 32575
execute if entity @e[type=marker,tag=SelectedMap,tag=UnderwaterBase] run schedule function underwater_base:activate 1s replace

execute if entity @e[type=marker,tag=SelectedMap,tag=Klut27] run forceload add 36848 36848 36895 36927
execute if entity @e[type=marker,tag=SelectedMap,tag=Klut27] run schedule function klut27:activate 1s replace

execute if entity @e[type=marker,tag=SelectedMap,tag=SworldIsland] run forceload add 40864 40912 41055 41023
execute if entity @e[type=marker,tag=SelectedMap,tag=SworldIsland] run schedule function sworld_island:activate 1s replace

execute if entity @e[type=marker,tag=SelectedMap,tag=MiddleAges] run forceload add 45025 45025 45089 45088
execute if entity @e[type=marker,tag=SelectedMap,tag=MiddleAges] run schedule function middle_ages:activate 1s replace

execute if entity @e[type=marker,tag=SelectedMap,tag=CubeBlock] run forceload add 49152 49152 49263 49263
execute if entity @e[type=marker,tag=SelectedMap,tag=CubeBlock] run schedule function cube_block:activate 1s replace

execute if entity @e[type=marker,tag=SelectedMap,tag=Monolith] run forceload add 53200 53200 53407 53455
execute if entity @e[type=marker,tag=SelectedMap,tag=Monolith] run schedule function monolith:activate 1s replace

execute if entity @e[type=marker,tag=SelectedMap,tag=AxolotlTreehouse] run forceload add 57536 57536 57663 57663
execute if entity @e[type=marker,tag=SelectedMap,tag=AxolotlTreehouse] run schedule function axolotl_treehouse:activate 1s replace
execute as @e[type=interaction,tag=vote_counter] if score @s vote_map_id = $selectedMap CmdData at @s run data merge entity @e[type=text_display,tag=VoteDisplay,sort=nearest,limit=1] {text:'{"text":"已选中","color":"green","bold":true}'}
function mcm:lobby/options/backend/update_displays
