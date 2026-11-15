data merge entity @s {text:'{"text":"[重新随机候选图]","color":"aqua","extra":[{"text":"\\n清空投票并重新抽取8张","color":"gray"}]}'}
execute if data storage mcm:options options{locked:1} run data merge entity @s {text:'{"text":"[重新随机候选图]","color":"gray","extra":[{"text":"\\n大厅设置已锁定","color":"gray"}]}'}
execute if score $gamestate CmdData matches 1.. run data merge entity @s {text:'{"text":"[重新随机候选图]","color":"gray","extra":[{"text":"\\n对局中不可修改","color":"gray"}]}'}
