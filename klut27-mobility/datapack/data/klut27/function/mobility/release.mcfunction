execute if entity @s[tag=KlutMobility] run gravity set_base_direction down @s
execute if entity @s[tag=KlutMobility] run effect clear @s minecraft:slow_falling
execute if entity @s[tag=KlutMobility] run effect clear @s minecraft:jump_boost
tag @s remove KlutMobility
tag @s remove KlutBootsEquipped
tag @s remove KlutBootsUp
