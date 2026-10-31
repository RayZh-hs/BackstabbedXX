"""KLUT mobility installation contracts; behavior is also exercised by GameTest."""
import json
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT/'.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/datapacks/mcm.zip'

class MobilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(PACK) as z: cls.files={n:z.read(n) for n in z.namelist()}
    def text(self,path):return self.files['data/'+path].decode('utf-8')
    def test_boots_equipment_and_thresholds(self):
        self.assertIn('armor.feet',self.text('klut27/function/mobility/player.mcfunction'))
        for name,value in [('low',{'max':-6}),('high',{'min':10})]:
            predicate=json.loads(self.text('klut27/predicate/boots_'+name+'.json'))
            self.assertEqual(predicate['predicate']['position']['y'],value)
        for direction in ('up','down'):
            self.assertIn('kb_cd 300',self.text('klut27/function/mobility/'+direction+'.mcfunction'))
    def test_hooks_retired_and_cleanup_not_guarded_by_old_hook_tag(self):
        self.assertNotIn('with gravity_changer:grappling_hook',self.text('klut27/function/give_hook.mcfunction'))
        self.assertNotIn('klut27:give_hook',self.text('mcm/function/maps/start.mcfunction'))
        cleanup=self.text('klut27/function/cleanup_player.mcfunction')
        self.assertNotIn('execute unless entity @s[tag=Klut27Hook] run return',cleanup)
        self.assertIn('klut27:mobility/cleanup',cleanup)
    def test_engineer_and_boots_trade(self):
        trade=self.text('klut27/function/mobility/merchant.mcfunction')
        self.assertIn('Engineer',trade);self.assertIn('minecraft:leather_boots',trade)
        self.assertIn('minecraft:dyed_color',trade);self.assertIn('klut27_boots',trade)
        self.assertNotIn('gravity_changer:grappling_hook',trade)
        snapshots=0
        for name,raw in self.files.items():
            if name.startswith('data/klut27/') and name.endswith('.mcfunction'):
                for line in raw.decode().splitlines():
                    if 'Klut27Engineer' in line and 'Offers:' in line:
                        snapshots+=1
                        self.assertIn('Engineer',line)
                        self.assertIn('klut27_boots',line)
                        self.assertNotIn('gravity_changer:grappling_hook',line)
        self.assertGreaterEqual(snapshots,3)
    def test_player_commands_use_native_rotation(self):
        for name in ('up','down','release'):
            body=self.text('klut27/function/mobility/'+name+'.mcfunction')
            self.assertIn('gravity set_base_direction',body)
            self.assertNotIn('gravity bridge',body)
    def test_elevator_hud_and_reverse_clearance(self):
        text=self.text('klut27/function/mobility/hud.mcfunction')
        self.assertIn('JUMP to go UP',text);self.assertIn('SNEAK to go DOWN',text)
        render=self.text('klut27/function/mobility/hud_render.mcfunction')
        self.assertIn('"yellow"',render);self.assertIn('"aqua"',render)
        landing=self.text('klut27_elevators/function/check_landing.mcfunction')
        self.assertIn('~ ~-1 ~',landing);self.assertIn('~ ~-2 ~',landing)
    def test_reviewed_overlay_matches_installed(self):
        source=ROOT/'klut27-mobility/datapack'
        self.assertTrue(source.is_dir())
        for p in source.rglob('*'):
            if p.is_file():self.assertEqual(p.read_bytes(),self.files[p.relative_to(source).as_posix()])

if __name__=='__main__':unittest.main()
