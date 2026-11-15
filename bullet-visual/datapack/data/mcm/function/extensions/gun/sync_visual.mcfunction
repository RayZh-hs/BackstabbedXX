# Full projectile UUID: crossing or coincident shots cannot steal a visual.
# Displays transmit positions every tick; they do not predict clamped arrow velocity.
$execute unless entity @e[type=arrow,tag=GunShot,nbt={UUID:$(arrow_uuid)},limit=1] run return run kill @s
$execute at @e[type=arrow,tag=GunShot,nbt={UUID:$(arrow_uuid)},limit=1] run tp @s ~ ~ ~
