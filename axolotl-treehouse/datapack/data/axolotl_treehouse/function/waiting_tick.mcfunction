execute unless score $selectedMap CmdData matches 25 run return 0
execute unless score $gamestate CmdData matches 0 run return 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s if predicate axolotl_treehouse:arena run tag @s add AxolotlTreehouseParticipant
execute as @a[tag=queued,tag=AxolotlTreehouseParticipant,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. if predicate axolotl_treehouse:lake_fall run function axolotl_treehouse:return_player
execute as @a[tag=queued,tag=AxolotlTreehouseParticipant,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. unless predicate axolotl_treehouse:arena run function axolotl_treehouse:return_player
