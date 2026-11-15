# Refresh only in the overworld lobby; short duration expires after leaving.
# Vanilla effect priority preserves stronger speed effects, e.g. test-range adrenaline.
execute as @a at @s if dimension minecraft:overworld if predicate mcm:bounding_boxes/lobby run effect give @s minecraft:speed 1 1 true
