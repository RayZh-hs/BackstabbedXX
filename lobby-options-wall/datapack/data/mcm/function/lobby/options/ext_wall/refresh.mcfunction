execute in minecraft:overworld as @e[type=text_display,tag=McmOptionsWall,tag=updatable] run function mcm:lobby/options/backend/call with entity @s Passengers[0].data
execute in minecraft:overworld as @e[type=interaction,tag=McmOptionsWall] run function mcm:lobby/options/backend/update_interactions with entity @s Passengers[0].data
scoreboard players operation $wall_state temp = $gamestate CmdData
