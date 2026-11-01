scoreboard objectives add bb_team dummy
scoreboard objectives add bb_respawn dummy
scoreboard objectives add bb_safe dummy
team add bb_red {"text":"Red","color":"red"}
team add bb_blue {"text":"Blue","color":"aqua"}
team modify bb_red color red
team modify bb_blue color aqua
team modify bb_red friendlyFire false
team modify bb_blue friendlyFire false
team modify bb_red collisionRule never
team modify bb_blue collisionRule never
team modify bb_red nametagVisibility hideForOtherTeams
team modify bb_blue nametagVisibility hideForOtherTeams
function mcm:modes/sync
