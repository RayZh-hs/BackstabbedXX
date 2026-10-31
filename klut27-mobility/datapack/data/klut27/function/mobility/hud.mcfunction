data modify storage klut27:hud line set value {hint:"",lift:"",boots:""}
execute if score @s ke_here matches 1 if score @s e.cooldown matches 0 if score @s ke_up matches 1 run data modify storage klut27:hud line.hint set value "JUMP to go UP"
execute if score @s ke_here matches 1 if score @s e.cooldown matches 0 if score @s ke_down matches 1 run data modify storage klut27:hud line.hint set value "SNEAK to go DOWN"
execute if score @s ke_here matches 1 if score @s e.cooldown matches 0 if score @s ke_up matches 1 if score @s ke_down matches 1 run data modify storage klut27:hud line.hint set value "JUMP to go UP | SNEAK to go DOWN"
execute if score @s e.cooldown matches 1.. run function klut27:mobility/hud_lift
execute if score @s kb_cd matches 1.. run function klut27:mobility/hud_boots
execute if data storage klut27:hud line{hint:"",lift:"",boots:""} run return run function klut27:mobility/hud_clear
tag @s add KlutMobilityHud
function klut27:mobility/hud_render with storage klut27:hud line
