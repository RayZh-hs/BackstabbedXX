execute unless score $pickedroles CmdData matches 1 run return 0
execute if score $graceperiod CmdData matches 1.. run return 0
execute unless score $mode CmdData matches 1..2 run return run function mcm:modes/classic
# Snapshot both teams before eliminating survivors, so simultaneous losses draw.
scoreboard players set $red_alive CmdData 0
scoreboard players set $blue_alive CmdData 0
execute if score $mode CmdData matches 1 store result score $red_alive CmdData if entity @a[tag=queued,tag=!spectating,tag=gunner,scores={bb_team=1}]
execute if score $mode CmdData matches 1 store result score $blue_alive CmdData if entity @a[tag=queued,tag=!spectating,tag=gunner,scores={bb_team=2}]
execute if score $mode CmdData matches 2 store result score $red_alive CmdData if entity @a[tag=queued,tag=!spectating,scores={bb_team=1}]
execute if score $mode CmdData matches 2 store result score $blue_alive CmdData if entity @a[tag=queued,tag=!spectating,scores={bb_team=2}]
execute if score $red_alive CmdData matches 0 if score $red_out CmdData matches 0 run function mcm:modes/eliminate {team:1,key:"red",name:"Red",color:"red"}
execute if score $blue_alive CmdData matches 0 if score $blue_out CmdData matches 0 run function mcm:modes/eliminate {team:2,key:"blue",name:"Blue",color:"aqua"}
# Rejoining cannot resurrect a team that was already eliminated.
execute if score $red_out CmdData matches 1 as @a[tag=queued,tag=!spectating,scores={bb_team=1}] run function mcm:game/playerdeath
execute if score $blue_out CmdData matches 1 as @a[tag=queued,tag=!spectating,scores={bb_team=2}] run function mcm:game/playerdeath
execute if score $red_out CmdData matches 1 run scoreboard players set @a[scores={bb_team=1}] bb_respawn 0
execute if score $blue_out CmdData matches 1 run scoreboard players set @a[scores={bb_team=2}] bb_respawn 0
execute if score $red_out CmdData matches 1 if score $blue_out CmdData matches 0 run scoreboard players set $winner CmdData 2
execute if score $blue_out CmdData matches 1 if score $red_out CmdData matches 0 run scoreboard players set $winner CmdData 1
execute if score $red_out CmdData matches 1 run scoreboard players set $gamestate CmdData 2
execute if score $blue_out CmdData matches 1 run scoreboard players set $gamestate CmdData 2
execute if score $gametimer CmdData matches ..0 run scoreboard players set $gamestate CmdData 2
execute unless score $gamestate CmdData matches 1 run return 0
scoreboard players remove @a[scores={bb_safe=1..}] bb_safe 1
execute if score $mode CmdData matches 1 as @a[tag=queued,tag=!spectating,tag=!gunner] run function mcm:modes/upgrade
execute as @a[tag=queued,tag=spectating,scores={bb_respawn=1}] run function mcm:modes/respawn
scoreboard players remove @a[scores={bb_respawn=1..}] bb_respawn 1
