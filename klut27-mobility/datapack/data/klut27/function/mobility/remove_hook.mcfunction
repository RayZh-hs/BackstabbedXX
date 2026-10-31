execute if entity @s[tag=Klut27Hook] run function klut27:hook_cancel
clear @s gravity_changer:grappling_hook[custom_data~{klut27_hook:1b}]
clear @s minecraft:stick[custom_data~{klut27_hook:1b}]
tag @s remove gravity_hook_no_cooldown
tag @s remove Klut27Hook
