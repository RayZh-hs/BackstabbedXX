"""Carriage links for the original station geometry; no block changes.

Coordinates are measured from the saved build. Each train has six carriages;
the touching middle pair still needs a link through its two closed end walls.
"""

import json


TRAINS = (
    (3, ((-116, -103), (-101, -88), (-86, -73), (-72, -59), (-57, -44), (-42, -29))),
    (10, ((-20, -7), (-5, 8), (10, 23), (24, 37), (39, 52), (54, 67))),
    (35, ((-95, -82), (-80, -67), (-65, -52), (-51, -38), (-36, -23), (-21, -8))),
    (42, ((-84, -71), (-69, -56), (-54, -41), (-40, -27), (-25, -12), (-10, 3))),
)


def links():
    """Forty directed links, ordered west to east and north to south."""
    for train, (x, carriages) in enumerate(TRAINS, 1):
        for carriage, (north, south) in enumerate(carriages, 1):
            for direction, step in (("previous", -1), ("next", 1)):
                target = carriage + step
                if not 1 <= target <= len(carriages):
                    continue
                dest_north, dest_south = carriages[target - 1]
                yield {
                    "id": f"train_{train}_{carriage}_{direction}",
                    "train": train, "carriage": carriage, "target_carriage": target,
                    "direction": direction,
                    "wall": [x + 20480, -57, (north if step < 0 else south) + 20480],
                    "label": [x + 20480.5, -56.65, (north + .83 if step < 0 else south + .17) + 20480],
                    "yaw": 0 if step < 0 else 180,
                    "source_min": [x + 20479, -59, north + 20480.8],
                    "source_max": [x + 20482, -54, south + 20480.2],
                    "destination": [x + 20480.5, -57.8125,
                                    (dest_south - 1.5 if step < 0 else dest_north + 2.5) + 20480],
                }


def patch_datapack(files):
    """Update only station behavior and its activation/reload hooks."""
    def put(path, text):
        files[f"data/subway_station/{path}"] = (text.strip() + "\n").encode()

    # Remove files from a previous generated version before replacing them.
    for path in list(files):
        if path.startswith(("data/subway_station/function/carriages/",
                            "data/subway_station/advancement/carriages/")):
            del files[path]
    files.pop("data/subway_station/function/return_player.mcfunction", None)
    put("function/functionality.mcfunction", """
# Automatic boundary-return teleportation is intentionally disabled.
# Carriage links run only when a participant right-clicks an end-wall label.
""")

    spawn = ["# Rebuild only carriage links, preserving players and spawn occupancy.",
             "kill @e[tag=SubwayStationCarriageLink]"]
    for link in links():
        name = link["id"]
        tag = "SubwayStationLink_" + name
        x, y, z = link["label"]
        # The interaction box sits slightly in front of the existing wall.
        iz = z + (.18 if link["direction"] == "previous" else -.18)
        tags = f'Tags:["MapEntity","SubwayStationRuntime","SubwayStationCarriageLink","{tag}"]'
        text = json.dumps([
            {"translate": f'subway_station.carriage.{link["direction"]}',
             "fallback": "← Previous carriage" if link["direction"] == "previous" else "Next carriage →",
             "color": "aqua", "bold": True},
            {"text": "\n"},
            {"translate": "subway_station.carriage.use", "fallback": "Right-click", "color": "white"},
        ], ensure_ascii=False, separators=(",", ":"))
        text = text.replace("\\", "\\\\").replace("'", "\\'")
        spawn.append(f"summon text_display {x:.4f} {y:.4f} {z:.4f} " + "{" + tags +
                     f",Rotation:[{link['yaw']}f,0f],billboard:\"fixed\",text:'{text}',"
                     'line_width:200,alignment:"center",background:1610612736,text_opacity:-1b,shadow:1b,'
                     'transformation:{translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],'
                     'scale:[0.45f,0.45f,0.45f],right_rotation:[0f,0f,0f,1f]},view_range:0.35f}')
        spawn.append(f"summon interaction {x:.4f} -57.4 {iz:.4f} " + "{" + tags +
                     ',width:1.2f,height:1.4f,response:1b}')
        advancement = {
            "criteria": {"use": {"trigger": "minecraft:player_interacted_with_entity",
                "conditions": {"entity": {"type": "minecraft:interaction", "nbt": f'{{Tags:["{tag}"]}}'}}}},
            "rewards": {"function": f"subway_station:carriages/{name}"},
        }
        put(f"advancement/carriages/{name}.json", json.dumps(advancement, indent=2))
        lo, hi = link["source_min"], link["source_max"]
        box = ",".join([*(f"{a}={v:g}" for a, v in zip("xyz", lo)),
                        *(f"d{a}={b-a0:g}" for a, a0, b in zip("xyz", lo, hi))])
        dx, dy, dz = link["destination"]
        put(f"function/carriages/{name}.mcfunction", f"""
# Revoke first so independent players and repeated clicks both work.
advancement revoke @s only subway_station:carriages/{name}
execute unless score $selectedMap CmdData matches 16 run return 0
execute unless score $gamestate CmdData matches 0..1 run return 0
execute unless dimension minecraft:overworld run return 0
execute unless entity @s[type=player,tag=queued,tag=!spectating,gamemode=!spectator] run return 0
execute if score @s dead matches 1.. run return 0
execute unless entity @s[{box}] run return 0
execute positioned {x:.4f} -56.7 {iz:.4f} unless entity @s[distance=..4.5] run return 0
execute in minecraft:overworld run tp @s {dx:.4f} {dy:.4f} {dz:.4f}
""")
    put("function/carriages/spawn.mcfunction", "\n".join(spawn))

    path = "data/subway_station/function/activate.mcfunction"
    text = files[path].decode()
    hook = "function subway_station:carriages/spawn"
    if hook not in text:
        text = text.rstrip() + "\n" + hook + "\n"
    files[path] = text.encode()

    # Only an active round bypasses the normal load reset. Refresh links before
    # that early return without reactivating the arena or resetting its blocks.
    path = "data/mcm/function/load.mcfunction"
    text = files[path].decode()
    hook = "execute if score $selectedMap CmdData matches 16 if score $gamestate CmdData matches 1 run function subway_station:carriages/spawn"
    if hook not in text:
        anchor = "schedule function subway_station:register 1s"
        if anchor not in text:
            raise ValueError("Missing station registration hook")
        text = text.replace(anchor, anchor + "\n" + hook, 1)
    files[path] = text.encode()


TRANSLATIONS = {
    "en_us": {
        "subway_station.ready": "| Subway Station is ready. Right-click the carriage end-wall labels to move between carriages.",
        "subway_station.carriage.previous": "← Previous carriage",
        "subway_station.carriage.next": "Next carriage →",
        "subway_station.carriage.use": "Right-click",
    },
    "zh_cn": {
        "subway_station.ready": "| 地铁站已准备就绪。右键车厢端墙上的文字可前往相邻车厢。",
        "subway_station.carriage.previous": "← 上一节车厢",
        "subway_station.carriage.next": "下一节车厢 →",
        "subway_station.carriage.use": "右键通行",
    },
}
