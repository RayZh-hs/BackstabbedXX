#> executed as a MapVote marker at a position for giving score to villager
scoreboard players operation @e[type=interaction,tag=vote_counter,limit=1,sort=nearest] vote_map_id = @s MapValues
#> Don't pick this marker again until next time
tag @s add selected

#-1: Random
# 1: Library
# 2: Floating Islands (airship)
# 3: Vineyard
# 4: Launch Complex (launchpad)
# 5: Color Filth (cyberpunk)
# 6: Murder on the Mississippi (riverboat)
# 7: Industry
# 8: A Tragedy on the Boreal Express (train)
# 9: Snowed Inn (cabin)
# 10: Gumdrop Plains
# 11: Canyon
# 12: Stagnant Sanctuary (sculk)
#> Map art item displays
execute if score @s MapValues matches -1 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/random"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 1 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/library"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 2 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/airship"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 3 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/vineyard"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 4 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/launchpad"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 5 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/cyberpunk"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 6 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/riverboat"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 7 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/industry"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 8 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/train"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 9 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/cabin"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 10 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/gumdrop"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 11 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/canyon"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}
execute if score @s MapValues matches 12 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {item:{id:paper,Count:1b,components:{item_model:"minecraft:posters/sculk"}},item_display:fixed,transformation:[2f,0f,0f,0f, 0f,2f,0f,0f, 0f,0f,2f,0f, 0f,0f,0f,1f],Tags:["vote_display"],Rotation:[90.0f,0.0f],brightness:{block:15,sky:15}}


#> Map art item frames (retired)
#execute if score @s MapValues matches -1 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1135}}}
#execute if score @s MapValues matches -1 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1136}}}
#execute if score @s MapValues matches -1 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1137}}}
#execute if score @s MapValues matches -1 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1138}}}
#execute if score @s MapValues matches -1 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1139}}}
#execute if score @s MapValues matches -1 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1140}}}

#execute if score @s MapValues matches 1 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1111}}}
#execute if score @s MapValues matches 1 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1112}}}
#execute if score @s MapValues matches 1 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1113}}}
#execute if score @s MapValues matches 1 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1114}}}
#execute if score @s MapValues matches 1 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1115}}}
#execute if score @s MapValues matches 1 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1116}}}

#execute if score @s MapValues matches 2 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1117}}}
#execute if score @s MapValues matches 2 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1118}}}
#execute if score @s MapValues matches 2 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1119}}}
#execute if score @s MapValues matches 2 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1120}}}
#execute if score @s MapValues matches 2 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1121}}}
#execute if score @s MapValues matches 2 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1122}}}

#execute if score @s MapValues matches 3 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1123}}}
#execute if score @s MapValues matches 3 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1124}}}
#execute if score @s MapValues matches 3 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1125}}}
#execute if score @s MapValues matches 3 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1126}}}
#execute if score @s MapValues matches 3 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1127}}}
#execute if score @s MapValues matches 3 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1128}}}

#execute if score @s MapValues matches 4 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1129}}}
#execute if score @s MapValues matches 4 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1132}}}
#execute if score @s MapValues matches 4 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1130}}}
#execute if score @s MapValues matches 4 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1133}}}
#execute if score @s MapValues matches 4 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1131}}}
#execute if score @s MapValues matches 4 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1134}}}

#execute if score @s MapValues matches 5 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1147}}}
#execute if score @s MapValues matches 5 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1148}}}
#execute if score @s MapValues matches 5 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1149}}}
#execute if score @s MapValues matches 5 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1150}}}
#execute if score @s MapValues matches 5 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1151}}}
#execute if score @s MapValues matches 5 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1152}}}

#execute if score @s MapValues matches 6 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1153}}}
#execute if score @s MapValues matches 6 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1154}}}
#execute if score @s MapValues matches 6 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1155}}}
#execute if score @s MapValues matches 6 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1156}}}
#execute if score @s MapValues matches 6 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1157}}}
#execute if score @s MapValues matches 6 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1158}}}

#Industry
#execute if score @s MapValues matches 7 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1159}}}
#execute if score @s MapValues matches 7 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1160}}}
#execute if score @s MapValues matches 7 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1161}}}
#execute if score @s MapValues matches 7 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1162}}}
#execute if score @s MapValues matches 7 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1163}}}
#execute if score @s MapValues matches 7 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1164}}}

#Train (Murder on the Boreal Express)
#execute if score @s MapValues matches 8 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1165}}}
#execute if score @s MapValues matches 8 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1166}}}
#execute if score @s MapValues matches 8 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1167}}}
#execute if score @s MapValues matches 8 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1168}}}
#execute if score @s MapValues matches 8 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1169}}}
#execute if score @s MapValues matches 8 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1170}}}

#Winter Cabin (Snowed Inn)
#execute if score @s MapValues matches 9 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1171}}}
#execute if score @s MapValues matches 9 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1172}}}
#execute if score @s MapValues matches 9 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1173}}}
#execute if score @s MapValues matches 9 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1174}}}
#execute if score @s MapValues matches 9 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1175}}}
#execute if score @s MapValues matches 9 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1176}}}

