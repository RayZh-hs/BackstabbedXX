execute unless score $gamestate CmdData matches 1 run return 0
execute if score $graceperiod CmdData matches 1.. run return run function bbe_arena:middle_ages/tp
execute if score $graceperiod CmdData matches ..0 run function mcm:game/playerdeath
