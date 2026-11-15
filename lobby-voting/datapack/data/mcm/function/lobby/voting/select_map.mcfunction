# One uniform random draw from valid highest-vote concrete slots.
tag @e[type=marker,tag=MapVote] remove SelectedMap
tag @e[type=interaction,tag=vote_counter] remove VoteEligible
tag @e[type=interaction,tag=vote_counter] remove VoteFinalist
scoreboard players reset $selectedMap CmdData
execute as @e[type=interaction,tag=vote_counter,tag=!map_random,tag=!disabled,scores={vote_map_id=1..}] run tag @s add VoteEligible
execute unless entity @e[type=interaction,tag=VoteEligible] run return fail
scoreboard players operation @e[type=interaction,tag=vote_counter,tag=map1] vote_count = map1 vote_count
scoreboard players operation @e[type=interaction,tag=vote_counter,tag=map2] vote_count = map2 vote_count
scoreboard players operation @e[type=interaction,tag=vote_counter,tag=map3] vote_count = map3 vote_count
scoreboard players operation @e[type=interaction,tag=vote_counter,tag=map4] vote_count = map4 vote_count
scoreboard players operation @e[type=interaction,tag=vote_counter,tag=map5] vote_count = map5 vote_count
scoreboard players operation @e[type=interaction,tag=vote_counter,tag=map6] vote_count = map6 vote_count
scoreboard players operation @e[type=interaction,tag=vote_counter,tag=map7] vote_count = map7 vote_count
scoreboard players operation @e[type=interaction,tag=vote_counter,tag=map8] vote_count = map8 vote_count
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
return 1
