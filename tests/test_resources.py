"""Check the complete voting-poster model, texture, and atlas dependency graph."""

import json
from pathlib import Path
import re
import struct
import unittest
import zipfile


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / ".minecraft/resourcepacks/backstabbed-resource/assets"
DATAPACK = ROOT / ".minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies/datapacks/mcm.zip"


def location(value):
    return value.split(":", 1) if ":" in value else ("minecraft", value)


def resource(kind, value, suffix=".json"):
    namespace, path = location(value)
    return ASSETS / namespace / kind / (path + suffix)


class VotingPosterTests(unittest.TestCase):
    def test_all_voting_posters_have_models_and_stitched_textures(self):
        with zipfile.ZipFile(DATAPACK) as archive:
            commands = archive.read("data/mcm/function/lobby/voting/map_position_id.mcfunction").decode()
        commands = "\n".join(line for line in commands.splitlines() if not line.lstrip().startswith("#"))
        posters = re.findall(r'(?:"(?:minecraft:)?item_model"|item_model):"([^"]+:posters/[^"]+)"', commands)
        self.assertTrue(posters)
        self.assertTrue({f"{name}:posters/{name}" for name in ("panda_village", "river_bank", "yacht")} <= set(posters))
        atlas = json.loads((ASSETS / "minecraft/atlases/blocks.json").read_text())["sources"]

        def stitched(texture):
            namespace, path = location(texture)
            for source in atlas:
                kind = source["type"].removeprefix("minecraft:")
                if kind == "single" and location(source.get("sprite", source["resource"])) == [namespace, path]:
                    return True
                if kind == "directory":
                    ns, directory = location(source["source"])
                    if ns == namespace and path.startswith(source["prefix"]):
                        relative = path.removeprefix(source["prefix"])
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
