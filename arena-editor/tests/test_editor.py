from contextlib import redirect_stdout
import copy
from io import BytesIO, StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import nbtlib as nbt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import editor
import pack
import world


def state():
    points = [{"id": i, "kind": kind, "x": 1.5, "y": 2.0, "z": 3.5, "yaw": 0.0, "pitch": 0.0}
              for i, kind in enumerate(("both", "ammo", "spectator", "return"), 1)]
    points.append(dict(id=5, kind="area", x=2.0, y=3.0, z=4.0, yaw=0.0, pitch=0.0,
                       x1=0.0, y1=0.0, z1=0.0, x2=4.0, y2=6.0, z2=8.0,
                       enabled=1, mode="keep_in", action="tp"))
    return dict(schema=1, next_id=6, boundary_enabled=1, outside_action="kill", objects=points, notes=[])


def chunk(x=0, z=0):
    return world.encode(nbt.File({"DataVersion": nbt.Int(4189), "xPos": nbt.Int(x), "zPos": nbt.Int(z),
                                  "block_entities": nbt.List[nbt.Compound]([nbt.parse_nbt('{id:"minecraft:chest",x:1,y:2,z:3,Items:[{id:"minecraft:diamond",count:3}]}')])}))


def write_fixture(root):
    source = root / "source"
    source.mkdir()
    nbt.File({"Data": nbt.parse_nbt('''{DataVersion:4189,Version:{Name:"1.21.4",Id:4189,Snapshot:0b,Series:"main"},
        WorldGenSettings:{seed:0L,dimensions:{"minecraft:overworld":{type:"minecraft:overworld",generator:{type:"minecraft:noise",settings:"minecraft:overworld"}}}},
        Player:{Pos:[1d,2d,3d]},GameRules:{},DragonFight:{},LevelName:"Original"}''')}, gzipped=True).save(source / "level.dat")
    (source / "session.lock").write_bytes(b"Minecraft lock")
    files = {
        "pack.mcmeta": b'{"pack":{"pack_format":61,"description":"game"}}',
        "data/mcm/function/lobby/voting/end.mcfunction": b'execute if entity @e[type=marker,tag=SelectedMap,tag=Example] run forceload add 0 0 15 15\nexecute if entity @e[type=marker,tag=SelectedMap,tag=Example] run schedule function example:activate 1s\n',
        "data/example/function/register.mcfunction": b'scoreboard players set @e[type=marker,tag=MapVote,tag=Example] MapValues 20\n',
        "data/example/function/activate.mcfunction": b'kill @e[tag=MapEntity]\nsummon marker 1.5 2 3.5 {Tags:["PlayerSpawn","ScrapSpawn","MapEntity"]}\nsummon marker 2.5 2 3.5 {Tags:["SpectatorSpawn","MapEntity"]}\nfunction example:restore_blocks\n',
        "data/example/function/check_player.mcfunction": b'execute unless predicate example:arena run return run function example:escape\nexecute if block ~ ~ ~ water run function example:escape\n',
        "data/example/function/restore_blocks.mcfunction": b'setblock 4 0 4 stone\n',
        "data/example/predicate/arena.json": json.dumps(editor.location(state()["objects"][-1])).encode(),
        "data/unrelated/function/logic.mcfunction": b'say unchanged\n',
        "data/minecraft/tags/function/tick.json": b'{"values":["mcm:everytick"]}',
    }
    (source / "datapacks").mkdir()
    with zipfile.ZipFile(source / "datapacks/mcm.zip", "w") as archive:
        for name, contents in files.items():
            archive.writestr(name, contents)
    world.write_region(source / "region/r.0.0.mca", {0: (1234, chunk()), 1: (1235, chunk(1))})
    entities = nbt.File({"DataVersion": nbt.Int(4189), "Position": nbt.IntArray([0, 0]), "Entities": nbt.List[nbt.Compound]([
        nbt.parse_nbt('{id:"minecraft:item_frame",Tags:["Decoration"]}'),
        nbt.parse_nbt('''{id:"minecraft:block_display",Tags:["UnderwaterBaseExitDisplay","UnderwaterBaseDecoration"],
            UUID:[I;1,2,3,4],Pos:[4d,2d,3d],Rotation:[0f,0f],
            block_state:{Name:"minecraft:waxed_exposed_copper_trapdoor",Properties:{facing:"east",open:"true",half:"top",waterlogged:"true",powered:"false"}},
            transformation:{translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],scale:[1f,1f,1f]}}'''),
        nbt.parse_nbt('{id:"minecraft:marker",Tags:["MapEntity","PlayerSpawn"]}'),
        nbt.parse_nbt('{id:"minecraft:text_display",Tags:["bbe.overlay"]}'),
    ])})
    world.write_region(source / "entities/r.0.0.mca", {0: (1234, world.encode(entities))})
    world.write_region(source / "poi/r.0.0.mca", {0: (1234, world.encode(nbt.File({"DataVersion": nbt.Int(4189), "Sections": nbt.Compound()})))})
    return source


class WorldTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = write_fixture(self.root)

    def test_extract_preserves_chest_and_poi_excludes_neighbor_and_runtime_entities(self):
        before = editor.source_hashes(self.source, [0, 0, 15, 15])
        target = self.root / "extracted"
        self.assertEqual(world.copy_chunks(self.source, target, [0, 0, 15, 15]), 1)
        selected = world.read_region(target / "region/r.0.0.mca")
        self.assertEqual(set(selected), {0})
        self.assertEqual(selected[0], world.read_region(self.source / "region/r.0.0.mca")[0])
        entities = nbt.File.parse(BytesIO(world.read_region(target / "entities/r.0.0.mca")[0][1]))
        self.assertEqual([str(e["id"]) for e in entities["Entities"]], ["minecraft:item_frame", "minecraft:block_display"])
        source_entities = nbt.File.parse(BytesIO(world.read_region(self.source / "entities/r.0.0.mca")[0][1]))
        self.assertEqual(entities["Entities"][1], source_entities["Entities"][1])
        self.assertEqual(world.read_region(target / "poi/r.0.0.mca"), world.read_region(self.source / "poi/r.0.0.mca"))
        self.assertEqual(before, editor.source_hashes(self.source, [0, 0, 15, 15]))

    def test_merge_preserves_neighbor_chunks_and_removes_deleted_selected_chunks(self):
        target = self.root / "merged"
        world.copy_chunks(self.source, target, [0, 0, 31, 15])
        neighbor = world.read_region(target / "region/r.0.0.mca")[1]
        empty = self.root / "empty"
        empty.mkdir()
        world.copy_chunks(empty, target, [0, 0, 15, 15], merge=True)
        self.assertEqual(world.read_region(target / "region/r.0.0.mca"), {1: neighbor})

    def test_negative_footprint_and_malformed_regions(self):
        self.assertEqual(world.footprint([-16, -16, -1, -1]), {"r.-1.-1.mca": {1023}})
        bad = self.root / "bad.mca"
        bad.write_bytes(b"short")
        with self.assertRaisesRegex(ValueError, "Truncated"):
            world.read_region(bad)
        bad.write_bytes(b"")
        self.assertEqual(world.read_region(bad), {})
        bad.write_bytes(b"\x00\x00\x01\x01" + bytes(8188))
        with self.assertRaisesRegex(ValueError, "location"):
            world.read_region(bad)

    def test_void_level_disables_game_pack_and_preserves_source(self):
        before = (self.source / "level.dat").read_bytes()
        target = self.root / "level"
        world.create_level(self.source, target, "Editor", [1.5, 2, 3.5])
        data = nbt.load(target / "level.dat")["Data"]
        self.assertNotIn("Player", data)
        self.assertEqual(list(map(str, data["DataPacks"]["Enabled"])), ["vanilla", "file/backstabbed-editor"])
        self.assertEqual(list(data["WorldGenSettings"]["dimensions"]["minecraft:overworld"]["generator"]["settings"]["layers"]), [])
        self.assertEqual(int(data["allowCommands"]), 1)
        self.assertEqual((self.source / "level.dat").read_bytes(), before)

    def test_java_record_lock_is_respected(self):
        code = 'import fcntl,sys; f=open(sys.argv[1],"r+b"); fcntl.lockf(f,fcntl.LOCK_EX); print("locked",flush=True); sys.stdin.read(1)'
        process = subprocess.Popen([sys.executable, "-c", code, str(self.source / "session.lock")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(process.stdout.readline().strip(), "locked")
            with self.assertRaisesRegex(ValueError, "Close this Minecraft world"):
                with world.stopped(self.source):
                    self.fail("Acquired a world held by a Java-compatible record lock")
        finally:
            process.communicate("x", timeout=5)
        with world.stopped(self.source):
            pass


class EditorTests(unittest.TestCase):
    setUp = WorldTests.setUp
    def settings(self):
        return dict(source_world=self.source, game_dir=self.root / "instance", launch_cwd=self.root)

    def prepared(self):
        with redirect_stdout(StringIO()):
            return editor.prepare(self.settings(), "example")

    def test_prepare_export_apply_metadata_and_reopen(self):
        session = self.prepared()
        source_region = (self.source / "region/r.0.0.mca").read_bytes()
        edited = world.saved_state(session)
        edited["objects"][0]["x"] = 8.125
        # Use the actual saved command-storage layout, rather than the seed.
        storage = nbt.File({"DataVersion": nbt.Int(4189), "data": nbt.Compound({"contents": nbt.Compound({
            "session": nbt.Compound({"state": pack.to_nbt(edited)})})})}, gzipped=True)
        (session / "data").mkdir()
        storage.save(session / "data/command_storage_bbe.dat")
        with redirect_stdout(StringIO()):
            exported = editor.export(self.settings(), "example", self.root / "export")
            with patch.object(editor, "ROOT", self.root):
                backup = editor.apply_export(exported)
        self.assertTrue(backup.exists())
        with zipfile.ZipFile(backup) as handle:
            self.assertIsNone(handle.testzip())
            self.assertEqual(handle.read("region/r.0.0.mca"), source_region)
        self.assertEqual((self.source / "region/r.0.0.mca").read_bytes(), source_region)
        files = editor.archive_files(self.source)
        self.assertEqual(files["data/unrelated/function/logic.mcfunction"], b"say unchanged\n")
        self.assertIn(b"8.125000000", files["data/bbe_arena/function/example/spawns.mcfunction"])
        self.assertNotIn(b"unless predicate example:arena", files["data/example/function/check_player.mcfunction"])
        self.assertIn(b"if block ~ ~ ~ water", files["data/example/function/check_player.mcfunction"])
        self.assertEqual(editor.seed_state(files, editor.discover(files)["example"]), edited)
        with self.assertRaisesRegex(ValueError, "Source changed"):
            editor.apply_export(exported)

    def test_apply_blocks_merges_only_selected_chunk(self):
        session = self.prepared()
        neighbor = world.read_region(self.source / "region/r.0.0.mca")[1]
        replacement = chunk(0, 0).replace(b"diamond", b"emerald")
        world.write_region(session / "region/r.0.0.mca", {0: (2000, replacement)})
        with redirect_stdout(StringIO()), patch.object(editor, "ROOT", self.root):
            exported = editor.export(self.settings(), "example", self.root / "export")
            editor.apply_export(exported, blocks=True)
        result = world.read_region(self.source / "region/r.0.0.mca")
        self.assertEqual(result[0], (2000, replacement))
        self.assertEqual(result[1], neighbor)

    def test_display_edits_and_deletion_survive_export_apply_and_reextraction(self):
        session = self.prepared()
        path = session / "entities/r.0.0.mca"
        entities = nbt.File.parse(BytesIO(world.read_region(path)[0][1]))
        display = entities["Entities"][1]
        display["Pos"][0] = nbt.Double(4.125)
        display["transformation"]["translation"][1] = nbt.Float(0.25)
        expected = copy.deepcopy(display)
        world.write_region(path, {0: (2000, world.encode(entities))})
        with redirect_stdout(StringIO()), patch.object(editor, "ROOT", self.root):
            exported = editor.export(self.settings(), "example", self.root / "display-export")
            editor.apply_export(exported, blocks=True)
        reextracted = self.root / "reextracted"
        world.copy_chunks(self.source, reextracted, [0, 0, 15, 15])
        result = nbt.File.parse(BytesIO(world.read_region(reextracted / "entities/r.0.0.mca")[0][1]))
        self.assertEqual(result["Entities"][1], expected)
        # A deliberate deletion is also a saved edit. Nothing recreates it.
        entities["Entities"].pop(1)
        world.write_region(path, {0: (2001, world.encode(entities))})
        manifest = json.loads((session / ".backstabbed-editor.json").read_text())
        manifest["source_hashes"] = editor.source_hashes(self.source, manifest["bounds"])
        editor.dump(session / ".backstabbed-editor.json", manifest)
        with redirect_stdout(StringIO()), patch.object(editor, "ROOT", self.root):
            exported = editor.export(self.settings(), "example", self.root / "deleted-display-export")
            editor.apply_export(exported, blocks=True)
        result = nbt.File.parse(BytesIO(world.read_region(self.source / "entities/r.0.0.mca")[0][1]))
        self.assertEqual([str(e["id"]) for e in result["Entities"]], ["minecraft:item_frame"])

    def test_existing_session_and_changed_source_are_not_overwritten(self):
        session = self.prepared()
        before = (session / "level.dat").read_bytes()
        with self.assertRaisesRegex(ValueError, "already exists"):
            editor.prepare(self.settings(), "example")
        self.assertEqual(before, (session / "level.dat").read_bytes())
        with redirect_stdout(StringIO()):
            exported = editor.export(self.settings(), "example", self.root / "export")
        archive = self.source / "datapacks/mcm.zip"
        archive.write_bytes(archive.read_bytes() + b"changed")
        before = archive.read_bytes()
        with self.assertRaisesRegex(ValueError, "Source changed"):
            editor.apply_export(exported)
        self.assertEqual(before, archive.read_bytes())

    def test_failed_apply_rolls_back_from_verified_backup(self):
        self.prepared()
        with redirect_stdout(StringIO()):
            exported = editor.export(self.settings(), "example", self.root / "export")
        before = editor.source_hashes(self.source, [0, 0, 15, 15])
        original = Path.replace
        def fail_on_chunks(path, destination):
            if Path(destination) == self.source / "region/r.0.0.mca":
                raise OSError("simulated write failure")
            return original(path, destination)
        with patch.object(editor, "ROOT", self.root), patch.object(Path, "replace", fail_on_chunks):
            with self.assertRaisesRegex(OSError, "simulated"):
                editor.apply_export(exported, blocks=True)
        self.assertEqual(before, editor.source_hashes(self.source, [0, 0, 15, 15]))

    def test_launch_preserves_argument_boundaries_and_has_no_shell(self):
        session = self.prepared()
        settings = self.settings()
        settings["launch_command"] = ["launcher", "--gameDir", "{game_dir}", "{unrelated}", "{world_name}", "literal $(echo unsafe)"]
        with patch.object(editor.subprocess, "run") as run, redirect_stdout(StringIO()):
            run.return_value.returncode = 0
            self.assertEqual(editor.launch(settings, "example"), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[2], str(settings["game_dir"]))
        self.assertEqual(command[-3:], ["{unrelated}", session.name, "literal $(echo unsafe)"])
        self.assertNotIn("shell", run.call_args.kwargs)
        self.assertEqual(settings["launch_command"][2], "{game_dir}")

    def test_backup_failure_never_writes_to_source(self):
        self.prepared()
        with redirect_stdout(StringIO()):
            exported = editor.export(self.settings(), "example", self.root / "export")
        before = editor.source_hashes(self.source, [0, 0, 15, 15])
        with patch.object(editor, "ROOT", self.root), patch.object(zipfile.ZipFile, "testzip", return_value="bad member"):
            with self.assertRaisesRegex(ValueError, "Backup verification failed"):
                editor.apply_export(exported)
        self.assertEqual(before, editor.source_hashes(self.source, [0, 0, 15, 15]))

    def test_missing_saved_state_is_not_silently_replaced_with_seed(self):
        session = self.prepared()
        (session / "data").mkdir()
        nbt.File({"data": nbt.Compound({"contents": nbt.Compound()})}, gzipped=True).save(session / "data/command_storage_bbe.dat")
        with self.assertRaisesRegex(ValueError, "missing its state"):
            world.saved_state(session)

    def test_config_resolves_paths_relative_to_config_and_preserves_command(self):
        path = self.root / "local.json"
        editor.dump(path, {"game_dir": "instance with spaces", "source_world": "source", "launch_command": ["launcher", "{world_name}"]})
        settings = editor.config(path)
        self.assertEqual(settings["game_dir"], self.root / "instance with spaces")
        self.assertEqual(settings["source_world"], self.source)
        self.assertEqual(settings["launch_command"], ["launcher", "{world_name}"])

    def test_rejects_version_downgrade_before_creating_target(self):
        level = nbt.load(self.source / "level.dat")
        level["Data"]["DataVersion"] = nbt.Int(4440)
        level.save(self.source / "level.dat")
        with self.assertRaisesRegex(ValueError, "does not convert"):
            self.prepared()
        self.assertFalse((self.settings()["game_dir"] / "saves/Backstabbed-Editor-example").exists())


class ImportTests(unittest.TestCase):
    def test_underwater_exit_displays_are_aligned_saved_decorations(self):
        files = editor.archive_files(editor.DEFAULT_WORLD)
        spec = editor.discover(files)["underwater_base"]
        displays = []
        for filename, slots in world.footprint(spec["bounds"]).items():
            for slot, (_, payload) in world.read_region(editor.DEFAULT_WORLD / "entities" / filename).items():
                if slot in slots:
                    entities = nbt.File.parse(BytesIO(payload)).get("Entities", [])
                    displays.extend(e for e in entities if "UnderwaterBaseExitDisplay" in map(str, e.get("Tags", [])))
        expected = {(32949, 45, 32532), (32950, 45, 32532), (32970, 42, 32529),
                    (32971, 42, 32529), (32972, 43, 32529), (32972, 44, 32529)}
        self.assertEqual(len(displays), 6)
        self.assertEqual({tuple(map(float, e["Pos"])) for e in displays}, expected)
        self.assertEqual(len({tuple(map(int, e["UUID"])) for e in displays}), 6)
        for entity in displays:
            self.assertEqual(str(entity["id"]), "minecraft:block_display")
            self.assertFalse(set(map(str, entity["Tags"])) & {"MapEntity", "UnderwaterBaseRuntime"})
            self.assertEqual(list(map(float, entity["transformation"]["translation"])), [0, 0, 0])
        self.assertNotIn("data/underwater_base/function/spawn_exit_displays.mcfunction", files)
        for name, contents in files.items():
            if name.endswith(".mcfunction"):
                self.assertNotIn(b"UnderwaterBaseExitDisplay", contents, name)
                self.assertNotIn(b"underwater_base:spawn_exit_displays", contents, name)

    def test_repository_arenas_import_without_losing_spawns(self):
        files = editor.archive_files(editor.DEFAULT_WORLD)
        registry = editor.discover(files)
        self.assertGreaterEqual(len(registry), 19)
        for arena, spec in registry.items():
            with self.subTest(arena=arena):
                value = editor.validate(editor.seed_state(files, spec))
                self.assertTrue(any(o["kind"] in ("player", "both") for o in value["objects"]))
                self.assertTrue(spec["map_id"])
        self.assertEqual(sum(o["kind"] == "area" for o in editor.seed_state(files, registry["meridian_base"])["objects"]), 825)
        conditional = [o for o in editor.seed_state(files, registry["canyon"])["objects"] if "guard" in o]
        self.assertTrue(any(o["guard"].endswith("matches 1") for o in conditional))
        self.assertTrue(any(o["guard"].endswith("matches 2") for o in conditional))
    def test_absolute_relative_and_conditional_spawns(self):
        point = editor.point_from_line('execute positioned -3.5 2 4 run summon marker ~ ~1 ~ {Tags:["PlayerSpawn","ScrapSpawn"]}')
        self.assertEqual([point[a] for a in "xyz"], [-3.5, 3, 4])
        self.assertEqual(point["kind"], "both")
        point = editor.point_from_line('execute if score $canyon_partition CmdData matches 2 positioned 1 2 3 run function mcm:game/markers/playerspawn')
        self.assertEqual(point["guard"], 'if score $canyon_partition CmdData matches 2')
        self.assertIsNone(editor.point_from_line('# summon marker 1 2 3 {Tags:["PlayerSpawn"]}'))

    def test_box_import_is_exact_and_rejects_other_conditions(self):
        box = state()["objects"][-1]
        restored = editor.predicate_boxes(editor.location(box))[0]
        self.assertEqual(restored["x1"], box["x1"])
        self.assertEqual(restored["z2"], box["z2"])
        value = editor.location(box)
        value["predicate"]["location"]["biome"] = "minecraft:plains"
        with self.assertRaisesRegex(ValueError, "non-box"):
            editor.predicate_boxes(value)

    def test_validation_prevents_broken_exports(self):
        for mutate in [lambda s: s["objects"].pop(3), lambda s: s["objects"][0].update(x=float("nan")),
                       lambda s: s["objects"][1].update(id=1), lambda s: s.update(outside_action="say hi"),
                       lambda s: s["objects"][-1].update(x1=99), lambda s: s.update(next_id=1)]:
            value = state()
            mutate(value)
            with self.assertRaises(ValueError):
                editor.validate(value)

    def test_exported_boundary_rules_preserve_union_and_exclusions(self):
        value = state()
        box = {**value["objects"][-1], "id": 6, "mode": "keep_out", "action": "kill"}
        value["objects"].append(box)
        files = editor.exported_files(value, dict(arena="example", tag="Example", map_id=20))
        check = files["data/bbe_arena/function/example/check_player.mcfunction"].decode()
        self.assertIn('if predicate bbe_arena:example/box_6', check)
        self.assertIn('unless predicate bbe_arena:example/keep_in', check)
        self.assertIn('$selectedMap CmdData matches 20', files["data/bbe_arena/function/example/tick.mcfunction"].decode())
        value["boundary_enabled"] = 0
        self.assertEqual(editor.exported_files(value, dict(arena="example", tag="Example", map_id=20))["data/bbe_arena/function/example/check_player.mcfunction"], b"\n")


if __name__ == "__main__":
    unittest.main()
