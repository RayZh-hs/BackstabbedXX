"""KLUT gravity-controller installation contracts; behavior is also exercised by GameTest."""
import zipfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT/'.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/datapacks/mcm.zip'
LEGACY = ('data/klut27/function/mobility/up.mcfunction',
          'data/klut27/function/mobility/down.mcfunction',
          'data/klut27/function/mobility/hud_boots.mcfunction',
          'data/klut27/function/mobility/hud_boots_text.mcfunction',
          'data/klut27/predicate/boots_low.json',
          'data/klut27/predicate/boots_high.json')


class MobilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(PACK) as z: cls.files={n:z.read(n) for n in z.namelist()}
    def text(self,path):return self.files['data/'+path].decode('utf-8')
    def test_controller_is_a_right_click_item(self):
        player=self.text('klut27/function/mobility/player.mcfunction')
        self.assertIn('carrot_on_a_stick[custom_data~{klut27_gravity_controller:1b}]',player)
        self.assertIn('items entity @s weapon.*',player)
        self.assertIn('klut27:mobility/controller',player)
        self.assertNotIn('armor.feet',player)
        self.assertIn('scoreboard objectives add kc_use minecraft.used:minecraft.carrot_on_a_stick',
                      self.text('klut27/function/mobility/load.mcfunction'))
    def test_inversion_and_cooldown(self):
        controller=self.text('klut27/function/mobility/controller.mcfunction')
        self.assertIn('gravity set_relative_base_direction up @s',controller)
        self.assertIn('scoreboard players set @s kc_cd 300',controller)
        self.assertNotIn('gravity bridge',controller)
        player=self.text('klut27/function/mobility/player.mcfunction')
        self.assertIn('if score @s kc_cd matches 0',player)
        self.assertIn('scoreboard players set @s kc_use 0',player)
    def test_boots_members_are_retired(self):
        for name in LEGACY:self.assertNotIn(name,self.files,name)
        self.assertNotIn('klut27_boots',self.text('klut27/function/mobility/merchant.mcfunction'))
    def test_engineer_and_controller_trade(self):
        trade=self.text('klut27/function/mobility/merchant.mcfunction')
        self.assertIn('Engineer',trade);self.assertIn('minecraft:carrot_on_a_stick',trade)
        self.assertIn('minecraft:repeating_command_block',trade);self.assertIn('klut27_gravity_controller',trade)
        self.assertIn('重力控制器',trade)
        self.assertNotIn('minecraft:leather_boots',trade)
        self.assertNotIn('gravity_changer:grappling_hook',trade)
        snapshots=0
        for name,raw in self.files.items():
            if name.startswith('data/klut27/') and name.endswith('.mcfunction'):
                for line in raw.decode().splitlines():
                    if 'Klut27Engineer' in line and 'Offers:' in line:
                        snapshots+=1
                        self.assertIn('Engineer',line)
                        self.assertIn('klut27_gravity_controller',line)
                        self.assertNotIn('klut27_boots',line)
                        self.assertNotIn('gravity_changer:grappling_hook',line)
        self.assertGreaterEqual(snapshots,3)
    def test_hooks_retired_and_cleanup_not_guarded_by_old_hook_tag(self):
        self.assertNotIn('with gravity_changer:grappling_hook',self.text('klut27/function/give_hook.mcfunction'))
        self.assertNotIn('klut27:give_hook',self.text('mcm/function/maps/start.mcfunction'))
        cleanup=self.text('klut27/function/cleanup_player.mcfunction')
        self.assertNotIn('execute unless entity @s[tag=Klut27Hook] run return',cleanup)
        self.assertIn('klut27:mobility/cleanup',cleanup)
    def test_lifecycle_restores_down(self):
        release=self.text('klut27/function/mobility/release.mcfunction')
        self.assertIn('gravity set_base_direction down @s',release)
        self.assertNotIn('gravity bridge',release)
        cleanup=self.text('klut27/function/mobility/cleanup.mcfunction')
        self.assertIn('scoreboard players set @s kc_cd 0',cleanup)
    def test_elevator_hud_shows_the_controller_cooldown(self):
        hud=self.text('klut27/function/mobility/hud.mcfunction')
        self.assertIn('JUMP to go UP',hud);self.assertIn('SNEAK to go DOWN',hud)
        self.assertIn('hud_ctrl',hud)
        text=self.text('klut27/function/mobility/hud_ctrl_text.mcfunction')
        self.assertIn('重力控制器 | $(bar) | $(sec).$(dec)s',text)
        render=self.text('klut27/function/mobility/hud_render.mcfunction')
        self.assertIn('"yellow"',render);self.assertIn('"aqua"',render)
        bar=self.text('klut27/function/mobility/hud_ctrl.mcfunction')
        self.assertIn('matches 271..300',bar)
        self.assertIn('■■■■■■■■■■',bar)
        landing=self.text('klut27_elevators/function/check_landing.mcfunction')
        self.assertIn('~ ~-1 ~',landing);self.assertIn('~ ~-2 ~',landing)
    def test_reviewed_overlay_matches_installed(self):
        source=ROOT/'klut27-mobility/datapack'
        self.assertTrue(source.is_dir())
        for p in source.rglob('*'):
            if p.is_file():self.assertEqual(p.read_bytes(),self.files[p.relative_to(source).as_posix()])


if __name__=='__main__':unittest.main()
