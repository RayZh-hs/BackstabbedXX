execute as @e[type=villager,tag=Klut27Engineer,tag=!Klut27Blasted] run data merge entity @s {Health:1000.0f,Gossips:[]}
execute as @e[type=iron_golem,tag=Klut27Golem] run data merge entity @s {Health:1000.0f}
execute as @e[type=villager,tag=Klut27Engineer,tag=!Klut27BootsVendor,tag=!Klut27Blasted] run function klut27:mobility/merchant
