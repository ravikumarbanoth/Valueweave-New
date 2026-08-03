#!/usr/bin/env python3
"""
Knowledge operations — priority, metrics, quality, integrity, the dashboard.

THE FINDING THIS MILESTONE STARTED FROM
----------------------------------------
Thirty admin pages, and not one of them looks at the knowledge platform. Every
table they read is `public.*` application data — opportunities, page_views,
search_events, research_articles, profiles — and the "Graph Dashboard" reads
lib/knowledge-graph.js, which is the older public.kg_* CMS tables.

So there was no admin view of the 647 entities, the eight packages, the
vocabulary crosswalk, the sync manifest, the collection queue, the source
registry or the stewardship ledger. The operational half of ValueWeave was
invisible from the panel it is operated from.

WHAT THESE TESTS HOLD
---------------------
  1  a reviewer sees the important thing first, and can see why
  2  every operational number is computed from committed artifacts, so it is
     reproducible — and a number that cannot be computed is UNKNOWN, never zero
  3  the dashboard adds no table, no query and no migration
  4  nothing here can publish, approve or write knowledge

    python3 tests/run_all.py --suite operations
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from collection import priority, review                              # noqa: E402
from ops import integrity, metrics, quality, report                  # noqa: E402

DASHBOARD = ROOT / "frontend" / "app" / "admin" / "knowledge-ops" / "page.js"
SNAPSHOT = ROOT / "frontend" / "lib" / "ops" / "snapshot.json"


def candidate(**kw):
    base = dict(candidate_id="s:1", source_id="s", source_name="S", item_key="1",
                title="T", url="u", published_at="", change="NEW",
                classified_as="News", classified_reason="", is_entity=False)
    base.update(kw)
    return review.Candidate(**base)


# ═══════════════════════════════ 1. feed priority
class PriorityTest(unittest.TestCase):

    def test_the_brief_s_own_ordering_comes_out_right(self):
        """The six worked examples, in the order the brief gives them."""
        cases = [
            ("Telangana Electronics Manufacturing Policy 2026 launched",
             "GovernmentScheme"),
            ("Prime Minister's Employment Generation Programme — new scheme launched",
             "GovernmentScheme"),
            ("National Skill Development Mission guidelines", "Skill"),
            ("Industry report on textile clusters", "Research"),
            ("Tender for supply of office furniture", "News"),
            ("Office circular regarding holiday list", "News"),
        ]
        scored = [(title, priority.score(candidate(title=title, classified_as=kind)).stars)
                  for title, kind in cases]
        stars = [s for _t, s in scored]
        self.assertEqual(stars, sorted(stars, reverse=True),
                         f"not in descending order: {scored}")
        self.assertGreaterEqual(stars[0], 4, "a state manufacturing policy is a five-star item")
        self.assertLessEqual(stars[-1], 2, "an office circular is a one-star item")

    def test_every_score_can_be_argued_with(self):
        """A priority decides what somebody spends their morning on. If they
        cannot see WHY, they cannot tell a good ranking from a broken one."""
        result = priority.score(candidate(title="New subsidy scheme for micro enterprises",
                                          classified_as="GovernmentScheme"))
        self.assertTrue(result.factors)
        for line in result.explain():
            self.assertRegex(line.strip(), r"^[+-]\d+\s+\S")

    def test_a_duplicate_sinks(self):
        base = candidate(title="Margin money subsidy scheme", classified_as="GovernmentScheme")
        dupe = candidate(title="Margin money subsidy scheme", classified_as="GovernmentScheme",
                         duplicate_of="s:0")
        self.assertLess(priority.score(dupe).score, priority.score(base).score)

    def test_an_amendment_rises(self):
        """Knowledge going stale is invisible; an amendment is the only signal
        that it has."""
        base = candidate(title="Solar rooftop subsidy guidelines", classified_as="GovernmentScheme")
        amended = candidate(title="Solar rooftop subsidy guidelines", supersedes="s:0",
                            classified_as="GovernmentScheme")
        self.assertGreater(priority.score(amended).score, priority.score(base).score)

    def test_recency_alone_cannot_lift_an_item_a_full_star(self):
        """An hourly feed would otherwise own the top of the queue forever."""
        now = datetime.now(timezone.utc)
        fresh = candidate(title="Office circular regarding parking",
                          published_at=now.isoformat())
        old = candidate(title="Office circular regarding parking",
                        published_at=(now - timedelta(days=200)).isoformat())
        self.assertLessEqual(priority.score(fresh, now=now).stars
                             - priority.score(old, now=now).stars, 1)

    def test_a_district_we_cover_is_recognised_from_the_graph(self):
        """Read from the graph, not hard-coded — both states have reorganised
        their districts recently."""
        districts = priority.district_names()
        self.assertIn("Medak", districts)
        with_district = candidate(title="Solar installation work in Medak district",
                                  classified_as="BusinessOpportunity")
        without = candidate(title="Solar installation work", classified_as="BusinessOpportunity")
        self.assertGreater(priority.score(with_district, districts=districts).score,
                           priority.score(without, districts=districts).score)

    def test_search_demand_reaches_the_queue(self):
        """The only factor that connects the review queue to real users rather
        than to our own taxonomy."""
        demand = {"battery recycling": 12.0}
        wanted = candidate(title="Battery recycling collection centre licences invited",
                           classified_as="BusinessOpportunity")
        other = candidate(title="Furniture polishing unit licences invited",
                          classified_as="BusinessOpportunity")
        self.assertGreater(priority.score(wanted, demand=demand).score,
                           priority.score(other, demand=demand).score)

    def test_the_queue_file_is_written_most_important_first(self):
        """The file is read by people as well as software."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "q.jsonl"
            review.save([
                candidate(candidate_id="a", priority=10, priority_stars=1,
                          state=review.NEEDS_REVIEW),
                candidate(candidate_id="b", priority=90, priority_stars=5,
                          state=review.NEEDS_REVIEW),
            ], path)
            order = [json.loads(line)["candidate_id"]
                     for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(order, ["b", "a"])


# ═══════════════════════════════ 2. metrics come from artifacts
class MetricsTest(unittest.TestCase):

    def test_the_overview_matches_the_graph_on_disk(self):
        entities = metrics.read_entities()
        overview = metrics.knowledge_overview()
        self.assertEqual(overview["entities"], len(entities))
        self.assertEqual(overview["relationships"], len(metrics.read_relationships()))

    def test_connectivity_counts_both_directions(self):
        """A district nothing points at but which points at forty things is not
        isolated; treating direction as significant reports half the graph as
        orphaned."""
        degree = metrics.degrees([{"from_entity": "a", "to_entity": "b"}])
        self.assertEqual(degree["a"], 1)
        self.assertEqual(degree["b"], 1)

    def test_a_missing_artifact_is_missing_and_not_zero(self):
        """"the crosswalk has 0 rows" and "the crosswalk summary has not been
        built" are different facts."""
        original = metrics.ARTIFACTS["crosswalk"]
        try:
            metrics.ARTIFACTS["crosswalk"] = Path("/nonexistent/nope.json")
            self.assertIsNone(metrics.load_artifact("crosswalk"))
        finally:
            metrics.ARTIFACTS["crosswalk"] = original

    def test_popularity_is_none_without_data(self):
        rows = metrics.entity_operations()
        self.assertTrue(rows)
        self.assertTrue(all(r["popularity"] is None for r in rows))

    def test_popularity_is_used_when_supplied(self):
        rows = metrics.entity_operations()
        target = rows[0]["global_entity_id"]
        supplied = metrics.entity_operations(popularity={target: 42})
        self.assertEqual(next(r["popularity"] for r in supplied
                              if r["global_entity_id"] == target), 42)

    def test_last_reviewed_is_none_because_nobody_has_reviewed(self):
        """The stewardship ledger holds only its header. A date here would be
        a date nobody earned."""
        ledger = (ROOT / "stewardship" / "review_ledger.csv").read_text(encoding="utf-8")
        self.assertEqual(len([line for line in ledger.splitlines() if line.strip()]), 1)
        self.assertTrue(all(r["last_reviewed"] is None
                            for r in metrics.entity_operations()))

    def test_demand_says_when_it_has_no_data(self):
        """An empty chart reads as "nobody searched for anything"."""
        self.assertFalse(metrics.demand(None)["has_data"])
        self.assertTrue(metrics.demand(
            [{"query": "x", "results_count": 0}])["has_data"])

    def test_the_snapshot_is_json_serialisable(self):
        json.dumps(metrics.snapshot(), default=str)


# ═══════════════════════════════ 3. the quality score
class QualityTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.result = quality.score()

    def test_an_unknown_dimension_is_excluded_rather_than_zeroed(self):
        """Scoring popularity zero would drag the total down for a reason about
        our instrumentation rather than about the knowledge."""
        popularity = next(d for d in self.result.dimensions if d.name == "popularity")
        self.assertIsNone(popularity.value)
        self.assertNotIn(popularity, self.result.known)
        mean = sum(d.value for d in self.result.known) / len(self.result.known)
        self.assertEqual(self.result.overall, round(mean, 1))

    def test_every_dimension_states_its_formula(self):
        for dimension in self.result.dimensions:
            with self.subTest(dimension=dimension.name):
                self.assertTrue(dimension.formula)
                self.assertTrue(dimension.detail)

    def test_verification_reports_the_empty_ledger_rather_than_hiding_it(self):
        """All 647 entities are VST-NEEDS_REVIEW because no steward has ever
        reviewed one. A score that rounded that up would be the single most
        misleading number on the dashboard."""
        verification = next(d for d in self.result.dimensions if d.name == "verification")
        self.assertEqual(verification.value, 0.0)
        self.assertIn("no steward", verification.detail)

    def test_source_diversity_measures_concentration_not_count(self):
        """Twenty sources of which one supplies 90% is more fragile than five
        supplying a fifth each, and a count cannot see that."""
        concentrated = quality._source_diversity(
            [{"source_package": "A"}] * 90 + [{"source_package": "B"}] * 10)
        even = quality._source_diversity(
            [{"source_package": "A"}] * 50 + [{"source_package": "B"}] * 50)
        self.assertLess(concentrated[0], even[0])

    def test_the_grade_is_a_letter(self):
        self.assertIn(self.result.grade, list("ABCDE") + ["UNKNOWN"])


# ═══════════════════════════════ 4. operational integrity
class IntegrityTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.result = integrity.check()

    def test_it_finds_what_the_graph_checks_pass_over(self):
        """G1–G11 pass. These are the failures that pass them."""
        validation = metrics.load_artifact("graph_validation") or {}
        self.assertEqual(validation.get("result"), "PASS")
        checks = {f.check for f in self.result.findings}
        self.assertIn("isolated_entities", checks)
        self.assertIn("missing_relationships", checks)

    def test_a_type_with_no_edges_at_all_is_named(self):
        """Certification: 30 rows, no edges, so nothing about a skill can ever
        lead to the certificate that proves it."""
        finding = next(f for f in self.result.findings
                       if f.check == "missing_relationships")
        self.assertIn("Certification", finding.detail)

    def test_broken_references_would_be_critical(self):
        result = integrity.check(
            entities=[{"global_entity_id": "a", "entity_type": "T",
                       "canonical_name": "A", "source_package": "P"}],
            relationships=[{"relationship_id": "r1", "from_entity": "a",
                            "to_entity": "missing"}])
        self.assertEqual(result.status, "critical")
        self.assertIn("broken_references", {f.check for f in result.findings})

    def test_a_graph_with_nothing_wrong_is_healthy(self):
        """The check must be capable of saying nothing is wrong, or it says
        nothing at all."""
        entities = [{"global_entity_id": f"e{i}", "entity_type": "District",
                     "canonical_name": f"E{i}", "source_package": "P"}
                    for i in range(4)]
        relationships = [{"relationship_id": f"r{i}", "from_entity": f"e{i}",
                          "to_entity": f"e{(i + 1) % 4}"} for i in range(4)]
        result = integrity.check(entities, relationships)
        self.assertEqual([f.check for f in result.findings
                          if f.check in ("isolated_entities", "broken_references",
                                         "missing_relationships")], [])

    def test_dead_link_checking_is_offline(self):
        """Fetching six hundred URLs on every dashboard render would be slow,
        rude and non-deterministic. This checks shape."""
        source = (ROOT / "ops" / "integrity.py").read_text(encoding="utf-8")
        code = "\n".join(line.split("#", 1)[0] for line in source.splitlines())
        for token in ("urlopen", "requests.get", "httpx"):
            with self.subTest(token=token):
                self.assertNotIn(token, code)


# ═══════════════════════════════ 5. the report
class ReportTest(unittest.TestCase):

    def test_it_renders_and_says_when_there_is_nothing_to_compare(self):
        text = report.render(metrics.snapshot(), previous=None)
        self.assertIn("first report, no comparison", text)
        self.assertIn("## Knowledge quality", text)

    def test_a_trend_appears_once_there_is_a_previous_week(self):
        snapshot = metrics.snapshot()
        previous = json.loads(json.dumps(snapshot, default=str))
        previous["quality"]["overall"] = (snapshot["quality"]["overall"] or 0) - 5
        text = report.render(snapshot, previous=previous)
        self.assertIn("was", text)

    def test_it_says_the_backlog_is_not_knowledge(self):
        text = report.render(metrics.snapshot(), previous=None)
        if "Research backlog" in text:
            self.assertIn("Gaps, not knowledge", text)

    def test_writing_leaves_both_halves(self):
        """The markdown a person reads and the JSON next week diffs against."""
        with tempfile.TemporaryDirectory() as tmp:
            path = report.write(metrics.snapshot(), report_dir=Path(tmp))
            self.assertTrue(path.exists())
            self.assertTrue(path.with_suffix(".json").exists())


# ═══════════════════════════════ 6. the dashboard
class DashboardTest(unittest.TestCase):

    def setUp(self):
        self.src = DASHBOARD.read_text(encoding="utf-8")

    def test_it_exists_and_is_in_the_admin_navigation(self):
        sidebar = (ROOT / "frontend" / "components" / "admin"
                   / "AdminSidebar.jsx").read_text(encoding="utf-8")
        self.assertIn("/admin/knowledge-ops", sidebar)

    def test_it_adds_no_table_and_no_migration(self):
        """This milestone's database impact is zero, and this is the assertion
        that keeps it zero."""
        self.assertIn("search_events", self.src)
        forbidden = ("create table", "insert into", "kg_entities", "rpc(")
        lowered = self.src.lower()
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, lowered)

    def test_the_only_query_it_makes_is_for_live_demand(self):
        """Everything else is the committed snapshot, so every number on the
        page is reproducible with one command."""
        self.assertEqual(re.findall(r'\.from\("(\w+)"\)', self.src), ["search_events"])
        self.assertIn('import snapshot from "@/lib/ops/snapshot.json"', self.src)

    def test_it_dates_itself(self):
        """A dashboard that does not date itself will one day show last month's
        numbers to somebody making a decision."""
        self.assertIn("generated_at", self.src)
        self.assertIn("ops.cli snapshot --write", self.src)

    def test_it_survives_the_query_failing(self):
        block = self.src[self.src.index("async function liveDemand"):]
        self.assertIn("catch", block[:block.index("\n}")])
        self.assertIn("return null", block[:block.index("\n}")])

    def test_the_committed_snapshot_is_current(self):
        """The page imports this file. A graph change without a regenerated
        snapshot leaves the dashboard showing yesterday's numbers, which is
        worse than showing none because it looks current.

        Skipped when the graph artifacts are dirty in the working tree. Some
        suites regenerate `knowledge_graph/*.csv` as a side effect — the
        long-standing churn deferred to the engineering cleanup sprint — and
        comparing a committed snapshot against a graph that changed mid-run
        would fail for a reason that has nothing to do with the snapshot. CI
        runs `ops.cli snapshot --check` on a clean checkout, where it is strict.
        """
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "knowledge_graph", "packages"],
            cwd=ROOT, capture_output=True, text=True, timeout=60).stdout.strip()
        if dirty:
            self.skipTest(f"graph artifacts modified in the working tree:\n{dirty}")
        result = subprocess.run(
            [sys.executable, "-m", "ops.cli", "snapshot", "--check"],
            cwd=ROOT, capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


# ═══════════════════════════════ 7. the boundary
class BoundaryTest(unittest.TestCase):

    def test_nothing_in_ops_writes_knowledge(self):
        """It reports on the platform. It does not change it."""
        forbidden = ("packages/", "kg_entities", "supabase", ".to_csv", "INSERT")
        for path in sorted((ROOT / "ops").glob("*.py")):
            body = path.read_text(encoding="utf-8")
            parts = body.split('"""')
            code = "".join(parts[i] for i in range(0, len(parts), 2))
            code = "\n".join(line.split("#", 1)[0] for line in code.splitlines())
            for token in forbidden:
                with self.subTest(path=path.name, token=token):
                    self.assertNotIn(token, code)

    def test_ops_never_opens_a_network_connection(self):
        """Live signals are passed in, so every number is reproducible offline
        and "we have no data" stays visible as UNKNOWN."""
        for path in sorted((ROOT / "ops").glob("*.py")):
            code = path.read_text(encoding="utf-8")
            for token in ("urllib.request", "http.client", "requests.", "socket."):
                with self.subTest(path=path.name, token=token):
                    self.assertNotIn(token, code)

    def test_the_weekly_workflow_never_syncs_or_publishes(self):
        body = (ROOT / ".github" / "workflows"
                / "knowledge-ops.yml").read_text(encoding="utf-8")
        self.assertIn("create-pull-request", body)
        self.assertNotIn("knowledge_sync", body)
        self.assertNotIn("git push origin main", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
