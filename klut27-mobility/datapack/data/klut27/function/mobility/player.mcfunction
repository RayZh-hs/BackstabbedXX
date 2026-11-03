execute unless dimension minecraft:overworld run return 0
function klut27:mobility/remove_hook
scoreboard players add @s kc_cd 0
execute if score @s kc_cd matches 1.. run scoreboard players remove @s kc_cd 1
tag @s add KlutMobility
execute if score @s kc_use matches 1.. if score @s kc_cd matches 0 if items entity @s weapon.* carrot_on_a_stick[custom_data~{klut27_gravity_controller:1b}] run function klut27:mobility/controller
scoreboard players set @s kc_use 0
