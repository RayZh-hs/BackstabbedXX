# Called as the interaction, before the legacy backend clears its click record.
data modify storage mcm:options_wall click.player set from entity @s interaction.player
data modify storage mcm:options_wall click.action set from entity @s Passengers[0].data.action
data remove entity @s interaction
function mcm:lobby/options/ext_wall/click_player with storage mcm:options_wall click
data remove storage mcm:options_wall click
