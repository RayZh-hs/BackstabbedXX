advancement revoke @s only mcm:map_votes/map3
execute unless score $gamestate CmdData matches -1 run return fail
execute unless entity @e[type=interaction,tag=vote_counter,tag=map3,tag=!disabled,nbt={response:1b}] run return fail
scoreboard players set @s vote_position 3
scoreboard players operation @s vote_map_id = @e[type=interaction,tag=vote_counter,tag=map3,limit=1] vote_map_id
function mcm:lobby/voting/player_vote
