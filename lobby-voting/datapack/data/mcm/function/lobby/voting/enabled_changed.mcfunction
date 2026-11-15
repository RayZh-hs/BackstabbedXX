execute unless score $gamestate CmdData matches -1..0 run return fail
execute if data storage mcm:options init run return fail
execute if score $gamestate CmdData matches 0 run function mcm:lobby/voting/cancel_preparation
function mcm:lobby/voting/start
tellraw @a {"text":"候选地图已更新，请重新投票。","color":"yellow"}
