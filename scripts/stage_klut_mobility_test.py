"""Prepare only the disposable NeoForge GameTest world's datapack.

Run after klut27_mobility.py. Pass --standalone to test the standalone overlay
with no Backstabbed death objective. No installed save is written.
"""
import argparse
import klut27_mobility as m

parser=argparse.ArgumentParser()
parser.add_argument('--standalone',action='store_true')
args=parser.parse_args()
source=m.readzip(m.STAGE/'mcm.zip')
if args.standalone:
    files=m.standalone_pack(source)
    # Fixture only: use the actual updated merchant snapshot in the test arena.
    reset=source['data/klut27/function/npc_reset.mcfunction'].decode()
    engineer=[line[line.index('summon minecraft:villager'):] for line in reset.splitlines() if 'summon minecraft:villager' in line and 'Klut27Engineer' in line]
    assert len(engineer)==1
    files['data/klut27/function/npc_reset.mcfunction']=('kill @e[type=villager,tag=Klut27Engineer]\n'+engineer[0]+'\n').encode()
else:
    files=source
for name in ('load','tick'):
    files[f'data/minecraft/tags/function/{name}.json']=b'{"values":[]}'
target=m.ROOT.parent/'GravityChangerMod/gravity-changer-neoforge/run-klut/world/datapacks/mcm.zip'
target.write_bytes(m.zipbytes(files))
print('Staged isolated GameTest pack:', 'standalone' if args.standalone else 'integrated')
