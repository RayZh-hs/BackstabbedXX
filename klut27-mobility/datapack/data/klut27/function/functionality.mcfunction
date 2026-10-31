execute unless score $selectedMap CmdData matches 20 run return 0
execute unless score $gamestate CmdData matches 1 run return 0
function klut27:mobility/tick
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. unless predicate klut27:arena run function klut27:fall
function klut27:air_tick
function klut27:npc_tick
function klut27:fire/tick
