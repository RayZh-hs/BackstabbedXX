execute unless entity @s[tag=queued,tag=!spectating,gamemode=!spectator,predicate=mcm:game/not_eliminated,tag=murderer] run return 0
execute unless entity @a[tag=queued,tag=!spectating,gamemode=!spectator,predicate=mcm:game/not_eliminated,tag=innocent,sort=nearest,limit=1] run return run title @s actionbar {"text":"没有可追踪的存活玩家","color":"gray"}
execute positioned as @a[tag=queued,tag=!spectating,gamemode=!spectator,predicate=mcm:game/not_eliminated,tag=innocent,sort=nearest,limit=1] run function mcm:game/items/player_tracker/find_player
