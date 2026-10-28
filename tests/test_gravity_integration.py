"""Datapack bridge contracts; physical behavior is covered by NeoForge GameTests."""
from pathlib import Path
import unittest
import zipfile

PACK = next((Path(__file__).resolve().parents[1] / '.minecraft/saves').glob('*/datapacks/mcm.zip'))

class GravityIntegration(unittest.TestCase):
    def text(self, path):
        with zipfile.ZipFile(PACK) as z:
            return z.read('data/mcm/function/' + path + '.mcfunction').decode('utf8')

    def test_gun_bridge_preserves_gameplay(self):
        t = self.text('extensions/gun/try_fire')
        self.assertIn('gravity bridge fire', t)
        self.assertIn('NoGravity:1b', t)
        self.assertIn('netherite_scrap 1', t)
        self.assertIn('~ ~-3', t)
        self.assertNotIn('positioned ~ ~1.5 ~', t)
        self.assertNotIn('Motion set from', self.text('extensions/gun/setspeed'))

    def test_knife_transfer_keeps_owner_epoch(self):
        self.assertIn('gravity bridge inherit @s', self.text('extensions/knife/throw_owned'))
        t = self.text('game/items/knife/throw_inner')
        self.assertIn('gravity bridge inherit @s', t)
        self.assertIn('Owner set from entity @s Owner', t)
        self.assertIn('extensions/knife/track_entity', t)
        self.assertIn('$(owner)', self.text('game/items/knife/kill_owned_entity'))

    def test_scrap_config_at_spawn_not_nearest_player(self):
        self.assertIn('extensions/gravity/spawn_scrap', self.text('game/loops/spawnscrap'))
        t = self.text('extensions/gravity/spawn_scrap')
        self.assertIn('gravity bridge marker @s', t)
        self.assertNotIn('@p', t)
        self.assertIn('count:1', t)

    def test_lifecycle_reset(self):
        for path in ['maps/tptospawn', 'player_leave', 'lobby/give_lobby_items']:
            self.assertIn('gravity bridge reset @s', self.text(path))

if __name__ == '__main__':
    unittest.main()
