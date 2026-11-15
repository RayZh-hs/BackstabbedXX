"""Track authoritative bullet positions without changing the .3 bridge or arrow physics."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'data/mcm/function/extensions/gun/setspeed.mcfunction'
ALIGN = 'data/mcm/function/extensions/gun/align_visual.mcfunction'
CAPTURE = 'data/mcm/function/extensions/gun/capture_visual_offset.mcfunction'
SYNC = 'data/mcm/function/extensions/gun/sync_visual.mcfunction'
SPAWN = 'data/mcm/function/extensions/gun/spawn_visual.mcfunction'
TRY_FIRE = 'data/mcm/function/extensions/gun/try_fire.mcfunction'
SHOOT = 'data/mcm/function/game/items/gun/shoot.mcfunction'
OLD_CALL = 'execute on passengers if entity @s[type=item_display,tag=BulletDeco] at @s run function mcm:extensions/gun/align_visual'
CALL = 'execute on passengers if entity @s[type=item_display,tag=BulletTemplate] at @s run function mcm:extensions/gun/align_visual'
VISIBLE_ITEM = 'item:{id:"minecraft:diamond_hoe",count:1,components:{"minecraft:item_model":"minecraft:misc/bullet"}},'
SAVE_UUID = 'data modify storage mcm:bullet_visual arrow_uuid set from entity @s UUID'
CLEAR_UUID = 'data remove storage mcm:bullet_visual arrow_uuid'
OLD_ORPHAN = 'execute as @e[type=item_display,tag=BulletDeco] at @s unless entity @e[type=arrow,tag=GunShot,distance=..200] run kill @s'
OLD_NEAREST = 'execute as @e[type=arrow,tag=GunShot,scores={gundelay=8..}] at @s run kill @e[type=item_display,tag=BulletDeco,limit=1,sort=nearest,distance=..4]'
ORPHAN = 'execute as @e[type=item_display,tag=BulletDeco] unless data entity @s item.components."minecraft:custom_data".arrow_uuid run kill @s'
TICK = 'execute as @e[type=item_display,tag=BulletDeco] run function mcm:extensions/gun/sync_visual with entity @s item.components."minecraft:custom_data"'


def lines(data):
    return data.decode().replace('\r\r\n', '\n').replace('\r\n', '\n').splitlines()


def patched(members):
    result = dict(members)
    setup = [line for line in lines(result[TARGET]) if line not in (OLD_CALL, CALL, SAVE_UUID, CLEAR_UUID)]
    result[TARGET] = ('\n'.join(setup).rstrip() + '\n' + '\n'.join((SAVE_UUID, CALL, CLEAR_UUID)) + '\n').encode()
    shoot = [line for line in lines(result[SHOOT]) if line not in (OLD_ORPHAN, OLD_NEAREST, ORPHAN, TICK)]
    # Run after projectile cleanup, so removed arrows lose only their own visual.
    result[SHOOT] = ('\n'.join(shoot).rstrip() + '\n' + ORPHAN + '\n' + TICK + '\n').encode()
    result.pop(CAPTURE, None)
    fire = lines(result[TRY_FIRE])
    summon_indices = [i for i, line in enumerate(fire) if line.startswith('summon arrow ')]
    if len(summon_indices) != 1:
        raise ValueError('Expected exactly one gun projectile summon')
    i = summon_indices[0]
    fire[i] = fire[i].replace('["BulletDeco","NewBullet"]', '["BulletTemplate","NewBullet"]')
    fire[i] = fire[i].replace(VISIBLE_ITEM, '').replace('interpolation_duration:8', 'interpolation_duration:0')
    if 'BulletTemplate' not in fire[i] or 'item:' in fire[i]:
        raise ValueError('Gun passenger must be an invisible orientation template')
    result[TRY_FIRE] = ('\n'.join(fire) + '\n').encode()
    for name in (ALIGN, SYNC, SPAWN):
        result[name] = (ROOT / 'bullet-visual/datapack' / name).read_bytes().replace(b'\r\n', b'\n')
    return result
