"""Generate the requested Bagger deaths and Underwater physical exit seals.

Used by configure_kaizen_bases and update_arena_containment. Contains no save I/O.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXIT_MANIFEST = ROOT / 'docs/arenas/underwater_base_exits.json'
WHEEL_MANIFEST = ROOT / 'docs/arenas/bagger_288_wheels.json'
DESCRIPTIONS = {
    'bagger_288': 'Falls outside the build, fluid escapes and feet below Y -45.5 eliminate live participants through mcm:game/playerdeath. Lower wheel/tread landings are checked first and announce "<player>" got squashed by giant wheels. No boundary-return teleportation. Applies during waiting after entry, grace and play; spectators, dead/unqueued players, other maps and inactive states are excluded.',
    'underwater_base': 'No boundary-return teleportation or fluid punishment. Six exterior hatch cells are full barriers, with non-interactive block displays preserving their original appearance. Internal doors, decoration and both bubble lifts remain usable. Seals persist in the saved map and are restored on activation/reset; displays are recreated without duplicates on activation and removed on reset.',
}


def location(position):
    return {'condition': 'minecraft:location_check', 'predicate': {
        'dimension': 'minecraft:overworld', 'position': position}}


def configure_containment(files):
    def put(name, value):
        files['data/' + name] = (value.rstrip() + '\n').encode()

    wheels = json.loads(WHEEL_MANIFEST.read_text())
    put('bagger_288/predicate/wheels.json', json.dumps({'condition': 'minecraft:any_of',
        'terms': [location(box) for box in wheels['boxes']]}, separators=(',', ':')))
    put('bagger_288/predicate/below_death_line.json', json.dumps(location({'y': {'max': -45.5}})))
    checks = ['execute if predicate bagger_288:wheels run return run function bagger_288:squashed',
              'execute if predicate bagger_288:below_death_line run return run function bagger_288:fall',
              'execute unless predicate bagger_288:arena run return run function bagger_288:fall']
    for dy in ('~', '~1'):
        for block in ('#bagger_288:fluids', '#bagger_288:waterloggable[waterlogged=true]'):
            checks.append(f'execute if block ~ {dy} ~ {block} run return run function bagger_288:fall')
    put('bagger_288/function/check_player.mcfunction', '\n'.join(checks))
    for reason, message in [('squashed', '\"%s\" got squashed by giant wheels'),
                            ('fall', '\"%s\" fell off Bagger 288')]:
        component = {'translate': 'bagger_288.death.' + reason, 'fallback': message,
                     'color': 'gold', 'with': [{'selector': '@s'}]}
        put(f'bagger_288/function/{reason}.mcfunction', '\n'.join([
            'execute unless score $selectedMap CmdData matches 18 run return 0',
            'execute unless score $gamestate CmdData matches 0..1 run return 0',
            'execute unless entity @s[tag=queued,tag=!spectating,gamemode=!spectator] run return 0',
            'execute if score @s dead matches 1.. run return 0',
            'tellraw @a ' + json.dumps(component, separators=(',', ':')),
            'function mcm:game/playerdeath']))
    files.pop('data/bagger_288/function/return_player.mcfunction', None)
    # Preserve arena-editor spawn/geometry edits while routing its additional
    # tick entry through the same ordered wheel/fall rules, including waiting.
    editor_prefix = 'bbe_arena/function/bagger_288/'
    if 'data/' + editor_prefix + 'tick.mcfunction' in files:
        put(editor_prefix + 'check_player.mcfunction', 'function bagger_288:check_player')
        put(editor_prefix + 'kill.mcfunction', 'function bagger_288:fall')
        put(editor_prefix + 'tick.mcfunction', '\n'.join([
            'execute unless score $selectedMap CmdData matches 18 run return 0',
            'execute if score $gamestate CmdData matches 0 run function bagger_288:waiting_tick',
            'execute if score $gamestate CmdData matches 1 run function bagger_288:functionality']))
        files.pop('data/' + editor_prefix + 'tp.mcfunction', None)
    for fn in ('functionality', 'waiting_tick'):
        put(f'underwater_base/function/{fn}.mcfunction', '# Physical hatch seals provide containment; no boundary teleportation.\nreturn 0')
    for fn in ('check_player', 'return_player'):
        files.pop(f'data/underwater_base/function/{fn}.mcfunction', None)
    for fn in ('everytick', 'game/loops/ingame'):
        path = f'data/mcm/function/{fn}.mcfunction'
        lines = files[path].decode().splitlines()
        files[path] = ('\n'.join(line for line in lines if not line.endswith(
            ('run function underwater_base:waiting_tick', 'run function underwater_base:functionality'))) + '\n').encode()
    manifest = json.loads(EXIT_MANIFEST.read_text())
    positions = {' '.join(map(str, c['position'])) for c in manifest['changes']}
    # Old reset commands must never temporarily restore an interactive hatch.
    for path, raw in list(files.items()):
        if path.startswith('data/underwater_base/function/restore') and path.endswith('.mcfunction'):
            files[path] = ('\n'.join(line for line in raw.decode().splitlines()
                if not any(line.startswith('setblock ' + p + ' ') for p in positions)) + '\n').encode()
    put('underwater_base/function/seal_exits.mcfunction', '\n'.join(
        'setblock ' + ' '.join(map(str, c['position'])) + ' minecraft:barrier' for c in manifest['changes']))
    display_tag = 'UnderwaterBaseExitDisplay'
    displays = [f'kill @e[type=block_display,tag={display_tag}]']
    for c in manifest['changes']:
        # block_display's origin and model space match a normal block at integer XYZ.
        data = {'Tags': ['MapEntity', 'UnderwaterBaseRuntime', display_tag],
                'block_state': c['display']}
        displays.append('summon block_display ' + ' '.join(map(str, c['position'])) + ' ' +
                        json.dumps(data, separators=(',', ':')))
    put('underwater_base/function/spawn_exit_displays.mcfunction', '\n'.join(displays))
    for function, hook in [('restore_blocks', 'seal_exits'), ('activate', 'spawn_exit_displays')]:
        path = f'data/underwater_base/function/{function}.mcfunction'
        command = f'function underwater_base:{hook}'
        lines = [line for line in files[path].decode().splitlines() if line != command]
        files[path] = ('\n'.join(lines) + '\n' + command + '\n').encode()
