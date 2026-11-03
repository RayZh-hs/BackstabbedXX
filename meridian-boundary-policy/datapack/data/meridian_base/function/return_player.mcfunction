#> Return to the nearest valid current-arena player spawn. The previous fixed
#> point stays as the fallback when no marker qualifies.
execute in minecraft:overworld unless entity @e[type=marker,tag=PlayerSpawn,tag=MeridianBaseRuntime,predicate=meridian_base:arena,sort=nearest,limit=1] run tp @s 24582.5 -29 24576.5
execute in minecraft:overworld if entity @e[type=marker,tag=PlayerSpawn,tag=MeridianBaseRuntime,predicate=meridian_base:arena,sort=nearest,limit=1] run tp @s @e[type=marker,tag=PlayerSpawn,tag=MeridianBaseRuntime,predicate=meridian_base:arena,sort=nearest,limit=1]
effect clear @s minecraft:levitation
effect clear @s minecraft:slow_falling
