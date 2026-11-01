execute unless entity @a[tag=queued,tag=murderer,tag=!spectating] if score $classic_red_out CmdData matches 0 run tellraw @a {"text":"Murderer team has been eliminated!","color":"red"}
execute unless entity @a[tag=queued,tag=murderer,tag=!spectating] run scoreboard players set $classic_red_out CmdData 1
execute unless entity @a[tag=queued,tag=innocent,tag=!spectating] if score $classic_blue_out CmdData matches 0 run tellraw @a {"text":"Innocent team has been eliminated!","color":"aqua"}
execute unless entity @a[tag=queued,tag=innocent,tag=!spectating] run scoreboard players set $classic_blue_out CmdData 1
