scoreboard players set $wall_dependency temp 0
execute if score $shield GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"首次10废料赠盾","value":"关闭","color":"red","note":"杀手获得一次性盾牌"}
execute if score $shield GameRules matches 1 run function mcm:lobby/options/ext_wall/render {"title":"首次10废料赠盾","value":"开启","color":"green","note":"杀手获得一次性盾牌"}
