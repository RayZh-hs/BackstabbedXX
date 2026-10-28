"""Modernize Supercam19's Simple Elevators for KLUT-27 / Java 1.21.4.

The original archive is never modified. Functions use modern container locks,
safe landing checks and per-player searches with rotation preserved.
"""
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT.parent / 'CandidateMaps/08_KLUT27/Klut-27'
STANDALONE = Path('C:/Users/dyf08/AppData/Roaming/PrismLauncher/instances/Backstabbed++/.minecraft/saves/KLUT-27 - 1.21.4 Fixed')
LOCK = 'minecraft:white_shulker_box{lock:{components:{"minecraft:custom_name":"\\\"5567353566-5331\\\""}}}'


def pack_files(namespace='elevators', integrated=False):
    files = {}
    def put(path, value):
        files[path] = (value.strip() + '\n').encode()
    def fn(name, value):
        put(f'data/{namespace}/function/{name}.mcfunction', value.replace('elevators:', namespace + ':'))
    put('pack.mcmeta', json.dumps({'pack': {'pack_format': 61, 'description': 'KLUT-27: Simple Elevators by Supercam19, migrated to 1.21.4'}}))
    fn('load', '''scoreboard objectives add e.jumped minecraft.custom:minecraft.jump
scoreboard objectives add e.sneakedTime minecraft.custom:minecraft.sneak_time
scoreboard objectives add e.steps dummy
scoreboard objectives add e.cooldown dummy
kill @e[type=marker,tag=klut.e.search]
gamerule doFireTick false''')
    gate = ' if predicate klut27:arena' if integrated else ''
    selector = '@a[tag=queued,tag=!spectating,gamemode=!spectator]' if integrated else '@a[gamemode=!spectator]'
    if integrated:
        path=f'data/{namespace}/function/load.mcfunction'
        files[path]+=b'scoreboard objectives add klut27_gravity dummy\n'
        gate+=' unless score @s dead matches 1.. if score @s klut27_gravity matches 1'
    before=f'execute as {selector} store result score @s klut27_gravity run gravity bridge is_down @s\n' if integrated else ''
    fn('tick', before+f'''scoreboard players add {selector} e.cooldown 0
execute as {selector} if score @s e.cooldown matches 1.. run scoreboard players remove @s e.cooldown 1
execute as {selector} at @s{gate} if score @s e.cooldown matches ..0 if score @s e.jumped matches 1.. if block ~ ~-1 ~ {LOCK} run function elevators:find_upper
execute as {selector} at @s{gate} if score @s e.cooldown matches ..0 if score @s e.sneakedTime matches 1.. if block ~ ~-1 ~ {LOCK} run function elevators:find_lower
scoreboard players set {selector} e.jumped 0
scoreboard players set {selector} e.sneakedTime 0''')
    for direction, step in [('upper',1),('lower',-1)]:
        fn('find_' + direction, f'''kill @e[type=marker,tag=klut.e.search]
execute align xyz positioned ~0.5 ~-1 ~0.5 run summon marker ~ ~ ~ {{Tags:["klut.e.search"]}}
scoreboard players set @e[type=marker,tag=klut.e.search] e.steps 120
execute as @e[type=marker,tag=klut.e.search,limit=1] at @s run function elevators:search_{direction}
execute if entity @e[type=marker,tag=klut.e.found] at @e[type=marker,tag=klut.e.found,limit=1] run tp @s ~ ~1 ~
execute if entity @e[type=marker,tag=klut.e.found] run scoreboard players set @s e.cooldown 30
kill @e[type=marker,tag=klut.e.search]''')
        fn('search_' + direction, f'''tp @s ~ ~{step} ~
execute at @s if block ~ ~ ~ {LOCK} run function elevators:check_landing
scoreboard players remove @s e.steps 1
execute if score @s e.steps matches 1.. unless entity @s[tag=klut.e.found] at @s run function elevators:search_{direction}''')
    fn('check_landing', '''execute unless block ~ ~1 ~ #elevators:clear run return 0
execute if block ~ ~2 ~ #elevators:clear run tag @s add klut.e.found
execute if block ~ ~2 ~ #minecraft:trapdoors[half=top,open=false,waterlogged=false] run tag @s add klut.e.found''')
    put(f'data/{namespace}/tags/block/clear.json', json.dumps({'values':['minecraft:air','minecraft:cave_air','minecraft:void_air','#minecraft:wall_signs']}))
    item = 'minecraft:white_shulker_box[minecraft:block_entity_data={id:"minecraft:shulker_box",lock:{components:{"minecraft:custom_name":"\\\"5567353566-5331\\\""}}},minecraft:custom_name=\'{"text":"Elevator","italic":false,"color":"white"}\']'
    fn('crafted_elevator', f'''recipe take @s elevators:elevator
advancement revoke @s only elevators:elevator_give
give @s {item}
clear @s minecraft:knowledge_book 1''')
    put(f'data/{namespace}/recipe/elevator.json', json.dumps({'type':'minecraft:crafting_shaped','pattern':['###','#E#','#R#'],'key':{'#':'minecraft:quartz_block','E':'minecraft:ender_pearl','R':'minecraft:redstone_block'},'result':{'id':'minecraft:knowledge_book','count':1}}))
    put(f'data/{namespace}/advancement/elevator_give.json', json.dumps({'criteria':{'Unlocked':{'trigger':'minecraft:recipe_unlocked','conditions':{'recipe':namespace+':elevator'}}},'rewards':{'function':namespace+':crafted_elevator'}}))
    if not integrated:
        for kind in ('load','tick'):
            put(f'data/minecraft/tags/function/{kind}.json', json.dumps({'values':[namespace+':'+kind]}))
    return files


def modernize_empty_bukkit(world):
    """Keep the original empty Bukkit wrapper, with target-version metadata."""
    metadata_path = world / 'datapacks/bukkit/pack.mcmeta'
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text())
        metadata['pack']['pack_format'] = 61
        metadata_path.write_text(json.dumps(metadata, indent=2) + '\n')


def install_standalone():
    import nbtlib as nbt
    if STANDALONE.exists():
        raise FileExistsError(STANDALONE)
    shutil.copytree(SOURCE, STANDALONE)
    old = STANDALONE / 'datapacks/simpleelevators-v1-1.zip'
    old.unlink()  # Original remains in the untouched source and verified backup.
    with zipfile.ZipFile(STANDALONE / 'datapacks/simpleelevators-1.21.4.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, value in pack_files().items():
            z.writestr(name,value)
    # Bukkit's empty wrapper should not retain an outdated format badge.
    modernize_empty_bukkit(STANDALONE)
    level = nbt.load(STANDALONE / 'level.dat')
    data = level['Data']
    data['GameRules']['doFireTick'] = nbt.String('false')
    data['LevelName'] = nbt.String('KLUT-27 - 1.21.4 Fixed')
    enabled = data['DataPacks']['Enabled']
    data['DataPacks']['Enabled'] = nbt.List[nbt.String]([s for s in enabled if str(s) != 'file/simpleelevators-v1-1.zip'] + ['file/simpleelevators-1.21.4.zip'])
    level.save(STANDALONE / 'level.dat')
    print(STANDALONE)


if __name__ == '__main__':
    install_standalone()
