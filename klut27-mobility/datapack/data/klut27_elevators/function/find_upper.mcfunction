kill @e[type=marker,tag=klut.e.search]
summon marker ~ ~ ~ {Tags:["klut.e.search"]}
execute if score @s ke_dir matches -1 run tag @e[type=marker,tag=klut.e.search] add klut.e.inverted
scoreboard players set @e[type=marker,tag=klut.e.search] e.steps 120
execute as @e[type=marker,tag=klut.e.search,limit=1] at @s run function klut27_elevators:search_upper
execute store success score @s ke_up if entity @e[type=marker,tag=klut.e.found]
execute if score @s ke_up matches 1 if score @s ke_input matches 1 if score @s e.cooldown matches 0 at @e[type=marker,tag=klut.e.found,limit=1] run function klut27_elevators:travel
kill @e[type=marker,tag=klut.e.search]
