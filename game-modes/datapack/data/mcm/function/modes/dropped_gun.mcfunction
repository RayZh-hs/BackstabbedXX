execute if entity @s[nbt={Age:5999s,PickupDelay:32767s}] run return run kill @s
data merge entity @s {PickupDelay:32767s,Age:-32768s}
execute unless data entity @s Thrower run return run kill @s
data modify storage mcm:gun_return owner set from entity @s Thrower
function mcm:extensions/gun/return_to_thrower with storage mcm:gun_return
