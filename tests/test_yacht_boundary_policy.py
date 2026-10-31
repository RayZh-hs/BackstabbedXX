"""Three edited arenas share Yacht's post-entry grace/active boundary policy."""
import sys,unittest
from pathlib import Path
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'arena-editor'))
import editor
PACK=ROOT/'.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/datapacks/mcm.zip'
ARENAS={'klut27':('Klut27',20),'middle_ages':('MiddleAges',22),'underwater_base':('UnderwaterBase',19)}

class YachtBoundaryPolicy(unittest.TestCase):
    def check_policy(self,files,ns,tag):
        prefix=f'data/bbe_arena/function/{ns}/'
        kill=files[prefix+'kill.mcfunction'].decode()
        self.assertIn('unless score $gamestate CmdData matches 1 run return 0',kill)
        self.assertIn(f'if score $graceperiod CmdData matches 1.. run return run function bbe_arena:{ns}/tp',kill)
        self.assertIn('if score $graceperiod CmdData matches ..0 run function mcm:game/playerdeath',kill)
        tp=files[prefix+'tp.mcfunction'].decode()
        self.assertIn(f'tag=PlayerSpawn,tag={tag}Runtime,predicate=bbe_arena:{ns}/arena,sort=nearest,limit=1',tp)
        self.assertIn('execute in minecraft:overworld run tp @s ',tp)
        self.assertIn('gravity bridge reset @s',tp)
        if ns=='klut27':self.assertIn('function klut27:mobility/release',tp)

    def test_installed_policies(self):
        with ZipFile(PACK)as z:files={n:z.read(n)for n in z.namelist()}
        for ns,(tag,_)in ARENAS.items():
            with self.subTest(arena=ns):self.check_policy(files,ns,tag)

    def test_editor_preserves_policy_when_reexporting(self):
        state={'objects':[{'kind':'return','x':1,'y':2,'z':3,'yaw':0,'pitch':0}], 'boundary_enabled':1,'outside_action':'kill'}
        for ns,(tag,id)in ARENAS.items():
            with self.subTest(arena=ns):self.check_policy(editor.exported_files(state,{'arena':ns,'tag':tag,'map_id':id}),ns,tag)

    def test_klut_legacy_path_does_not_bypass_grace(self):
        with ZipFile(PACK)as z:fall=z.read('data/klut27/function/fall.mcfunction').decode()
        guard='execute if score $graceperiod CmdData matches 1.. run return run function bbe_arena:klut27/tp'
        self.assertIn(guard,fall)
        self.assertLess(fall.index(guard),fall.index('tellraw'))
        self.assertIn('unless score $gamestate CmdData matches 1 run return 0',fall)

if __name__=='__main__':unittest.main()
