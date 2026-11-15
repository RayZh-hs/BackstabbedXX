scoreboard players set $wall_dependency temp 0
execute if score $mode GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"游戏模式","value":"经典模式","color":"green","note":"点击下方选择"}
execute if score $mode GameRules matches 1 run function mcm:lobby/options/ext_wall/render {"title":"游戏模式","value":"枪手模式","color":"aqua","note":"点击下方选择"}
execute if score $mode GameRules matches 2 run function mcm:lobby/options/ext_wall/render {"title":"游戏模式","value":"杀手模式","color":"red","note":"点击下方选择"}
