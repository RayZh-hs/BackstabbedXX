execute if score $winner CmdData matches 0 run title @a[tag=queued] title {"text":"Draw","color":"gold"}
execute if score $winner CmdData matches 0 run tellraw @a {"text":"Round ended in a draw.","color":"gold"}
execute if score $winner CmdData matches 1 run title @a[tag=queued] title [{"selector":"@a[tag=bb_killer_winner]"},{"text":" Wins!","color":"gold"}]
execute if score $winner CmdData matches 1 run tellraw @a [{"selector":"@a[tag=bb_killer_winner]"},{"text":" is the last player standing!","color":"gold"}]
execute if score $winner CmdData matches 1 run tag @a[tag=bb_killer_winner] add WonLast
