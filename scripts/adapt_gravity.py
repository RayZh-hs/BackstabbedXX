"""Apply the gravity bridge integration to an existing mcm datapack, preserving all other entries."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACK = next((ROOT / '.minecraft/saves').glob('*/datapacks/mcm.zip'))

def apply(pack=PACK):
    with zipfile.ZipFile(pack) as z:
        entries = {n: z.read(n) for n in z.namelist()}
    changed = {}
    def read(name):
        return entries['data/mcm/function/' + name + '.mcfunction'].decode('utf8').replace('\r\r\n', '\n').replace('\r\n', '\n')
    def put(name, text):
        changed['data/mcm/function/' + name + '.mcfunction'] = text.encode('utf8')
    t = read('extensions/gun/try_fire')
    if 'gravity bridge fire' in t:
        raise SystemExit('Already adapted; refusing to repeat patch')
    t = t.replace('execute facing ^ ^ ^14 positioned 0.0 0 0.0 run summon arrow ^ ^ ^7', 'summon arrow ~ ~ ~')
    t = t.replace('execute positioned ~ ~1.5 ~ as @e[type=arrow,tag=NewGunShot,limit=1] run function mcm:extensions/gun/setspeed',
                  'gravity bridge fire @e[type=arrow,tag=NewGunShot,limit=1]\nexecute as @e[type=arrow,tag=NewGunShot,limit=1] run function mcm:extensions/gun/setspeed')
    put('extensions/gun/try_fire', t)
    put('extensions/gun/setspeed', '# Position, world velocity, owner and display orientation are initialized by the mod.\ntag @s remove NewGunShot\ntag @s add Fired\nexecute on passengers run tag @s remove NewBullet\n')
    t = read('extensions/knife/throw_owned')
    line = '$execute as @e[type=snowball,nbt={Owner:$(owner)},sort=nearest,limit=1] at @s run function'
    t = t.replace(line, '$gravity bridge inherit @s @e[type=snowball,nbt={Owner:$(owner)},sort=nearest,limit=1]\n' + line)
    put('extensions/knife/throw_owned', t)
    t = read('game/items/knife/throw_inner')
    t = t.replace('execute as @e[type=arrow,tag=new,tag=knife] run function',
                  'gravity bridge inherit @s @e[type=arrow,tag=new,tag=knife]\ngravity bridge inherit @s @e[type=item,tag=new,tag=knifeCosmetic]\n\nexecute as @e[type=arrow,tag=new,tag=knife] run function')
    put('game/items/knife/throw_inner', t)
    t = read('game/loops/spawnscrap')
    spawn_line = next(l for l in t.splitlines() if 'run summon item ' in l)
    command = spawn_line.split('run summon item ', 1)[1]
    command = command.replace('{Item:', '{Tags:["McmNewScrap","KeyItem"],Item:', 1)
    put('extensions/gravity/spawn_scrap', '# Runs as the selected ScrapSpawn marker; commands complete before the next entity tick.\n'
        + 'summon item ' + command + '\ngravity bridge marker @s @e[type=item,tag=McmNewScrap]\ntag @e[type=item,tag=McmNewScrap] remove McmNewScrap\n')
    put('game/loops/spawnscrap', t.replace(spawn_line, spawn_line.split('run summon item ', 1)[0] + 'run function mcm:extensions/gravity/spawn_scrap'))
    t = read('game/drop_items_on_death')
    t = t.replace('tag @e[type=item,tag=temp_drop,limit=1] remove temp_drop',
                  'execute if entity @e[type=item,tag=temp_drop,limit=1] run gravity bridge drop @s @e[type=item,tag=temp_drop,limit=1]\ntag @e[type=item,tag=temp_drop,limit=1] remove temp_drop')
    put('game/drop_items_on_death', t)
    for name in ['maps/tptospawn', 'player_leave', 'lobby/give_lobby_items']:
        text = read(name)
        if name == 'lobby/give_lobby_items':
            put(name, text.replace('clear @s', 'clear @s\ngravity bridge reset @s', 1))
        else:
            put(name, '# Clear the previous arena gravity before spawning/returning to the lobby.\ngravity bridge reset @s\n' + text)
    entries.update(changed)
    temp = pack.with_suffix('.gravity.tmp')
    with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, content in entries.items(): z.writestr(name, content)
    with zipfile.ZipFile(temp) as z:
        assert z.testzip() is None
    temp.replace(pack)
    print('Updated', len(changed), 'entries')

if __name__ == '__main__':
    apply()
