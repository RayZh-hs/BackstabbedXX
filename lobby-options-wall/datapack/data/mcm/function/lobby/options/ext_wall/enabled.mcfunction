execute if score $gamestate CmdData matches 1.. run return fail
execute if data storage mcm:options options{locked:1} run return fail
$scoreboard players set $wall_action temp $(action)
execute if score $wall_action temp matches 4..5 unless score $gunner_scrap GameRules matches 1 run return fail
execute if score $wall_action temp matches 7 if score $knife_seconds GameRules matches ..5 run return fail
execute if score $wall_action temp matches 8 if score $knife_seconds GameRules matches 30.. run return fail
return 1
