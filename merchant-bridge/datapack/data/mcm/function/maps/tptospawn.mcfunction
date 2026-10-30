# Clear the previous arena gravity before spawning/returning to the lobby.
gravity bridge reset @s
#> If all spawns are full, remove the occupied tag from them and start again
execute unless entity @e[type=marker,tag=PlayerSpawn,tag=!Occupied] as @e[type=marker,tag=PlayerSpawn,tag=Occupied] run tag @s remove Occupied

#> John Spawnpoint (launchpad only)
execute if score $selectedMap CmdData matches 4 as @r[limit=1] at @s if entity @s[name=JohnStar128,tag=queued,tag=!murderer] run tp @s @e[type=marker,tag=JohnSpawn,limit=1]
#> Blocky Spawnpoint (launchpad only)
execute if score $selectedMap CmdData matches 4 as @r[limit=1] at @s if entity @s[name=BlockyM_,tag=queued,tag=!murderer] run tp @s @e[type=marker,tag=BlockySpawn,limit=1]

# Cube Block uses one selected marker for both gravity and teleport.
execute if score $selectedMap CmdData matches 23 run return run function cube_block:spawn

#> Teleport players to spawns
tp @s @e[type=marker,tag=PlayerSpawn,tag=!Occupied,limit=1,sort=random]

execute as @s at @s run tag @e[type=marker,tag=PlayerSpawn,limit=1,sort=nearest,distance=..1] add Occupied
