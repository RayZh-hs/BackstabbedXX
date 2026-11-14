# Runs as the bullet display AFTER gravity bridge fire has set its world rotation.
# Arrow passengers sit +0.5 world-Y above the actual trajectory. In the display's
# inverse yaw/pitch frame the correction is (0, -0.5*cos(pitch), +0.5*sin(pitch)).
# Vanilla local coordinates supply sine/cosine; no mod changes are required.
# Decimal coordinates avoid command parser's +0.5 X/Z block-centering.
execute rotated 0 ~ positioned 0.0 0.0 0.0 positioned ^ ^0.5 ^ summon marker run function mcm:extensions/gun/capture_visual_offset
data modify entity @s transformation.translation[0] set value 0.0f
execute store result entity @s transformation.translation[1] float -0.000001 run data get storage mcm:bullet_visual offset[1] 1000000
execute store result entity @s transformation.translation[2] float 0.000001 run data get storage mcm:bullet_visual offset[2] 1000000
data merge entity @s {interpolation_duration:0}
data remove storage mcm:bullet_visual offset