#Gumdrop Plains
#execute if score @s MapValues matches 10 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1141}}}
#execute if score @s MapValues matches 10 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1142}}}
#execute if score @s MapValues matches 10 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1143}}}
#execute if score @s MapValues matches 10 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1144}}}
#execute if score @s MapValues matches 10 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1145}}}
#execute if score @s MapValues matches 10 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:1146}}}

#Canyon
#execute if score @s MapValues matches 11 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:222222231}}}
#execute if score @s MapValues matches 11 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:222222230}}}
#execute if score @s MapValues matches 11 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:222222229}}}
#execute if score @s MapValues matches 11 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:222222228}}}
#execute if score @s MapValues matches 11 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:222222227}}}
#execute if score @s MapValues matches 11 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:222222226}}}

#Stagnant Sanctuary (Sculk)

#execute if score @s MapValues matches 12 positioned ~0.5 ~2.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:86753092}}}
#execute if score @s MapValues matches 12 positioned ~0.5 ~2.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:86753095}}}
#execute if score @s MapValues matches 12 positioned ~0.5 ~1.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:86753093}}}
#execute if score @s MapValues matches 12 positioned ~0.5 ~1.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:86753096}}}
#execute if score @s MapValues matches 12 positioned ~0.5 ~0.5 ~-0.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:86753094}}}
#execute if score @s MapValues matches 12 positioned ~0.5 ~0.5 ~1.5 as @e[type=glow_item_frame,limit=1,sort=nearest] run data merge entity @s {Item:{id:"minecraft:filled_map",Count:1b,tag:{map:86753097}}}

# Panda Village integration
execute if score @s MapValues matches 13 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {Tags:["vote_display","PandaVillagePoster"],Rotation:[90f,0f],brightness:{block:15,sky:15},item_display:"fixed",item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"panda_village:posters/panda_village"}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

# River Bank integration
execute if score @s MapValues matches 14 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {Tags:["vote_display","RiverBankPoster"],Rotation:[90f,0f],brightness:{block:15,sky:15},item_display:"fixed",item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"river_bank:posters/river_bank"}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

# Yacht integration
execute if score @s MapValues matches 15 positioned ~0.99 ~1 ~1 run summon item_display ~ ~ ~ {Tags:["vote_display","YachtPoster"],Rotation:[90f,0f],brightness:{block:15,sky:15},item_display:"fixed",item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"yacht:posters/yacht"}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

# Subway Station integration

# Subway Station integration

# Subway Station integration
execute if score @s MapValues matches 16 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {Tags:["vote_display","SubwayStationPoster"],Rotation:[90f,0f],brightness:{block:15,sky:15},item_display:"fixed",item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"subway_station:posters/subway_station"}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

execute if score @s MapValues matches 17 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {Tags:["vote_display","MeridianBasePoster"],Rotation:[90f,0f],brightness:{block:15,sky:15},item_display:"fixed",item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"meridian_base:posters/meridian_base"}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

execute if score @s MapValues matches 18 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {Tags:["vote_display","Bagger288Poster"],Rotation:[90f,0f],brightness:{block:15,sky:15},item_display:"fixed",item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"bagger_288:posters/bagger_288"}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

execute if score @s MapValues matches 19 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {Tags:["vote_display","UnderwaterBasePoster"],Rotation:[90f,0f],brightness:{block:15,sky:15},item_display:"fixed",item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"underwater_base:posters/underwater_base"}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

execute if score @s MapValues matches 20 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {Tags:["vote_display","Klut27Poster"],Rotation:[90f,0f],brightness:{block:15,sky:15},item_display:"fixed",item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"klut27:posters/klut27"}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

execute if score @s MapValues matches 21 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {"Tags":["vote_display","SworldIslandPoster"],"Rotation":[90f,0f],"brightness":{"block":15,"sky":15},"item_display":"fixed","item":{"id":"minecraft:paper","count":1,"components":{"minecraft:item_model":"sworld_island:posters/sworld_island"}},"transformation":[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

execute if score @s MapValues matches 22 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {"Tags":["vote_display","MiddleAgesPoster"],"Rotation":[90f,0f],"brightness":{"block":15,"sky":15},"item_display":"fixed","item":{"id":"minecraft:paper","count":1,"components":{"minecraft:item_model":"middle_ages:posters/middle_ages"}},"transformation":[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

execute if score @s MapValues matches 23 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {"Tags":["vote_display","CubeBlockPoster"],"Rotation":[90f,0f],"brightness":{"block":15,"sky":15},"item_display":"fixed","item":{"id":"minecraft:paper","count":1,"components":{"minecraft:item_model":"cube_block:posters/cube_block"}},"transformation":[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

execute if score @s MapValues matches 24 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {"Tags":["vote_display","MonolithPoster"],"Rotation":[90f,0f],"brightness":{"block":15,"sky":15},"item_display":"fixed","item":{"id":"minecraft:paper","count":1,"components":{"minecraft:item_model":"monolith:posters/monolith"}},"transformation":[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}

execute if score @s MapValues matches 25 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {"Tags":["vote_display","AxolotlTreehousePoster"],"Rotation":[90f,0f],"brightness":{"block":15,"sky":15},"item_display":"fixed","item":{"id":"minecraft:paper","count":1,"components":{"minecraft:item_model":"axolotl_treehouse:posters/axolotl_treehouse"}},"transformation":[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}
