execute if score $gamestate CmdData matches 1.. run return fail
schedule clear mcm:lobby/voting/end
function mcm:maps/reset
function mcm:lobby/voting/set_maps
tag @e[type=marker,tag=SelectedMap] remove SelectedMap
execute positioned 28.99 3 90 run kill @e[type=item_display,tag=vote_display,distance=..2.2]
execute positioned 28.99 3 90 run kill @e[tag=MonolithPoster,distance=..2.2]
execute positioned 28.0 2.0 89.0 as @e[type=marker,tag=MapVote,tag=Monolith,limit=1] run function mcm:lobby/voting/map_position_id
scoreboard players set map1 vote_count 1000000
scoreboard players set map2 vote_count 0
scoreboard players set map3 vote_count 0
scoreboard players set map4 vote_count 0
scoreboard players set map5 vote_count 0
scoreboard players set map6 vote_count 0
scoreboard players set random vote_count 0
function mcm:lobby/voting/end
