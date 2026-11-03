#> Yacht-style boundary timing: preparation rescues, the active round eliminates.
#> Bounds, probes, coordinates and the dispenser pads are unchanged.
execute unless score $gamestate CmdData matches 1 run return 0

#> Exterior ocean contact: rescue during preparation, eliminate in the active round.
execute if predicate meridian_base:ocean_height run function meridian_base:check_ocean
execute if score @s dead matches 1.. run return 0

#> Out of scene: rescue during preparation, eliminate in the active round.
execute if score $graceperiod CmdData matches 1.. unless predicate meridian_base:scene run return run function meridian_base:return_player
execute if score $graceperiod CmdData matches ..0 unless predicate meridian_base:scene run return run function mcm:game/playerdeath

scoreboard players set @s MeridianPad 0
execute if predicate meridian_base:pad_1 run scoreboard players set @s MeridianPad 1
execute if predicate meridian_base:pad_2 run scoreboard players set @s MeridianPad 2
execute if predicate meridian_base:pad_3 run scoreboard players set @s MeridianPad 3
execute if predicate meridian_base:pad_4 run scoreboard players set @s MeridianPad 4
execute if predicate meridian_base:pad_5 run scoreboard players set @s MeridianPad 5
execute if predicate meridian_base:pad_6 run scoreboard players set @s MeridianPad 6
execute if predicate meridian_base:pad_7 run scoreboard players set @s MeridianPad 7
execute if score @s MeridianPad matches 1.. unless score @s MeridianPad = @s MeridianLastPad run function meridian_base:dispenser/step
scoreboard players operation @s MeridianLastPad = @s MeridianPad
