function klut27:mobility/release
gravity bridge reset @s
execute in minecraft:overworld if entity @e[type=marker,tag=PlayerSpawn,tag=Klut27Runtime,predicate=bbe_arena:klut27/arena,sort=nearest,limit=1] run return run tp @s @e[type=marker,tag=PlayerSpawn,tag=Klut27Runtime,predicate=bbe_arena:klut27/arena,sort=nearest,limit=1]
execute in minecraft:overworld run tp @s 36873.5 16 36879.5 90 0
