tp @s ~ ~-1 ~
execute at @s if block ~ ~ ~ minecraft:white_shulker_box{lock:{components:{"minecraft:custom_name":"\"5567353566-5331\""}}} run function klut27_elevators:check_landing
scoreboard players remove @s e.steps 1
execute if score @s e.steps matches 1.. unless entity @s[tag=klut.e.found] at @s run function klut27_elevators:search_lower
