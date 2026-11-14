execute unless entity @e[type=marker,tag=MapVote,tag=AxolotlTreehouse] run summon marker 0 -50 70 {Tags:["MapVote","AxolotlTreehouse"]}
scoreboard players set @e[type=marker,tag=MapVote,tag=AxolotlTreehouse] MapValues 25
function mcm:lobby/options/map_toggle/init
