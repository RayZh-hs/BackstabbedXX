scoreboard objectives add kb_cd dummy
scoreboard objectives add kb_sec dummy
scoreboard objectives add kb_dec dummy
scoreboard objectives add kb_bar dummy
scoreboard objectives add kb_math dummy
scoreboard objectives add ke_dir dummy
scoreboard objectives add ke_up dummy
scoreboard objectives add ke_down dummy
scoreboard objectives add ke_scan dummy
scoreboard objectives add ke_here dummy
scoreboard objectives add ke_input dummy
scoreboard objectives add ke_move dummy
scoreboard players set $two kb_math 2
scoreboard players set $ten kb_math 10
scoreboard players set $three kb_math 3
scoreboard players set $thirty kb_math 30
kill @e[type=marker,tag=KlutBootsGravity]
execute as @a[tag=Klut27Hook] run function klut27:mobility/remove_hook
execute as @e[type=villager,tag=Klut27Engineer] run function klut27:mobility/merchant
