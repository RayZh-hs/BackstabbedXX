# Keep merchants fixed in their shops when players collide with them.
team add ArenaMerchants
team modify ArenaMerchants collisionRule never
# Idempotent and included in normal map cleanup.
kill @e[tag=PandaToyShop]
summon panda 8370.5 106 8373.5 {Tags:["MapEntity","PandaVillageRuntime","PandaToyShop"],CustomName:'{"text":"玩具商"}',CustomNameVisible:1b,NoAI:1b,NoGravity:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:1b,Rotation:[90f,0f],MainGene:"normal",HiddenGene:"normal"}
summon minecraft:marker 8370.5 106 8373.5 {"Tags":["MapEntity","PandaVillageRuntime","PandaToyShop","PandaToyOffers"],"data":{"offers":{"Recipes":[{"uses":0,"maxUses":2147483647,"rewardExp":0b,"xp":0,"demand":0,"specialPrice":0,"priceMultiplier":0.0,"buy":{"id":"minecraft:netherite_scrap","count":4},"sell":{"id":"minecraft:stick","count":1,"components":{"minecraft:item_model":"minecraft:role_items/gun","minecraft:max_stack_size":1,"minecraft:custom_data":{"panda_toy_gun":1b},"minecraft:custom_name":"{\"text\":\"玩具枪\",\"italic\":false}","minecraft:lore":["{\"text\":\"与真枪外观相同，但无法发射。\",\"color\":\"gray\",\"italic\":false}"]}}}]}}}
team join ArenaMerchants @e[type=minecraft:panda,tag=PandaToyShop]
