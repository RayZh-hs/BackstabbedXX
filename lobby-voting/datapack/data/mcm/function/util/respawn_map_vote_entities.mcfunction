kill @e[tag=MapVoteEntity]
summon interaction 27.8125 2 84.0 {width:2f,height:3f,Tags:["MapVoteEntity","vote_counter","map_random"],response:1b}
scoreboard players set @e[type=interaction,tag=vote_counter,tag=map_random] vote_position -1
summon interaction 28.8125 2 90.0 {width:2f,height:3f,Tags:["MapVoteEntity","vote_counter","map1"],response:1b}
scoreboard players set @e[type=interaction,tag=vote_counter,tag=map1] vote_position 1
summon interaction 28.8125 2 95.0 {width:2f,height:3f,Tags:["MapVoteEntity","vote_counter","map2"],response:1b}
scoreboard players set @e[type=interaction,tag=vote_counter,tag=map2] vote_position 2
summon interaction 28.8125 2 100.0 {width:2f,height:3f,Tags:["MapVoteEntity","vote_counter","map3"],response:1b}
scoreboard players set @e[type=interaction,tag=vote_counter,tag=map3] vote_position 3
summon interaction 28.8125 2 106.0 {width:2f,height:3f,Tags:["MapVoteEntity","vote_counter","map4"],response:1b}
scoreboard players set @e[type=interaction,tag=vote_counter,tag=map4] vote_position 4
summon interaction 28.8125 2 111.0 {width:2f,height:3f,Tags:["MapVoteEntity","vote_counter","map5"],response:1b}
scoreboard players set @e[type=interaction,tag=vote_counter,tag=map5] vote_position 5
summon interaction 28.8125 2 116.0 {width:2f,height:3f,Tags:["MapVoteEntity","vote_counter","map6"],response:1b}
scoreboard players set @e[type=interaction,tag=vote_counter,tag=map6] vote_position 6
summon interaction 28.8125 2 121.0 {width:2f,height:3f,Tags:["MapVoteEntity","vote_counter","map7"],response:1b}
scoreboard players set @e[type=interaction,tag=vote_counter,tag=map7] vote_position 7
summon interaction 28.8125 2 126.0 {width:2f,height:3f,Tags:["MapVoteEntity","vote_counter","map8"],response:1b}
scoreboard players set @e[type=interaction,tag=vote_counter,tag=map8] vote_position 8
function mcm:lobby/voting/vote_displays
function mcm:lobby/voting/ensure_reroll
team join posters @e[tag=MapVoteEntity]
