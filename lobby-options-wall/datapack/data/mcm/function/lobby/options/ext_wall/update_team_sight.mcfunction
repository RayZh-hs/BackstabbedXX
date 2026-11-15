scoreboard players set $wall_dependency temp 0
execute if score $team_sight GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"杀手互相透视","value":"关闭","color":"red","note":"范围32格，仅杀手可见"}
execute if score $team_sight GameRules matches 1 run function mcm:lobby/options/ext_wall/render {"title":"杀手互相透视","value":"开启","color":"green","note":"范围32格，仅杀手可见"}
