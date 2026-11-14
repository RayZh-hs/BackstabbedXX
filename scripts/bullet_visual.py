"""Align bullet displays using only datapack commands and the unchanged .3 bridge."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'data/mcm/function/extensions/gun/setspeed.mcfunction'
ALIGN = 'data/mcm/function/extensions/gun/align_visual.mcfunction'
CAPTURE = 'data/mcm/function/extensions/gun/capture_visual_offset.mcfunction'
CALL = 'execute on passengers if entity @s[type=item_display,tag=BulletDeco] at @s run function mcm:extensions/gun/align_visual'


def patched(members):
    result = dict(members)
    text = result[TARGET].decode().replace('\r\r\n', '\n').replace('\r\n', '\n')
    if CALL not in text:
        text = text.rstrip('\n') + '\n' + CALL + '\n'
    result[TARGET] = text.encode()
    for name in (ALIGN, CAPTURE):
        result[name] = (ROOT / 'bullet-visual/datapack' / name).read_bytes().replace(b'\r\n', b'\n')
    return result
