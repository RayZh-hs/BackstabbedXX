# The exact recorded clicker, never the nearest player or everyone in the room.
$execute as @a[nbt={UUID:$(player)},limit=1] at @s run function mcm:lobby/options/ext_wall/apply {action:$(action)}
