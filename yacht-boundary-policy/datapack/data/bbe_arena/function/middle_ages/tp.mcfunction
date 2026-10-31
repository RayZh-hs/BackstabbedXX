gravity bridge reset @s
execute in minecraft:overworld if entity @e[type=marker,tag=PlayerSpawn,tag=MiddleAgesRuntime,predicate=bbe_arena:middle_ages/arena,sort=nearest,limit=1] run return run tp @s @e[type=marker,tag=PlayerSpawn,tag=MiddleAgesRuntime,predicate=bbe_arena:middle_ages/arena,sort=nearest,limit=1]
execute in minecraft:overworld run tp @s 45061.5 96 45056.5 0 0
