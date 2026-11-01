scoreboard players operation $mode GameRules = @s mcm_options
scoreboard players remove $mode GameRules 15
execute store result storage mcm:options options.ext.mode int 1 run scoreboard players get $mode GameRules
