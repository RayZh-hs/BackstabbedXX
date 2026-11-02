execute unless entity @s[tag=queued,tag=!spectating,gamemode=!spectator,predicate=mcm:game/not_eliminated,tag=murderer] run return 0
# Invalidate both loaded and unloaded copies before issuing a replacement.
data modify storage mcm:knife_recall owner set from entity @s UUID
scoreboard players add @s mcm_epoch 1
execute as @e[type=arrow,tag=knife] run function mcm:game/items/knife/kill_owned_entity with storage mcm:knife_recall
execute as @e[type=item] if items entity @s contents snowball[custom_data~{knife:1b}] run function mcm:game/items/knife/kill_owned_entity with storage mcm:knife_recall
clear @s carrot_on_a_stick[custom_data~{knife_retrieve:1}]
function mcm:items/give_item_cleanup
execute store result storage mcm:args id int 1 run scoreboard players get @s loadout_knife
function mcm:items/id with storage mcm:args
function mcm:extensions/knife/load_item with storage mcm:args
function mcm:extensions/knife/deliver with storage mcm:knife_restore
function mcm:items/give_item_cleanup
scoreboard players set @s mcm_missing 0
scoreboard players set @s throw_delay 20
tag @s add has_knife
tellraw @s {"text":"丢刀超时：已免费恢复你的飞刀。","color":"green"}
