# Execute-summon supplies @s directly, even if world origin's chunk is unloaded.
tag @s add McmBulletVisualOffset
data modify storage mcm:bullet_visual offset set from entity @s Pos
kill @s
