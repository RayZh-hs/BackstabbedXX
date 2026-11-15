execute unless score $gamestate CmdData matches -1..0 run return fail
execute if data storage mcm:options options{locked:1} run return fail
function mcm:lobby/voting/enabled_changed
