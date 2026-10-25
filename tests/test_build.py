import gzip
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import build
from nbt import level_name, rename_level


def string(value):
    encoded = value.encode("utf-8")
    return struct.pack(">H", len(encoded)) + encoded


def tag(kind, name, payload):
    return bytes([kind]) + string(name) + payload


def world_data(name):
    # Exercise every payload type, plus a decoy LevelName in a nested compound.
    preceding = b"".join([
        tag(1, "byte", b"\x01"),
        tag(2, "short", struct.pack(">h", -2)),
        tag(3, "int", struct.pack(">i", 42)),
        tag(4, "long", struct.pack(">q", 123456789)),
        tag(5, "float", struct.pack(">f", 1.25)),
        tag(6, "double", struct.pack(">d", 2.5)),
        tag(7, "bytes", struct.pack(">i", 3) + b"abc"),
        tag(8, "other", string("unchanged")),
        tag(9, "list", b"\x08" + struct.pack(">i", 2) + string("a") + string("b")),
        tag(10, "nested", tag(8, "LevelName", string("decoy")) + b"\0"),
        tag(11, "ints", struct.pack(">iii", 2, 17, -23)),
        tag(12, "longs", struct.pack(">iqq", 2, 101, -202)),
    ])
    data = preceding + tag(8, "LevelName", string(name)) + tag(3, "after", struct.pack(">i", 7))
    return tag(10, "", preceding + tag(10, "Data", data + b"\0") + b"\0")


def world_file(name):
    return gzip.compress(world_data(name), mtime=0)


class LevelNameTests(unittest.TestCase):
    def test_changes_only_the_world_display_name(self):
        original = world_file("Source World")
        renamed = rename_level(original, "Source World v2.3.4 地图")
        self.assertEqual(level_name(renamed), "Source World v2.3.4 地图")
        self.assertEqual(gzip.decompress(renamed), world_data("Source World v2.3.4 地图"))
        self.assertEqual(level_name(original), "Source World")
        self.assertEqual(renamed, rename_level(original, "Source World v2.3.4 地图"))

    def test_missing_or_invalid_metadata_fails(self):
        payloads = [b"\x01\0\0", tag(10, "", b"\0"), tag(10, "", b"\x0a")]
        for payload in payloads:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                rename_level(gzip.compress(payload), "Name")


class VersionTests(unittest.TestCase):
    def test_explicit_versions_and_credits(self):
        self.assertEqual(build.release_version("v2.3.4"), "2.3.4")
        self.assertEqual(build.release_version("2.3.4"), "2.3.4")
        self.assertEqual(build.release_version("v1.1.1-alpha"), "1.1.1-alpha")
        self.assertEqual(build.release_version("1.1.1-rc.2"), "1.1.1-rc.2")
        self.assertEqual(build.versioned_name("World by Author", "2.3.4"), "World v2.3.4 by Author")
        self.assertEqual(build.versioned_name("World", "2.3.4"), "World v2.3.4")

    def test_environment_and_git_tag_defaults(self):
        with patch.dict(os.environ, {"VERSION": "v2.3.4"}):
            self.assertEqual(build.release_version(), "2.3.4")
        result = subprocess.CompletedProcess([], 0, stdout="v3.4.5\n")
        with patch.dict(os.environ, {"VERSION": ""}), patch.object(build.subprocess, "run", return_value=result):
            self.assertEqual(build.release_version(), "3.4.5")

    def test_invalid_versions_fail(self):
        for version in ["latest", "../world", "v1.2", "v1.2.3/extra", "v1.2.3-", "v1.2.3-alpha..1", "v1.2.3-alpha/extra"]:
            with self.subTest(version=version), self.assertRaises(SystemExit):
                build.release_version(version)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / ".minecraft/saves/World by Author"
        self.source.mkdir(parents=True)
        for name in ["level.dat", "level.dat_old"]:
            (self.source / name).write_bytes(world_file("World by Author"))
        (self.source / "region").mkdir()
        (self.source / "region/r.0.0.mca").write_bytes(b"unchanged region data")
        (self.source / "session.lock").write_bytes(b"runtime lock")
        self.patcher = patch.multiple(build, ROOT=self.root, DIST=self.root / "dist", MAP_SOURCE=self.source)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_separate_versioned_maps_preserve_sources(self):
        originals = {p: p.read_bytes() for p in self.source.rglob("*") if p.is_file()}
        for version in ["2.3.4", "3.4.5", "1.1.1-alpha"]:
            build.build_map(version)
            with zipfile.ZipFile(self.root / f"dist/Backstabbed++-map-v{version}.zip") as archive:
                folder = f"World v{version} by Author"
                self.assertEqual(set(archive.namelist()), {
                    f"{folder}/level.dat", f"{folder}/level.dat_old", f"{folder}/region/r.0.0.mca",
                })
                for name in ["level.dat", "level.dat_old"]:
                    self.assertEqual(level_name(archive.read(f"{folder}/{name}")), folder)
                self.assertEqual(archive.read(f"{folder}/region/r.0.0.mca"), b"unchanged region data")
        self.assertTrue(all(p.read_bytes() == data for p, data in originals.items()))

    def test_rebuilding_map_removes_deleted_files(self):
        build.build_map("2.3.4")
        (self.source / "region/r.0.0.mca").unlink()
        build.build_map("2.3.4")
        with zipfile.ZipFile(self.root / "dist/Backstabbed++-map-v2.3.4.zip") as archive:
            self.assertFalse(any(name.endswith(".mca") for name in archive.namelist()))

    def test_client_pack_excludes_worlds_even_without_packignore_rule(self):
        (self.root / ".packignore").write_text("")
        (self.root / "mmc-pack.json").write_text("{}")
        (self.root / "instance.cfg.example").write_text("[General]\nInstanceType=OneSix\n")
        resourcepack = self.root / "resourcepack.zip"
        resourcepack.write_bytes(b"resource pack bytes")
        names = ["mmc-pack.json", str((self.source / "level.dat").relative_to(self.root))]
        result = subprocess.CompletedProcess([], 0, stdout=("\0".join(names) + "\0").encode())
        with patch.object(build.subprocess, "run", return_value=result):
            build.build_pack(resourcepack)
        with zipfile.ZipFile(self.root / "dist/Backstabbed++.zip") as archive:
            self.assertFalse(any(name.startswith(".minecraft/saves/") for name in archive.namelist()))
            self.assertEqual(archive.read(".minecraft/resourcepacks/backstabbed-resource.zip"), b"resource pack bytes")


if __name__ == "__main__":
    unittest.main()
