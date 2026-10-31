execute if entity @s[tag=klut.e.inverted] if block ~ ~-1 ~ #klut27_elevators:clear if block ~ ~-2 ~ #klut27_elevators:clear run tag @s add klut.e.found
execute if entity @s[tag=klut.e.inverted] run return 0
execute unless block ~ ~1 ~ #klut27_elevators:clear run return 0
execute if block ~ ~2 ~ #klut27_elevators:clear run tag @s add klut.e.found
execute if block ~ ~2 ~ #minecraft:trapdoors[half=top,open=false,waterlogged=false] run tag @s add klut.e.found
