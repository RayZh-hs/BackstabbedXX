tag @s add disabled
data merge entity @s {response:0b}
tag @e[type=text_display,tag=VoteDisplay,sort=nearest,limit=1] add disabled
data merge entity @e[type=text_display,tag=VoteDisplay,sort=nearest,limit=1] {text:'{"text":"未启用地图","color":"gray"}'}
