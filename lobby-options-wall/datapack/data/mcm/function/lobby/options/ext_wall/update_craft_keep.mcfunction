scoreboard players set $wall_dependency temp 0
execute unless score $gunner_scrap GameRules matches 1 run scoreboard players set $wall_dependency temp 1
execute if score $craft_keep GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"10废料获枪只扣8","value":"关闭","color":"red","note":"关闭时扣除全部废料"}
execute if score $craft_keep GameRules matches 1 run function mcm:lobby/options/ext_wall/render {"title":"10废料获枪只扣8","value":"开启","color":"green","note":"关闭时扣除全部废料"}
