execute unless entity @e[type=marker,tag=MapVote,tag=Monolith] run summon marker 0 -50 70 {Tags:["MapVote","Monolith"]}
scoreboard players set @e[type=marker,tag=MapVote,tag=Monolith] MapValues 24
function mcm:lobby/options/map_toggle/init
