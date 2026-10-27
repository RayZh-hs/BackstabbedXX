"""Regression checks for River Bank's saved geometry and playable markers."""

import json
import math
import re
import unittest
import zipfile

from test_yacht_spawns import WorldBlocks, WORLD

class RiverBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(WORLD / "datapacks/mcm.zip") as pack:
            cls.activate = pack.read("data/river_bank/function/activate.mcfunction").decode()
            cls.predicate = json.loads(pack.read("data/river_bank/predicate/arena.json"))
        cls.blocks = WorldBlocks()
        cls.markers = []
        for line in cls.activate.splitlines():
            match = re.search(r'summon marker (\S+) (\S+) (\S+) .*Tags:\[(.*?)\]', line)
            if match:
                positioned = re.search(r'execute positioned ([\d.]+) ([\d.]+) ([\d.]+)', line)
                origin = tuple(map(float, positioned.groups())) if positioned else (0, 0, 0)
                point = tuple(base + float(value[1:] or 0) if value.startswith("~") else float(value)
                              for base, value in zip(origin, match.group(1, 2, 3)))
                cls.markers.append((point, set(re.findall(r'"([^"]+)"', match[4]))))

    def inside(self, point):
        for term in self.predicate["terms"]:
            location = term["predicate"]["location"]
            if location["dimension"] != "minecraft:overworld":
                continue
            if all(location["position"][axis]["min"] <= value <= location["position"][axis]["max"]
                   for axis, value in zip("xyz", point)):
                return True
        return False

    def test_spawn_and_scrap_counts_are_distinct(self):
        players = [p for p, tags in self.markers if "PlayerSpawn" in tags]
        scraps = [p for p, tags in self.markers if "ScrapSpawn" in tags]
        market = [p for p, tags in self.markers if "RiverMarketScrap" in tags]
        self.assertEqual(len(players), 32)
        self.assertEqual(len(scraps), 38)
        self.assertEqual(len(set(scraps)), 38)
        self.assertEqual(len(market), 6)
        self.assertTrue(set(players) <= set(scraps))
        self.assertFalse(set(players) & set(market))

    def test_all_points_are_inside_and_stand_on_clear_saved_ground(self):
        for point, tags in self.markers:
            if "ScrapSpawn" not in tags:
                continue
            with self.subTest(point=point):
                self.assertTrue(self.inside(point))
                x, y, z = map(math.floor, point)
                self.assertEqual(self.blocks.block(x, y, z), "air")
                self.assertEqual(self.blocks.block(x, y + 1, z), "air")
                self.assertNotIn(self.blocks.block(x, y - 1, z),
                                 {"air", "water", "lava", "barrier", "fire", "cactus", "magma_block"})

    def test_hill_and_southern_isolated_regions_are_excluded(self):
        for point in [(12500.5, 40, 12370.5), (12529.5, 16, 12535.5),
                      (12469.5, 10, 12549.5), (12407.5, 19, 12549.5)]:
            with self.subTest(point=point):
                self.assertFalse(self.inside(point))
        for point in [(12485.5, 20, 12380.5), (12505.5, 13, 12514.5),
                      (12469.5, 11, 12537.5), (12407.5, 24, 12537.5)]:
            with self.subTest(point=point):
                self.assertTrue(self.inside(point))

    def test_market_points_cover_both_stall_clusters(self):
        market = [p for p, tags in self.markers if "RiverMarketScrap" in tags]
        self.assertEqual(sum(12358 <= x <= 12402 and 12410 <= z <= 12468 for x, y, z in market), 3)
        self.assertEqual(sum(12410 <= x <= 12434 and 12432 <= z <= 12468 for x, y, z in market), 3)
        for point, tags in self.markers:
            if "RiverMarketScrap" in tags:
                self.assertTrue({"MapEntity", "RiverBankRuntime", "ScrapSpawn"} <= tags)
                self.assertNotIn("PlayerSpawn", tags)

    def test_retained_internal_barriers_and_new_hill_screen(self):
        for point in [(12506, 9, 12501), (12491, 10, 12515)]:
            self.assertEqual(self.blocks.block(*point), "barrier")
        # The new north-east mountain exclusion must have a physical high screen.
        self.assertEqual(self.blocks.block(12491, 100, 12370), "barrier")


if __name__ == "__main__":
    unittest.main()
