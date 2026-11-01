scoreboard players operation @s bb_team = $next_team CmdData
execute if score @s bb_team matches 1 run team join bb_red @s
execute if score @s bb_team matches 2 run team join bb_blue @s
execute if score @s bb_team matches 1 run title @s title {"text":"Red Team","color":"red"}
execute if score @s bb_team matches 2 run title @s title {"text":"Blue Team","color":"aqua"}
scoreboard players set $next_team CmdData 1
execute if score @s bb_team matches 1 run scoreboard players set $next_team CmdData 2
