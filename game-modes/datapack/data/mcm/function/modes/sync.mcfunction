execute store result score $mode GameRules run data get storage mcm:options options.ext.mode
execute unless score $mode GameRules matches 0..2 run scoreboard players set $mode GameRules 0
execute store result storage mcm:options options.ext.mode int 1 run scoreboard players get $mode GameRules
scoreboard players set $gunner_respawn GameRules 10
execute store result score $gunner_respawn GameRules run data get storage mcm:options options.ext.gunner_respawn
execute unless score $gunner_respawn GameRules matches 3 unless score $gunner_respawn GameRules matches 5 unless score $gunner_respawn GameRules matches 10 unless score $gunner_respawn GameRules matches 20 unless score $gunner_respawn GameRules matches 30 run scoreboard players set $gunner_respawn GameRules 10
execute store result storage mcm:options options.ext.gunner_respawn int 1 run scoreboard players get $gunner_respawn GameRules
scoreboard players operation $gunner_respawn_ticks GameRules = $gunner_respawn GameRules
scoreboard players operation $gunner_respawn_ticks GameRules *= $twenty math
