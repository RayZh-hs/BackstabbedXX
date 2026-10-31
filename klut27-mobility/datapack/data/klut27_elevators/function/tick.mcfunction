scoreboard players add @a[tag=queued,tag=!spectating,gamemode=!spectator] e.cooldown 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] if score @s e.cooldown matches 1.. run scoreboard players remove @s e.cooldown 1
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. run function klut27_elevators:detect
scoreboard players set @a[tag=queued,tag=!spectating,gamemode=!spectator] e.jumped 0
scoreboard players set @a[tag=queued,tag=!spectating,gamemode=!spectator] e.sneakedTime 0
