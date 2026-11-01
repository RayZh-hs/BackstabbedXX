$scoreboard players set $$(key)_out CmdData 1
$tellraw @a {"text":"$(name) team has been eliminated!","color":"$(color)"}
$execute as @a[tag=queued,tag=!spectating,scores={bb_team=$(team)}] run function mcm:game/playerdeath
$scoreboard players set @a[scores={bb_team=$(team)}] bb_respawn 0
