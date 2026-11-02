"""Install Gunner and free-for-all Killer modes into the Classic lifecycle."""
import importlib.util
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('merchant_sync', ROOT / 'merchant-bridge/sync_datapack.py')
locking = importlib.util.module_from_spec(spec)
spec.loader.exec_module(locking)


def patched(members):
    members = dict(members)

    def edit(name, transform):
        key = f'data/mcm/function/{name}.mcfunction'
        members[key] = transform(members[key].decode().replace('\r\n', '\n')).encode()

    def prepend(name, command):
        edit(name, lambda s: s if command in s else command + '\n' + s)

    def append(name, command):
        edit(name, lambda s: s if command in s else s.rstrip() + '\n' + command + '\n')

    append('extensions/load', 'function mcm:modes/load')
    append('extensions/options/init', 'execute unless data storage mcm:options options.ext.mode run data modify storage mcm:options options.ext.mode set value 0\nfunction mcm:modes/sync')
    append('extensions/options/sync', 'function mcm:modes/sync')
    append('extensions/options/menu', 'function mcm:modes/menu')
    edit('extensions/options/change', lambda s: s if 'modes/select' in s else s.replace('function mcm:extensions/options/sync', 'execute if score @s mcm_options matches 15..17 run function mcm:modes/select\nfunction mcm:extensions/options/sync'))
    prepend('maps/start', 'function mcm:modes/reset\nscoreboard players operation $mode CmdData = $mode GameRules')
    prepend('game/pick_roles', 'execute if score $mode CmdData matches 1..2 run return run function mcm:modes/start')
    prepend('game/player_hit', 'execute if score $mode CmdData matches 1..2 run return run function mcm:modes/hit')
    prepend('game/innocentshot', 'execute if score $mode CmdData matches 1..2 run return run advancement revoke @s only mcm:hit_detection/innocent_killed')
    append('game/playerdeath', 'execute if score $mode CmdData matches 1..2 run function mcm:modes/death')
    prepend('game/items/scrap_function', 'execute if score $mode CmdData matches 1 run return run function mcm:modes/upgrade')
    # Alternate modes award guns through roles/crafting only, never through dead drops.
    edit('extensions/gun/assign_pickup', lambda s: s.replace('execute if score $mode CmdData matches 1..2 if score $gamestate CmdData matches 1 run return run kill @s\n', ''))
    prepend('extensions/gun/assign_pickup', 'execute if score $mode CmdData matches 1..2 if score $gamestate CmdData matches 1 run return run function mcm:modes/dropped_gun')
    append('game/loops/ingame', 'execute if score $mode CmdData matches 2 as @a[tag=queued,tag=!spectating,predicate=mcm:items/hold_tracker] at @s run function mcm:modes/tracker')
    prepend('game/items/murderer/teleporter', 'execute if score $mode CmdData matches 2 run return run function mcm:modes/teleporter')
    edit('game/loops/ingame', patch_ingame)
    edit('game/loops/game_timer', lambda s: '\n'.join(
        'execute unless score $mode CmdData matches 1..2 run ' + line
        if line.startswith('execute if score $gametimer CmdData matches 0 run') and 'unless score $mode' not in line
        else line for line in s.split('\n')))
    # Keep the counter moving for arena animations, without Killer time warnings.
    edit('game/loops/game_timer', lambda s: s if 'execute if score $mode CmdData matches 2 run return 0' in s else s.replace(
        'scoreboard players remove $gametimer CmdData 1',
        'scoreboard players remove $gametimer CmdData 1\nexecute if score $mode CmdData matches 2 run return 0'))
    append('game/loops/gameend', 'execute if score $gamestate CmdData matches -1 run function mcm:modes/reset')
    # Run the mode result after Classic clears the previous winner and titles.
    edit('game/loops/gameend', lambda s: s if 'modes/result' in s else s.replace('execute if score $gameEndTimer CmdData matches 200 run title @a clear', 'execute if score $gameEndTimer CmdData matches 200 run title @a clear\nexecute if score $gameEndTimer CmdData matches 200 if score $mode CmdData matches 1..2 run function mcm:modes/result'))
    prepend('game/game_end_stats', 'execute if score $mode CmdData matches 1..2 run return 0')
    append('game/loops/updatebossbar', 'execute if score $mode CmdData matches 1..2 run function mcm:modes/bossbar')
    append('player_leave', 'scoreboard players reset @s bb_team\nscoreboard players reset @s bb_respawn\nscoreboard players reset @s bb_safe')
    for path in (ROOT / 'game-modes/datapack').rglob('*.mcfunction'):
        members[path.relative_to(ROOT / 'game-modes/datapack').as_posix()] = path.read_bytes()
    return members


def patch_ingame(s):
    if 'function mcm:modes/tick' in s:
        return s
    start = s.index('#> Win conditions')
    end = s.index('#> Play ambient sounds', start)
    block = s[start:end]
    block = '\n'.join('execute unless score $mode CmdData matches 1..2 run ' + line
                      if line.startswith('execute ') else line for line in block.split('\n'))
    s = s[:start] + 'function mcm:modes/tick\n' + block + s[end:]
    s = s.replace('execute as @a[tag=murderer,tag=!spectating] at @s run particle',
                  'execute unless score $mode CmdData matches 1..2 as @a[tag=murderer,tag=!spectating] at @s run particle')
    return s


def main():
    with locking.stopped():
        path = locking.WORLD / 'datapacks/mcm.zip'
        before = path.read_bytes()
        with ZipFile(path) as z:
            infos = z.infolist()
            assert len(infos) == len({i.filename for i in infos}), 'Duplicate ZIP members'
            members = {i.filename: z.read(i) for i in infos}
        changes = patched(members)
        pending = path.with_suffix('.modes-pending')
        try:
            with ZipFile(pending, 'w', compression=ZIP_DEFLATED) as z:
                for info in infos:
                    z.writestr(info, changes.pop(info.filename))
                for name, content in sorted(changes.items()):
                    z.writestr(name, content)
            if path.read_bytes() != before:
                raise RuntimeError('Datapack changed concurrently')
            pending.replace(path)
        finally:
            pending.unlink(missing_ok=True)
    print('Game modes synchronized.')


if __name__ == '__main__':
    main()
