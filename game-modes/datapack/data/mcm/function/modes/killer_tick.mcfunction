execute unless score $gamestate CmdData matches 1 run return 0
execute store result score $killer_alive CmdData if entity @a[tag=queued,tag=!spectating]
execute if score $killer_alive CmdData matches 1 run tag @a[tag=queued,tag=!spectating] add bb_killer_winner
execute if score $killer_alive CmdData matches 1 run scoreboard players set $winner CmdData 1
execute if score $killer_alive CmdData matches ..1 run scoreboard players set $gamestate CmdData 2
