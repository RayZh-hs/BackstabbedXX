scoreboard players set $wall_dependency temp 0
execute if score $global_glow GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"全体存活玩家高亮","value":"关闭","color":"red","note":"每2分钟5秒／最后20秒"}
execute if score $global_glow GameRules matches 1 run function mcm:lobby/options/ext_wall/render {"title":"全体存活玩家高亮","value":"开启","color":"green","note":"每2分钟5秒／最后20秒"}
