spectate
clear @s
effect clear @s
tag @s remove spectating
tag @s remove lostGun
tag @s remove shotGun
scoreboard players set @s dead 0
scoreboard players set @s bb_respawn 0
scoreboard players set @s bb_safe 40
gamemode adventure @s
function mcm:maps/tptospawn
item replace entity @s hotbar.7 with spyglass[custom_data={NoDrop:1b,no_drop_on_death:1b}]
execute if score $darkness GameRules matches 1 run effect give @s minecraft:darkness 600 0 true
execute if score $selectedMap CmdData matches 20 run function klut27:give_hook
