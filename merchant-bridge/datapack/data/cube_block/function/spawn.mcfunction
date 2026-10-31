# Called as the spawning player, after the shared occupancy pool refresh.
# Select exactly once: gravity and destination must come from the same marker.
tag @e[type=marker,tag=CubeBlockSelectedSpawn] remove CubeBlockSelectedSpawn
tag @e[type=marker,tag=PlayerSpawn,tag=CubeBlockRuntime,tag=!Occupied,sort=random,limit=1] add CubeBlockSelectedSpawn
execute store success score @s cube_spawn run arena_spawn_gravity @e[type=marker,tag=CubeBlockSelectedSpawn,limit=1]
execute unless score @s cube_spawn matches 1 run tag @e[type=marker,tag=CubeBlockSelectedSpawn] remove CubeBlockSelectedSpawn
execute unless score @s cube_spawn matches 1 run return 0
tp @s @e[type=marker,tag=CubeBlockSelectedSpawn,limit=1]
tag @e[type=marker,tag=CubeBlockSelectedSpawn] add Occupied
tag @e[type=marker,tag=CubeBlockSelectedSpawn] remove CubeBlockSelectedSpawn
