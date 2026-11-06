execute unless score $selectedMap CmdData matches 24 run return 0
execute unless score $gamestate CmdData matches 0..1 run return 0
forceload add 53200 53200 53407 53455
monolith cleanup
kill @e[tag=MapEntity]
tag @a remove MonolithParticipant
summon marker 53205.5 135 53238.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53257.5 129 53244.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53207.5 134 53280.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53238.5 141 53269.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53231.5 118 53234.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53215.5 154 53260.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53231.5 141 53250.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53219.5 123 53247.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53221.5 142 53273.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53241.5 153 53257.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53248.5 135 53255.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53203.5 132 53266.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53369.5 130 53347.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53333.5 148 53322.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53378.5 118 53305.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53359.5 137 53323.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53351.5 151 53343.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53381.5 123 53329.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53361.5 123 53308.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53336.5 151 53338.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53373.5 131 53317.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53349.5 143 53313.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53347.5 145 53328.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53360.5 140 53337.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53213.5 132 53373.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53245.5 150 53396.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53251.5 119 53365.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53235.5 136 53378.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53229.5 120 53361.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53225.5 148 53401.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53218.5 151 53381.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53233.5 132 53404.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53247.5 138 53385.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53232.5 149 53389.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53211.5 121 53363.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53246.5 124 53376.5 {Tags:["MapEntity","MonolithRuntime","PlayerSpawn","ScrapSpawn"]}
summon marker 53230.5 148 53265.5 {Tags:["MapEntity","MonolithRuntime","MonolithAltar","MonolithAltar0"],data:{altar_id:0,target_x:53228.5d,target_y:161d,target_z:53265.5d,rune_right_x:1d,rune_right_z:0d,rune_x:53228.5d,rune_y:158d,rune_z:53265.5d}}
summon marker 53342.5 154 53330.5 {Tags:["MapEntity","MonolithRuntime","MonolithAltar","MonolithAltar1"],data:{altar_id:1,target_x:53342.5d,target_y:166d,target_z:53329.5d,rune_right_x:0d,rune_right_z:1d,rune_x:53342.5d,rune_y:163d,rune_z:53329.5d}}
summon marker 53229.5 149 53394.5 {Tags:["MapEntity","MonolithRuntime","MonolithAltar","MonolithAltar2"],data:{altar_id:2,target_x:53230.5d,target_y:159d,target_z:53395.5d,rune_right_x:1d,rune_right_z:0d,rune_x:53230.5d,rune_y:159d,rune_z:53395.5d}}
summon marker 53275 185 53330 {Tags:["MapEntity","MonolithRuntime","SpectatorSpawn"]}
tellraw @a {"translate":"monolith.ready","fallback":"Monolith ready","color":"aqua"}
