execute store result score $mode GameRules run data get storage mcm:options options.ext.mode
execute unless score $mode GameRules matches 0..2 run scoreboard players set $mode GameRules 0
execute store result storage mcm:options options.ext.mode int 1 run scoreboard players get $mode GameRules
