from contextlib import redirect_stdout
import base64
from io import StringIO
import json
from pathlib import Path
import subprocess
import platform
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import editor
import world
from test_editor import write_fixture


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = write_fixture(self.root)
        self.settings = dict(source_world=self.source, game_dir=self.root / "instance", launch_cwd=self.root,
                             launch_command=["local-launcher", "{world_name}"])

    def test_choose_lists_all_names_accepts_number_and_retries_invalid(self):
        registry = {"subway_station": {"map_id": 16, "title": "Subway Station"}, "yacht": {"map_id": 15, "title": "Yacht"}}
        output = StringIO()
        with patch("builtins.input", side_effect=["invalid", "2"]), redirect_stdout(output):
            self.assertEqual(editor.choose_arena(registry), "subway_station")
        self.assertIn("subway_station", output.getvalue())
        self.assertIn("yacht", output.getvalue())
        self.assertIn("Unknown arena", output.getvalue())
        with patch("builtins.input", return_value="Subway Station"), redirect_stdout(StringIO()):
            self.assertEqual(editor.choose_arena(registry), "subway_station")

    def test_cancel_selection_creates_no_session_or_source_changes(self):
        before = editor.source_hashes(self.source, [0, 0, 15, 15])
        with patch("builtins.input", return_value=""), redirect_stdout(StringIO()):
            self.assertEqual(editor.edit(self.settings), 0)
        self.assertFalse(self.settings["game_dir"].exists())
        self.assertEqual(before, editor.source_hashes(self.source, [0, 0, 15, 15]))

    def test_decline_writeback_keeps_edit_and_export_but_never_applies(self):
        before = editor.source_hashes(self.source, [0, 0, 15, 15])
        with patch.object(editor, "ROOT", self.root), patch.object(editor, "launch_for_edit", return_value=0) as launch, \
                patch.object(editor, "apply_export") as apply, patch("builtins.input", return_value="no"), redirect_stdout(StringIO()):
            self.assertEqual(editor.edit(self.settings, "example"), 0)
        launch.assert_called_once_with(self.settings, "example")
        apply.assert_not_called()
        self.assertTrue(editor.session(self.settings, "example").exists())
        self.assertEqual(len(list((self.root / "dev/arena-editor/exports").iterdir())), 1)
        self.assertEqual(before, editor.source_hashes(self.source, [0, 0, 15, 15]))

    def test_confirm_writes_blocks_and_metadata_then_rebases_for_next_edit(self):
        def simulated_edit(settings, arena):
            session = editor.session(settings, arena)
            # Change actual terrain payload in the extracted world.
            chunks = world.read_region(session / "region/r.0.0.mca")
            stamp, payload = chunks[0]
            chunks[0] = (stamp, payload.replace(b"diamond", b"emerald"))
            world.write_region(session / "region/r.0.0.mca", chunks)
            return 0
        with patch.object(editor, "ROOT", self.root), patch.object(editor, "launch_for_edit", side_effect=simulated_edit), \
                patch("builtins.input", return_value="yes"), redirect_stdout(StringIO()):
            self.assertEqual(editor.edit(self.settings, "example"), 0)
        self.assertIn(b"emerald", world.read_region(self.source / "region/r.0.0.mca")[0][1])
        self.assertEqual(len(list((self.root / "dev/arena-editor/backups").glob("*.zip"))), 1)
        session = editor.session(self.settings, "example")
        manifest = json.loads((session / ".backstabbed-editor.json").read_text())
        editor.check_baseline(self.source, manifest)
        # A second invocation resumes this session, and 'no' does not reapply.
        with patch.object(editor, "ROOT", self.root), patch.object(editor, "launch_for_edit", return_value=0), \
                patch.object(editor, "prepare") as prepare, patch.object(editor, "apply_export") as apply, \
                patch("builtins.input", return_value="no"), redirect_stdout(StringIO()):
            self.assertEqual(editor.edit(self.settings, "example"), 0)
        prepare.assert_not_called()
        apply.assert_not_called()

    def test_failed_launch_does_not_offer_or_perform_writeback(self):
        with patch.object(editor, "launch_for_edit", return_value=7), patch("builtins.input") as prompt, \
                patch.object(editor, "export") as export, redirect_stdout(StringIO()):
            self.assertEqual(editor.edit(self.settings, "example"), 7)
        prompt.assert_not_called()
        export.assert_not_called()

    def test_default_confirmation_applies(self):
        for reply in ("", " \t"):
            with self.subTest(reply=reply), patch.object(editor, "ROOT", self.root), \
                    patch.object(editor, "launch_for_edit", return_value=0), patch.object(editor, "apply_export") as apply, \
                    patch("builtins.input", return_value=reply) as prompt, redirect_stdout(StringIO()):
                self.assertEqual(editor.edit(self.settings, "example"), 0)
                prompt.assert_called_once_with("Write this edited arena back to the source world? [Y/n] ")
                apply.assert_called_once()
                self.assertTrue(apply.call_args.kwargs["blocks"])

    def test_decline_invalid_input_and_eof_never_apply(self):
        for reply in ("n", "no", " N ", "invalid", EOFError()):
            with self.subTest(reply=reply), patch.object(editor, "ROOT", self.root), \
                    patch.object(editor, "launch_for_edit", return_value=0), patch.object(editor, "apply_export") as apply, \
                    patch("builtins.input", side_effect=[reply]), redirect_stdout(StringIO()):
                self.assertEqual(editor.edit(self.settings, "example"), 0)
                apply.assert_not_called()

    def test_world_close_is_detected_while_client_remains_running(self):
        process = Mock()
        process.poll.return_value = None
        with patch.object(editor, "world_is_open", side_effect=[False, True, True, False]), \
                patch.object(editor.time, "sleep"), patch("builtins.input") as prompt, redirect_stdout(StringIO()):
            self.assertEqual(editor.wait_for_edit_close(self.source, process, editor.save_signature(self.source)), 0)
        prompt.assert_not_called()

    def test_detached_launcher_watches_world_without_terminal_acknowledgement(self):
        process = Mock()
        process.poll.return_value = 0
        with patch.object(editor, "world_is_open", side_effect=[False, True, True, False]), \
                patch.object(editor.time, "sleep"), \
                patch("builtins.input", side_effect=AssertionError("Detached launcher must keep monitoring, not block on input")), \
                redirect_stdout(StringIO()):
            self.assertEqual(editor.wait_for_edit_close(self.source, process, editor.save_signature(self.source)), 0)

    def test_nested_world_lock_remains_held_after_inner_helper_finishes(self):
        code = 'import fcntl,sys; f=open(sys.argv[1],"r+b"); fcntl.lockf(f,fcntl.LOCK_EX|fcntl.LOCK_NB)'
        with world.stopped(self.source):
            with world.stopped(self.source):
                pass
            result = subprocess.run([sys.executable, "-c", code, str(self.source / "session.lock")], capture_output=True)
            self.assertNotEqual(result.returncode, 0, "Nested helper released the outer Java-compatible lock")
        result = subprocess.run([sys.executable, "-c", code, str(self.source / "session.lock")], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless("microsoft" in platform.release().lower() and shutil.which("powershell.exe"),
                         "Requires WSL and Windows PowerShell")
    def test_windows_game_lock_is_visible_from_wsl(self):
        # Use the Windows checkout volume, not WSL's private /tmp filesystem.
        with tempfile.TemporaryDirectory(prefix="bbe-'测试-", dir=Path(__file__).resolve().parents[2]) as directory:
            save = Path(directory)
            lock = save / "session.lock"
            lock.write_bytes(b"Minecraft lock")
            winpath = subprocess.check_output(["wslpath", "-w", str(lock)], text=True).strip()
            if len(winpath) < 3 or winpath[1:3] != ":\\":
                self.skipTest("Requires a checkout on a Windows drive")
            script = ("$ErrorActionPreference='Stop'; $f=[IO.File]::Open('" + winpath.replace("'", "''") +
                      "',[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::ReadWrite); "
                      "$f.Lock(0,[long]::MaxValue); [Console]::WriteLine('ready'); "
                      "[Console]::ReadLine() | Out-Null; $f.Dispose()")
            encoded = base64.b64encode(script.encode("utf-16-le")).decode()
            process = subprocess.Popen(["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                self.assertEqual(process.stdout.readline().strip(), "ready")
                self.assertTrue(editor.world_is_open(save), "Windows game lock was invisible to WSL")
                with self.assertRaises(world.WorldOpenError):
                    with world.stopped(save):
                        self.fail("Allowed writes while Windows game holds the world")
                launcher = Mock()
                launcher.poll.return_value = None
                output = StringIO()
                with patch.object(editor.time, "sleep", side_effect=lambda _: process.communicate("\n", timeout=15)), \
                        redirect_stdout(output):
                    self.assertEqual(editor.wait_for_edit_close(save, launcher, editor.save_signature(save)), 0)
                self.assertIn("Editor world is closed.", output.getvalue())
            finally:
                if process.poll() is None:
                    process.communicate("\n", timeout=15)
            self.assertFalse(editor.world_is_open(save))
            # The guard must also keep Windows out during writes, including
            # after a nested operation has returned.
            with world.stopped(save):
                with world.stopped(save):
                    pass
                probe = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                                       input="\n", capture_output=True, text=True, errors="replace", timeout=15)
                self.assertNotEqual(probe.returncode, 0)
                self.assertNotIn("ready", probe.stdout)
            self.assertEqual(lock.read_bytes(), b"Minecraft lock")

    def test_make_optional_name_never_runs_another_target(self):
        root = Path(__file__).resolve().parents[2]
        for goals in (["edit"], ["edit", "subway_station"], ["edit", "test"], ["edit", "edit"]):
            with self.subTest(goals=goals):
                result = subprocess.run(["make", "--no-print-directory", "-n", *goals], cwd=root, capture_output=True, text=True, check=True)
                self.assertIn("arena-editor/editor.py edit", result.stdout)
                self.assertNotIn("unittest", result.stdout)
                self.assertNotIn("scripts/build.py", result.stdout)
        result = subprocess.run(["make", "-n", "edit", "yacht", "subway_station"], cwd=root, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage: make edit", result.stderr)


if __name__ == "__main__":
    unittest.main()
