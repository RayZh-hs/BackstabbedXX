# Only a living participating owner can pull a stuck knife. Compare the full UUID.
execute unless data entity @s Owner run return 0
data modify storage mcm:knife_unstuck owner set from entity @s Owner
function mcm:game/items/knife/unstick_owned with storage mcm:knife_unstuck
