scoreboard players set @s bb_respawn 0
execute if score $mode CmdData matches 1 if entity @s[tag=!gunner] run scoreboard players set @s bb_respawn 60
