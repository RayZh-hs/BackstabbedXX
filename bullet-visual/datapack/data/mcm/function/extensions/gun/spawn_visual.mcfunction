# Spawn at the authoritative muzzle, with final orientation already in the spawn packet.
# Never mount this visible entity: vanilla can omit same-tick dismount packets.
$execute at @e[type=arrow,tag=GunShot,nbt={UUID:$(arrow_uuid)},limit=1] run summon item_display ~ ~ ~ {Tags:["BulletDeco"],Rotation:$(rotation),transformation:$(transformation),interpolation_duration:0,teleport_duration:1,item:{id:"minecraft:diamond_hoe",count:1,components:{"minecraft:item_model":"minecraft:misc/bullet","minecraft:custom_data":{arrow_uuid:$(arrow_uuid)}}}}
