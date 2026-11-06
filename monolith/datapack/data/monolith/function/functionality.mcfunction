execute unless score $selectedMap CmdData matches 24 run return 0
execute unless score $gamestate CmdData matches 1 run return 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. run function monolith:check_player
execute if score $graceperiod CmdData matches ..0 as @a[tag=queued,tag=!spectating,tag=!MonolithEquipped,gamemode=!spectator] unless score @s dead matches 1.. run function monolith:equipment
