scoreboard players set $wall_dependency temp 0
execute if score $gunner_respawn GameRules matches 3 run function mcm:lobby/options/ext_wall/render {"title":"枪手复活时间","value":"3 秒","color":"yellow","note":"仅枪手模式生效"}
execute if score $gunner_respawn GameRules matches 5 run function mcm:lobby/options/ext_wall/render {"title":"枪手复活时间","value":"5 秒","color":"yellow","note":"仅枪手模式生效"}
execute if score $gunner_respawn GameRules matches 10 run function mcm:lobby/options/ext_wall/render {"title":"枪手复活时间","value":"10 秒","color":"yellow","note":"仅枪手模式生效"}
execute if score $gunner_respawn GameRules matches 20 run function mcm:lobby/options/ext_wall/render {"title":"枪手复活时间","value":"20 秒","color":"yellow","note":"仅枪手模式生效"}
execute if score $gunner_respawn GameRules matches 30 run function mcm:lobby/options/ext_wall/render {"title":"枪手复活时间","value":"30 秒","color":"yellow","note":"仅枪手模式生效"}
