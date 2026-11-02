function mcm:extensions/round_start
tag @a[tag=queued] remove murderer
tag @a[tag=queued] remove innocent
tag @a[tag=queued] remove gunner
scoreboard players set @a[tag=queued] bb_team 0
scoreboard players set $next_team CmdData 1
execute if score $mode CmdData matches 1 as @a[tag=queued,sort=random] run function mcm:modes/assign
execute if score $mode CmdData matches 2 run team join ingame_players @a[tag=queued]
execute if score $mode CmdData matches 1 run tag @a[tag=queued] add innocent
execute if score $mode CmdData matches 1 as @a[tag=queued,scores={bb_team=1},sort=random,limit=1] run function mcm:modes/gunner
execute if score $mode CmdData matches 1 as @a[tag=queued,scores={bb_team=2},sort=random,limit=1] run function mcm:modes/gunner
execute if score $mode CmdData matches 2 run tag @a[tag=queued] add murderer
execute if score $mode CmdData matches 2 as @a[tag=queued] run function mcm:items/loadouts/murderer
execute if score $mode CmdData matches 2 run tag @a[tag=queued] add free_knife
item replace entity @a[tag=queued] hotbar.7 with spyglass[custom_data={NoDrop:1b,no_drop_on_death:1b}]
scoreboard players set $pickedroles CmdData 1
execute if score $mode CmdData matches 1 run tellraw @a {"text":"Gunner Mode","color":"aqua"}
execute if score $mode CmdData matches 2 run tellraw @a {"text":"Killer Mode: Free for all. Be the last player standing! Each kill drops an extra adrenaline bottle.","color":"red"}
execute if score $mode CmdData matches 1 run tellraw @a [{"text":"Red: ","color":"red"},{"selector":"@a[tag=queued,scores={bb_team=1}]"},{"text":" | Blue: ","color":"aqua"},{"selector":"@a[tag=queued,scores={bb_team=2}]"}]
execute if score $selectedMap CmdData matches 20 run function klut27:hook_roles
