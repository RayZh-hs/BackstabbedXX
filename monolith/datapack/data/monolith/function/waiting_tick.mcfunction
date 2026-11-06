execute unless score $selectedMap CmdData matches 24 run return 0
execute unless score $gamestate CmdData matches 0 run return 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s if predicate monolith:arena run tag @s add MonolithParticipant
execute as @a[tag=queued,tag=MonolithParticipant,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. unless predicate monolith:arena run function monolith:return_player
