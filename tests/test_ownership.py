#!/usr/bin/env python3
"""
Work Package 6 — Ownership rule tests (ADR-003).

The point of these tests is that the ADR-003 decision cannot decay quietly. A
governance decision recorded only in a Markdown file drifts the moment someone
adds a scheme row and forgets; these tests fail the build instead.

They check the decision from both ends: that the crosswalk is internally sound,
and that the five domain datasets actually carry what the decision requires.
"""

import csv
import sys
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PV = "PENDING_VERIFICATION"
DEPRECATED = "DEPRECATED_REFERENCE"
DOMAIN_CANONICAL = "DOMAIN_CANONICAL"

DOMAIN_SCHEME_DATASETS = {
    "Package002_Education": "scholarships.csv",
    "Package003_Healthcare": "government_health_insurance_schemes.csv",
    "Package004_Industries": "msme_entrepreneurship_support_schemes.csv",
    "Package005_Agriculture": "agriculture_schemes.csv",
    "Package006_Skills_and_Training": "government_skill_schemes.csv",
}


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class OwnershipRegistryTest(unittest.TestCase):
    def setUp(self):
        self.registry = read(ROOT / "knowledge_graph" / "ownership" / "ownership_registry.csv")
        self.overlaps = read(ROOT / "knowledge_graph" / "ownership" / "known_overlaps.csv")

    def test_every_entity_type_has_exactly_one_owner(self):
        owners = defaultdict(set)
        for row in self.registry:
            owners[row["entity_type"]].add(row["owner_package"])
        multi = {k: sorted(v) for k, v in owners.items() if len(v) > 1}
        self.assertEqual(multi, {}, f"entity types with more than one owner: {multi}")

    def test_package007_owns_government_scheme(self):
        row = next(r for r in self.registry if r["entity_type"] == "GovernmentScheme")
        self.assertEqual(row["owner_package"], "Package007_Government_Schemes")

    def test_adr_003_overlap_is_resolved(self):
        row = next(r for r in self.overlaps if r["adr"] == "ADR-003")
        self.assertEqual(row["status"], "RESOLVED",
                         "ADR-003 is decided; known_overlaps.csv must say so")

    def test_remaining_unresolved_overlaps_are_declared_and_attributed(self):
        """Honesty check: anything still open must name the ADR that owns it."""
        unresolved = [r for r in self.overlaps if r["status"] == "UNRESOLVED"]
        for r in unresolved:
            with self.subTest(entity_type=r["entity_type"]):
                self.assertTrue(r["adr"].startswith("ADR-"),
                                f"{r['entity_type']} is UNRESOLVED with no ADR")
                self.assertNotEqual(r["adr"], "ADR-003",
                                    "ADR-003 must no longer own an unresolved overlap")


class SchemeCrosswalkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.crosswalk = read(ROOT / "governance" / "ownership" / "scheme_crosswalk.csv")
        cls.canonical = {r["scheme_id"] for r in read(
            ROOT / "packages" / "Package007_Government_Schemes" / "datasets"
            / "government_schemes.csv")}

    def test_every_domain_scheme_row_appears_exactly_once(self):
        seen = defaultdict(int)
        for c in self.crosswalk:
            seen[(c["domain_package"], c["domain_dataset"], c["domain_row_id"])] += 1
        dupes = {k: v for k, v in seen.items() if v > 1}
        self.assertEqual(dupes, {}, f"duplicated crosswalk rows: {dupes}")

        for pkg, dataset in DOMAIN_SCHEME_DATASETS.items():
            rows = read(ROOT / "packages" / pkg / "datasets" / dataset)
            covered = sum(1 for c in self.crosswalk if c["domain_package"] == pkg)
            self.assertEqual(covered, len(rows),
                             f"{pkg}/{dataset}: {len(rows)} rows but {covered} crosswalk entries")

    def test_matched_rows_point_at_a_real_canonical_scheme(self):
        for c in self.crosswalk:
            if c["scheme_ownership"] == DEPRECATED:
                with self.subTest(row=c["domain_row_id"]):
                    self.assertIn(c["package007_scheme_id"], self.canonical)

    def test_unmatched_rows_carry_the_bare_sentinel(self):
        for c in self.crosswalk:
            if c["scheme_ownership"] == DOMAIN_CANONICAL:
                with self.subTest(row=c["domain_row_id"]):
                    self.assertEqual(c["package007_scheme_id"], PV)

    def test_no_row_is_matched_without_a_named_method(self):
        for c in self.crosswalk:
            if c["scheme_ownership"] == DEPRECATED:
                with self.subTest(row=c["domain_row_id"]):
                    self.assertIn(c["match_method"],
                                  {"EXACT_NAME", "ACRONYM", "PORTAL", "FUZZY"},
                                  "a match with no recorded method is a guess")

    def test_fuzzy_matches_clear_the_declared_threshold(self):
        from governance.ownership.build_scheme_crosswalk import FUZZY_THRESHOLD
        for c in self.crosswalk:
            if c["match_method"] == "FUZZY":
                with self.subTest(row=c["domain_row_id"]):
                    self.assertGreaterEqual(float(c["match_score"]), FUZZY_THRESHOLD)


class DomainDatasetGovernanceTest(unittest.TestCase):
    """What the five domain datasets must carry, checked directly rather than
    inferred from the crosswalk."""

    def test_governance_columns_present_and_valid(self):
        for pkg, dataset in DOMAIN_SCHEME_DATASETS.items():
            with self.subTest(package=pkg):
                rows = read(ROOT / "packages" / pkg / "datasets" / dataset)
                self.assertTrue(rows, f"{pkg}/{dataset} is empty")
                for col in ("package007_scheme_id", "scheme_ownership"):
                    self.assertIn(col, rows[0], f"{pkg}/{dataset} lacks {col}")
                for r in rows:
                    self.assertIn(r["scheme_ownership"], {DEPRECATED, DOMAIN_CANONICAL})

    def test_backward_compatibility_no_column_was_removed(self):
        """v2.2 appended two columns. Nothing may have been dropped to make room."""
        import io
        import subprocess
        for pkg, dataset in DOMAIN_SCHEME_DATASETS.items():
            rel = f"packages/{pkg}/datasets/{dataset}"
            before = subprocess.run(["git", "show", f"main:{rel}"], cwd=ROOT,
                                    capture_output=True, text=True)
            if before.returncode != 0:
                self.skipTest("main is not available for comparison")
            old_header = next(csv.reader(io.StringIO(before.stdout)), [])
            with open(ROOT / rel, newline="", encoding="utf-8") as f:
                new_header = next(csv.reader(f), [])
            with self.subTest(package=pkg):
                self.assertEqual(new_header[:len(old_header)], old_header,
                                 f"{rel}: existing columns changed order or were removed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
