scoreboard players set @s ke_here 1
tag @s add KlutMobility
scoreboard players add @s ke_scan 0
scoreboard players remove @s ke_scan 1
scoreboard players set @s ke_input 0
execute if score @s e.cooldown matches 0 if score @s e.jumped matches 1.. run scoreboard players set @s ke_input 1
execute if score @s e.cooldown matches 0 if score @s e.sneakedTime matches 1.. run scoreboard players set @s ke_input -1
execute unless score @s ke_input matches 0 run scoreboard players set @s ke_scan 0
execute if score @s ke_scan matches ..0 run function klut27_elevators:probe
