function mcm:lobby/voting/clear_ballots
function mcm:lobby/options/sync_maps
kill @e[type=item_display,tag=vote_display]
kill @e[tag=AxolotlTreehousePoster]
kill @e[tag=Bagger288Poster]
kill @e[tag=CubeBlockPoster]
kill @e[tag=Klut27Poster]
kill @e[tag=MeridianBasePoster]
kill @e[tag=MiddleAgesPoster]
kill @e[tag=MonolithPoster]
kill @e[tag=PandaVillagePoster]
kill @e[tag=RiverBankPoster]
kill @e[tag=SubwayStationPoster]
kill @e[tag=SworldIslandPoster]
kill @e[tag=UnderwaterBasePoster]
kill @e[tag=YachtPoster]
function mcm:util/respawn_map_vote_entities
tag @e[type=marker,tag=MapVote] remove selected
scoreboard players set @e[type=interaction,tag=vote_counter] vote_map_id -2
fill 27 1 88 27 5 129 crimson_trapdoor[open=true,facing=west] replace warped_trapdoor
execute positioned 28.0 2.0 89.0 as @e[type=marker,tag=MapVote,tag=!Random,tag=!disabled,tag=!selected,limit=1,sort=random] run function mcm:lobby/voting/map_position_id
execute positioned 28.0 2.0 94.0 as @e[type=marker,tag=MapVote,tag=!Random,tag=!disabled,tag=!selected,limit=1,sort=random] run function mcm:lobby/voting/map_position_id
execute positioned 28.0 2.0 99.0 as @e[type=marker,tag=MapVote,tag=!Random,tag=!disabled,tag=!selected,limit=1,sort=random] run function mcm:lobby/voting/map_position_id
execute positioned 28.0 2.0 105.0 as @e[type=marker,tag=MapVote,tag=!Random,tag=!disabled,tag=!selected,limit=1,sort=random] run function mcm:lobby/voting/map_position_id
execute positioned 28.0 2.0 110.0 as @e[type=marker,tag=MapVote,tag=!Random,tag=!disabled,tag=!selected,limit=1,sort=random] run function mcm:lobby/voting/map_position_id
execute positioned 28.0 2.0 115.0 as @e[type=marker,tag=MapVote,tag=!Random,tag=!disabled,tag=!selected,limit=1,sort=random] run function mcm:lobby/voting/map_position_id
execute positioned 28.0 2.0 120.0 as @e[type=marker,tag=MapVote,tag=!Random,tag=!disabled,tag=!selected,limit=1,sort=random] run function mcm:lobby/voting/map_position_id
execute positioned 28.0 2.0 125.0 as @e[type=marker,tag=MapVote,tag=!Random,tag=!disabled,tag=!selected,limit=1,sort=random] run function mcm:lobby/voting/map_position_id
execute positioned 27.0 2.0 83.0 as @e[type=marker,tag=MapVote,tag=Random,limit=1] run function mcm:lobby/voting/map_position_id
execute as @e[type=interaction,tag=vote_counter,scores={vote_map_id=-2}] at @s run function mcm:lobby/voting/disable_slot
execute unless entity @e[type=interaction,tag=vote_counter,tag=!map_random,tag=!disabled] as @e[type=interaction,tag=map_random] at @s run function mcm:lobby/voting/disable_slot
function mcm:lobby/voting/refresh_votes
function mcm:lobby/options/backend/update_displays
