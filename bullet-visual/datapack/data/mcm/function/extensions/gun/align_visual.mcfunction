# Runs as the invisible orientation template after the unchanged gravity bridge.
# Do not reuse/dismount it: clients can retain its passenger link for the entire shot.
data modify storage mcm:bullet_visual rotation set from entity @s Rotation
data modify storage mcm:bullet_visual transformation set from entity @s transformation
data modify storage mcm:bullet_visual transformation.translation set value [0.0f,0.0f,0.0f]
function mcm:extensions/gun/spawn_visual with storage mcm:bullet_visual
data remove storage mcm:bullet_visual rotation
data remove storage mcm:bullet_visual transformation
kill @s
