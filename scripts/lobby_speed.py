"""Install the lobby-only Speed II refresh without modifying arena effects."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FUNCTION = 'data/mcm/function/lobby/speed.mcfunction'
CALLER = 'data/mcm/function/lobby/lobby_functions.mcfunction'
HOOK = 'function mcm:lobby/speed'


def patched(members):
    result = dict(members)
    result[FUNCTION] = (ROOT/'lobby-speed/datapack'/FUNCTION).read_bytes().replace(b'\r\n',b'\n')
    text = result[CALLER].decode().replace('\r\r\n','\n').replace('\r\n','\n')
    if HOOK not in text.splitlines():
        text = text.rstrip()+'\n\n'+HOOK+'\n'
    result[CALLER] = text.encode()
    return result
