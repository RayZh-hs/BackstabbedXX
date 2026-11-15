scoreboard players set $wall_dependency temp 0
execute if score $scrap_rate GameRules matches 50 run function mcm:lobby/options/ext_wall/render {"title":"碎片刷新倍率","value":"0.5×","color":"yellow","note":"右键循环切换"}
execute if score $scrap_rate GameRules matches 80 run function mcm:lobby/options/ext_wall/render {"title":"碎片刷新倍率","value":"0.8×","color":"yellow","note":"右键循环切换"}
execute if score $scrap_rate GameRules matches 100 run function mcm:lobby/options/ext_wall/render {"title":"碎片刷新倍率","value":"1×","color":"yellow","note":"右键循环切换"}
execute if score $scrap_rate GameRules matches 150 run function mcm:lobby/options/ext_wall/render {"title":"碎片刷新倍率","value":"1.5×","color":"yellow","note":"右键循环切换"}
execute if score $scrap_rate GameRules matches 200 run function mcm:lobby/options/ext_wall/render {"title":"碎片刷新倍率","value":"2×","color":"yellow","note":"右键循环切换"}
