execute if score $mode CmdData matches 2 run return run function mcm:modes/killer_result
execute if score $winner CmdData matches 0 run title @a[tag=queued] title {"text":"Draw","color":"gold"}
execute if score $winner CmdData matches 0 run tellraw @a {"text":"Round ended in a draw.","color":"gold"}
execute if score $winner CmdData matches 1 run title @a[tag=queued] title {"text":"Red Team Wins!","color":"red"}
execute if score $winner CmdData matches 1 run tellraw @a {"text":"Red Team Wins!","color":"red"}
execute if score $winner CmdData matches 2 run title @a[tag=queued] title {"text":"Blue Team Wins!","color":"aqua"}
execute if score $winner CmdData matches 2 run tellraw @a {"text":"Blue Team Wins!","color":"aqua"}
execute as @a[tag=queued] if score @s bb_team = $winner CmdData run tag @s add WonLast
