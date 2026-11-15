scoreboard players set $wall_dependency temp 0
execute if score $kill_reward GameRules matches -1 run function mcm:lobby/options/ext_wall/render {"title":"杀手击杀废料奖励","value":"受害者全部废料","color":"yellow","note":"右键循环切换"}
execute if score $kill_reward GameRules matches 0 run function mcm:lobby/options/ext_wall/render {"title":"杀手击杀废料奖励","value":"0 个废料","color":"yellow","note":"右键循环切换"}
execute if score $kill_reward GameRules matches 2 run function mcm:lobby/options/ext_wall/render {"title":"杀手击杀废料奖励","value":"2 个废料","color":"yellow","note":"右键循环切换"}
execute if score $kill_reward GameRules matches 3 run function mcm:lobby/options/ext_wall/render {"title":"杀手击杀废料奖励","value":"3 个废料","color":"yellow","note":"右键循环切换"}
execute if score $kill_reward GameRules matches 5 run function mcm:lobby/options/ext_wall/render {"title":"杀手击杀废料奖励","value":"5 个废料","color":"yellow","note":"右键循环切换"}
