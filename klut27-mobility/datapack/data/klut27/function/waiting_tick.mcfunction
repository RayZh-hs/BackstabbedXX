execute unless score $selectedMap CmdData matches 20 run return 0
execute unless score $gamestate CmdData matches 0 run return 0
function klut27:mobility/tick
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s if predicate klut27:arena run tag @s add Klut27Participant
execute as @a[tag=queued,tag=Klut27Participant,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. unless predicate klut27:arena run function klut27:fall
