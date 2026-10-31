execute unless score $selectedMap CmdData matches 20 run return 0
execute unless score $gamestate CmdData matches 1 run return 0
execute unless entity @s[tag=queued,tag=!spectating,gamemode=!spectator] run return 0
execute if score @s dead matches 1.. run return 0
execute if score $graceperiod CmdData matches 1.. run return run function bbe_arena:klut27/tp
execute unless score $graceperiod CmdData matches ..0 run return 0
tellraw @a {"translate":"klut27.death.fall","fallback":"%s drifted away from KLUT-27","with":[{"selector":"@s"}],"color":"gold"}
function mcm:game/playerdeath
