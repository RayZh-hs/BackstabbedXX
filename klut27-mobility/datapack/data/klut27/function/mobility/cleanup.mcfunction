function klut27:mobility/release
scoreboard players set @s kb_cd 0
scoreboard players set @s e.cooldown 0
scoreboard players set @s ke_scan 0
scoreboard players set @s ke_here 0
execute if entity @s[tag=KlutMobilityHud] run title @s actionbar ""
tag @s remove KlutMobilityHud
tag @s remove KlutMobility
