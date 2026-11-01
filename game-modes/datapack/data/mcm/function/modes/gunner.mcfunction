tag @s add gunner
function mcm:extensions/gun/give
title @s subtitle {"text":"Gunner","color":"gold"}
tellraw @a [{"selector":"@s"},{"text":" is now a gunner!","color":"gold"}]
