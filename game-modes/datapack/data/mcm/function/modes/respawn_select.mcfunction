execute if score @s mcm_options matches 18 run scoreboard players set $gunner_respawn GameRules 3
execute if score @s mcm_options matches 19 run scoreboard players set $gunner_respawn GameRules 5
execute if score @s mcm_options matches 20 run scoreboard players set $gunner_respawn GameRules 10
execute if score @s mcm_options matches 21 run scoreboard players set $gunner_respawn GameRules 20
execute if score @s mcm_options matches 22 run scoreboard players set $gunner_respawn GameRules 30
execute store result storage mcm:options options.ext.gunner_respawn int 1 run scoreboard players get $gunner_respawn GameRules
