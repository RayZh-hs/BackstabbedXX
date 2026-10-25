from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import release_notes


class ReleaseNotesTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        patcher = patch.object(release_notes, "ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.git("init", "-q")
        self.commit("Initial release")
        self.git("tag", "v1.0.0")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, text=True)

    def commit(self, subject):
        self.git("-c", "user.name=Release Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", subject)

    def test_every_new_commit_gets_one_note_and_the_correct_comparison(self):
        self.commit("fix: block killer gun pickup")
        self.commit("fix: restore map posters")
        self.git("tag", "v1.0.1-alpha")
        notes = release_notes.release_notes("v1.0.1-alpha", "owner/project")
        self.assertEqual(notes.count("fix: block killer gun pickup"), 1)
        self.assertEqual(notes.count("fix: restore map posters"), 1)
        self.assertNotIn("Initial release", notes)
        self.assertIn("/compare/v1.0.0...v1.0.1-alpha", notes)
        self.assertIn("Backstabbed++-map-v1.0.1-alpha.zip", notes)
        self.assertEqual(notes.count("/commit/"), 2)

    def test_first_release_includes_all_commits(self):
        notes = release_notes.release_notes("v1.0.0", "owner/project")
        self.assertIn("Initial release", notes)
        self.assertIn("/commits/v1.0.0", notes)
        self.assertNotIn("/compare/", notes)

    def test_an_earlier_tag_does_not_include_later_commits(self):
        self.commit("A future change")
        notes = release_notes.release_notes("v1.0.0", "owner/project")
        self.assertNotIn("A future change", notes)

    def test_missing_tag_or_invalid_repository_fails(self):
        with self.assertRaises(subprocess.CalledProcessError):
            release_notes.release_notes("v9.9.9", "owner/project")
        with self.assertRaises(ValueError):
            release_notes.release_notes("v1.0.0", "../project")


if __name__ == "__main__":
    unittest.main()
