advancement revoke @s only mcm:hit_detection/gun_hit
advancement revoke @s only mcm:hit_detection/knife_hit
advancement revoke @s only mcm:hit_detection/knife_melee_hit
execute unless score $gamestate CmdData matches 1 run return 0
execute unless score $pickedroles CmdData matches 1 run return 0
execute if score @s bb_safe matches 1.. run return 0
scoreboard players operation $victim_team temp = @s bb_team
scoreboard players set $enemy_hit temp 0
execute on attacker if entity @s[type=player,tag=queued,tag=!spectating] if score @s bb_team matches 1..2 unless score @s bb_team = $victim_team temp run scoreboard players set $enemy_hit temp 1
execute if score $enemy_hit temp matches 1 run function mcm:extensions/reward/lethal_hit
