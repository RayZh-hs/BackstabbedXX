"""Validate player spawns against the actual saved Yacht blocks, without mods."""

from collections import deque
from functools import lru_cache
import math
from pathlib import Path
import re
import struct
import sys
import unittest
import zipfile
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from nbt import Reader


WORLD = Path(__file__).resolve().parent.parent / ".minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies"


def payload(reader, kind):
    """Decode the NBT needed to inspect Anvil block-state palettes."""
    if kind in (1, 2, 3, 4, 5, 6):
        return reader.number({1: "b", 2: "h", 3: "i", 4: "q", 5: "f", 6: "d"}[kind])
    if kind == 8:
        return reader.string().decode("utf-8", errors="replace")
    if kind == 9:
        subtype, count = reader.number("B"), reader.number("i")
        return [payload(reader, subtype) for _ in range(count)]
    if kind == 10:
        result = {}
        while subtype := reader.number("B"):
            name = reader.string().decode("utf-8", errors="replace")
            result[name] = payload(reader, subtype)
        return result
    if kind in (7, 11, 12):
        count = reader.number("i")
        fmt = {7: "b", 11: "i", 12: "q"}[kind]
        return struct.unpack(">" + str(count) + fmt, reader.read(count * struct.calcsize(">" + fmt)))
    raise ValueError(f"Unexpected NBT type: {kind}")


class WorldBlocks:
    @lru_cache(None)
    def region(self, x, z):
        return (WORLD / f"region/r.{x}.{z}.mca").read_bytes()

    @lru_cache(None)
    def chunk(self, x, z):
        data = self.region(x // 32, z // 32)
        index = (z % 32) * 32 + x % 32
        offset = int.from_bytes(data[index * 4:index * 4 + 3], "big") * 4096
        if not offset:
            return {}
        length = struct.unpack_from(">I", data, offset)[0]
        if data[offset + 4] != 2:
            raise ValueError("Expected a zlib-compressed Anvil chunk")
        reader = Reader(zlib.decompress(data[offset + 5:offset + 4 + length]))
        if reader.number("B") != 10:
            raise ValueError("Expected a compound chunk root")
        reader.string()
        return {section["Y"]: section.get("block_states", {}) for section in payload(reader, 10)["sections"]}

    @lru_cache(None)
    def block(self, x, y, z):
        states = self.chunk(x // 16, z // 16).get(y // 16, {})
        palette = states.get("palette", [{"Name": "minecraft:air"}])
        index = 0
        if len(palette) > 1:
            bits = max(4, (len(palette) - 1).bit_length())
            per_long = 64 // bits
            position = (y % 16) * 256 + (z % 16) * 16 + x % 16
            index = (states["data"][position // per_long] >> ((position % per_long) * bits)) & ((1 << bits) - 1)
        return palette[index]["Name"].removeprefix("minecraft:")


class YachtSpawnTests(unittest.TestCase):
    def test_player_spawns_stand_on_the_connected_ship_with_headroom(self):
        with zipfile.ZipFile(WORLD / "datapacks/mcm.zip") as archive:
            source = archive.read("data/yacht/function/activate.mcfunction").decode()
        spawns = [
            tuple(math.floor(float(value)) for value in match)
            for match in re.findall(r'^summon marker ([\d.]+) ([\d.]+) ([\d.]+).*"PlayerSpawn"', source, re.M)
        ]
        self.assertGreaterEqual(len(spawns), 16)
        self.assertEqual(len(spawns), len(set(spawns)))
        blocks = WorldBlocks()
        # Flood the built ship from a known hull block. Natural island material,
        # ocean, and arena barriers cannot connect an island to the hull.
        excluded = {
            "air", "cave_air", "void_air", "water", "lava", "barrier", "light",
            "stone", "dirt", "grass_block", "sand", "sandstone", "gravel",
            "seagrass", "tall_seagrass", "kelp", "bedrock",
        }
        anchor = (16468, 5, 16482)
        self.assertEqual(blocks.block(*anchor), "light_gray_concrete")
        ship = {anchor}
        pending = deque([anchor])
        while pending:
            x, y, z = pending.popleft()
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                point = (x + dx, y + dy, z + dz)
                px, py, pz = point
                if point in ship or not (16410 <= px <= 16530 and 4 <= py <= 60 and 16448 <= pz <= 16520):
                    continue
                if blocks.block(*point) not in excluded:
                    ship.add(point)
                    pending.append(point)
        for x, y, z in spawns:
            with self.subTest(spawn=(x, y, z)):
                self.assertIn((x, y - 1, z), ship, "Spawn is disconnected from the ship")
                self.assertEqual(blocks.block(x, y, z), "air", "Spawn feet are obstructed")
                self.assertEqual(blocks.block(x, y + 1, z), "air", "Spawn head is obstructed")


if __name__ == "__main__":
    unittest.main()
