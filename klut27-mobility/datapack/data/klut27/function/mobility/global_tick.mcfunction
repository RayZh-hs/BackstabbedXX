execute unless score $selectedMap CmdData matches 20 as @a[tag=KlutMobility] run function klut27:cleanup_player
execute unless score $gamestate CmdData matches 0..1 as @a[tag=KlutMobility] run function klut27:cleanup_player
execute as @a[tag=KlutMobility,tag=!queued] run function klut27:cleanup_player
execute as @a[tag=KlutMobility,tag=spectating] run function klut27:cleanup_player
execute as @a[tag=KlutMobility,gamemode=spectator] run function klut27:cleanup_player
execute as @a[tag=KlutMobility,scores={dead=1..}] run function klut27:cleanup_player
execute as @a[tag=KlutMobility,nbt={Health:0.0f}] run function klut27:cleanup_player
execute as @a[tag=KlutMobility] at @s unless dimension minecraft:overworld run function klut27:cleanup_player
