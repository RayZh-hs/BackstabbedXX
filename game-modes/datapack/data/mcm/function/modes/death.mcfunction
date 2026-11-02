scoreboard players set @s bb_respawn 0
execute unless score $mode CmdData matches 1 run return 0
# playerdeath already marked this player as spectating; only living teammates count.
scoreboard players operation $dead_team temp = @s bb_team
scoreboard players set $other_gunners temp 0
execute as @a[tag=queued,tag=!spectating,tag=gunner] if score @s bb_team = $dead_team temp run scoreboard players add $other_gunners temp 1
execute unless score $other_gunners temp matches 1.. run return 0
# Clear the old gun now so the main game loop cannot restore the gunner tag.
clear @s warped_fungus_on_a_stick
tag @s remove gunner
scoreboard players operation @s bb_respawn = $gunner_respawn_ticks GameRules
