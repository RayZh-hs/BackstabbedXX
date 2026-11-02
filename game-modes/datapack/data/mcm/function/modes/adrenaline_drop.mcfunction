# Use the same components as the loadout bottle, including its model and use action.
execute at @s run summon item ~ ~ ~ {Tags:["KeyItem","bb_kill_adrenaline","bb_new_adrenaline"],PickupDelay:10s,Invulnerable:1b,Item:{id:"minecraft:carrot_on_a_stick",count:1}}
execute as @e[type=item,tag=bb_new_adrenaline] run data modify entity @s Item.components set from storage mcm:items adrenaline.nbt
tag @e[type=item,tag=bb_new_adrenaline] remove bb_new_adrenaline
