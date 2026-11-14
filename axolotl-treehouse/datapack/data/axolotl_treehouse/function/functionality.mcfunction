execute unless score $selectedMap CmdData matches 25 run return 0
execute unless score $gamestate CmdData matches 1 run return 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. run function axolotl_treehouse:check_player
