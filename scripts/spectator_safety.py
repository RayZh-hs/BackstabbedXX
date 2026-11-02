"""Apply spectator isolation to an existing datapack without changing its world."""
from pathlib import Path
import argparse
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'spectator-safety/datapack'
ACTIVE = 'tag=queued,tag=!spectating,gamemode=!spectator,predicate=mcm:game/not_eliminated'
GUARD = f'execute unless entity @s[{ACTIVE},tag=murderer] run return 0\n'


def patched(members):
    result = dict(members)
    def edit(name, transform):
        key = f'data/mcm/function/{name}.mcfunction'
        text = result[key].decode().replace('\r\r\n', '\n').replace('\r\n', '\n')
        result[key] = transform(text).encode()
    for name in ('extensions/knife/recover', 'game/items/knife_retrieve', 'game/items/knife/throw'):
        edit(name, lambda s: s if s.startswith(GUARD) else GUARD + s)
    edit('extensions/knife/tick', lambda s: s.replace(
        '@a[tag=queued,tag=murderer,tag=!spectating]', f'@a[{ACTIVE},tag=murderer]'))
    old = 'execute as @a[tag=murderer,tag=!spectating,predicate=mcm:items/hold_tracker] at @s positioned as @a[tag=innocent,tag=!spectating,limit=1,sort=nearest] run function mcm:game/items/player_tracker/find_player'
    new = f'execute unless score $mode CmdData matches 2 as @a[{ACTIVE},tag=murderer,predicate=mcm:items/hold_tracker] at @s run function mcm:game/items/player_tracker/track'
    edit('game/loops/ingame', lambda s: s.replace(old, new).replace(
        'as @a[tag=queued,tag=!spectating,predicate=mcm:items/hold_tracker]',
        f'as @a[{ACTIVE},tag=murderer,predicate=mcm:items/hold_tracker]'))
    for name in ('predicate/game/not_eliminated.json', 'function/game/items/knife/stuck.mcfunction',
                 'function/game/items/knife/unstick_owned.mcfunction',
                 'function/game/items/player_tracker/track.mcfunction', 'function/modes/tracker.mcfunction'):
        key = 'data/mcm/' + name
        result[key] = (SOURCE / key).read_bytes()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path, help='New staged ZIP; never overwrite the source save')
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error('Use a separate output path; back up and stop the world before installing.')
    with ZipFile(args.source) as z:
        assert len(z.namelist()) == len(set(z.namelist())), 'Duplicate ZIP members'
        before = {n: z.read(n) for n in z.namelist()}
    after = patched(before)
    with ZipFile(args.output, 'w', ZIP_DEFLATED) as z:
        for name, content in after.items():
            z.writestr(name, content)
    with ZipFile(args.output) as z:
        assert z.testzip() is None
        assert {n: z.read(n) for n in z.namelist()} == after
    print(f'Staged {sum(before.get(n) != b for n, b in after.items())} changed members: {args.output}')


if __name__ == '__main__':
    main()
