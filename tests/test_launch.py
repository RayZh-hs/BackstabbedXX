from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import launch
import local_playtest


ROOT = Path(__file__).resolve().parent.parent


class LocalLaunchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.game = self.root / ".minecraft"
        self.world = self.game / "saves" / local_playtest.WORLD_NAME
        self.world.mkdir(parents=True)
        (self.world / "level.dat").write_bytes(b"original world")
        (self.world / "session.lock").write_bytes(b"source lock")
        for name in ("config", "mods", "resourcepacks"):
            (self.game / name).mkdir()
            (self.game / name / "source").write_bytes(b"original")
        (self.game / "options.txt").write_text('music:0.2\nresourcePacks:["vanilla","file/other.zip"]\n')
        (self.root / "mmc-pack.json").write_text(json.dumps({"components": [
            {"uid": "net.minecraft", "version": "1.21.4"},
            {"uid": "net.neoforged", "version": "21.4.158"},
        ]}))

    def test_disposable_world_and_settings_never_write_to_source(self):
        originals = {p: p.read_bytes() for p in self.game.rglob("*") if p.is_file()}
        with local_playtest.local_game_directory(self.root) as game:
            world = game / "saves" / local_playtest.WORLD_NAME
            self.assertFalse((world / "session.lock").exists())
            self.assertTrue((world / ".backstabbed-local").is_file())
            (world / "level.dat").write_bytes(b"played world")
            for name in ("config", "mods", "resourcepacks"):
                (game / name / "source").write_bytes(b"game wrote settings")
            launch.enable_resourcepack(game)
            self.assertIn('music:0.2\n', (game / "options.txt").read_text())
            self.assertIn('file/other.zip', (game / "options.txt").read_text())
            self.assertIn('file/backstabbed-resource.zip', (game / "options.txt").read_text())
        self.assertFalse(game.exists())
        self.assertEqual(originals, {p: p.read_bytes() for p in self.game.rglob("*") if p.is_file()})

    def test_missing_world_fails_before_staging(self):
        (self.world / "level.dat").unlink()
        with self.assertRaisesRegex(SystemExit, "Playtest world is missing"):
            with local_playtest.local_game_directory(self.root):
                self.fail("Staged a missing world")

    def run_launcher(self, args, callback):
        cli = ModuleType("portablemc.cli")
        cli.main = callback
        cli.CliRunner = type("Runner", (), {"run": lambda self, env: None})
        portablemc = ModuleType("portablemc")
        portablemc.cli = cli
        original_runner = cli.CliRunner
        with patch.dict(sys.modules, {"portablemc": portablemc, "portablemc.cli": cli}), \
                patch.object(launch, "ROOT", self.root), \
                patch.object(launch, "configure_download_proxy"), \
                patch.dict(os.environ, {"MINECRAFT_RUNTIME_DIR": str(self.root / "runtime")}), \
                patch.object(sys, "argv", ["launch.py", *args]), redirect_stdout(io.StringIO()):
            try:
                launch.main()
            finally:
                self.assertIs(cli.CliRunner, original_runner)

    def test_normal_launch_uses_source_without_helper(self):
        callback = Mock()
        self.run_launcher(["--username", "Ray"], callback)
        args = callback.call_args.args[0]
        self.assertEqual(args[args.index("--work-dir") + 1], str(self.game))
        self.assertEqual(args[-2:], ["--username", "Ray"])
        self.assertFalse((self.root / "dev").exists())

    def test_local_flag_is_consumed_and_cleanup_survives_launcher_exit(self):
        staged = []

        def callback(args):
            self.assertNotIn("--local", args)
            self.assertEqual(args[-2:], ["--username", "Ray"])
            game = Path(args[args.index("--work-dir") + 1])
            self.assertNotEqual(game, self.game)
            staged.append(game)
            import portablemc.cli
            env = SimpleNamespace(jvm_args=["java"], game_args=[], context=SimpleNamespace(work_dir=game))
            portablemc.cli.CliRunner().run(env)
            build.assert_called_once()
            self.assertEqual(env.game_args, ["--quickPlaySingleplayer", local_playtest.WORLD_NAME])
            raise SystemExit(7)

        with patch.object(local_playtest, "build_helper") as build, self.assertRaises(SystemExit) as result:
            self.run_launcher(["--local", "--username", "Ray"], callback)
        self.assertEqual(result.exception.code, 7)
        self.assertFalse(staged[0].exists())

    def test_local_mode_rejects_multiplayer_quickplay(self):
        for arg in ("--server=example.com", "--server", "--server-port=25565"):
            with self.subTest(arg=arg), self.assertRaisesRegex(SystemExit, "singleplayer"):
                self.run_launcher(["--local", arg], Mock())

    def test_make_local_forms_forward_flag_only_to_launcher(self):
        for args in (["launch", "--", "--local"], ["launch", "LOCAL=1"],
                     ["launch", "LAUNCH_ARGS=--local"], ["launch"]):
            with self.subTest(args=args):
                result = subprocess.run(["make", "--no-print-directory", "-n", *args],
                                        cwd=ROOT, check=True, text=True, capture_output=True)
                commands = result.stdout.splitlines()
                launcher = next(line for line in commands if "scripts/launch.py" in line)
                self.assertEqual("--local" in launcher, args != ["launch"])
                self.assertNotIn("--local", commands[0])


if __name__ == "__main__":
    unittest.main()
