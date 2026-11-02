# Stamp thrown or manually dropped items, then remove stale generations after chunk reload.
execute as @e[type=item] if items entity @s contents snowball[custom_data~{knife:1b}] run function mcm:extensions/knife/track_entity
execute as @e[type=arrow,tag=knife] run function mcm:extensions/knife/track_entity
execute as @e[type=arrow,tag=knife,tag=mcm_knife_tracked] run function mcm:extensions/knife/check_entity
execute as @e[type=item,tag=mcm_knife_tracked] if items entity @s contents snowball[custom_data~{knife:1b}] run function mcm:extensions/knife/check_entity
execute unless score $knife_timeout GameRules matches 1 run return run scoreboard players set @a mcm_missing 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator,predicate=mcm:game/not_eliminated,tag=murderer] if items entity @s container.* snowball[custom_data~{knife:1b}] run scoreboard players set @s mcm_missing 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator,predicate=mcm:game/not_eliminated,tag=murderer] if items entity @s weapon.* snowball[custom_data~{knife:1b}] run scoreboard players set @s mcm_missing 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator,predicate=mcm:game/not_eliminated,tag=murderer] unless items entity @s container.* snowball[custom_data~{knife:1b}] unless items entity @s weapon.* snowball[custom_data~{knife:1b}] run scoreboard players add @s mcm_missing 1
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator,predicate=mcm:game/not_eliminated,tag=murderer] if score @s mcm_missing >= $knife_ticks GameRules at @s run function mcm:extensions/knife/recover
