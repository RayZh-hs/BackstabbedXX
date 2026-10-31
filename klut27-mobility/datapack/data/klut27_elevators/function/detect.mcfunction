scoreboard players set @s ke_here 0
execute unless dimension minecraft:overworld run return 0
execute unless predicate klut27:arena run return 0

scoreboard players set @s ke_dir 0
execute store result score @s ke_dir run gravity bridge is_down @s
execute if entity @s[nbt={"neoforge:attachments":{"gravity_changer:gravity_data":{currentGravityDirection:"up"}}}] run scoreboard players set @s ke_dir -1
execute if score @s ke_dir matches 1 positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:white_shulker_box{lock:{components:{"minecraft:custom_name":"\"5567353566-5331\""}}} align xyz positioned ~0.5 ~ ~0.5 run function klut27_elevators:player
execute if score @s ke_dir matches -1 positioned ~ ~0.01 ~ if block ~ ~ ~ minecraft:white_shulker_box{lock:{components:{"minecraft:custom_name":"\"5567353566-5331\""}}} align xyz positioned ~0.5 ~ ~0.5 run function klut27_elevators:player
execute if score @s ke_dir matches -1 unless score @s ke_here matches 1 positioned ~ ~1 ~ if block ~ ~ ~ minecraft:white_shulker_box{lock:{components:{"minecraft:custom_name":"\"5567353566-5331\""}}} align xyz positioned ~0.5 ~ ~0.5 run function klut27_elevators:player
execute if score @s ke_here matches 0 run scoreboard players set @s ke_scan 0
