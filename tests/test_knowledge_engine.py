#!/usr/bin/env python3
"""
Work Package 6 — Knowledge Engine tests (recovery-focused).

The engine ships 117 unit tests of its own at `knowledge_engine/tests/`, which
cover its internal behaviour. Repeating them here would be duplication. What those
tests cannot cover is the thing v2.2 actually changed: whether the recovered engine
works *against this repository* — its real packages, its real conventions, its real
graph.

So these tests assert the recovery, not the engine:
  - every module named in the recovery imports
  - the compatibility check passes all nine of its checks
  - the engine's constants agree with the data actually in the packages
  - the source registry names collectors and parsers that really import
"""

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _history_is_truncated():
    """True when this clone cannot answer questions about the past.

    `actions/checkout@v4` fetches depth 1 by default. Tests that assert facts
    about history then fail on evidence the checkout discarded — and, worse,
    fail with a message blaming the code. This lets them say what is actually
    wrong instead.
    """
    out = subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                         cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        return True, "this directory is not a git repository"
    if out.stdout.strip() == "true":
        depth = subprocess.run(["git", "rev-list", "--count", "HEAD"],
                               cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return True, (f"this is a SHALLOW clone ({depth} commit(s)). CI must check "
                      f"out with `fetch-depth: 0` — see .github/workflows/")
    return False, ""


class RecoveryTest(unittest.TestCase):
    def test_all_62_recovered_files_are_tracked(self):
        out = subprocess.run(["git", "ls-files", "knowledge_engine"],
                             cwd=ROOT, capture_output=True, text=True).stdout
        tracked = [line for line in out.splitlines() if line.strip()]
        # 62 recovered from 71ac7e1, plus what v2.2 added on top.
        self.assertGreaterEqual(len(tracked), 62,
                                f"only {len(tracked)} knowledge_engine files are tracked")

    def test_history_was_preserved_not_recopied(self):
        """A file recovered by merge keeps its original commit; a copied one does not."""
        out = subprocess.run(
            ["git", "log", "--format=%h", "--", "knowledge_engine/core/types.py"],
            cwd=ROOT, capture_output=True, text=True).stdout.split()
        if "71ac7e1" in out:
            return

        # Still a failure — never a skip. But say which failure it is: a shallow
        # clone means the evidence is absent, not that the claim is false, and
        # the original message accused the repository of a regression that had
        # not happened.
        truncated, why = _history_is_truncated()
        self.fail(
            f"cannot see 71ac7e1 in the history of knowledge_engine/core/types.py.\n"
            + (f"  CAUSE: {why}\n"
               f"  The history exists; this checkout does not have it.\n"
               if truncated else
               "  History is complete, so this is real: the engine was re-added "
               "rather than recovered, and its provenance is lost.\n")
            + f"  commits seen for that file: {out or 'none'}")

    def test_every_declared_module_imports(self):
        import importlib
        for name in ["core.types", "core.provenance", "collectors", "parsers",
                     "validation", "provenance", "package_builder", "versioning",
                     "update_engine", "rule_engine"]:
            with self.subTest(module=name):
                importlib.import_module(f"knowledge_engine.{name}")


class CompatibilityTest(unittest.TestCase):
    """The compatibility report is generated; these tests assert what it must say."""

    @classmethod
    def setUpClass(cls):
        result = subprocess.run([sys.executable, "knowledge_engine/check_compatibility.py"],
                                cwd=ROOT, capture_output=True, text=True)
        cls.exit_code = result.returncode
        cls.report = json.loads(
            (ROOT / "knowledge_engine" / "compatibility_report.json").read_text())

    def test_check_exits_clean(self):
        self.assertEqual(self.exit_code, 0)

    def test_all_nine_checks_pass(self):
        failed = [c["check"] for c in self.report["checks"] if c["status"] != "PASS"]
        self.assertEqual(failed, [], f"failing compatibility checks: {failed}")
        self.assertEqual(self.report["passed"], 9)
        self.assertEqual(self.report["result"], "COMPATIBLE")

    def test_engine_sentinel_matches_the_packages(self):
        from knowledge_engine.core.types import PENDING_VERIFICATION
        self.assertEqual(PENDING_VERIFICATION, "PENDING_VERIFICATION")

    def test_verification_enum_covers_observed_values(self):
        from knowledge_engine.core.types import VerificationStatus
        observed = set()
        for pkg in sorted(p for p in (ROOT / "packages").iterdir() if p.is_dir()):
            ds = pkg / "datasets"
            for f in sorted(ds.glob("*.csv")) if ds.exists() else []:
                with open(f, newline="", encoding="utf-8") as fh:
                    for row in csv.DictReader(fh):
                        v = (row.get("verification_status") or "").strip()
                        if v:
                            observed.add(v)
        self.assertTrue(observed.issubset({s.value for s in VerificationStatus}),
                        f"packages use statuses the engine does not model: "
                        f"{observed - {s.value for s in VerificationStatus}}")

    def test_every_dataset_can_receive_a_provenance_record(self):
        """ProvenanceRecord emits six columns; every dataset must have all six."""
        mandatory = {"data_source", "source_url", "collection_date",
                     "confidence_score", "verification_status", "notes"}
        missing = []
        for pkg in sorted(p for p in (ROOT / "packages").iterdir() if p.is_dir()):
            ds = pkg / "datasets"
            for f in sorted(ds.glob("*.csv")) if ds.exists() else []:
                with open(f, newline="", encoding="utf-8") as fh:
                    header = set(next(csv.reader(fh), []))
                if not mandatory.issubset(header):
                    missing.append(f"{pkg.name}/{f.name}: {sorted(mandatory - header)}")
        self.assertEqual(missing, [], f"datasets missing provenance columns: {missing}")


class SourceRegistryTest(unittest.TestCase):
    def test_assigned_collectors_and_parsers_import(self):
        path = ROOT / "source_registry" / "sources.csv"
        if not path.exists():
            self.skipTest("source registry not built")
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        seen = set()
        for r in rows:
            for dotted in (r["collector"], r["parser"]):
                if dotted == "PENDING_IMPLEMENTATION" or dotted in seen:
                    continue
                seen.add(dotted)
                module, _, cls = dotted.rpartition(".")
                mod = __import__(module, fromlist=[cls])
                self.assertTrue(hasattr(mod, cls),
                                f"sources.csv names {dotted}, which does not exist")
        self.assertTrue(seen, "no collector or parser was assigned to any source")


if __name__ == "__main__":
    unittest.main(verbosity=2)
