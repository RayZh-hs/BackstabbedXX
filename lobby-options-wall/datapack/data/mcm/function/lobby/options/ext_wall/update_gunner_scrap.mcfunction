scoreboard players set $wall_dependency temp 0
execute if score $gunner_scrap GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"持枪玩家存废料","value":"关闭","color":"red","note":"允许保留和拾取废料"}
execute if score $gunner_scrap GameRules matches 1 run function mcm:lobby/options/ext_wall/render {"title":"持枪玩家存废料","value":"开启","color":"green","note":"允许保留和拾取废料"}
