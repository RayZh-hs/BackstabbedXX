execute unless score $selectedMap CmdData matches 20 run return 0
execute unless score $gamestate CmdData matches 0..1 run return 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. run function klut27:mobility/player
function klut27_elevators:tick
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. run function klut27:mobility/hud
