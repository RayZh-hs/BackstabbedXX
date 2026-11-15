schedule clear axolotl_treehouse:activate
schedule clear bagger_288:activate
schedule clear cube_block:activate
schedule clear klut27:activate
schedule clear mcm:maps/airship/activate
schedule clear mcm:maps/cabin/activate
schedule clear mcm:maps/canyon/activate
schedule clear mcm:maps/cyberpunk/activate
schedule clear mcm:maps/gumdrop/activate
schedule clear mcm:maps/industry/activate
schedule clear mcm:maps/launchpad/activate
schedule clear mcm:maps/library/activate
schedule clear mcm:maps/library2/activate
schedule clear mcm:maps/riverboat/activate
schedule clear mcm:maps/sculk/activate
schedule clear mcm:maps/train/activate
schedule clear mcm:maps/vineyard/activate
schedule clear mcm:maps/vineyard2/activate
schedule clear meridian_base:activate
schedule clear middle_ages:activate
schedule clear monolith:activate
schedule clear panda_village:activate
schedule clear river_bank:activate
schedule clear subway_station:activate
schedule clear sworld_island:activate
schedule clear underwater_base:activate
schedule clear yacht:activate
function mcm:maps/reset
scoreboard players set $start CmdData 0
scoreboard players set $startcountdown CmdData 200
stopsound @a record minecraft:movie_start
