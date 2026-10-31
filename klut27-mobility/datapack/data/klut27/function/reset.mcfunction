execute as @a[tag=KlutMobility] run function klut27:cleanup_player
execute as @a[tag=Klut27Hook] run function klut27:mobility/remove_hook
schedule clear klut27:activate
kill @e[tag=Klut27Runtime]
kill @e[tag=klut.e.search]
tag @a remove Klut27Participant
function klut27:fire/reset
function klut27:restore_blocks
function klut27:npc_reset
function klut27:residents/reset
