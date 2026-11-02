tag @s add bb_tracking
execute positioned as @a[tag=queued,tag=!spectating,tag=!bb_tracking,sort=nearest,limit=1] run function mcm:game/items/player_tracker/find_player
tag @s remove bb_tracking
