"""Editor boundaries must not treat queued lobby players as escaped players."""
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'arena-editor'))
import editor

class LobbyBoundaryGate(unittest.TestCase):
    def test_editor_exports_only_post_entry_boundary_checks(self):
        state={'objects':[{'kind':'return','x':0,'y':1,'z':0,'yaw':0,'pitch':0}],
               'boundary_enabled':1,'outside_action':'kill'}
        files=editor.exported_files(state,{'arena':'fixture','map_id':20,'tag':'Fixture'})
        body=files['data/bbe_arena/function/fixture/tick.mcfunction'].decode()
        self.assertIn('execute unless score $gamestate CmdData matches 1 run return 0',body)
        self.assertNotIn('matches 0..1',body)

    def test_installed_generated_boundaries_do_not_run_in_lobby(self):
        with ZipFile(ROOT/'.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/datapacks/mcm.zip')as z:
            found=[]
            for name in z.namelist():
                if name.startswith('data/bbe_arena/function/')and name.endswith('/tick.mcfunction'):
                    body=z.read(name).decode()
                    if 'run function bbe_arena:' not in body:continue
                    found.append(name)
                    with self.subTest(function=name):
                        self.assertIn('execute unless score $gamestate CmdData matches 1 run return 0',body)
                        self.assertIn('tag=queued,tag=!spectating,gamemode=!spectator',body)
                        self.assertIn('unless score @s dead matches 1..',body)
            self.assertGreaterEqual(len(found),3)

if __name__=='__main__':unittest.main()
