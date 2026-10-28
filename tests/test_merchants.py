"""Check the installed merchant data, client assets and checked-in mod artifact."""
import hashlib
import json
from pathlib import Path
import re
import struct
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / ".minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies"
ASSETS = ROOT / ".minecraft/resourcepacks/backstabbed-resource/assets"


def summon_data(text, entity):
    line = next(line for line in text.splitlines() if line.startswith(f"summon minecraft:{entity} "))
    # These tracked summons use JSON keys/strings with SNBT byte/float scalars.
    # Replace only scalars outside quoted strings, preserving custom-name JSON.
    token = r'("(?:\\.|[^"\\])*")|\b(1b|0b|-?\d+(?:\.\d+)?f)\b'
    raw = line[line.index("{"):]
    raw = re.sub(token, lambda m: m[1] if m[1] else
                 {"1b": "true", "0b": "false"}.get(m[2], m[2][:-1]), raw)
    return json.loads(raw)


class MerchantIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with ZipFile(WORLD / "datapacks/mcm.zip") as z:
            cls.names = z.namelist()
            cls.members = {name: z.read(name) for name in cls.names}

    def text(self, name):
        return self.members[name].decode()

    def test_reviewed_sources_match_installed_datapack(self):
        source = ROOT / "merchant-bridge/datapack"
        self.assertEqual(len(self.names), len(set(self.names)))
        for path in source.rglob("*"):
            if path.is_file():
                self.assertEqual(path.read_bytes(), self.members[path.relative_to(source).as_posix()])

    def test_underwater_potion_and_lifecycle(self):
        spawn = self.text("data/underwater_base/function/trader/spawn.mcfunction")
        npc = summon_data(spawn, "zombie")
        self.assertTrue(npc["NoAI"] and npc["Invulnerable"] and npc["PersistenceRequired"])
        self.assertIn("MapEntity", npc["Tags"])
        self.assertIn("UnderwaterBaseRuntime", npc["Tags"])
        marker = summon_data(spawn, "marker")
        self.assertIn("team modify ArenaMerchants collisionRule never", spawn)
        self.assertIn("team join ArenaMerchants @e[type=minecraft:zombie,tag=UnderwaterPotionTrader]", spawn)
        offer, = marker["data"]["offers"]["Recipes"]
        self.assertEqual(offer["buy"], {"id": "minecraft:netherite_scrap", "count": 4})
        self.assertEqual(offer["sell"]["id"], "minecraft:potion")
        effect, = offer["sell"]["components"]["minecraft:potion_contents"]["custom_effects"]
        self.assertEqual((effect["id"], effect["duration"], effect["amplifier"]),
                         ("minecraft:invisibility", 400, 0))
        self.assertEqual(offer["priceMultiplier"], 0)
        self.assertFalse(offer["rewardExp"])
        self.assertIn("function underwater_base:trader/spawn", self.text("data/underwater_base/function/activate.mcfunction"))
        self.assertIn("kill @e[tag=UnderwaterBaseRuntime]", self.text("data/underwater_base/function/reset.mcfunction"))

    def test_panda_offer_preserves_toy_and_retires_immediate_purchase(self):
        spawn = self.text("data/panda_village/function/toy_shop/spawn.mcfunction")
        self.assertIn("summon panda 8370.5 106 8373.5", spawn)
        self.assertNotIn("summon interaction", spawn)
        self.assertIn("team modify ArenaMerchants collisionRule never", spawn)
        self.assertIn("team join ArenaMerchants @e[type=minecraft:panda,tag=PandaToyShop]", spawn)
        marker = summon_data(spawn, "marker")
        offer, = marker["data"]["offers"]["Recipes"]
        self.assertEqual(offer["buy"], {"id": "minecraft:netherite_scrap", "count": 4})
        loot = json.loads(self.text("data/panda_village/loot_table/toy_gun.json"))
        components = loot["pools"][0]["entries"][0]["functions"][0]["components"]
        self.assertEqual(offer["sell"]["components"], components)
        advancement = json.loads(self.text("data/panda_village/advancement/toy_shop.json"))
        self.assertEqual(advancement["criteria"]["retired"]["trigger"], "minecraft:impossible")
        self.assertNotIn("loot give", self.text("data/panda_village/function/toy_shop/buy.mcfunction"))

    def test_full_copper_suit_and_grate_model_resolve(self):
        npc = summon_data(self.text("data/underwater_base/function/trader/spawn.mcfunction"), "zombie")
        self.assertEqual(len(npc["ArmorItems"]), 4)
        for item, slot in zip(npc["ArmorItems"][:3], ("feet", "legs", "chest")):
            self.assertEqual(item["components"]["minecraft:equippable"],
                             {"slot": slot, "asset_id": "underwater_base:copper"})
        equipment = json.loads((ASSETS / "underwater_base/equipment/copper.json").read_text())
        for layer in ("humanoid", "humanoid_leggings"):
            self.assertEqual(equipment["layers"][layer][0]["texture"], "underwater_base:copper")
            png = ASSETS / f"underwater_base/textures/entity/equipment/{layer}/copper.png"
            raw = png.read_bytes()
            self.assertEqual(raw[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", raw[16:24]), (64, 32))
        head = npc["ArmorItems"][3]["components"]
        self.assertEqual(head["minecraft:item_model"], "underwater_base:diver_helmet")
        self.assertNotIn("asset_id", head["minecraft:equippable"])
        item = json.loads((ASSETS / "underwater_base/items/diver_helmet.json").read_text())
        model = item["model"]["model"].split(":")[1]
        model = json.loads((ASSETS / f"underwater_base/models/{model}.json").read_text())
        self.assertEqual(model["textures"]["grate"], "minecraft:block/oxidized_copper_grate")
        self.assertEqual(len(model["elements"]), 2)  # grate head and copper helmet
        atlas = json.loads((ASSETS / "minecraft/atlases/blocks.json").read_text())
        resources = {entry.get("resource") for entry in atlas["sources"]}
        self.assertIn(model["textures"]["copper"], resources)

    def test_shipped_mod_matches_its_reviewable_source(self):
        with ZipFile(ROOT / ".minecraft/mods/backstabbed-merchants-1.0.0.jar") as z:
            metadata = json.loads(z.read("backstabbed-merchants-build.json"))
            for name, digest in metadata["sources"].items():
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)
            self.assertIn("backstabbed/merchants/ArenaMerchants.class", z.namelist())
            self.assertFalse(any("mixin" in n or n.endswith("payload.class") for n in z.namelist()))


if __name__ == "__main__":
    unittest.main()
