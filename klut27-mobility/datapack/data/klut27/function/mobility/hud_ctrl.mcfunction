scoreboard players operation @s kc_sec = @s kc_cd
scoreboard players add @s kc_sec 1
scoreboard players operation @s kc_sec /= $two kc_math
scoreboard players operation @s kc_dec = @s kc_sec
scoreboard players operation @s kc_dec %= $ten kc_math
scoreboard players operation @s kc_sec /= $ten kc_math
execute store result storage klut27:hud line.sec int 1 run scoreboard players get @s kc_sec
execute store result storage klut27:hud line.dec int 1 run scoreboard players get @s kc_dec
execute if score @s kc_cd matches 1..30 run data modify storage klut27:hud line.bar set value "■—————————"
execute if score @s kc_cd matches 31..60 run data modify storage klut27:hud line.bar set value "■■————————"
execute if score @s kc_cd matches 61..90 run data modify storage klut27:hud line.bar set value "■■■———————"
execute if score @s kc_cd matches 91..120 run data modify storage klut27:hud line.bar set value "■■■■——————"
execute if score @s kc_cd matches 121..150 run data modify storage klut27:hud line.bar set value "■■■■■—————"
execute if score @s kc_cd matches 151..180 run data modify storage klut27:hud line.bar set value "■■■■■■————"
execute if score @s kc_cd matches 181..210 run data modify storage klut27:hud line.bar set value "■■■■■■■———"
execute if score @s kc_cd matches 211..240 run data modify storage klut27:hud line.bar set value "■■■■■■■■——"
execute if score @s kc_cd matches 241..270 run data modify storage klut27:hud line.bar set value "■■■■■■■■■—"
execute if score @s kc_cd matches 271..300 run data modify storage klut27:hud line.bar set value "■■■■■■■■■■"
function klut27:mobility/hud_ctrl_text with storage klut27:hud line
