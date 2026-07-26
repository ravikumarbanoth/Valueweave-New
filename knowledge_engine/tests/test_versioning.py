import json
import tempfile
import unittest
from pathlib import Path

from knowledge_engine.versioning import SemVer, VersionHistory


class SemVerTest(unittest.TestCase):
    def test_parse_simple(self):
        v = SemVer.parse("1.2.3")
        self.assertEqual((v.major, v.minor, v.patch, v.prerelease), (1, 2, 3, None))

    def test_parse_with_prerelease(self):
        v = SemVer.parse("1.0.0-RC1")
        self.assertEqual(v.prerelease, "RC1")
        self.assertEqual(str(v), "1.0.0-RC1")

    def test_invalid_string_raises(self):
        with self.assertRaises(ValueError):
            SemVer.parse("not-a-version")

    def test_prerelease_sorts_before_release(self):
        self.assertLess(SemVer.parse("1.0.0-RC1"), SemVer.parse("1.0.0"))

    def test_bump_major_resets_minor_and_patch(self):
        v = SemVer.parse("1.2.3")
        self.assertEqual(str(v.bump_major()), "2.0.0")

    def test_bump_minor_resets_patch(self):
        v = SemVer.parse("1.2.3")
        self.assertEqual(str(v.bump_minor()), "1.3.0")

    def test_bump_patch(self):
        v = SemVer.parse("1.2.3")
        self.assertEqual(str(v.bump_patch()), "1.2.4")

    def test_drop_prerelease(self):
        v = SemVer.parse("1.0.0-RC1")
        self.assertEqual(str(v.drop_prerelease()), "1.0.0")

    def test_ordering_across_versions(self):
        versions = [SemVer.parse(v) for v in ["1.0.0", "1.0.0-RC1", "0.9.0", "2.0.0"]]
        ordered = [str(v) for v in sorted(versions)]
        self.assertEqual(ordered, ["0.9.0", "1.0.0-RC1", "1.0.0", "2.0.0"])


class VersionHistoryTest(unittest.TestCase):
    def test_record_and_latest(self):
        history = VersionHistory()
        history.record("1.0.0-RC1", "Initial RC", {"version": "1.0.0-RC1"})
        history.record("1.0.0", "Promoted to stable", {"version": "1.0.0"})
        self.assertEqual(history.latest().version, "1.0.0")

    def test_duplicate_version_raises(self):
        history = VersionHistory()
        history.record("1.0.0", "First", {})
        with self.assertRaises(ValueError):
            history.record("1.0.0", "Second", {})

    def test_malformed_version_raises(self):
        history = VersionHistory()
        with self.assertRaises(ValueError):
            history.record("not-a-version", "x", {})

    def test_rollback_returns_manifest_snapshot(self):
        history = VersionHistory()
        history.record("1.0.0-RC1", "Initial RC", {"total_records": 63})
        history.record("1.0.0", "Enriched", {"total_records": 63, "columns": 36})
        self.assertEqual(history.rollback_to("1.0.0-RC1"), {"total_records": 63})

    def test_rollback_unknown_version_raises(self):
        history = VersionHistory()
        with self.assertRaises(KeyError):
            history.rollback_to("9.9.9")

    def test_all_versions_sorted(self):
        history = VersionHistory()
        history.record("1.1.0", "x", {})
        history.record("1.0.0", "y", {})
        self.assertEqual(history.all_versions(), ["1.0.0", "1.1.0"])

    def test_save_and_load_round_trip(self):
        history = VersionHistory()
        history.record("1.0.0-RC1", "Initial RC", {"a": 1})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.json"
            history.save(path)
            self.assertTrue(path.exists())
            loaded = VersionHistory.load(path)
            self.assertEqual(loaded.all_versions(), ["1.0.0-RC1"])
            self.assertEqual(loaded.get("1.0.0-RC1").change_summary, "Initial RC")

    def test_saved_file_is_valid_json(self):
        history = VersionHistory()
        history.record("1.0.0", "x", {"k": "v"})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.json"
            history.save(path)
            data = json.loads(path.read_text())
            self.assertIn("entries", data)


if __name__ == "__main__":
    unittest.main()
