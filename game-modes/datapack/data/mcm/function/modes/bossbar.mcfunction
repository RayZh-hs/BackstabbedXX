execute if score $mode CmdData matches 2 store result bossbar gamedisplay max if entity @a[tag=queued]
execute if score $mode CmdData matches 2 store result bossbar gamedisplay value run scoreboard players get $killer_alive CmdData
execute if score $mode CmdData matches 2 run return run bossbar set gamedisplay name [{"text":"Players left: ","color":"red"},{"score":{"name":"$killer_alive","objective":"CmdData"}}]
bossbar set gamedisplay name [{"text":"Red: ","color":"red"},{"score":{"name":"$red_alive","objective":"CmdData"}},{"text":" | "},{"score":{"name":"$gameminutes","objective":"CmdData"}},{"text":"m "},{"score":{"name":"$gameseconds","objective":"CmdData"}},{"text":"s | Blue: ","color":"aqua"},{"score":{"name":"$blue_alive","objective":"CmdData"}}]
