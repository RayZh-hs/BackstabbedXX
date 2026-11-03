"""Keep round items single: one knife per killer and no pickable bullet arrows.

Two player-visible regressions this repairs:

* A killer could end up holding two knives (hotbar slots 1 and 2).  The killer
  loadout placed its kit with `/give` whenever the target slot was occupied, so
  a second application spilled the knife into the first free slot.  The timeout
  recovery had the same shape: it never checked whether the owner had already
  picked the thrown knife back up, and `/give` put the replacement next to it.
* A gunner firing into their own feet could pick up the bullet.  The bullet is
  an arrow, and ``GravityBridge.fire`` calls ``setOwner``, which flips a vanilla
  arrow's pickup rule back to ALLOWED.

All edits are text transforms so they compose with the other overlays.
"""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]

LOADOUT = """\
function mcm:items/set_loadout_defaults

#> Replace the killer's kit in place.  `/give` lands an item in the first free
#> slot, which used to leave a second knife beside the first one; `replace`
#> forces the exact hotbar slot instead.  Any older knife is cleared first so
#> the killer can never own two.
clear @s snowball[custom_data~{knife:1b}]

data merge storage mcm:args {slot:1,replace:1b,nbt:{murderer:1b}}
function mcm:items/give_loadout_item {item:knife}

data merge storage mcm:args {slot:2,replace:1b,nbt:{murderer:1b}}
function mcm:items/give_loadout_item {item:1}

data merge storage mcm:args {slot:3,replace:1b,nbt:{murderer:1b}}
function mcm:items/give_loadout_item {item:2}

data merge storage mcm:args {slot:4,replace:1b,nbt:{murderer:1b}}
function mcm:items/give_loadout_item {item:3}
"""

RECOVER_ANCHOR = '# Invalidate both loaded and unloaded copies before issuing a replacement.'
RECOVER_GUARD = """\
#> The owner can pick the thrown knife back up on the same tick the timeout
#> expires.  Never hand out a replacement while they already hold one.
execute if items entity @s container.* snowball[custom_data~{knife:1b}] run scoreboard players set @s mcm_missing 0
execute if items entity @s weapon.* snowball[custom_data~{knife:1b}] run scoreboard players set @s mcm_missing 0
execute if items entity @s container.* snowball[custom_data~{knife:1b}] run return 0
execute if items entity @s weapon.* snowball[custom_data~{knife:1b}] run return 0
"""

PICKUP_FIX = 'data merge entity @s {pickup:0b}'
PICKUP_COMMENT = '#> A bullet must never be pickable; setting the owner re-opens vanilla arrow pickup.'
SHOOT_GUARD = """\
#> Keep every bullet unpickable. The gravity bridge sets the arrow owner, which
#> re-enables vanilla pickup, and a gunner standing on their own shot would take it.
execute as @e[type=arrow,tag=GunShot] run data merge entity @s {pickup:0b}
"""


def _text(members, name):
    return members[f'data/mcm/function/{name}.mcfunction'].decode().replace('\r\r\n', '\n').replace('\r\n', '\n')


def _store(members, name, text):
    members[f'data/mcm/function/{name}.mcfunction'] = text.encode()


def guard_recover(text):
    if 'Never hand out a replacement' in text:
        return text
    assert RECOVER_ANCHOR in text, 'knife recovery changed; review the guard anchor'
    return text.replace(RECOVER_ANCHOR, RECOVER_GUARD + '\n' + RECOVER_ANCHOR, 1)


def force_unpickable(text):
    if PICKUP_FIX in text:
        return text
    return text.rstrip('\n') + '\n' + PICKUP_COMMENT + '\n' + PICKUP_FIX + '\n'


def guard_bullet_tick(text):
    if 'Keep every bullet unpickable' in text:
        return text
    return text.rstrip('\n') + '\n' + SHOOT_GUARD


def patched(members):
    result = dict(members)
    _store(result, 'items/loadouts/murderer', LOADOUT)
    _store(result, 'extensions/knife/recover', guard_recover(_text(result, 'extensions/knife/recover')))
    _store(result, 'extensions/gun/setspeed', force_unpickable(_text(result, 'extensions/gun/setspeed')))
    _store(result, 'game/items/gun/shoot', guard_bullet_tick(_text(result, 'game/items/gun/shoot')))
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
