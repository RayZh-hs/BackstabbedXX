gravity bridge reset @s
execute in minecraft:overworld if entity @e[type=marker,tag=PlayerSpawn,tag=UnderwaterBaseRuntime,predicate=bbe_arena:underwater_base/arena,sort=nearest,limit=1] run return run tp @s @e[type=marker,tag=PlayerSpawn,tag=UnderwaterBaseRuntime,predicate=bbe_arena:underwater_base/arena,sort=nearest,limit=1]
execute in minecraft:overworld run tp @s 32958.5 43 32465.5 0 0
