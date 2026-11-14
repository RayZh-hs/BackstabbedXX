tag @s add AxolotlTreehouseParticipant
# Falling to lake level outside the island is lethal from round start, including grace.
# There is deliberately no water/fluid contact check. Island ponds and waterfalls are safe.
execute if predicate axolotl_treehouse:lake_fall run return run function mcm:game/playerdeath
execute unless predicate axolotl_treehouse:arena run return run function axolotl_treehouse:escape
