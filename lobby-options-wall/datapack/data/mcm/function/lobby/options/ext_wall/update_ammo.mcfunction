scoreboard players set $wall_dependency temp 0
execute unless score $gunner_scrap GameRules matches 1 run scoreboard players set $wall_dependency temp 1
execute if score $ammo GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"每发子弹消耗废料","value":"关闭","color":"red","note":"每次开枪消耗1个废料"}
execute if score $ammo GameRules matches 1 run function mcm:lobby/options/ext_wall/render {"title":"每发子弹消耗废料","value":"开启","color":"green","note":"每次开枪消耗1个废料"}
