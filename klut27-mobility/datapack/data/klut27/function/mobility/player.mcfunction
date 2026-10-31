execute unless dimension minecraft:overworld run return 0
function klut27:mobility/remove_hook
scoreboard players add @s kb_cd 0
execute if score @s kb_cd matches 1.. run scoreboard players remove @s kb_cd 1
execute unless items entity @s armor.feet minecraft:leather_boots[custom_data~{klut27_boots:1b}] run function klut27:mobility/release
execute unless items entity @s armor.feet minecraft:leather_boots[custom_data~{klut27_boots:1b}] run return 0
tag @s add KlutMobility
tag @s add KlutBootsEquipped
execute if score @s kb_cd matches 0 unless entity @s[tag=KlutBootsUp] if predicate klut27:boots_low run function klut27:mobility/up
execute if score @s kb_cd matches 0 if entity @s[tag=KlutBootsUp] if predicate klut27:boots_high run function klut27:mobility/down
