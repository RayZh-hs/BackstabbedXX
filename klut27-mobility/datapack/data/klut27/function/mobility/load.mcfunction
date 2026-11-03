scoreboard objectives add kc_cd dummy
scoreboard objectives add kc_sec dummy
scoreboard objectives add kc_dec dummy
scoreboard objectives add kc_math dummy
scoreboard objectives add ke_dir dummy
scoreboard objectives add ke_up dummy
scoreboard objectives add ke_down dummy
scoreboard objectives add ke_scan dummy
scoreboard objectives add ke_here dummy
scoreboard objectives add ke_input dummy
scoreboard objectives add ke_move dummy
scoreboard objectives add kc_use minecraft.used:minecraft.carrot_on_a_stick
scoreboard players set $two kc_math 2
scoreboard players set $ten kc_math 10
scoreboard players set $three kc_math 3
scoreboard players set $thirty kc_math 30
kill @e[type=marker,tag=KlutBootsGravity]
execute as @a[tag=Klut27Hook] run function klut27:mobility/remove_hook
execute as @e[type=villager,tag=Klut27Engineer] run function klut27:mobility/merchant
