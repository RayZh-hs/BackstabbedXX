execute if entity @e[type=interaction,tag=VoteReroll,tag=VoteRerollLeft,nbt={Pos:[26.87d,2.85d,80.5d]}] run return 1
# Migrate the previous right-hand control and remove its callback passengers.
execute as @e[tag=VoteReroll] on passengers run kill @s
kill @e[tag=VoteReroll]
execute positioned 25.86 3.0 80.5 run function mcm:lobby/options/summon_updatable_text {data:{Tags:["VoteReroll","VoteRerollLeft"],Rotation:[90f,0f],line_width:112},extra:{},callback:"mcm:lobby/voting/reroll_text"}
execute positioned 26.87 2.85 80.5 run function mcm:lobby/options/summon_interaction {data:{Tags:["VoteReroll","VoteRerollLeft"],width:2f,height:0.9f,response:1b},extra:{enable_callback:"mcm:lobby/voting/reroll_enabled"},callback:"mcm:lobby/voting/reroll"}
