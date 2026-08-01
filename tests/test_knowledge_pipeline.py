#!/usr/bin/env python3
"""
Knowledge → Database pipeline: the audit's findings, held in place.

WHAT THE AUDIT FOUND
--------------------
The pipeline from Packages 001-008 to Supabase is complete, correct and covered
by 114 tests. It had never been executed. The only evidence of any run in the
whole repository was two lines in `knowledge_sync/state/sync_log.jsonl`, both
`"mode": "dry-run"`, both `"applied": false` — and there was no CI at all, so
nothing was ever going to invoke it.

That is why production shows "This information is being prepared" everywhere:
the code is right and the tables are empty.

WHAT THESE TESTS ARE FOR
------------------------
Three things, none of which any existing test covered:

1.  Every source file the sync reads must exist. A package dataset renamed or
    moved breaks the import at run time, in CI, after a merge — the slowest
    possible place to find out.

2.  The invocation must exist and must stay honest. A workflow that plans but
    never applies, or that verifies with the service-role key, would look like
    a working pipeline and deliver an empty database.

3.  The coverage the audit measured must not silently get worse.

    python3 tests/run_all.py --suite knowledge_pipeline
"""

import csv
import json
import re
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from knowledge_sync.config import TABLE_SPECS  # noqa: E402

WORKFLOW = ROOT / ".github" / "workflows" / "knowledge-sync.yml"
ENTITIES = ROOT / "knowledge_graph" / "entities" / "entities.csv"
RELATIONSHIPS = ROOT / "knowledge_graph" / "relationships" / "relationships.csv"


