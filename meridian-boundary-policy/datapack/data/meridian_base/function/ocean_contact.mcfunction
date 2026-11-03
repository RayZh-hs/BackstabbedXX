#> The exterior ocean only rescues while the round is still in preparation.
#> Once the round is active it eliminates, matching the arena boundary.
execute if score $graceperiod CmdData matches 1.. run return run function meridian_base:return_player
function mcm:game/playerdeath
