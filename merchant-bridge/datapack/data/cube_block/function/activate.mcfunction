execute unless score $selectedMap CmdData matches 23 run return 0
execute unless score $gamestate CmdData matches 0..1 run return 0
execute as @a[tag=CubeBlockHook] run function cube_block:cleanup_player
kill @e[tag=MapEntity]
gamerule doFireTick false
summon marker 49196.500 88.000 49202.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"down",gravity_strength:1.0d}}
summon marker 49216.500 87.000 49231.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"down",gravity_strength:1.0d}}
summon marker 49192.500 87.000 49226.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"down",gravity_strength:1.0d}}
summon marker 49217.500 92.000 49209.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"down",gravity_strength:1.0d}}
summon marker 49184.500 87.000 49212.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"down",gravity_strength:1.0d}}
summon marker 49205.500 88.000 49218.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"down",gravity_strength:1.0d}}
summon marker 49203.500 45.999 49213.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"up",gravity_strength:1.0d}}
summon marker 49187.500 45.999 49200.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"up",gravity_strength:1.0d}}
summon marker 49184.500 46.999 49220.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"up",gravity_strength:1.0d}}
summon marker 49201.500 46.999 49199.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"up",gravity_strength:1.0d}}
summon marker 49191.500 46.999 49211.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"up",gravity_strength:1.0d}}
summon marker 49196.500 46.999 49205.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"up",gravity_strength:1.0d}}
summon marker 49180.999 66.500 49215.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"east",gravity_strength:1.0d}}
summon marker 49179.999 83.500 49200.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"east",gravity_strength:1.0d}}
summon marker 49180.999 51.500 49231.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"east",gravity_strength:1.0d}}
summon marker 49178.999 51.500 49199.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"east",gravity_strength:1.0d}}
summon marker 49180.999 83.500 49222.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"east",gravity_strength:1.0d}}
summon marker 49223.001 66.500 49215.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"west",gravity_strength:1.0d}}
summon marker 49221.001 82.500 49232.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"west",gravity_strength:1.0d}}
summon marker 49223.001 83.500 49200.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"west",gravity_strength:1.0d}}
summon marker 49221.001 51.500 49232.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"west",gravity_strength:1.0d}}
summon marker 49221.001 53.500 49199.500 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"west",gravity_strength:1.0d}}
summon marker 49200.500 66.500 49195.999 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"south",gravity_strength:1.0d}}
summon marker 49185.500 83.500 49193.999 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"south",gravity_strength:1.0d}}
summon marker 49217.500 53.500 49193.999 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"south",gravity_strength:1.0d}}
summon marker 49185.500 51.500 49191.999 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"south",gravity_strength:1.0d}}
summon marker 49206.500 83.500 49192.999 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"south",gravity_strength:1.0d}}
summon marker 49200.500 64.500 49237.001 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"north",gravity_strength:1.0d}}
summon marker 49216.500 80.500 49236.001 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"north",gravity_strength:1.0d}}
summon marker 49215.500 50.500 49236.001 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"north",gravity_strength:1.0d}}
summon marker 49197.500 83.500 49236.001 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"north",gravity_strength:1.0d}}
summon marker 49184.500 71.500 49236.001 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity","CubeBlockRuntime"],Rotation:[0.0f,0.0f],data:{gravity_direction:"north",gravity_strength:1.0d}}
summon marker 49200.5 119 49204.5 {Tags:["SpectatorSpawn","MapEntity","CubeBlockRuntime"]}
tellraw @a {"translate":"cube_block.ready","fallback":"Cube Block ready","color":"aqua"}
