#!/usr/bin/env python3
"""
Platform v3.0 Step 0 — vocabulary crosswalk tests.

Two things are protected here.

The first is integrity: a crosswalk row is an assertion that a user's word means a
particular entity, and a wrong one silently redirects that user with nothing
downstream able to detect it. So every row must name the matcher that produced it,
every resolved row must point at a real entity of the right type, and every
unresolved row must point at nothing.

The second is honesty about coverage. `test_onboarding_resolve_rate_is_reported`
does not assert a target — it asserts that the number is computed and published,
because the temptation when a rate is disappointing is to stop measuring it.
"""

import csv
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOCAB = ROOT / "governance" / "vocabulary"
sys.path.insert(0, str(ROOT))

KINDS = ("skill", "sector", "district")
TARGET_TYPE = {"skill": "Skill", "sector": "Industry", "district": "District"}
NO_COUNTERPART = "NO_COUNTERPART"
METHODS = {"EXACT_NAME", "ALIAS", "PREFIX", "FUZZY", "CURATED", NO_COUNTERPART}


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class ArtifactTest(unittest.TestCase):
    def test_all_three_crosswalks_exist_and_are_populated(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                path = VOCAB / f"{kind}_crosswalk.csv"
                self.assertTrue(path.exists(), f"{path.name} is missing")
                self.assertTrue(read(path), f"{path.name} is empty")

    def test_summary_exists(self):
        self.assertTrue((VOCAB / "crosswalk_summary.json").exists())


class IntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {k: read(VOCAB / f"{k}_crosswalk.csv") for k in KINDS}
        cls.entities = {e["global_entity_id"]: e for e in read(
            ROOT / "knowledge_graph" / "entities" / "entities.csv")}

    def test_every_row_names_its_matcher(self):
        """A row with no recorded method is a guess wearing a decision's clothes."""
        for kind, rows in self.rows.items():
            for r in rows:
                with self.subTest(kind=kind, term=r["source_term"]):
                    self.assertIn(r["match_method"], METHODS)

    def test_resolved_rows_point_at_a_real_entity(self):
        for kind, rows in self.rows.items():
            for r in rows:
                if r["match_method"] == NO_COUNTERPART:
                    continue
                with self.subTest(kind=kind, term=r["source_term"]):
                    self.assertIn(r["global_entity_id"], self.entities,
                                  f"{r['source_term']!r} points at a missing entity")

    def test_resolved_rows_point_at_the_right_entity_type(self):
        for kind, rows in self.rows.items():
            for r in rows:
                if r["match_method"] == NO_COUNTERPART:
                    continue
                with self.subTest(kind=kind, term=r["source_term"]):
                    self.assertEqual(self.entities[r["global_entity_id"]]["entity_type"],
                                     TARGET_TYPE[kind])

    def test_unresolved_rows_point_at_nothing(self):
        """The constraint migration 009 enforces, checked at the source."""
        for kind, rows in self.rows.items():
            for r in rows:
                if r["match_method"] != NO_COUNTERPART:
                    continue
                with self.subTest(kind=kind, term=r["source_term"]):
                    self.assertEqual(r["global_entity_id"], "")
                    self.assertEqual(r["canonical_name"], "")

    def test_denormalised_name_agrees_with_the_id(self):
        """Same check the packages run: a name column must agree with its id."""
        for kind, rows in self.rows.items():
            for r in rows:
                if not r["global_entity_id"]:
                    continue
                with self.subTest(kind=kind, term=r["source_term"]):
                    self.assertEqual(r["canonical_name"],
                                     self.entities[r["global_entity_id"]]["canonical_name"])

    def test_no_duplicate_terms_within_a_vocabulary(self):
        for kind, rows in self.rows.items():
            seen = [(r["source_vocab"], r["normalised_term"]) for r in rows]
            with self.subTest(kind=kind):
                self.assertEqual(len(seen), len(set(seen)))

    def test_every_unresolved_row_explains_itself(self):
        for kind, rows in self.rows.items():
            for r in rows:
                if r["match_method"] != NO_COUNTERPART:
                    continue
                with self.subTest(kind=kind, term=r["source_term"]):
                    self.assertTrue(r["notes"].strip(),
                                    "an unresolved term must say why")

    def test_fuzzy_matches_clear_the_declared_threshold(self):
        from governance.vocabulary.build_crosswalk import FUZZY_THRESHOLD
        for kind, rows in self.rows.items():
            for r in rows:
                if r["match_method"] == "FUZZY":
                    with self.subTest(term=r["source_term"]):
                        self.assertGreaterEqual(float(r["match_score"]), FUZZY_THRESHOLD)


class CuratedOverrideTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads((VOCAB / "curated_overrides.json").read_text())
        cls.entities = {e["global_entity_id"]: e for e in read(
            ROOT / "knowledge_graph" / "entities" / "entities.csv")}

    def test_every_override_carries_a_reason(self):
        """A curated row is a person's assertion and must be reviewable as one."""
        for kind, entries in self.raw.items():
            if kind.startswith("_"):
                continue
            for term, entry in entries.items():
                with self.subTest(kind=kind, term=term):
                    self.assertTrue(entry.get("reason", "").strip())

    def test_override_targets_exist_and_have_the_right_type(self):
        for kind, entries in self.raw.items():
            if kind.startswith("_"):
                continue
            for term, entry in entries.items():
                with self.subTest(kind=kind, term=term):
                    gid = entry["global_entity_id"]
                    self.assertIn(gid, self.entities)
                    self.assertEqual(self.entities[gid]["entity_type"], TARGET_TYPE[kind])

    def test_multi_candidate_entries_stay_unresolved(self):
        """A term spanning several entities must not be forced to one of them."""
        for kind, entries in self.raw.get("_multi_candidate", {}).items():
            rows = {r["source_term"]: r for r in read(VOCAB / f"{kind}_crosswalk.csv")}
            for term, entry in entries.items():
                with self.subTest(kind=kind, term=term):
                    self.assertTrue(entry.get("reason", "").strip())
                    for gid in entry.get("candidates", []):
                        self.assertIn(gid, self.entities)
                    row = rows.get(term)
                    if row:
                        self.assertEqual(row["match_method"], NO_COUNTERPART)
                        self.assertTrue(row["notes"].startswith("MULTI:"))

    def test_a_term_is_not_both_curated_and_multi(self):
        for kind in KINDS:
            curated = set(self.raw.get(kind, {}))
            multi = set(self.raw.get("_multi_candidate", {}).get(kind, {}))
            with self.subTest(kind=kind):
                self.assertEqual(curated & multi, set())


class CoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads((VOCAB / "crosswalk_summary.json").read_text())

    def test_onboarding_resolve_rate_is_reported(self):
        """
        Deliberately asserts that the number EXISTS, not that it is high.

        It is 22.8% and the target is 60%. The gap is a Package006 collection
        problem, not a matching problem — 50 skills users are nudged to claim have
        no counterpart in the knowledge base at all. Asserting a threshold here
        would fail the build for a data gap the build cannot fix; the risk worth
        guarding against is that the number quietly stops being measured.
        """
        s = self.summary
        self.assertIn("onboarding_skill_resolve_pct", s)
        self.assertGreater(s["onboarding_skill_terms"], 0)
        self.assertEqual(
            round(100 * s["onboarding_skill_resolved"] / s["onboarding_skill_terms"], 1),
            s["onboarding_skill_resolve_pct"])

    def test_districts_fully_resolve(self):
        """Districts are the one vocabulary with no data gap, so this one IS a floor."""
        self.assertEqual(self.summary["by_kind"]["district"]["no_counterpart"], 0,
                         "a district failed to resolve; the crosswalk regressed")

    def test_counts_reconcile(self):
        s = self.summary
        self.assertEqual(s["resolved_total"] + s["no_counterpart_total"], s["terms_total"])
        for kind, p in s["by_kind"].items():
            with self.subTest(kind=kind):
                self.assertEqual(p["resolved"] + p["no_counterpart"], p["terms"])

    def test_collection_backlog_is_published(self):
        """The unresolved list is the Package006 collection backlog. It must be visible."""
        self.assertTrue(self.summary["collection_backlog"]["skill"])


class ReproducibilityTest(unittest.TestCase):
    def test_rebuild_matches_the_committed_files(self):
        r = subprocess.run(
            [sys.executable, "governance/vocabulary/build_crosswalk.py", "--check"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0,
                         f"committed crosswalks differ from a fresh build:\n{r.stdout[-1500:]}")


class MigrationTest(unittest.TestCase):
    """The migration is a projection of the CSVs; the two must not disagree."""

    @classmethod
    def setUpClass(cls):
        cls.sql = (ROOT / "frontend" / "migrations"
                   / "009_vocabulary_crosswalk.sql").read_text()

    def test_migration_exists_and_creates_the_table(self):
        self.assertIn("create table if not exists public.kg_vocabulary_map", self.sql)

    def test_check_constraint_covers_every_match_method(self):
        for m in METHODS:
            with self.subTest(method=m):
                self.assertIn(f"'{m}'", self.sql)

    def test_coherence_constraint_is_present(self):
        """Resolved rows point somewhere; unresolved ones do not — enforced in SQL."""
        self.assertIn("kg_vocab_resolution_is_coherent", self.sql)

    def test_rls_is_enabled(self):
        self.assertIn("enable row level security", self.sql)
        self.assertIn("is_valueweave_admin()", self.sql)

    def test_no_application_code_is_touched_by_this_step(self):
        """Step 0 adds a migration file. It must not edit a page or a component."""
        changed = subprocess.run(
            ["git", "diff", "--name-only", "main...HEAD"],
            cwd=ROOT, capture_output=True, text=True).stdout.split()
        offenders = [f for f in changed
                     if f.startswith("frontend/") and not f.startswith("frontend/migrations/")]
        self.assertEqual(offenders, [],
                         f"Step 0 modified application code: {offenders}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
