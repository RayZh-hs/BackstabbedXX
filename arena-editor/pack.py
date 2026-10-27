"""Generate the vanilla 1.21.4 datapack, including its book and chat interface.

All durable editor data lives in `bbe:session state`, independent of loaded
chunks. Display/interaction entities are disposable views of that storage.
"""

import json
from pathlib import Path

import nbtlib as nbt


def component(label, action, color="aqua", objective="bbe.ui"):
    return {"text": label, "color": color, "clickEvent": {
        "action": "run_command", "value": f"/trigger {objective} set {action}"}}


def build(target, state):
    files = {}

    def put(name, text):
        files[f"data/bbe/function/{name}.mcfunction"] = text.strip() + "\n"

    def tell(parts):
        return "tellraw @s " + json.dumps(parts, separators=(",", ":"))

    menu = [
        [component("[Add player] ", 10), component("[Ammo] ", 11, "gold"), component("[Both] ", 12, "green"), component("[Spectator] ", 13, "light_purple"), component("[Return]", 14)],
        [component("[Select nearest] ", 4), component("[List IDs] ", 3), component("[Go to selected] ", 5), component("[Move here] ", 6), component("[Face my way]", 16)],
        [component("[Cycle spawn type] ", 15), component("[Delete] ", 7, "red"), component("[Undo] ", 8), component("[Redo] ", 9), component("[Overlays on/off]", 17)],
        [component("[Corner A here] ", 21), component("[Corner B here] ", 22), component("[New box] ", 23), component("[Resize selected box]", 24)],
        [component("[Select containing box] ", 30), component("[Keep in / keep out] ", 25), component("[Box kill / TP] ", 26), component("[Box enabled]", 27)],
        [component("[Boundaries on/off] ", 19), component("[Outside kill / TP] ", 20), component("[Test on/off]", 18, "yellow")],
        [component("[X+] ", 31), component("[X−] ", 32), component("[Y+] ", 33), component("[Y−] ", 34), component("[Z+] ", 35), component("[Z−]", 36), {"text": "  (0.5 blocks)", "color": "gray"}],
    ]
    put("menu", "\n".join([
        tell({"text": "Backstabbed++ Arena Editor — click an action", "color": "yellow"}),
        *[tell(row) for row in menu],
        tell([component("[Editor book] ", 2), {"text": "Right-click a spawn label to select it. /trigger bbe.pick set <ID>", "color": "gray"}]),
        'tellraw @s [{"text":"Boundaries: "},{"nbt":"state.boundary_enabled","storage":"bbe:session"},{"text":"; outside action: "},{"nbt":"state.outside_action","storage":"bbe:session"},{"text":"; test: "},{"score":{"name":"@s","objective":"bbe.test"}}]',
    ]))
    pages = []
    for title, rows in zip(["Add spawns", "Select and move", "Edit spawns", "Box corners", "Box settings", "Boundary testing", "Nudge 0.5 blocks"], [[row] for row in menu]):
        parts = [{"text": title + "\n\n", "color": "gold"}]
        for row in rows:
            for part in row:
                part = dict(part)
                part["text"] += "\n"
                parts.append(part)
            parts.append({"text": "\n"})
        pages.append({"raw": json.dumps(parts, separators=(",", ":"))})
    book = nbt.Compound({"title": nbt.String("Arena Editor"), "author": nbt.String("Backstabbed++"),
                         "pages": nbt.List[nbt.Compound]([nbt.Compound({"raw": nbt.String(p["raw"])}) for p in pages])})
    put("tools", f'give @s minecraft:written_book[minecraft:written_book_content={book.snbt()}]\nfunction bbe:menu')

    seed = to_nbt(state).snbt()
    put("initialize", f"data modify storage bbe:session state set value {seed}\ndata modify storage bbe:session show set value 1b")
    put("load", "\n".join([
        *[f"scoreboard objectives add {name} {kind}" for name, kind in [
            ("bbe.ui", "trigger"), ("bbe.pick", "trigger"), ("bbe.sel", "dummy"),
            ("bbe.id", "dummy"), ("bbe.tmp", "dummy"), ("bbe.page", "dummy"),
            ("bbe.test", "dummy"), ("bbe.deaths", "deathCount"), ("bbe.rev", "dummy")]],
        "execute unless data storage bbe:session state run function bbe:initialize",
        "scoreboard players set $clock bbe.tmp 0",
        "scoreboard players set $draw bbe.tmp 0",
        "scoreboard players set $two bbe.tmp 2",
        "scoreboard players set @a bbe.test 0",
        "function bbe:rebuild",
    ]))
    put("join", """
tag @s add bbe.editor
gamemode creative @s
scoreboard players set @s bbe.test 0
scoreboard players set @s bbe.page 0
scoreboard players set @s bbe.deaths 0
data modify storage bbe:session work.target set from storage bbe:session state.objects[{kind:"return"}]
function bbe:teleport with storage bbe:session work.target
function bbe:tools
""")
    dispatch = {1: "menu", 2: "tools", 3: "list", 4: "nearest", 5: "goto", 6: "move",
                7: "delete", 8: "undo", 9: "redo", 15: "cycle", 16: "face", 17: "visibility",
                18: "test", 19: "boundaries", 20: "outside", 21: "corner_a", 22: "corner_b",
                23: "new_area", 24: "resize", 25: "mode", 26: "action", 27: "enabled",
                28: "next_page", 29: "previous_page", 30: "containing"}
    for action, kind in [(10, "player"), (11, "ammo"), (12, "both"), (13, "spectator"), (14, "return")]:
        dispatch[action] = "add_" + kind
        put("add_" + kind, f'data modify storage bbe:session work.kind set value "{kind}"\nfunction bbe:add')
    for action, axis, delta in [(31, "x", .5), (32, "x", -.5), (33, "y", .5), (34, "y", -.5), (35, "z", .5), (36, "z", -.5)]:
        dispatch[action] = f"nudge_{action}"
        put(f"nudge_{action}", f"""
execute unless function bbe:context run return 0
execute if data storage bbe:session work.object{{kind:"area"}} run return 0
function bbe:snapshot
execute store result score $value bbe.tmp run data get storage bbe:session work.object.{axis} 1000
scoreboard players {'add' if delta > 0 else 'remove'} $value bbe.tmp {abs(int(delta * 1000))}
execute store result storage bbe:session work.object.{axis} double 0.001 run scoreboard players get $value bbe.tmp
function bbe:commit
""")
    put("tick", "\n".join([
        "execute as @a[tag=!bbe.editor] at @s run function bbe:join",
        "scoreboard players enable @a bbe.ui", "scoreboard players enable @a bbe.pick",
        "execute as @a[scores={bbe.pick=1..}] at @s run function bbe:pick",
        *[f"execute as @a[scores={{bbe.ui={i}}}] at @s run function bbe:{fn}" for i, fn in dispatch.items()],
        "scoreboard players set @a bbe.ui 0",
        'execute as @e[type=minecraft:interaction,tag=bbe.hit] if data entity @s interaction run function bbe:clicked',
        "execute as @a[scores={bbe.deaths=1..}] run scoreboard players set @s bbe.test 0",
        "scoreboard players set @a bbe.deaths 0",
        "scoreboard players add $clock bbe.tmp 1",
        "execute if score $clock bbe.tmp matches 5.. run function bbe:slow_tick",
    ]))
    put("slow_tick", """
scoreboard players set $clock bbe.tmp 0
scoreboard players add $draw bbe.tmp 5
execute if score $draw bbe.tmp matches 20.. run function bbe:refresh
execute as @e[type=minecraft:interaction,tag=bbe.hit,tag=bbe.player] at @s run particle minecraft:dust{color:[0.1,0.8,1.0],scale:0.8} ~ ~0.1 ~ 0.15 0.05 0.15 0 2 normal
execute as @e[type=minecraft:interaction,tag=bbe.hit,tag=bbe.ammo] at @s run particle minecraft:dust{color:[1.0,0.6,0.1],scale:0.8} ~ ~0.1 ~ 0.15 0.05 0.15 0 2 normal
execute as @e[type=minecraft:interaction,tag=bbe.hit,tag=bbe.both] at @s run particle minecraft:dust{color:[0.2,1.0,0.3],scale:0.8} ~ ~0.1 ~ 0.15 0.05 0.15 0 2 normal
execute if data storage bbe:session state{boundary_enabled:1b} as @a[scores={bbe.test=1}] at @s run function bbe:check
""")
    put("pick", """
scoreboard players operation @s bbe.sel = @s bbe.pick
scoreboard players set @s bbe.pick 0
function bbe:selected
""")
    put("clicked", """
scoreboard players operation $pick bbe.id = @s bbe.id
execute on target run scoreboard players operation @s bbe.sel = $pick bbe.id
execute on target at @s run function bbe:selected
data remove entity @s interaction
""")
    put("context", """
data modify storage bbe:session work.object set value {}
execute store result storage bbe:session work.id int 1 run scoreboard players get @s bbe.sel
function bbe:context_macro with storage bbe:session work
execute unless data storage bbe:session work.object.id run tellraw @s {"text":"Select an object first (right-click its label or use List IDs).","color":"yellow"}
execute unless data storage bbe:session work.object.id run return 0
return 1
""")
    put("context_macro", '$data modify storage bbe:session work.object set from storage bbe:session state.objects[{id:$(id)}]')
    put("selected", """
execute unless function bbe:context run return 0
function bbe:outline
function bbe:describe with storage bbe:session work.object
""")
    put("describe", "\n".join([
        '$tellraw @s {"text":"Selected #$(id) $(kind) at $(x), $(y), $(z)","color":"yellow"}',
        'execute if data storage bbe:session work.object{kind:"area"} run tellraw @s [{"nbt":"work.object","storage":"bbe:session"}]',
        tell([component("[Move here] ", 6), component("[Go there] ", 5), component("[Delete] ", 7, "red"), component("[Menu]", 1)]),
    ]))
    put("nearest", """
execute unless entity @e[tag=bbe.hit,distance=..8] run tellraw @s {"text":"No visible spawn within 8 blocks. Use List IDs for distant points and boxes.","color":"yellow"}
execute unless entity @e[tag=bbe.hit,distance=..8] run return 0
scoreboard players operation @s bbe.sel = @e[tag=bbe.hit,distance=..8,sort=nearest,limit=1] bbe.id
function bbe:selected
""")
    put("goto", """
execute unless function bbe:context run return 0
data modify storage bbe:session work.target set from storage bbe:session work.object
function bbe:teleport with storage bbe:session work.target
""")
    put("teleport", "$execute in minecraft:overworld run tp @s $(x) $(y) $(z) $(yaw) $(pitch)")
    put("snapshot", "data modify storage bbe:session undo set from storage bbe:session state\ndata remove storage bbe:session redo")
    for name, other in [("undo", "redo"), ("redo", "undo")]:
        put(name, f"""
execute unless data storage bbe:session {name} run return 0
data modify storage bbe:session {other} set from storage bbe:session state
data modify storage bbe:session state set from storage bbe:session {name}
data remove storage bbe:session {name}
function bbe:rebuild
function bbe:menu
""")
    put("new_id", """
data modify storage bbe:session work.object.id set from storage bbe:session state.next_id
execute store result score $next bbe.tmp run data get storage bbe:session state.next_id
scoreboard players operation @s bbe.sel = $next bbe.tmp
scoreboard players add $next bbe.tmp 1
execute store result storage bbe:session state.next_id int 1 run scoreboard players get $next bbe.tmp
""")
    coords = "\n".join(f"data modify storage bbe:session work.object.{a} set from entity @s Pos[{i}]" for i, a in enumerate("xyz"))
    angles = "\n".join(f"data modify storage bbe:session work.object.{a} set from entity @s Rotation[{i}]" for i, a in enumerate(("yaw", "pitch")))
    put("add", f"""
function bbe:snapshot
execute if data storage bbe:session work{{kind:"return"}} run data remove storage bbe:session state.objects[{{kind:"return"}}]
data modify storage bbe:session work.object set value {{kind:"player",x:0d,y:0d,z:0d,yaw:0f,pitch:0f}}
data modify storage bbe:session work.object.kind set from storage bbe:session work.kind
{coords}
{angles}
function bbe:new_id
data modify storage bbe:session state.objects append from storage bbe:session work.object
function bbe:rebuild
function bbe:selected
""")
    put("move", f"""
execute unless function bbe:context run return 0
execute if data storage bbe:session work.object{{kind:"area"}} run tellraw @s {{"text":"Resize boxes with Corner A/B and Resize selected box.","color":"yellow"}}
execute if data storage bbe:session work.object{{kind:"area"}} run return 0
function bbe:snapshot
{coords}
{angles}
function bbe:commit
""")
    put("face", f"""
execute unless function bbe:context run return 0
execute if data storage bbe:session work.object{{kind:"area"}} run return 0
function bbe:snapshot
{angles}
function bbe:commit
""")
    put("commit", "function bbe:commit_macro with storage bbe:session work.object\nfunction bbe:rebuild\nfunction bbe:selected")
    put("commit_macro", '$data modify storage bbe:session state.objects[{id:$(id)}] set from storage bbe:session work.object')
    put("delete", """
execute unless function bbe:context run return 0
execute if data storage bbe:session work.object{kind:"return"} run tellraw @s {"text":"Keep one return point. Move it or add a new Return instead.","color":"yellow"}
execute if data storage bbe:session work.object{kind:"return"} run return 0
function bbe:snapshot
function bbe:delete_macro with storage bbe:session work.object
function bbe:rebuild
""")
    put("delete_macro", '$data remove storage bbe:session state.objects[{id:$(id)}]')
    put("cycle", """
execute unless function bbe:context run return 0
execute if data storage bbe:session work.object{kind:"area"} run return 0
execute if data storage bbe:session work.object{kind:"return"} run return 0
function bbe:snapshot
data modify storage bbe:session work.old_kind set from storage bbe:session work.object.kind
execute if data storage bbe:session work{old_kind:"player"} run data modify storage bbe:session work.object.kind set value "ammo"
execute if data storage bbe:session work{old_kind:"ammo"} run data modify storage bbe:session work.object.kind set value "both"
execute if data storage bbe:session work{old_kind:"both"} run data modify storage bbe:session work.object.kind set value "spectator"
execute if data storage bbe:session work{old_kind:"spectator"} run data modify storage bbe:session work.object.kind set value "player"
function bbe:commit
""")
    put("visibility", """
execute store result score $show bbe.tmp run data get storage bbe:session show
data modify storage bbe:session show set value 1b
execute if score $show bbe.tmp matches 1 run data modify storage bbe:session show set value 0b
function bbe:rebuild
""")
    put("test", """
execute unless score @s bbe.test matches 0..1 run scoreboard players set @s bbe.test 0
scoreboard players add @s bbe.test 1
execute if score @s bbe.test matches 2.. run scoreboard players set @s bbe.test 0
tellraw @s [{"text":"Boundary test: "},{"score":{"name":"@s","objective":"bbe.test"}},{"text":" (1 = active). Boundaries must also be enabled. A kill test ends automatically on death."}]
""")
    put("boundaries", """
function bbe:snapshot
execute store result score $old bbe.tmp run data get storage bbe:session state.boundary_enabled
data modify storage bbe:session state.boundary_enabled set value 1b
execute if score $old bbe.tmp matches 1 run data modify storage bbe:session state.boundary_enabled set value 0b
function bbe:menu
""")
    put("outside", """
function bbe:snapshot
data modify storage bbe:session work.old_action set from storage bbe:session state.outside_action
data modify storage bbe:session state.outside_action set value "tp"
execute if data storage bbe:session work{old_action:"tp"} run data modify storage bbe:session state.outside_action set value "kill"
function bbe:menu
""")
    for corner in ("a", "b"):
        put("corner_" + corner, f'data modify storage bbe:session corner_{corner} set from entity @s Pos\ntellraw @s [{{"text":"Corner {corner.upper()}: "}},{{"nbt":"corner_{corner}","storage":"bbe:session"}}]')
    put("normalize", "\n".join([
        'execute unless data storage bbe:session corner_a run return 0',
        'execute unless data storage bbe:session corner_b run return 0',
        *[line for i, axis in enumerate("xyz") for line in [
            f"execute store result score $a bbe.tmp run data get storage bbe:session corner_a[{i}] 1000",
            f"execute store result score $b bbe.tmp run data get storage bbe:session corner_b[{i}] 1000",
            "scoreboard players operation $min bbe.tmp = $a bbe.tmp",
            "scoreboard players operation $min bbe.tmp < $b bbe.tmp",
            "scoreboard players operation $max bbe.tmp = $a bbe.tmp",
            "scoreboard players operation $max bbe.tmp > $b bbe.tmp",
            f"execute store result storage bbe:session work.object.{axis}1 double 0.001 run scoreboard players get $min bbe.tmp",
            f"execute store result storage bbe:session work.object.{axis}2 double 0.001 run scoreboard players get $max bbe.tmp",
            "scoreboard players operation $min bbe.tmp += $max bbe.tmp",
            f"execute store result storage bbe:session work.object.{axis} double 0.0005 run scoreboard players get $min bbe.tmp",
        ]], "return 1",
    ]))
    put("new_area", """
execute unless data storage bbe:session corner_a run return run tellraw @s {"text":"Set Corner A first.","color":"yellow"}
execute unless data storage bbe:session corner_b run return run tellraw @s {"text":"Set Corner B first.","color":"yellow"}
function bbe:snapshot
data modify storage bbe:session work.object set value {kind:"area",mode:"keep_in",action:"tp",enabled:1b,yaw:0f,pitch:0f}
function bbe:normalize
function bbe:new_id
data modify storage bbe:session state.objects append from storage bbe:session work.object
function bbe:selected
""")
    put("resize", """
execute unless function bbe:context run return 0
execute unless data storage bbe:session work.object{kind:"area"} run return 0
execute unless data storage bbe:session corner_a run return 0
execute unless data storage bbe:session corner_b run return 0
function bbe:snapshot
function bbe:normalize
function bbe:commit
""")
    for name, key, first, second in [("mode", "mode", "keep_in", "keep_out"), ("action", "action", "tp", "kill")]:
        put(name, f"""
execute unless function bbe:context run return 0
execute unless data storage bbe:session work.object{{kind:"area"}} run return 0
function bbe:snapshot
data modify storage bbe:session work.old set from storage bbe:session work.object.{key}
data modify storage bbe:session work.object.{key} set value "{first}"
execute if data storage bbe:session work{{old:"{first}"}} run data modify storage bbe:session work.object.{key} set value "{second}"
function bbe:commit
""")
    put("enabled", """
execute unless function bbe:context run return 0
execute unless data storage bbe:session work.object{kind:"area"} run return 0
function bbe:snapshot
execute store result score $old bbe.tmp run data get storage bbe:session work.object.enabled
data modify storage bbe:session work.object.enabled set value 1b
execute if score $old bbe.tmp matches 1 run data modify storage bbe:session work.object.enabled set value 0b
function bbe:commit
""")
    put("rebuild", """
scoreboard players add $revision bbe.rev 1
kill @e[tag=bbe.overlay]
execute unless data storage bbe:session {show:1b} run return 0
data modify storage bbe:session render_queue set from storage bbe:session state.objects
function bbe:render/loop
""")
    put("refresh", """
scoreboard players set $draw bbe.tmp 0
execute as @e[tag=bbe.overlay] unless score @s bbe.rev = $revision bbe.rev run kill @s
execute unless data storage bbe:session {show:1b} run return 0
data modify storage bbe:session render_queue set from storage bbe:session state.objects
function bbe:render/loop
""")
    put("render/loop", """
execute unless data storage bbe:session render_queue[0] run return 0
function bbe:render/object with storage bbe:session render_queue[0]
data remove storage bbe:session render_queue[0]
function bbe:render/loop
""")
    put("render/object", """
$execute if data storage bbe:session state.objects[{id:$(id),kind:"area"}] run return 0
$execute positioned $(x) $(y) $(z) unless loaded ~ ~ ~ run return 0
$execute if entity @e[type=minecraft:interaction,tag=bbe.hit,scores={bbe.id=$(id)}] run return 0
$summon minecraft:interaction $(x) $(y) $(z) {Tags:["bbe.overlay","bbe.hit","bbe.$(kind)","bbe.new"],width:0.65f,height:1.0f,response:1b}
$scoreboard players set @e[tag=bbe.new] bbe.id $(id)
$execute positioned $(x) $(y) $(z) run summon minecraft:text_display ~ ~1 ~ {Tags:["bbe.overlay","bbe.new"],billboard:"center",alignment:"center",text:'{"text":"#$(id) $(kind)","color":"aqua"}',background:1073741824,see_through:1b,view_range:0.5f,brightness:{sky:15,block:15},transformation:{translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],scale:[0.65f,0.65f,0.65f]}}
scoreboard players operation @e[tag=bbe.new] bbe.rev = $revision bbe.rev
tag @e[tag=bbe.new] remove bbe.new
""")
    put("outline", """
kill @e[tag=bbe.wire]
execute unless data storage bbe:session {show:1b} run return 0
execute unless data storage bbe:session work.object{kind:"area"} run return run function bbe:point_outline with storage bbe:session work.object
function bbe:dimensions
function bbe:box_outline with storage bbe:session work.object
""")
    put("point_outline", '$execute positioned $(x) $(y) $(z) rotated $(yaw) $(pitch) run particle minecraft:end_rod ^ ^0.1 ^1.2 0.05 0.05 0.05 0 10 force @s')
    put("dimensions", "\n".join(line for axis in "xyz" for line in [
        f"execute store result score $min bbe.tmp run data get storage bbe:session work.object.{axis}1 1000",
        f"execute store result score $max bbe.tmp run data get storage bbe:session work.object.{axis}2 1000",
        "scoreboard players operation $max bbe.tmp -= $min bbe.tmp",
        f"execute store result storage bbe:session work.object.d{axis} float 0.001 run scoreboard players get $max bbe.tmp",
    ]))
    edges = []
    for axis in range(3):
        others = [i for i in range(3) if i != axis]
        for one in (1, 2):
            for two in (1, 2):
                corner = [1, 1, 1]
                corner[others[0]], corner[others[1]] = one, two
                xyz = " ".join(f"$({a}{c})" for a, c in zip("xyz", corner))
                scale = ["0.035f"] * 3
                scale[axis] = f"$(d{'xyz'[axis]})f"
                edges.append(f'$summon minecraft:block_display {xyz} {{Tags:["bbe.overlay","bbe.wire","bbe.new"],block_state:{{Name:"minecraft:yellow_concrete"}},brightness:{{sky:15,block:15}},view_range:2f,transformation:{{translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],scale:[{",".join(scale)}]}}}}')
    edges += ["scoreboard players operation @e[tag=bbe.new] bbe.rev = $revision bbe.rev", "tag @e[tag=bbe.new] remove bbe.new"]
    put("box_outline", "\n".join(edges))

    put("list", "\n".join([
        'data modify storage bbe:session list_queue set from storage bbe:session state.objects',
        'scoreboard players operation $skip bbe.tmp = @s bbe.page',
        'scoreboard players set $ten bbe.tmp 10',
        'scoreboard players operation $skip bbe.tmp *= $ten bbe.tmp',
        'scoreboard players set $shown bbe.tmp 0',
        'function bbe:list_loop',
        tell([component("[Previous page] ", 29), component("[Next page] ", 28), component("[Menu]", 1)]),
    ]))
    put("list_loop", """
execute unless data storage bbe:session list_queue[0] run return 0
execute if score $shown bbe.tmp matches 10.. run return 0
execute if score $skip bbe.tmp matches ..0 run function bbe:list_row with storage bbe:session list_queue[0]
execute if score $skip bbe.tmp matches ..0 run scoreboard players add $shown bbe.tmp 1
scoreboard players remove $skip bbe.tmp 1
data remove storage bbe:session list_queue[0]
function bbe:list_loop
""")
    put("list_row", '$tellraw @s {"text":"[#$(id) $(kind)] $(x), $(y), $(z)","color":"aqua","clickEvent":{"action":"run_command","value":"/trigger bbe.pick set $(id)"}}')
    put("next_page", "scoreboard players add @s bbe.page 1\nfunction bbe:list")
    put("previous_page", "scoreboard players remove @s bbe.page 1\nexecute if score @s bbe.page matches ..-1 run scoreboard players set @s bbe.page 0\nfunction bbe:list")

    # Inline location predicates compare feet coordinates, avoiding the extra
    # block / bounding-box intersection semantics of selector dx/dy/dz.
    inside = '{condition:"minecraft:entity_properties",entity:"this",predicate:{location:{dimension:"minecraft:overworld",position:{' + ",".join(f'{a}:{{min:$({a}1),max:$({a}2)}}' for a in "xyz") + '}}}}'
    put("containing", """
scoreboard players set $found bbe.tmp 0
data modify storage bbe:session area_queue set from storage bbe:session state.objects
function bbe:containing_loop
execute if score $found bbe.tmp matches 1 run function bbe:selected
execute if score $found bbe.tmp matches 0 run tellraw @s {"text":"Your feet are outside all boxes.","color":"yellow"}
""")
    put("containing_loop", """
execute unless data storage bbe:session area_queue[0] run return 0
data modify storage bbe:session area_current set from storage bbe:session area_queue[0]
execute if data storage bbe:session area_current{kind:"area"} run function bbe:containing_box with storage bbe:session area_current
execute if score $found bbe.tmp matches 1 run return 0
data remove storage bbe:session area_queue[0]
function bbe:containing_loop
""")
    put("containing_box", f'$execute unless predicate {inside} run return 0\n$scoreboard players set @s bbe.sel $(id)\nscoreboard players set $found bbe.tmp 1')
    put("check", """
scoreboard players set $has_in bbe.tmp 0
scoreboard players set $inside bbe.tmp 0
scoreboard players set $acted bbe.tmp 0
data modify storage bbe:session check_queue set from storage bbe:session state.objects
function bbe:check_loop
execute if score $acted bbe.tmp matches 1 run return 0
execute if score $has_in bbe.tmp matches 1 if score $inside bbe.tmp matches 0 run function bbe:outside_response
""")
    put("check_loop", """
execute unless data storage bbe:session check_queue[0] run return 0
data modify storage bbe:session check_current set from storage bbe:session check_queue[0]
execute if data storage bbe:session check_current{kind:"area",enabled:1b} run function bbe:check_box with storage bbe:session check_current
execute if score $acted bbe.tmp matches 1 run return 0
data remove storage bbe:session check_queue[0]
function bbe:check_loop
""")
    put("check_box", f"""
$execute if data storage bbe:session state.objects[{{id:$(id),mode:"keep_in"}}] run scoreboard players set $has_in bbe.tmp 1
$execute if data storage bbe:session state.objects[{{id:$(id),mode:"keep_in"}}] if predicate {inside} run scoreboard players set $inside bbe.tmp 1
$execute if data storage bbe:session state.objects[{{id:$(id),mode:"keep_out"}}] if predicate {inside} run function bbe:response_$(action)
""")
    put("outside_response", "function bbe:outside_macro with storage bbe:session state")
    put("outside_macro", "$function bbe:response_$(outside_action)")
    put("response_kill", "scoreboard players set $acted bbe.tmp 1\nscoreboard players set @s bbe.test 0\nkill @s")
    put("response_tp", """
scoreboard players set $acted bbe.tmp 1
data modify storage bbe:session work.target set from storage bbe:session state.objects[{kind:"return"}]
function bbe:teleport with storage bbe:session work.target
""")
    # Explicit function API for precise, scriptable changes; the GUI covers the
    # normal workflow. These functions use the same undo and rendering path.
    put("set_point", """
$scoreboard players set @s bbe.sel $(id)
execute unless function bbe:context run return 0
execute if data storage bbe:session work.object{kind:"area"} run return 0
function bbe:snapshot
$data merge storage bbe:session {work:{object:{x:$(x)d,y:$(y)d,z:$(z)d,yaw:$(yaw)f,pitch:$(pitch)f}}}
function bbe:commit
""")
    files["pack.mcmeta"] = json.dumps({"pack": {"pack_format": 61, "description": "Backstabbed++ Arena Editor (Java 1.21.4)"}}, indent=2) + "\n"
    for tag in ("load", "tick"):
        files[f"data/minecraft/tags/function/{tag}.json"] = json.dumps({"values": [f"bbe:{tag}"]}) + "\n"
    for name, text in files.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return files


def to_nbt(value, key=""):
    if isinstance(value, dict):
        return nbt.Compound({k: to_nbt(v, k) for k, v in value.items()})
    if isinstance(value, list):
        if not value:
            return nbt.List[nbt.Compound]([])
        return nbt.List([to_nbt(v) for v in value])
    if isinstance(value, str):
        return nbt.String(value)
    if key in ("enabled", "boundary_enabled"):
        return nbt.Byte(value)
    if isinstance(value, (float, int)) and key in ("x", "y", "z", "x1", "y1", "z1", "x2", "y2", "z2", "yaw", "pitch"):
        return nbt.Double(value)
    return nbt.Int(value)
