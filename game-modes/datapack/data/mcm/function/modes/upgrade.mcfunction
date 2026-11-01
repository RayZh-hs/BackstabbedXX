advancement revoke @s only mcm:item_counts/scrap
execute unless score $gamestate CmdData matches 1 run return 0
execute unless entity @s[tag=queued,tag=!spectating,tag=!gunner] run return 0
execute unless score @s bb_team matches 1..2 run return 0
execute store result score $scrap temp run clear @s netherite_scrap 0
execute unless score $scrap temp matches 10.. run return 0
tag @s add gunner
clear @s netherite_scrap 10
function mcm:modes/gunner
