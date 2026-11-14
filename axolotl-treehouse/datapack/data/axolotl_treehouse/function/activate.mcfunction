execute unless score $selectedMap CmdData matches 25 run return 0
execute unless score $gamestate CmdData matches 0..1 run return 0
forceload add 57536 57536 57663 57663
kill @e[tag=MapEntity]
tag @a remove AxolotlTreehouseParticipant
summon marker 57578.5 74 57599.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57639.5 74 57608.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57615.5 74 57563.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57607.5 74 57636.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57572.5 74 57628.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57588.5 74 57572.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57622.5 74 57595.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57592.5 74 57623.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57561.5 74 57607.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57622.5 74 57614.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57623.5 74 57632.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57607.5 74 57577.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57578.5 74 57614.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57561.5 74 57592.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57636.5 74 57594.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57611.5 74 57623.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57600.5 88 57600.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57583.5 76 57618.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57616.5 76 57618.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57616.5 76 57582.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57584.5 76 57582.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57600.5 75 57607.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57616.5 76 57600.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57596.5 83 57586.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57593.5 86 57612.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57599.5 75 57593.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57604.5 76 57582.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57604.5 76 57618.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57611.5 76 57609.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57583.5 76 57592.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57593.5 76 57618.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57612.5 76 57591.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 57600.5 115 57600.5 {Tags:["MapEntity","AxolotlTreehouseRuntime","SpectatorSpawn"]}
tellraw @a {"translate":"axolotl_treehouse.ready","color":"aqua"}
