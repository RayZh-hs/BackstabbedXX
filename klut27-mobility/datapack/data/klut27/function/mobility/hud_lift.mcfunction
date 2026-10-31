scoreboard players operation @s kb_sec = @s e.cooldown
scoreboard players add @s kb_sec 1
scoreboard players operation @s kb_sec /= $two kb_math
scoreboard players operation @s kb_dec = @s kb_sec
scoreboard players operation @s kb_dec %= $ten kb_math
scoreboard players operation @s kb_sec /= $ten kb_math
execute store result storage klut27:hud line.sec int 1 run scoreboard players get @s kb_sec
execute store result storage klut27:hud line.dec int 1 run scoreboard players get @s kb_dec
execute if score @s e.cooldown matches 1..3 run data modify storage klut27:hud line.bar set value "■—————————"
execute if score @s e.cooldown matches 4..6 run data modify storage klut27:hud line.bar set value "■■————————"
execute if score @s e.cooldown matches 7..9 run data modify storage klut27:hud line.bar set value "■■■———————"
execute if score @s e.cooldown matches 10..12 run data modify storage klut27:hud line.bar set value "■■■■——————"
execute if score @s e.cooldown matches 13..15 run data modify storage klut27:hud line.bar set value "■■■■■—————"
execute if score @s e.cooldown matches 16..18 run data modify storage klut27:hud line.bar set value "■■■■■■————"
execute if score @s e.cooldown matches 19..21 run data modify storage klut27:hud line.bar set value "■■■■■■■———"
execute if score @s e.cooldown matches 22..24 run data modify storage klut27:hud line.bar set value "■■■■■■■■——"
execute if score @s e.cooldown matches 25..27 run data modify storage klut27:hud line.bar set value "■■■■■■■■■—"
execute if score @s e.cooldown matches 28..30 run data modify storage klut27:hud line.bar set value "■■■■■■■■■■"
function klut27:mobility/hud_lift_text with storage klut27:hud line
