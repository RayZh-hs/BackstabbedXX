execute if score @s bb_team matches 1 positioned as @a[tag=queued,tag=!spectating,scores={bb_team=2},sort=nearest,limit=1] run function mcm:game/items/player_tracker/find_player
execute if score @s bb_team matches 2 positioned as @a[tag=queued,tag=!spectating,scores={bb_team=1},sort=nearest,limit=1] run function mcm:game/items/player_tracker/find_player
