#!/usr/bin/env python3
"""Wire Subway Station into the existing datapack, preserving unrelated entries.

Run after import_subway_station.py with ``uv run --with nbtlib python ...``.
The reset snapshot records original interactive states; it does not redesign
or seal any part of the station. Spawns use the connected central platform.
"""

import json
from pathlib import Path
import zipfile

import nbtlib as nbt

from import_subway_station import ROOT, WORLD
from subway_station_carriages import TRANSLATIONS, patch_datapack


def main():
    archive = WORLD / 'datapacks/mcm.zip'
    with zipfile.ZipFile(archive) as saved:
        files = {name: saved.read(name) for name in saved.namelist()}

    def put(name, value):
        files['data/' + name] = (value.strip() + '\n').encode()

    def append(name, value):
        path = 'data/mcm/function/' + name + '.mcfunction'
        text = files[path].decode()
        if value.strip() not in text:
            files[path] = (text.rstrip() + '\n\n' + value.strip() + '\n').encode()

    structure = nbt.load(ROOT / 'map-previewer/maps/subway-station/subway-station.nbt')
    palette = structure['palette']
    blocks = {tuple(int(b['pos'][i]) + [-12, -60, -214][i] for i in range(3)): palette[int(b['state'])] for b in structure['blocks']}
    support = {'granite', 'polished_granite', 'bricks', 'coarse_dirt'}

    def safe(x, z):
        for ox, oz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            if str(blocks.get((x + ox, -59, z + oz), {}).get('Name', '')).removeprefix('minecraft:') not in support:
                return False
            if any((x + ox, y, z + oz) in blocks for y in (-58, -57, -56)):
                return False
        return True

    sources = []
    # Preserve the showcase build's geometry. The central platform provides one
    # connected spawn pool without requiring crossings over the lowered tracks.
    for index in range(24):
        platform, along = (19, 23, 26)[index % 3], -112 + index * 8
        candidates = [(platform + ox, along + oz) for ox in range(-3, 4) for oz in range(-3, 4)]
        candidates.sort(key=lambda p: (p[0] - platform) ** 2 + (p[1] - along) ** 2)
        x, z = next(p for p in candidates if safe(*p) and
                    all((p[0]+.5-s[0])**2+(p[1]+.5-s[2])**2 >= 30 for s in sources))
        sources.append([x + .5, -58, z + .5])
    spawns = [[x + 20480, y, z + 20480] for x, y, z in sources]
    activation = ['kill @e[tag=MapEntity]', 'function subway_station:restore_blocks']
    for x, y, z in spawns:
        activation.append(f'summon marker {x:g} {y:g} {z:g} {{Tags:["PlayerSpawn","ScrapSpawn","MapEntity","SubwayStationRuntime"]}}')
    activation += [
        'summon marker 20502.5 -46 20458.5 {Tags:["SpectatorSpawn","MapEntity","SubwayStationRuntime"]}',
        'tellraw @a {"translate":"subway_station.ready","color":"aqua"}',
    ]
    put('subway_station/function/activate.mcfunction', '\n'.join(activation))
    put('subway_station/function/register.mcfunction', '''
execute unless entity @e[type=marker,tag=MapVote,tag=SubwayStation] run summon marker 0 -50 70 {Tags:["MapVote","SubwayStation"]}
scoreboard players set @e[type=marker,tag=MapVote,tag=SubwayStation] MapValues 16
function mcm:lobby/options/map_toggle/init
''')
    # Recorded station footprint for spawn validation. It is not enforced by
    # automatic teleportation; the user requested free movement in the station.
    bands = [(-59, -40, -9.7, 55.7), (-40, -38, -8.7, 54.7),
             (-38, -35, -7.7, 53.7), (-35, -33, -6.7, 52.7),
             (-33, -32, -5.7, 51.7), (-32, -31, -4.7, 50.7),
             (-31, -30, -3.7, 49.7), (-30, -29, -2.7, 48.7),
             (-29, -28, -.7, 46.7)]
    predicate = {'condition': 'minecraft:any_of', 'terms': []}
    for ymin, ymax, xmin, xmax in bands:
        predicate['terms'].append({'condition': 'minecraft:location_check', 'predicate': {
            'dimension': 'minecraft:overworld', 'position': {
                'x': {'min': xmin + 20480, 'max': xmax + 20480},
                'y': {'min': ymin, 'max': ymax},
                'z': {'min': 20356.3, 'max': 20555.7}}}})
    put('subway_station/predicate/arena.json', json.dumps(predicate, indent=2))
    # Restore the original interactive block states (no new barriers/geometry).
    restore = ['# Original source states: doors, trapdoors, buttons, plates, levers and containers.']
    for (x, y, z), state in sorted(blocks.items()):
        name = str(state['Name'])
        short = name.removeprefix('minecraft:')
        if short.endswith(('_door', '_trapdoor', '_button', '_pressure_plate')) or short == 'lever':
            props = ','.join(f'{k}={v}' for k, v in state.get('Properties', {}).items())
            restore.append(f'setblock {x+20480} {y} {z+20480} {name}[{props}]')
        elif short in ('barrel', 'hopper', 'furnace'):
            restore.append(f'data modify block {x+20480} {y} {z+20480} Items set value []')
    # Preserve the optional second-floor furniture reset when reconfiguring the
    # existing integration from the original source structure.
    if 'data/subway_station/function/furnishings/restore.mcfunction' in files:
        restore.append('function subway_station:furnishings/restore')
    put('subway_station/function/restore_blocks.mcfunction', '\n'.join(restore))
    put('subway_station/function/reset.mcfunction', '''
schedule clear subway_station:activate
kill @e[tag=SubwayStationRuntime]
function subway_station:restore_blocks
''')
    # A developer entry point uses the normal vote, loading, and activation path.
    select = files['data/yacht/function/select.mcfunction'].decode().replace('Yacht', 'SubwayStation')
    select = select.replace('positioned 28 2 89 as', 'positioned 28.0 2.0 89.0 as')
    put('subway_station/function/select.mcfunction', select)
    load_path = 'data/mcm/function/load.mcfunction'
    load = files[load_path].decode()
    if 'schedule function subway_station:register' not in load:
        load = load.replace('schedule function yacht:register 1s', 'schedule function yacht:register 1s\nschedule function subway_station:register 1s')
        reset_lines = 'execute if score $selectedMap CmdData matches 16 run function subway_station:reset\nexecute if score $selectedMap CmdData matches 16 run forceload remove 20464 20256 20543 20655\n'
        load = load.replace('schedule function mcm:respawn_entities 1s', reset_lines + 'schedule function mcm:respawn_entities 1s')
        files[load_path] = load.encode()
    append('respawn_entities', '''
# Subway Station integration
execute unless entity @e[type=marker,tag=MapVote,tag=SubwayStation] run summon marker 0 -50 70 {Tags:["MapVote","SubwayStation"]}
scoreboard players set @e[type=marker,tag=MapVote,tag=SubwayStation] MapValues 16
''')
    append('maps/start', 'execute if score $selectedMap CmdData matches 16 run time set 6000')
    append('maps/reset', '''
execute if score $selectedMap CmdData matches 16 run function subway_station:reset
execute if score $selectedMap CmdData matches 16 run forceload remove 20464 20256 20543 20655
''')
    append('game/loops/ingame', 'execute if score $selectedMap CmdData matches 16 run function subway_station:functionality')
    append('lobby/voting/end', '''
# Subway Station: 5 x 25 chunks, below the per-command 256 chunk limit.
execute if entity @e[type=marker,tag=SelectedMap,tag=SubwayStation] run forceload add 20464 20256 20543 20655
execute if entity @e[type=marker,tag=SelectedMap,tag=SubwayStation] run schedule function subway_station:activate 1s replace
''')
    poster_path = 'data/mcm/function/lobby/voting/map_position_id.mcfunction'
    files[poster_path] = ('\n'.join(line for line in files[poster_path].decode().splitlines()
        if not line.startswith('execute if score @s MapValues matches 16 ')) + '\n').encode()
    append('lobby/voting/map_position_id', '''
# Subway Station integration
execute if score @s MapValues matches 16 positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {Tags:["vote_display","SubwayStationPoster"],Rotation:[90f,0f],brightness:{block:15,sky:15},item_display:"fixed",item:{id:"minecraft:paper",count:1,components:{"minecraft:item_model":"subway_station:posters/subway_station"}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}
''')
    # Cleanup must precede creation; putting it at the function's end would
    # remove the newly selected station poster in normal random voting.
    set_maps_path = 'data/mcm/function/lobby/voting/set_maps.mcfunction'
    set_maps = files[set_maps_path].decode().replace('kill @e[tag=SubwayStationPoster]', '')
    set_maps = set_maps.replace('kill @e[tag=YachtPoster]', 'kill @e[tag=YachtPoster]\nkill @e[tag=SubwayStationPoster]')
    files[set_maps_path] = set_maps.encode()
    append('lobby/voting/player_vote', 'tellraw @s[scores={vote_map_id=16}] {"translate":"subway_station.voted","color":"green"}')
    options_path = 'data/mcm/function/lobby/options/map_toggle/init.mcfunction'
    options = files[options_path].decode()
    if 'name:SubwayStation' not in options:
        options = options.replace('execute store result score count temp', 'function mcm:lobby/options/map_toggle/add_map {name:SubwayStation,translate:"subway_station.name"}\n\nexecute store result score count temp')
        files[options_path] = options.encode()
    put('subway_station/credits.txt', '''
Subway Station - Original Build by KnotXackly
https://www.minecraftmaps.com/51929-subway-station-original-build
Reuse in builds/maps with credit to KnotXackly and a link to the map post when publishing.
Original source save: Minecraft Java 1.20.4, DataVersion 3700.
Backstabbed++ arena integration: subway_station, map ID 16, Minecraft Java 1.21.4.
Voting poster generated with OpenAI built-in imagegen, 26 October 2026.
The original architecture is preserved. Source teleport/spawn commands are disabled.
''')
    patch_datapack(files)
    temporary = archive.with_suffix('.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as saved:
        for name, value in files.items():
            saved.writestr(name, value)
    temporary.replace(archive)

    assets = ROOT / '.minecraft/resourcepacks/backstabbed-resource/assets'
    model = json.loads((assets / 'yacht/models/posters/yacht.json').read_text())
    # The station display is already at X=27.99 (offset -0.01). Keep its
    # face centred at Z=8; Yacht uses Z=0 with the legacy +0.99 offset.
    for element in model['elements']:
        element['from'][2] = element['to'][2] = 8
    model['credit'] = 'Subway Station by KnotXackly; https://www.minecraftmaps.com/51929-subway-station-original-build. Poster: OpenAI built-in imagegen, 26 October 2026.'
    model['textures'] = {k: 'subway_station:posters/subway_station' for k in model['textures']}
    for kind, value in [('models', model), ('items', {'model': {'type': 'minecraft:model', 'model': 'subway_station:posters/subway_station'}})]:
        path = assets / f'subway_station/{kind}/posters/subway_station.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + '\n')
    atlas_path = assets / 'minecraft/atlases/blocks.json'
    atlas = json.loads(atlas_path.read_text())
    entry = {'type': 'single', 'resource': 'subway_station:posters/subway_station'}
    if entry not in atlas['sources']:
        atlas['sources'].append(entry)
    atlas_path.write_text(json.dumps(atlas, indent=2) + '\n')
    translations = {
        'en_us': {'name': 'Subway Station', 'voted': '| Voted: Subway Station'},
        'zh_cn': {'name': '地铁站', 'voted': '| 已投票：地铁站'},
    }
    for language, values in translations.items():
        path = assets / f'subway_station/lang/{language}.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        values = {'subway_station.' + k: v for k, v in values.items()}
        values.pop('subway_station.boundary', None)
        values.update(TRANSLATIONS[language])
        path.write_text(json.dumps(values, ensure_ascii=False, indent=2) + '\n')
    report_path = ROOT / 'docs/arenas/subway_station.json'
    report = json.loads(report_path.read_text())
    report.update({'source_player_spawns': sources, 'destination_player_spawns': spawns,
                   'return_position': [20502.5, -58, 20470.5], 'reset_commands': len(restore) - 1,
                   'spawn_selection': '24 distributed points on the connected central platform. Original architecture preserved; no crossings or geometry repairs applied.',
                   'play_area': 'Original station and trains. Automatic boundary returns are disabled by user request; carriage end-wall links provide deliberate travel between adjacent carriages.'})
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Configured map 16, {len(spawns)} spawns, {len(restore)-1} reset commands')


if __name__ == '__main__':
    main()
