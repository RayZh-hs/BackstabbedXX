scoreboard players set @s ke_up 0
scoreboard players set @s ke_down 0
scoreboard players set @s ke_move 0
function klut27_elevators:find_upper
execute if score @s ke_move matches 0 run function klut27_elevators:find_lower
scoreboard players set @s ke_scan 5