def rows(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ═══════════════════════════════════════════ 1. the pipeline can actually read
class PipelineSourcesTest(unittest.TestCase):
    """Every file the sync reads must be there, and must have rows.

    `knowledge_sync/config.py` names 12 source files by path across 8 table
    specs. Nothing checked they exist. A dataset renamed during a package
    revision would pass every existing test and fail at import time — in CI,
    after a merge, against production.
    """

    def test_every_declared_source_file_exists(self):
        missing = []
        for spec in TABLE_SPECS:
            for src in spec.sources:
                if not Path(src.path).exists():
                    missing.append(f"{spec.name} <- {src.path}")
        self.assertEqual(missing, [], "sync sources that do not exist:\n  "
                                      + "\n  ".join(missing))

    def test_every_source_file_has_rows(self):
        """An empty CSV imports cleanly and delivers nothing."""
        empty = []
        for spec in TABLE_SPECS:
            for src in spec.sources:
                p = Path(src.path)
                if p.exists() and len(rows(p)) == 0:
                    empty.append(f"{spec.name} <- {p.name}")
        self.assertEqual(empty, [], f"source files with no data rows: {empty}")

    def test_the_key_column_exists_in_every_source(self):
        """The key column is how change detection identifies a row."""
        bad = []
        for spec in TABLE_SPECS:
            for src in spec.sources:
                p = Path(src.path)
                if not p.exists():
                    continue
                header = rows(p)[0].keys() if rows(p) else []
                if src.key_column not in header:
                    bad.append(f"{spec.name}: {p.name} has no '{src.key_column}'")
        self.assertEqual(bad, [], "\n  ".join(bad))

    def test_every_package_with_entities_also_feeds_a_detail_table(self):
        """Entities carry identity; detail tables carry what a user reads.

        The axis is the SOURCE FILES, not `owner_package`. Package004's four
        business datasets feed `kg_businesses`, which Package008 owns — checking
        ownership would have wrongly reported Package004 as unprojected. (It did,
        on the first run of this test.)

        Package002 is genuinely absent: its 66 Institution entities reach the
        graph but no detail table, so an institution page shows a name and its
        links and nothing else. Package003 produces no entities at all. Both are
        pinned here so that fixing either registers as a change.
        """
        feeding = {part for spec in TABLE_SPECS for src in spec.sources
                   for part in Path(src.path).parts if part.startswith("Package")}
        with_entities = {r["source_package"] for r in rows(ENTITIES)}

        self.assertEqual(
            sorted(with_entities - feeding), ["Package002_Education"],
            "packages whose entities exist but whose detail rows are not projected")
        self.assertNotIn("Package003_Healthcare", with_entities,
                         "Package003 contributes no entities; if it now does, it "
                         "also needs a TableSpec")


# ═══════════════════════════════════════════ 2. something has to invoke it
class InvocationTest(unittest.TestCase):
    """A pipeline nothing calls is a pipeline that has never run."""

    @classmethod
    def setUpClass(cls):
        cls.src = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""

    def test_a_workflow_exists(self):
        self.assertTrue(WORKFLOW.exists(),
                        "nothing in the repository invokes the import; that is why "
                        "the production tables are empty")

    def test_it_runs_when_the_research_changes(self):
        """A package edit and a live database that disagree is the bug."""
        for path in ("packages/**", "knowledge_graph/**", "knowledge_sync/**"):
            with self.subTest(path=path):
                self.assertIn(path, self.src)

    def test_it_applies_and_does_not_only_plan(self):
        """A plan-only workflow looks green and delivers nothing."""
        runs = [l.split("run:", 1)[1].strip()
                for l in self.src.splitlines() if l.strip().startswith("run:")]
        self.assertIn("scripts/run_sync.sh --plan-only", runs)
        self.assertIn("scripts/run_sync.sh", runs,
                      "the workflow must apply, not only plan")

    def test_it_fails_loudly_when_the_secrets_are_absent(self):
        """Half-running against no database is worse than not starting."""
        self.assertIn("SUPABASE_SERVICE_ROLE_KEY", self.src)
        self.assertIn("::error::Missing repository secrets", self.src)

    def test_the_service_role_key_comes_only_from_secrets(self):
        """It bypasses RLS. It must never be inlined or made public.

        Checked line by line rather than with a lookahead: `\\s*(?!...)` lets the
        `\\s*` match zero characters, so the lookahead fires against the space and
        passes on a value that is perfectly fine. It reported a false failure
        here first time round.
        """
        for line in self.src.splitlines():
            stripped = line.strip()
            if not stripped.startswith("SUPABASE_SERVICE_ROLE_KEY:"):
                continue
            value = stripped.split(":", 1)[1].strip()
            with self.subTest(line=stripped):
                self.assertTrue(
                    value.startswith("${{ secrets."),
                    f"the service role key must come from a secret, got: {value}")
        self.assertNotIn("NEXT_PUBLIC_SUPABASE_SERVICE", self.src)

    def test_verification_uses_the_anon_key(self):
        """The service role can read a schema the browser cannot.

        Verifying with it would report a healthy deployment while every page
        rendered empty — the exact failure this sprint was called to diagnose.
        """
        self.assertIn("NEXT_PUBLIC_SUPABASE_ANON_KEY", self.src)
        self.assertIn("scripts/health_check.sh", self.src)

    def test_the_checkout_fetches_full_history(self):
        """`actions/checkout@v4` defaults to depth 1, and two tests need more.

        `test_history_was_preserved_not_recopied` proves the knowledge engine was
        recovered by merge rather than re-added by copy.
        `test_no_page_lost_more_than_a_handful_of_lines` measures Step 2's own
        commit. Neither can see anything in a one-commit clone, and the first one
        failed by accusing the repository of a regression that had not happened.

        Reproduced by cloning this repository with `--depth 1` and running the
        suite: same two suites, same two failures as CI reported.
        """
        self.assertIn("fetch-depth: 0", self.src,
                      "CI must check out full history; two suites assert facts "
                      "about the past and a depth-1 clone throws it away")

    def test_two_syncs_cannot_run_at_once(self):
        self.assertIn("concurrency:", self.src)
        self.assertIn("cancel-in-progress: false", self.src)


# ═══════════════════════════════════════════ 3. coverage must not regress
class CoverageTest(unittest.TestCase):
    """What the frontend will actually be able to show, once the import runs.

    Running the import is necessary and not sufficient: 34 of 61 districts have
    no incoming edge at all, so most district pages would stay near-empty even
    on a perfectly synced database. These numbers are asserted as floors so the
    next graph change can only improve them.
    """

    @classmethod
    def setUpClass(cls):
        cls.entities = rows(ENTITIES)
        cls.rels = rows(RELATIONSHIPS)
        cls.incoming = defaultdict(list)
        for r in cls.rels:
            cls.incoming[r["to_entity"]].append(r)

    def test_the_research_that_the_import_would_publish(self):
        self.assertGreaterEqual(len(self.entities), 647)
        self.assertGreaterEqual(len(self.rels), 865)

    def test_every_expansion_card_has_research_behind_it(self):
        """Each card the frontend marks LIVE must have rows to be live with."""
        counts = Counter(r["entity_type"] for r in self.entities)
        for entity_type, floor in [
            ("Skill", 45), ("Certification", 30), ("TrainingProvider", 25),
            ("BusinessOpportunity", 45), ("Machinery", 69), ("RawMaterial", 21),
            ("ExportCountry", 29), ("Market", 11), ("FinancialInstitution", 21),
            ("Institution", 66),
        ]:
            with self.subTest(entity_type=entity_type):
                self.assertGreaterEqual(counts[entity_type], floor)

    def test_district_link_coverage_is_recorded_not_assumed(self):
        """The number that decides whether a district page has anything on it."""
        districts = [e for e in self.entities if e["entity_type"] == "District"]
        linked = [d for d in districts
                  if self.incoming[d["global_entity_id"]]]
        self.assertEqual(len(districts), 61)
        # 27 of 61 as measured. A floor, so recovery work shows as a pass.
        self.assertGreaterEqual(
            len(linked), 27,
            "districts with at least one linked record — the audit measured 27 "
            "of 61, which is why most district pages stay sparse after a sync")

    def test_the_search_terms_the_audit_checked_still_resolve(self):
        """`searchKnowledge()` ilikes canonical_name and nothing else.

        Five of the six terms the brief named return results. "Dairy" returns
        zero despite appearing in 11 package rows, because it lives in
        descriptions and category names that the entity registry does not carry.
        Asserted exactly as measured — including the miss, so that closing it
        registers as a change rather than passing unnoticed.
        """
        names = [e["canonical_name"].lower() for e in self.entities]
        for term, expected_min in [("construction", 4), ("electrician", 2),
                                   ("solar", 6), ("bakery", 1), ("robot", 6)]:
            with self.subTest(term=term):
                self.assertGreaterEqual(sum(term in n for n in names), expected_min)
        self.assertEqual(
            sum("dairy" in n for n in names), 0,
            "if this now matches, entity search reaches beyond canonical_name — "
            "update SEARCH_PIPELINE_REPORT.md and remove this assertion")


if __name__ == "__main__":
    unittest.main(verbosity=2)
