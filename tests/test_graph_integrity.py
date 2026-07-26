#!/usr/bin/env python3
"""Work Package 6 — Graph integrity tests.

`validate_graph.py` is the authority on graph correctness and runs 11 checks. These
tests do two things it does not: they assert that the validator itself still passes
(so integrity failures surface in the test run, not only in a manual invocation),
and they assert the invariants that v2.2 newly depends on — G11's scheme ownership,
and the graph properties the API and search layers assume.
"""

import csv
import json
import re
import subprocess
import sys
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KG = ROOT / "knowledge_graph"
sys.path.insert(0, str(ROOT))


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class ValidatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = subprocess.run([sys.executable, "knowledge_graph/validate_graph.py"],
                                    cwd=ROOT, capture_output=True, text=True)
        cls.summary = json.loads((KG / "validation_summary.json").read_text())

    def test_validator_exits_clean(self):
        self.assertEqual(self.result.returncode, 0,
                         f"validate_graph.py failed:\n{self.result.stdout[-3000:]}")

    def test_zero_violations(self):
        self.assertEqual(self.summary["violations"], 0)
        self.assertEqual(self.summary["result"], "PASS")

    def test_g11_runs_and_governs_every_domain_scheme_row(self):
        self.assertIn("G11-SCHEME_OWNERSHIP", self.summary["checks_run"])
        self.assertEqual(self.summary["domain_scheme_rows_governed"], 79)
        self.assertEqual(self.summary["domain_scheme_rows_deprecated_reference"], 21)

    def test_all_eleven_checks_ran(self):
        self.assertEqual(len(self.summary["checks_run"]), 11)


class GraphStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entities = read(KG / "entities" / "entities.csv")
        cls.edges = read(KG / "relationships" / "relationships.csv")
        cls.by_gid = {e["global_entity_id"]: e for e in cls.entities}

    def test_entity_ids_are_unique(self):
        ids = [e["global_entity_id"] for e in self.entities]
        self.assertEqual(len(ids), len(set(ids)))

    def test_entity_ids_are_well_formed(self):
        for e in self.entities:
            with self.subTest(gid=e["global_entity_id"]):
                self.assertRegex(e["global_entity_id"], r"^vw:[a-z0-9-]+:[a-z0-9-]+$")

    def test_no_dangling_edges(self):
        dangling = [r["relationship_id"] for r in self.edges
                    if r["from_entity"] not in self.by_gid
                    or r["to_entity"] not in self.by_gid]
        self.assertEqual(dangling, [])

    def test_no_self_loops(self):
        self.assertEqual([r["relationship_id"] for r in self.edges
                          if r["from_entity"] == r["to_entity"]], [])

    def test_no_duplicate_edge_triples(self):
        seen = defaultdict(int)
        for r in self.edges:
            seen[(r["from_entity"], r["relationship_type"], r["to_entity"])] += 1
        self.assertEqual({k: v for k, v in seen.items() if v > 1}, {})

    def test_every_edge_has_provenance(self):
        for r in self.edges:
            with self.subTest(rel=r["relationship_id"]):
                self.assertTrue(r["provenance_package"])
                self.assertTrue(r["provenance_dataset"])
                self.assertTrue(r["provenance_row_id"])

    def test_confidence_is_an_integer_in_range(self):
        for e in self.entities:
            with self.subTest(gid=e["global_entity_id"]):
                self.assertTrue(0 <= int(e["confidence_score"]) <= 100)
        for r in self.edges:
            with self.subTest(rel=r["relationship_id"]):
                self.assertTrue(0 <= int(r["confidence"]) <= 100)

    def test_every_entity_names_a_real_package(self):
        dirs = {p.name for p in (ROOT / "packages").iterdir() if p.is_dir()}
        for e in self.entities:
            with self.subTest(gid=e["global_entity_id"]):
                self.assertIn(e["source_package"], dirs)


class CrossPackageReferenceTest(unittest.TestCase):
    """Zero broken cross-package references was v2.1's strongest finding. v2.2 added
    a new reference column, so the property is re-checked rather than assumed."""

    def test_package007_scheme_ids_all_resolve(self):
        canonical = {r["scheme_id"] for r in read(
            ROOT / "packages" / "Package007_Government_Schemes" / "datasets"
            / "government_schemes.csv")}
        broken = []
        for pkg in sorted(p for p in (ROOT / "packages").iterdir() if p.is_dir()):
            ds = pkg / "datasets"
            for f in sorted(ds.glob("*.csv")) if ds.exists() else []:
                rows = read(f)
                if not rows or "package007_scheme_id" not in rows[0]:
                    continue
                for i, r in enumerate(rows, start=2):
                    v = r["package007_scheme_id"]
                    if v and v != "PENDING_VERIFICATION" and v not in canonical:
                        broken.append(f"{pkg.name}/{f.name}:{i} -> {v}")
        self.assertEqual(broken, [], f"broken package007_scheme_id references: {broken}")


class GraphRebuildTest(unittest.TestCase):
    """The graph is derived (ADR-001). Rebuilding it must be idempotent, or the
    'derived' claim is false and some state is hiding in the artifacts."""

    ARTIFACTS = ["entities/entities.csv", "entities/aliases.csv",
                 "relationships/relationships.csv"]

    def test_rebuild_is_idempotent(self):
        """Compare the artifacts to themselves across a rebuild, not to `main`.

        Comparing to `main` would only prove the graph has not changed since the
        last commit — and it always has, because `derived_at` carries the build
        date. What matters is that building twice from the same packages produces
        the same bytes.
        """
        before = {a: (KG / a).read_text() for a in self.ARTIFACTS}
        subprocess.run([sys.executable, "knowledge_graph/build_graph.py"],
                       cwd=ROOT, capture_output=True, text=True, check=True)
        for a in self.ARTIFACTS:
            with self.subTest(artifact=a):
                self.assertEqual((KG / a).read_text(), before[a],
                                 f"rebuilding changed {a}: the graph is not purely derived")

    def test_entity_count_is_stable_across_a_rebuild(self):
        before = len(read(KG / "entities" / "entities.csv"))
        subprocess.run([sys.executable, "knowledge_graph/build_graph.py"],
                       cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(len(read(KG / "entities" / "entities.csv")), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
