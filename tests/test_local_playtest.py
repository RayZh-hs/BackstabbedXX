"""A disposable playtest must retain diagnostics before deleting its game directory."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from local_playtest import WORLD_NAME, local_game_directory


class PlaytestDiagnosticsTests(unittest.TestCase):
    def fixture(self, root):
        world = root / ".minecraft/saves" / WORLD_NAME
        world.mkdir(parents=True)
        (world / "level.dat").write_bytes(b"original world metadata")
        (root / ".minecraft/resourcepacks").mkdir()
        return world

    def test_crash_report_and_log_survive_temporary_directory_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            world = self.fixture(root)
            with local_game_directory(root) as game:
                (game / "crash-reports").mkdir()
                (game / "crash-reports/crash-server.txt").write_text("Original exception and stack")
                (game / "logs").mkdir()
                (game / "logs/latest.log").write_text("Events before the crash")
                retained = root / "dev/local-playtest-runs" / game.name
            self.assertFalse(game.exists())
            self.assertEqual((retained / "crash-reports/crash-server.txt").read_text(),
                             "Original exception and stack")
            self.assertEqual((retained / "logs/latest.log").read_text(), "Events before the crash")
            self.assertEqual(json.loads((retained / "run.json").read_text())["crash_reports"],
                             ["crash-server.txt"])
            self.assertEqual((world / "level.dat").read_bytes(), b"original world metadata")

    def test_exception_also_retains_logs_without_claiming_a_crash_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            with self.assertRaisesRegex(RuntimeError, "launcher failed"):
                with local_game_directory(root) as game:
                    (game / "logs").mkdir()
                    (game / "logs/latest.log").write_text("Launch failure")
                    retained = root / "dev/local-playtest-runs" / game.name
                    raise RuntimeError("launcher failed")
            self.assertFalse(game.exists())
            self.assertEqual((retained / "logs/latest.log").read_text(), "Launch failure")
            self.assertEqual(json.loads((retained / "run.json").read_text())["crash_reports"], [])


if __name__ == "__main__":
    unittest.main()
