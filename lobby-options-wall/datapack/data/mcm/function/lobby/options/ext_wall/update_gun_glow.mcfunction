scoreboard players set $wall_dependency temp 0
execute if score $gun_glow GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"掉落真枪全图透视","value":"关闭","color":"red","note":"高亮地图中的掉落真枪"}
execute if score $gun_glow GameRules matches 1 run function mcm:lobby/options/ext_wall/render {"title":"掉落真枪全图透视","value":"开启","color":"green","note":"高亮地图中的掉落真枪"}
