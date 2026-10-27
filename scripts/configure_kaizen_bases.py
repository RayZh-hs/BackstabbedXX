#!/usr/bin/env python3
"""Register the imported bases, saved spawn plans, boundaries and voting art.

Requires nbtlib and the preserved import/spawn records. Repeated configuration
replaces generated entries and preserves unrelated datapack members and assets.
Run only while the source save is stopped.
"""
from collections import defaultdict
import copy
import fcntl
import importlib.util
import json
from pathlib import Path
import zipfile

from furnish_subway_station import unpack, block_command, state_key
from import_kaizen_bases import MAPS, ROOT, WORLD, WORK
from arena_containment import configure_containment, DESCRIPTIONS


def original_states(spec):
    collision_states = json.loads((ROOT / 'tests/fixtures/kaizen_collision_shapes.json').read_text())['states']
    module_spec = importlib.util.spec_from_file_location('world_export', ROOT / 'map-previewer/export-java-world.py')
    exporter = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(exporter)
    dx, _, dz = spec['translation']
    bounds = spec['chunks']
    regions = {WORLD / 'region' / f'r.{(x+dx//16)//32}.{(z+dz//16)//32}.mca'
               for x in range(bounds[0], bounds[1]+1) for z in range(bounds[2], bounds[3]+1)}
    class Folder:
        def glob(self, _):
            return sorted(regions)
    for chunk in exporter.chunks(Folder()):
        cx, cz = int(chunk['xPos']), int(chunk['zPos'])
        if not (bounds[0] <= cx-dx//16 <= bounds[1] and bounds[2] <= cz-dz//16 <= bounds[3]):
            continue
        tiles = {tuple(int(t[a]) for a in 'xyz'): t for t in chunk.get('block_entities', [])}
        for section in chunk.get('sections', []):
            states = section.get('block_states')
            if not states:
                continue
            values = None
            for index, state in enumerate(states['palette']):
                short = str(state['Name']).split(':')[1]
                dry = spec['namespace'] == 'underwater_base' and short in ('air', 'cave_air')
                name, properties = state_key(state)
                key = name + '[' + ','.join(f'{k}={v}' for k, v in properties) + ']'
                fragile = spec['namespace'] == 'underwater_base' and short not in (
                    'air', 'cave_air', 'void_air', 'water', 'lava', 'bubble_column', 'barrier',
                    'kelp', 'kelp_plant', 'seagrass', 'tall_seagrass') and (
                    not collision_states[key] or short.endswith('_carpet'))
                reset = (short.endswith(('_door', '_trapdoor', '_button', '_pressure_plate', '_fence_gate')) or
                         short in ('lever', 'repeater', 'comparator', 'redstone_wire', 'tripwire', 'tripwire_hook',
                                   'wheat', 'carrots', 'potatoes', 'beetroots', 'nether_wart', 'cocoa', 'sweet_berry_bush',
                                   'farmland', 'composter', 'cave_vines', 'cave_vines_plant', 'daylight_detector'))
                if spec['namespace'] == 'underwater_base' and (short.startswith('potted_') or short in
                        ('fern', 'dead_bush', 'pink_petals', 'short_grass', 'large_fern', 'tall_grass',
                         'torch', 'wall_torch', 'soul_torch', 'soul_wall_torch', 'redstone_torch',
                         'redstone_wall_torch', 'end_rod', 'ladder', 'flower_pot')):
                    reset = True
                if not reset and not dry and not fragile:
                    continue
                if values is None:
                    values = unpack(states)
                for q, value in enumerate(values):
                    if int(value) == index:
                        pos = [cx*16+(q&15), int(section['Y'])*16+(q>>8), cz*16+((q>>4)&15)]
                        if dry:
                            if all(spec['build_min'][a] + spec['translation'][a] <= pos[a] <=
                                   spec['build_max'][a] + spec['translation'][a] for a in range(3)):
                                yield ('dry', pos, str(state['Name']))
                        elif fragile and all(spec['build_min'][a] + spec['translation'][a] <= pos[a] <=
                                             spec['build_max'][a] + spec['translation'][a] for a in range(3)):
                            yield ('fragile', pos, state)
                        elif reset:
                            yield ('state', pos, state)
        for pos, tile in tiles.items():
            yield ('tile', pos, tile)


def configure():
    archive = WORLD / 'datapacks/mcm.zip'
    with zipfile.ZipFile(archive) as saved:
        if len(saved.namelist()) != len(set(saved.namelist())):
            raise ValueError('Duplicate datapack members')
        files = {n: saved.read(n) for n in saved.namelist()}

    def put(path, content):
        files['data/' + path] = (content.rstrip() + '\n').encode()

    def append(function, content):
        path = 'data/mcm/function/' + function + '.mcfunction'
        text = files[path].decode()
        if content.strip() not in text:
            files[path] = (text.rstrip() + '\n\n' + content.strip() + '\n').encode()

    assets = ROOT / '.minecraft/resourcepacks/backstabbed-resource/assets'
    atlas_path = assets / 'minecraft/atlases/blocks.json'
    atlas = json.loads(atlas_path.read_text())
    for spec in MAPS:
        ns, title, tag, mid = [spec[k] for k in ('namespace', 'title', 'tag', 'map_id')]
        runtime, participant = tag + 'Runtime', tag + 'Participant'
        report_path = ROOT / f'docs/arenas/{ns}.json'
        report = json.loads(report_path.read_text())
        x0, x1, z0, z1 = spec['chunks']
        dx, _, dz = spec['translation']
        envelope = f'{x0*16+dx} {z0*16+dz} {x1*16+dx+15} {z1*16+dz+15}'
        report['forceload_bounds'] = [x0*16+dx, z0*16+dz, x1*16+dx+15, z1*16+dz+15]
        activation = [f'execute unless score $selectedMap CmdData matches {mid} run return 0',
                      'execute unless score $gamestate CmdData matches 0..1 run return 0',
                      'kill @e[tag=MapEntity]', f'tag @a remove {participant}', f'function {ns}:restore_blocks']
        for p in report['destination_player_spawns']:
            activation.append(f'summon marker {" ".join(f"{v:g}" for v in p)} {{Tags:["PlayerSpawn","ScrapSpawn","MapEntity","{runtime}"]}}')
        activation.append(f'summon marker {" ".join(f"{v:g}" for v in report["spectator_position"])} {{Tags:["SpectatorSpawn","MapEntity","{runtime}"]}}')
        activation.append(f'tellraw @a {{"translate":"{ns}.ready","fallback":"{title} ready","color":"aqua"}}')
        put(f'{ns}/function/activate.mcfunction', '\n'.join(activation))
        put(f'{ns}/function/register.mcfunction', f'''execute unless entity @e[type=marker,tag=MapVote,tag={tag}] run summon marker 0 -50 70 {{Tags:["MapVote","{tag}"]}}
scoreboard players set @e[type=marker,tag=MapVote,tag={tag}] MapValues {mid}
function mcm:lobby/options/map_toggle/init''')
        predicate = {'condition': 'minecraft:any_of', 'terms': [
            {'condition': 'minecraft:location_check', 'predicate': {'dimension': 'minecraft:overworld', 'position': box}}
            for box in report['boundary_boxes']]}
        put(f'{ns}/predicate/arena.json', json.dumps(predicate, separators=(',', ':')))
        files.pop(f'data/{ns}/predicate/fluid.json', None)
        put(f'{ns}/tags/block/fluids.json', json.dumps({'values': ['minecraft:' + name for name in
            ('water', 'lava', 'bubble_column', 'kelp', 'kelp_plant', 'seagrass', 'tall_seagrass')]}))
        audited = json.loads((WORK / 'states.json').read_text())
        target_states = json.loads((WORK / 'collision-audit.json').read_text())['states']
        waterloggable = sorted({state['Name'] for key, state in audited.items()
                               if key in target_states and 'waterlogged' in state.get('Properties', {})})
        put(f'{ns}/tags/block/waterloggable.json', json.dumps({'values': waterloggable}))
        put(f'{ns}/function/return_player.mcfunction', f'''execute in minecraft:overworld run tp @s {" ".join(f"{v:g}" for v in report["return_position"])}
effect clear @s minecraft:levitation
effect clear @s minecraft:slow_falling''')
        # Waiting participants are marked only after reaching this arena. This
        # avoids pulling queued lobby players into a not-yet-loaded selection.
        put(f'{ns}/function/waiting_tick.mcfunction', f'''execute unless score $selectedMap CmdData matches {mid} run return 0
execute unless score $gamestate CmdData matches 0 run return 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s if predicate {ns}:arena run tag @s add {participant}
execute as @a[tag=queued,tag={participant},tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. run function {ns}:check_player''')
        response = f'{ns}:escape' if ns == 'meridian_base' else f'{ns}:return_player'
        if ns == 'meridian_base':
            # Use round elimination at the perimeter as well as in water, so
            # falling players cannot be rescued just before reaching the ocean.
            put(f'{ns}/function/escape.mcfunction', f'''execute if score $gamestate CmdData matches 1 run return run function mcm:game/playerdeath
function {ns}:return_player''')
        put(f'{ns}/function/check_player.mcfunction', f'''execute unless predicate {ns}:arena run return run function {response}
execute if block ~ ~ ~ #{ns}:fluids run return run function {response}
execute if block ~ ~1 ~ #{ns}:fluids run return run function {response}
execute if block ~ ~ ~ #{ns}:waterloggable[waterlogged=true] run return run function {response}
execute if block ~ ~1 ~ #{ns}:waterloggable[waterlogged=true] run function {response}''')
        put(f'{ns}/function/functionality.mcfunction', f'''execute unless score $selectedMap CmdData matches {mid} run return 0
execute unless score $gamestate CmdData matches 1 run return 0
execute as @a[tag=queued,tag=!spectating,gamemode=!spectator] at @s unless score @s dead matches 1.. run function {ns}:check_player''')
        restore = ['# Original imported interactive states and inventories; architecture is unchanged.']
        dry_cells = defaultdict(set)
        fragile_states, fragile_tiles, fragile_positions = [], [], set()
        for kind, pos, value in original_states(spec):
            coords = ' '.join(map(str, pos))
            if kind == 'dry':
                dry_cells[pos[1], pos[2], value].add(pos[0])
            elif kind == 'fragile':
                fragile_positions.add(tuple(pos))
                fragile_states.append(block_command(pos, value))
            elif kind == 'state':
                restore.append(block_command(pos, value))
            elif str(value['id']) == 'minecraft:mob_spawner':
                # Existing cave spawners are outside the play mask. Their saved
                # blocks/NBT remain intact; keep them from running during rounds.
                restore.append(f'data merge block {coords} {{Delay:32767s}}')
            else:
                # Merge original NBT to reset inventory/book/furnace/crafter state.
                original = copy.deepcopy(value)
                for key in ('id', 'x', 'y', 'z', 'keepPacked'):
                    original.pop(key, None)
                command = f'data merge block {coords} {original.snbt()}'
                if tuple(pos) in fragile_positions:
                    fragile_tiles.append(command)
                else:
                    restore.append(command)
        # Close/reset hatches first, then remove only water that entered cells
        # originally saved dry. Existing ocean and waterlogged detail are kept.
        dry_restore = []
        for (y, z, name), xs in sorted(dry_cells.items()):
            runs = []
            for x in sorted(xs):
                if runs and x == runs[-1][1]+1:
                    runs[-1][1] = x
                else:
                    runs.append([x, x])
            for lo, hi in runs:
                dry_restore.append(f'fill {lo} {y} {z} {hi} {y} {z} {name} replace minecraft:water')
        if dry_restore:
            put(f'{ns}/function/restore_dry_cells.mcfunction', '\n'.join(dry_restore))
            restore.append(f'function {ns}:restore_dry_cells')
            report['dry_reset_commands'] = len(dry_restore)
            report['original_dry_cells'] = sum(map(len, dry_cells.values()))
        if fragile_states:
            put(f'{ns}/function/restore_fragile_details.mcfunction', '\n'.join(fragile_states + fragile_tiles))
            restore.append(f'function {ns}:restore_fragile_details')
            report['fragile_reset_commands'] = len(fragile_states) + len(fragile_tiles)
        # Split reset work into functions well below vanilla command-chain limits.
        for index in range(0, len(restore), 1500):
            put(f'{ns}/function/restore/part_{index//1500}.mcfunction', '\n'.join(restore[index:index+1500]))
        put(f'{ns}/function/restore_blocks.mcfunction', '\n'.join(
            f'function {ns}:restore/part_{i}' for i in range((len(restore)+1499)//1500)))
        put(f'{ns}/function/reset.mcfunction', f'''schedule clear {ns}:activate
kill @e[tag={runtime}]
tag @a remove {participant}
function {ns}:restore_blocks''')
        select = files['data/yacht/function/select.mcfunction'].decode().replace('Yacht', tag)
        select = select.replace('positioned 28 2 89 as', 'positioned 28.0 2.0 89.0 as')
        put(f'{ns}/function/select.mcfunction', select)
        load_path = 'data/mcm/function/load.mcfunction'
        load = files[load_path].decode()
        register = f'schedule function {ns}:register 1s'
        if register not in load:
            load = load.replace('execute unless score $gamestate CmdData matches ..0 run return 1',
                                register + '\nexecute unless score $gamestate CmdData matches ..0 run return 1')
            load = load.replace('schedule function mcm:respawn_entities 1s',
                f'execute if score $selectedMap CmdData matches {mid} run function {ns}:reset\n'
                f'execute if score $selectedMap CmdData matches {mid} run forceload remove {envelope}\n'
                'schedule function mcm:respawn_entities 1s')
            files[load_path] = load.encode()
        append('respawn_entities', f'function {ns}:register')
        append('maps/start', f'execute if score $selectedMap CmdData matches {mid} run time set 6000')
        append('maps/reset', f'''execute if score $selectedMap CmdData matches {mid} run function {ns}:reset
execute if score $selectedMap CmdData matches {mid} run forceload remove {envelope}''')
        append('game/loops/ingame', f'execute if score $selectedMap CmdData matches {mid} run function {ns}:functionality')
        append('everytick', f'execute if score $gamestate CmdData matches 0 if score $selectedMap CmdData matches {mid} run function {ns}:waiting_tick')
        append('lobby/voting/end', f'''execute if entity @e[type=marker,tag=SelectedMap,tag={tag}] run forceload add {envelope}
execute if entity @e[type=marker,tag=SelectedMap,tag={tag}] run schedule function {ns}:activate 1s replace''')
        append('lobby/voting/map_position_id', f'''execute if score @s MapValues matches {mid} positioned ~-0.01 ~1 ~1 run summon item_display ~ ~ ~ {{Tags:["vote_display","{tag}Poster"],Rotation:[90f,0f],brightness:{{block:15,sky:15}},item_display:"fixed",item:{{id:"minecraft:paper",count:1,components:{{"minecraft:item_model":"{ns}:posters/{ns}"}}}},transformation:[2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,2f,0f,0f,0f,0f,1f]}}''')
        path = 'data/mcm/function/lobby/voting/set_maps.mcfunction'
        if f'kill @e[tag={tag}Poster]' not in files[path].decode():
            files[path] = (f'kill @e[tag={tag}Poster]\n' + files[path].decode()).encode()
        append('lobby/voting/player_vote', f'tellraw @s[scores={{vote_map_id={mid}}}] {{"translate":"{ns}.voted","color":"green"}}')
        path = 'data/mcm/function/lobby/options/map_toggle/init.mcfunction'
        if f'name:{tag},' not in files[path].decode():
            files[path] = files[path].decode().replace('execute store result score count temp',
                f'function mcm:lobby/options/map_toggle/add_map {{name:{tag},translate:"{ns}.name"}}\n\nexecute store result score count temp').encode()
        # Map IDs listed in the voting entry point help future integrations.
        append('lobby/voting/start', f'# {mid}: {title} ({ns})')
        put(f'{ns}/credits.txt', f'''{title} by KAIZEN87
{report['source_url']}
License notice: all rights reserved; personal use only. Terms: https://www.patreon.com/posts/license-usage-70505678
Source 1.21.8, adapted to Java 1.21.4; map ID {mid}. Original download preserved.
Voting art reuses KAIZEN87 webpage imagery, adapted with OpenAI built-in imagegen.
User-authorized decoration substitutions: {report['compatibility_changes']}. Buildings and routes preserved.''')
        source_world = ROOT / report['source_world']
        notice = next(source_world.rglob('License & Usage Terms.txt'), None)
        if notice:
            files[f'data/{ns}/source-license-notice.txt'] = notice.read_bytes()
        model = json.loads((assets / 'subway_station/models/posters/subway_station.json').read_text())
        model['credit'] = f'{title} by KAIZEN87; {report["source_url"]}. Webpage imagery adapted with OpenAI built-in imagegen; final Meridian image selected/supplied by the user.'
        model['textures'] = {key: f'{ns}:posters/{ns}' for key in model['textures']}
        for kind, value in [('models', model), ('items', {'model': {'type': 'minecraft:model', 'model': f'{ns}:posters/{ns}'}})]:
            path = assets / f'{ns}/{kind}/posters/{ns}.json'
            path.parent.mkdir(exist_ok=True, parents=True)
            path.write_text(json.dumps(value, indent=2) + '\n')
        entry = {'type': 'single', 'resource': f'{ns}:posters/{ns}'}
        if entry not in atlas['sources']:
            atlas['sources'].append(entry)
        chinese = {'meridian_base': '子午线基地', 'bagger_288': '巴格尔288', 'underwater_base': '水下基地'}[ns]
        for lang, label in [('en_us', title), ('zh_cn', chinese)]:
            path = assets / f'{ns}/lang/{lang}.json'
            path.parent.mkdir(exist_ok=True, parents=True)
            values = {f'{ns}.name': label, f'{ns}.voted': ('| Voted: ' if lang == 'en_us' else '| 已投票：') + label,
                f'{ns}.ready': label + (' ready' if lang == 'en_us' else '已就绪')}
            if ns == 'bagger_288':
                values.update({f'{ns}.death.squashed': '\"%s\" got squashed by giant wheels' if lang == 'en_us' else '“%s”被巨型车轮碾碎了',
                               f'{ns}.death.fall': '\"%s\" fell off Bagger 288' if lang == 'en_us' else '“%s”从巴格尔288上坠落了'})
            path.write_text(json.dumps(values, ensure_ascii=False, indent=2) + '\n')
        report['reset_main_commands'] = len(restore)-1
        report['reset_commands'] = (len(restore)-1 +
            (len(dry_restore)-1 if dry_restore else 0) +
            (len(fragile_states)+len(fragile_tiles)-1 if fragile_states else 0))
        if ns in DESCRIPTIONS:
            report['containment'] = DESCRIPTIONS[ns]
            report['boundary_teleport_enabled'] = False
        report_path.write_text(json.dumps(report, indent=2) + '\n')
        print(f'{title}: map {mid}, 24 spawns, {len(report["boundary_boxes"])} boundary boxes, {len(restore)-1} reset commands')
    atlas_path.write_text(json.dumps(atlas, indent=2) + '\n')
    configure_containment(files)
    temporary = archive.with_suffix('.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as saved:
        for name, content in files.items():
            saved.writestr(name, content)
    temporary.replace(archive)


if __name__ == '__main__':
    with (WORLD / 'session.lock').open('a+b') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        configure()
