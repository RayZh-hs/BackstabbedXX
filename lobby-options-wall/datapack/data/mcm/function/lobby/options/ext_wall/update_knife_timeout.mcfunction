scoreboard players set $wall_dependency temp 0
execute if score $knife_timeout GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"丢刀超时保底","value":"关闭","color":"red","note":"超时后自动恢复飞刀"}
execute if score $knife_timeout GameRules matches 1 run function mcm:lobby/options/ext_wall/render {"title":"丢刀超时保底","value":"开启","color":"green","note":"超时后自动恢复飞刀"}
