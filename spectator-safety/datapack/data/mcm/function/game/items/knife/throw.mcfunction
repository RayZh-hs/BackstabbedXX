execute unless entity @s[tag=queued,tag=!spectating,gamemode=!spectator,predicate=mcm:game/not_eliminated,tag=murderer] run return 0
# Inventory-change callbacks execute as the owner; capture that identity before entity switches.
data modify storage mcm:knife_throw owner set from entity @s UUID
execute if score @s droppedKnife matches 1.. run return run function mcm:extensions/knife/drop
function mcm:extensions/knife/throw_owned with storage mcm:knife_throw
