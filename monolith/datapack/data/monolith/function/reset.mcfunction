monolith cleanup
kill @e[tag=MonolithRuntime]
schedule clear monolith:activate
forceload remove 53200 53200 53407 53455
tag @a remove MonolithParticipant
kill @e[type=item,nbt={Item:{components:{"minecraft:custom_data":{monolith_float:1b}}}}]
