tag @s add bb_teleport_user
tag @e[type=marker,tag=PlayerSpawn] remove Occupied
execute as @a[tag=queued,tag=!spectating,tag=!bb_teleport_user] at @s run function mcm:game/items/murderer/teleport_players
tag @s remove bb_teleport_user
execute as @a[tag=queued] at @s run playsound minecraft:entity.enderman.teleport ambient @s ~ ~ ~ 1 1 1
tag @s add usedTeleport
execute if items entity @s weapon.mainhand carrot_on_a_stick[custom_data~{teleporter:1b}] run function mcm:items/retrieve/mainhand
execute if items entity @s weapon.offhand carrot_on_a_stick[custom_data~{teleporter:1b}] run function mcm:items/retrieve/offhand
function mcm:util/reset_carrot_on_stick
