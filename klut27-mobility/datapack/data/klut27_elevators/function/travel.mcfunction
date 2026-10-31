execute if score @s ke_dir matches 1 run tp @s ~ ~1 ~
execute if score @s ke_dir matches -1 run tp @s ~ ~-0.000002 ~
scoreboard players set @s e.cooldown 30
scoreboard players set @s ke_move 1
scoreboard players set @s ke_scan 0
