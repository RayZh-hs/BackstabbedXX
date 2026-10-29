"""The saved station has usable spawn routes on both levels and in trains."""
from collections import Counter, deque
import json
import math
from pathlib import Path
import re
import unittest
from zipfile import ZipFile

from world_geometry import World, in_region

ROOT = Path(__file__).resolve().parents[1]
SAVE = ROOT / ".minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies"
CLEAR = {"minecraft:air", "minecraft:cave_air", "minecraft:light"}


class StationSpawns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = World(SAVE)
        cls.report = json.loads((ROOT / "docs/arenas/subway_station_spawn_update.json").read_text())
        with ZipFile(SAVE / "datapacks/mcm.zip") as z:
            cls.activate = z.read("data/subway_station/function/activate.mcfunction").decode()
            cls.arena = json.loads(z.read("data/subway_station/predicate/arena.json"))

    def test_actual_marker_distribution(self):
        actual = [tuple(map(float, m)) for m in re.findall(
            r'summon marker (\S+) (\S+) (\S+) \{Tags:\["PlayerSpawn","ScrapSpawn"', self.activate)]
        expected = [tuple(row["position"]) for row in self.report["spawns"]]
        self.assertEqual(actual, expected)
        self.assertEqual(len(set(actual)), 24)
        self.assertEqual(Counter(row["area"] for row in self.report["spawns"]),
                         {"lower_platform": 8, "upper_concourse": 8, "train_interior": 8})

    def test_saved_collision_and_membership(self):
        for row in self.report["spawns"]:
            point = row["position"]
            with self.subTest(point=point, area=row["area"]):
                x, y, z = (math.floor(v) for v in point)
                self.assertTrue(in_region(self.arena, point))
                if row["area"] == "train_interior":
                    floor = self.world.block(x, y, z)
                    self.assertEqual(floor["Name"], "minecraft:iron_trapdoor")
                    self.assertEqual(floor["Properties"]["half"], "bottom")
                    self.assertEqual(floor["Properties"]["open"], "false")
                    self.assertEqual(point[1], y + 3 / 16)
                    low = y + 1
                else:
                    floor = self.world.block(x, y - 1, z)
                    self.assertIn(floor["Name"], {"minecraft:cyan_terracotta", "minecraft:granite",
                                                "minecraft:polished_granite", "minecraft:coarse_dirt"})
                    low = y
                for cy in range(low, math.ceil(point[1] + 1.8)):
                    self.assertIn(self.world.block(x, cy, z)["Name"], CLEAR)

    def test_upper_points_have_connected_walkways(self):
        def walkable(x, z):
            return (self.world.block(x, -49, z)["Name"] in
                    {"minecraft:cyan_terracotta", "minecraft:smooth_stone"}
                    and all(self.world.block(x, y, z)["Name"] in CLEAR for y in (-48, -47)))

        for row in self.report["spawns"]:
            if row["area"] != "upper_concourse":
                continue
            x, _, z = map(math.floor, row["position"])
            seen, queue = {(x, z)}, deque([(x, z)])
            while queue and len(seen) < 100:
                a, b = queue.popleft()
                for q in [(a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)]:
                    if q not in seen and walkable(*q):
                        seen.add(q)
                        queue.append(q)
            self.assertGreaterEqual(len(seen), 100, row)

    def test_train_points_have_clear_aisles(self):
        for row in self.report["spawns"]:
            if row["area"] != "train_interior":
                continue
            x, _, z = map(math.floor, row["position"])
            for dz in [-2, -1, 1, 2]:
                self.assertIn(self.world.block(x, -57, z + dz)["Name"], CLEAR)
                self.assertIn(self.world.block(x, -56, z + dz)["Name"], CLEAR)
                floor = self.world.block(x, -58, z + dz)
                self.assertEqual(floor["Name"], "minecraft:iron_trapdoor")
                self.assertEqual(floor["Properties"]["open"], "false")
