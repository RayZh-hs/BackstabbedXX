tellraw @s [{"text":"Game Mode: ","color":"gold"},{"text":"[Classic] ","color":"green","clickEvent":{"action":"run_command","value":"/trigger mcm_options set 15"}},{"text":"[Gunner] ","color":"aqua","clickEvent":{"action":"run_command","value":"/trigger mcm_options set 16"}},{"text":"[Killer]","color":"red","clickEvent":{"action":"run_command","value":"/trigger mcm_options set 17"}}]
execute if score $mode GameRules matches 0 run tellraw @s {"text":"Selected: Classic Mode","color":"green"}
execute if score $mode GameRules matches 1 run tellraw @s {"text":"Selected: Gunner Mode","color":"aqua"}
execute if score $mode GameRules matches 2 run tellraw @s {"text":"Selected: Killer Mode","color":"red"}
