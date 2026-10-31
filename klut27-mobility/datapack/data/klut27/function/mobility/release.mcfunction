execute if entity @s[tag=KlutBootsEquipped] run gravity set_base_direction down @s
execute if entity @s[tag=KlutBootsEquipped] run effect clear @s minecraft:slow_falling
execute if entity @s[tag=KlutBootsEquipped] run effect clear @s minecraft:jump_boost
tag @s remove KlutBootsEquipped
tag @s remove KlutBootsUp
