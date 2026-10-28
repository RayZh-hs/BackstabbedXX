"""Check the complete voting-poster model, texture, and atlas dependency graph."""

import json
import math
from pathlib import Path
import re
import struct
import unittest
import zipfile


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / ".minecraft/resourcepacks/backstabbed-resource/assets"
DATAPACK = ROOT / ".minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/datapacks/mcm.zip"


def location(value):
    return tuple(value.split(":", 1)) if ":" in value else ("minecraft", value)


def resource(kind, value, suffix=".json"):
    namespace, path = location(value)
    return ASSETS / namespace / kind / (path + suffix)


class VotingPosterTests(unittest.TestCase):
    def test_poster_faces_clear_the_saved_voting_booth_wall(self):
        from test_yacht_spawns import WorldBlocks

        with zipfile.ZipFile(DATAPACK) as archive:
            commands = archive.read("data/mcm/function/lobby/voting/map_position_id.mcfunction").decode()
            slots = archive.read("data/mcm/function/lobby/voting/set_maps.mcfunction").decode()
        booths = [tuple(map(float, match)) for match in re.findall(
            r'execute positioned ([\d.]+) ([\d.]+) ([\d.]+) as @e\[type=marker,.*run function mcm:lobby/voting/map_position_id', slots)]
        self.assertEqual(len(booths), 7)
        blocks = WorldBlocks()
        checked = set()
        for line in commands.splitlines():
            if line.lstrip().startswith("#") or "run summon item_display" not in line:
                continue
            poster = re.search(r'(?:"(?:minecraft:)?item_model"|item_model):"([^"]+)"', line)[1]
            offsets = re.search(r'positioned ~([\d.-]*) ~([\d.-]*) ~([\d.-]*) run summon', line)
            offset_x = float(offsets[1] or 0)
            definition = json.loads(resource("items", poster).read_text())
            model = json.loads(resource("models", definition["model"]["model"]).read_text())
            # Check the actual render contract before projecting model vertices:
            # fixed context, 2x scale, yaw 90, no pitch or model-space offset.
            self.assertRegex(line, r'item_display:(?:"fixed"|fixed)')
            rotation = re.search(r'Rotation:\[([^]]+)\]', line)[1]
            self.assertEqual([float(v.rstrip("f")) for v in rotation.split(",")], [90, 0])
            matrix = re.search(r'transformation:\[([^]]+)\]', line)[1]
            self.assertEqual([float(v.strip().rstrip("f")) for v in matrix.split(",")],
                             [2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1])
            fixed = model.get("display", {}).get("fixed", {})
            self.assertEqual(fixed.get("rotation", [0, 0, 0]), [0, 0, 0])
            self.assertEqual(fixed.get("translation", [0, 0, 0]), [0, 0, 0])
            self.assertEqual(fixed.get("scale", [1, 1, 1]), [1, 1, 1])
            targets = [booth for booth in booths if (booth[0] == 27) == ("matches -1 " in line)]
            for booth_x, booth_y, booth_z in targets:
                for element in model["elements"]:
                    self.assertIn("north", element["faces"])
                    self.assertEqual(element["from"][2], element["to"][2], "Expected a flat poster")
                    # Item models are centred at 8/16. Scaling by two and
                    # rotating onto the west wall turns model Z into world X.
                    face_x = booth_x + offset_x + (element["from"][2] / 16 - .5) * 2
                    with self.subTest(poster=poster, booth_z=booth_z, face_x=face_x):
                        self.assertAlmostEqual(face_x, booth_x - .01)
                        self.assertEqual(blocks.block(math.floor(face_x), int(booth_y + 1), int(booth_z + 1)), "air")
                        self.assertEqual(blocks.block(int(booth_x), int(booth_y + 1), int(booth_z + 1)), "light_gray_terracotta")
            checked.add(poster)
        self.assertEqual(len(checked), 21)

    def test_all_voting_posters_have_models_and_stitched_textures(self):
        with zipfile.ZipFile(DATAPACK) as archive:
            commands = archive.read("data/mcm/function/lobby/voting/map_position_id.mcfunction").decode()
        commands = "\n".join(line for line in commands.splitlines() if not line.lstrip().startswith("#"))
        posters = re.findall(r'(?:"(?:minecraft:)?item_model"|item_model):"([^"]+:posters/[^"]+)"', commands)
        self.assertTrue(posters)
        self.assertTrue({f"{name}:posters/{name}" for name in ("panda_village", "river_bank", "yacht", "subway_station", "meridian_base", "bagger_288", "underwater_base", "klut27")} <= set(posters))
        atlas = json.loads((ASSETS / "minecraft/atlases/blocks.json").read_text())["sources"]

        def stitched(texture):
            namespace, path = location(texture)
            for source in atlas:
                kind = source["type"].split(":")[-1]
                if kind == "single" and location(source.get("sprite", source["resource"])) == (namespace, path):
                    return True
                if kind == "directory":
                    ns, directory = location(source["source"])
                    if ns == namespace and path.startswith(source["prefix"]):
                        relative = path[len(source["prefix"]):]
                        if resource("textures", f"{ns}:{directory}/{relative}", ".png").is_file():
                            return True
            return False

        def check_model(name, seen):
            self.assertNotIn(name, seen, f"Cyclic model inheritance: {name}")
            path = resource("models", name)
            self.assertTrue(path.is_file(), f"Missing model: {name}")
            model = json.loads(path.read_text())
            if "parent" in model:
                check_model(model["parent"], seen | {name})
            for texture in model.get("textures", {}).values():
                if texture.startswith("#") or location(texture)[1].startswith("block/"):
                    continue
                path = resource("textures", texture, ".png")
                self.assertTrue(path.is_file(), f"Missing texture: {texture}")
                data = path.read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertTrue(all(struct.unpack(">II", data[16:24])))
                self.assertTrue(stitched(texture), f"Texture absent from block atlas: {texture}")

        for poster in posters:
            with self.subTest(poster=poster):
                path = resource("items", poster)
                self.assertTrue(path.is_file(), f"Missing item definition: {poster}")
                definition = json.loads(path.read_text())["model"]
                self.assertEqual(definition["type"], "minecraft:model")
                check_model(definition["model"], set())


if __name__ == "__main__":
    unittest.main()
