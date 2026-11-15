# Remove the old physical reset control, including its callback passenger.
tag @e[type=interaction,tag=option,nbt={Passengers:[{data:{callback:"mcm:lobby/options/reset_to_defaults"}}]}] add McmOldReset
execute as @e[tag=McmOldReset] on passengers run kill @s
kill @e[tag=McmOldReset]
# The legacy text has only the generic option tag; identify its exact original location.
execute positioned 26.9 9.75 84.5 run kill @e[type=text_display,tag=option,tag=!McmOptionsWall,distance=..0.1]
