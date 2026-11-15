$data modify storage mcm:options_wall ui set value {title:"$(title)",value:"$(value)",color:"$(color)",note:"$(note)"}
execute if score $wall_dependency temp matches 1 run data modify storage mcm:options_wall ui merge value {color:"dark_gray",note:"需先开启持枪玩家存废料"}
execute if score $gamestate CmdData matches 1.. run data modify storage mcm:options_wall ui merge value {color:"gray",note:"对局中不可修改"}
execute if data storage mcm:options options{locked:1} run data modify storage mcm:options_wall ui merge value {color:"gray",note:"大厅设置已锁定"}
function mcm:lobby/options/ext_wall/render_inner with storage mcm:options_wall ui
