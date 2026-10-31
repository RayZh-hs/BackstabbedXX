execute unless score $selectedMap CmdData matches 22 run return 0
execute unless score $gamestate CmdData matches 1 run return 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. run function bbe_arena:middle_ages/check_player
