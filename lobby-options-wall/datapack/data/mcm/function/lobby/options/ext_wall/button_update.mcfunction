$data modify storage mcm:options_wall button set value {label:"$(label)",color:"aqua"}
execute store success score $wall_enabled temp run function mcm:lobby/options/ext_wall/enabled with entity @s Passengers[0].data
execute if score $wall_enabled temp matches 0 run data modify storage mcm:options_wall button.color set value "dark_gray"
$execute if score $wall_enabled temp matches 1 if score $$(option) GameRules matches $(selected) run data modify storage mcm:options_wall button.color set value "green"
function mcm:lobby/options/ext_wall/button_render with storage mcm:options_wall button
