"""Regression coverage for the HMCL release archive."""

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build


class ModrinthPackTest(unittest.TestCase):
    def test_portable_manifest_and_complete_payload(self):
        components = {"components": [
            {"uid": "org.lwjgl3", "version": "3.3.3"},
            {"uid": "net.minecraft", "version": "1.21.4"},
            {"uid": "net.neoforged", "version": "21.4.158"},
        ]}
        files = {
            "mmc-pack.json": json.dumps(components).encode(),
            "instance.cfg": b"developer settings",
            ".minecraft/modrinth.index.json": b"stale 21.4.149 manifest",
            ".minecraft/hmclversion.cfg": b"local Java path",
            ".minecraft/PCL/Setup.ini": b"local Java path",
            ".minecraft/.hmcl/config/settings.json": b"local settings",
            ".minecraft/saves/world/level.dat": b"world",
            ".minecraft/mods/example.jar": b"mod bytes",
            ".minecraft/resourcepacks/backstabbed-resource.zip": b"resource bytes",
            ".minecraft/config/example.toml": b"configuration",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(build, "ROOT", root), patch.object(build, "DIST", root):
                build.build_modrinth_pack(files, "1.1.2-alpha")
                path = root / "Backstabbed++.mrpack"
                original = path.read_bytes()
                with zipfile.ZipFile(path) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(set(archive.namelist()), {
                        "modrinth.index.json", "overrides/mods/example.jar",
                        "overrides/resourcepacks/backstabbed-resource.zip",
                        "overrides/config/example.toml",
                    })
                    index = json.loads(archive.read("modrinth.index.json"))
                    self.assertEqual(index["versionId"], "1.1.2-alpha")
                    self.assertEqual(index["formatVersion"], 1)
                    self.assertEqual(index["game"], "minecraft")
                    self.assertEqual(index["files"], [])
                    self.assertEqual(index["dependencies"], {
                        "minecraft": "1.21.4", "neoforge": "21.4.158",
                    })
                    self.assertEqual(archive.read("overrides/mods/example.jar"), b"mod bytes")
                    self.assertEqual(archive.read("overrides/resourcepacks/backstabbed-resource.zip"), b"resource bytes")
                build.build_modrinth_pack(files, "1.1.2-alpha")
                self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
