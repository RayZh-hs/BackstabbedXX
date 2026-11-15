scoreboard players set $wall_dependency temp 0
execute if score $scrap_boost GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"开局30秒碎片加速","value":"关闭","color":"red","note":"刷新速率额外翻倍"}
execute if score $scrap_boost GameRules matches 1 run function mcm:lobby/options/ext_wall/render {"title":"开局30秒碎片加速","value":"开启","color":"green","note":"刷新速率额外翻倍"}
