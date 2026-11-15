$scoreboard players set @s mcm_options $(action)
execute if score @s mcm_options matches 2..22 run function mcm:extensions/options/change
scoreboard players set @s mcm_options 0
scoreboard players enable @s mcm_options
