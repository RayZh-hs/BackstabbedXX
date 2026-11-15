function mcm:lobby/voting/clear_ballots
scoreboard players set $gamestate CmdData -1
tellraw @a {"text":"没有可选地图，请先启用至少一张地图。","color":"yellow"}
