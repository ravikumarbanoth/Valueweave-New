#!/usr/bin/env python3
"""
Platform v3.0 Step 1.5 — User Intelligence Engine tests.

No Supabase credentials, no network. The engine reads the Git knowledge artifacts
and takes profiles as plain dicts, so the whole suite runs against real knowledge
data and synthetic users.

Four things are being protected, in order of how badly they would hurt:

  1. **Reproducibility.** A recommendation a user acted on must be explainable
     months later. `result_hash` must be identical across runs.
  2. **The UNAVAILABLE / NO_SIGNAL distinction.** One is our gap, the other is
     theirs. Collapsing them tells a user their district has no opportunity when
     the truth is we have not collected it.
  3. **Every recommendation carries reason, evidence, confidence, timestamp.**
     The brief requires all four; a missing one is a silent regression.
  4. **Nothing is invented.** `mentors` and `events` have no data and must return
     NO_DATA_SOURCE, not a plausible-looking list.
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def files_changed_by_commit(subject):
    """
    The files changed by the one commit that delivered a step, or None if that
    commit is not in this clone.

    The scope tests below used to diff `main...HEAD`. That was correct only while
    the branch held nothing but their own step: a later step landing on the same
    branch made the test fail on *that* step's legitimate changes, and once the
    branch merged, the diff would be empty and the test would pass by measuring
    nothing — which is worse, because it reports confidence it never earned.

    A step's scope is a claim about that step's commit. Once committed, it is a
    fact fixed in history that no later work can invalidate, so that is what is
    measured.
    """
    log = subprocess.run(["git", "log", "--all", "--format=%H%x09%s"],
                         cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    sha = next((line.split("\t", 1)[0] for line in log
                if line.split("\t", 1)[-1].strip() == subject), None)
    if sha is None:
        return None
    return subprocess.run(["git", "diff", "--name-only", f"{sha}^", sha],
                          cwd=ROOT, capture_output=True, text=True).stdout.split()

from user_intelligence import RULES_VERSION, __version__            # noqa: E402
from user_intelligence import fixtures                              # noqa: E402
from user_intelligence.config import (CATEGORIES_BY_KEY, INPUTS,     # noqa: E402
                                      MISSING, OUTPUT_TABLES,
                                      RECOMMENDATION_CATEGORIES, SCORES,
                                      SCORES_BY_KEY, STARTUP_WEIGHTS)
from user_intelligence.context import UserContext, from_supabase_rows  # noqa: E402
from user_intelligence.engine import IntelligenceEngine             # noqa: E402
from user_intelligence.knowledge import KnowledgeSnapshot           # noqa: E402
from user_intelligence.recommenders import NO_DATA_SOURCE           # noqa: E402
from user_intelligence.rules import (APPLIED, NO_SIGNAL, UNAVAILABLE,  # noqa: E402
                                     Evidence, applied, combine, no_signal,
                                     unavailable)

ENGINE = None


def engine():
    """One snapshot for the whole suite — loading it 60 times is pointless."""
    global ENGINE
    if ENGINE is None:
        ENGINE = IntelligenceEngine()
    return ENGINE


# ═══════════════════════════════════════════════════════ knowledge snapshot
class SnapshotTest(unittest.TestCase):
    def test_snapshot_loads_the_real_graph(self):
        kn = engine().snapshot
        self.assertGreater(len(kn.entities), 600)
        self.assertGreater(len(kn.edges), 800)

    def test_snapshot_hash_is_stable_across_loads(self):
        self.assertEqual(KnowledgeSnapshot().snapshot_hash,
                         KnowledgeSnapshot().snapshot_hash)

    def test_step0_crosswalks_are_loaded(self):
        kn = engine().snapshot
        for kind in ("skill", "sector", "district"):
            with self.subTest(kind=kind):
                self.assertTrue(kn.crosswalk[kind], f"{kind} crosswalk is empty")

    def test_curated_crosswalk_entries_resolve(self):
        """Step 0 curated 'AC Repair' -> HVAC Technician. It must still work."""
        entity, row = engine().snapshot.resolve("skill", "AC Repair")
        self.assertIsNotNone(entity)
        self.assertEqual(entity["canonical_name"], "HVAC Technician")
        self.assertEqual(row["match_method"], "CURATED")

    def test_no_counterpart_is_explained_not_silent(self):
        kn = engine().snapshot
        entity, _ = kn.resolve("skill", "Data Entry")
        self.assertIsNone(entity)
        reason = kn.explain_unresolved("skill", "Data Entry")
        self.assertIn("no researched counterpart", reason)

    def test_unknown_term_is_distinguished_from_no_counterpart(self):
        kn = engine().snapshot
        self.assertIn("not in the skill vocabulary",
                      kn.explain_unresolved("skill", "Quidditch Coaching"))

    def test_traversal_is_deterministically_ordered(self):
        kn = engine().snapshot
        turmeric = "vw:crop:turmeric"
        a = [e["relationship_id"] for _, e in kn.neighbours(turmeric)]
        b = [e["relationship_id"] for _, e in kn.neighbours(turmeric)]
        self.assertEqual(a, b)
        self.assertEqual(a, sorted(a))


# ═══════════════════════════════════════════════════════════ the rule engine
class RuleEngineTest(unittest.TestCase):
    def test_unavailable_is_excluded_from_the_denominator(self):
        """
        The most important behaviour in the module.

        Two rules, one applied at 100 and one unavailable. If UNAVAILABLE counted
        as zero the score would be 50 — a claim about the user caused by a gap in
        our data.
        """
        result = combine("t", "T", [applied("A", 100, "ok"),
                                    unavailable("B", "no input")])
        self.assertEqual(result.score, 100.0)
        self.assertEqual(result.status, APPLIED)
        self.assertIn("B", result.reason)

    def test_no_signal_does_count_as_zero(self):
        """NO_SIGNAL means we measured and found nothing. That is a real zero."""
        result = combine("t", "T", [applied("A", 100, "ok"),
                                    no_signal("B", "nothing found")])
        self.assertEqual(result.score, 50.0)

    def test_all_unavailable_gives_no_score_not_zero(self):
        result = combine("t", "T", [unavailable("A", "missing input")])
        self.assertIsNone(result.score, "a missing input must not produce a 0 score")
        self.assertEqual(result.status, UNAVAILABLE)

    def test_all_no_signal_reports_no_signal_status(self):
        result = combine("t", "T", [no_signal("A", "nothing")], low_means="nothing yet")
        self.assertEqual(result.status, NO_SIGNAL)
        self.assertEqual(result.score, 0.0)

    def test_weights_are_respected(self):
        result = combine("t", "T", [applied("A", 100, "", weight=3.0),
                                    applied("B", 0, "", weight=1.0)])
        self.assertEqual(result.score, 75.0)

    def test_scores_are_clamped(self):
        self.assertEqual(applied("A", 5000, "").value, 100.0)
        self.assertEqual(applied("A", -20, "").value, 0.0)

    def test_confidence_is_the_minimum_not_the_mean(self):
        """A chain is as trustworthy as its weakest link."""
        result = combine("t", "T", [applied("A", 50, "", evidence=[
            Evidence("entity", "a", confidence=90),
            Evidence("entity", "b", confidence=40)])])
        self.assertEqual(result.confidence, 40)

    def test_confidence_and_score_are_independent(self):
        result = combine("t", "T", [applied("A", 100, "", evidence=[
            Evidence("entity", "a", confidence=50)])])
        self.assertEqual(result.score, 100.0)
        self.assertEqual(result.confidence, 50)


# ══════════════════════════════════════════════════════════ the eight scores
class ScoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolving = engine().run(fixtures.resolving_user())
        cls.unresolvable = engine().run(fixtures.unresolvable_user())
        cls.empty = engine().run(fixtures.empty_user())

    def test_all_eight_scores_are_produced(self):
        self.assertEqual(set(self.resolving.scores), {s.key for s in SCORES})
        self.assertEqual(len(SCORES), 8)

    def test_every_score_is_in_range_or_none(self):
        for result in (self.resolving, self.unresolvable, self.empty):
            for key, s in result.scores.items():
                with self.subTest(user=result.ctx.user_id, score=key):
                    if s.score is not None:
                        self.assertGreaterEqual(s.score, 0)
                        self.assertLessEqual(s.score, 100)

    def test_every_score_carries_a_reason(self):
        for result in (self.resolving, self.unresolvable, self.empty):
            for key, s in result.scores.items():
                with self.subTest(user=result.ctx.user_id, score=key):
                    self.assertTrue(s.reason.strip(), "a score with no reason")

    def test_resolving_user_scores_above_the_unresolvable_one(self):
        self.assertGreater(self.resolving.scores["skill_profile"].score,
                           self.unresolvable.scores["skill_profile"].score)
        self.assertGreater(self.resolving.scores["startup_readiness"].score,
                           self.unresolvable.scores["startup_readiness"].score)

    def test_unresolvable_skills_are_reported_not_hidden(self):
        """The user's skills are real. We have no data. Say which ones."""
        table = self.unresolvable.user_skill_profile()
        self.assertEqual(table["resolved_skill_count"], 0)
        self.assertEqual(len(table["unresolved_skills"]),
                         len(fixtures.UNRESOLVABLE_SKILLS))
        for entry in table["unresolved_skills"]:
            self.assertTrue(entry["reason"], "an unresolved skill with no reason")

    def test_empty_profile_produces_no_crash_and_honest_statuses(self):
        for key, s in self.empty.scores.items():
            with self.subTest(score=key):
                self.assertIn(s.status, (APPLIED, NO_SIGNAL, UNAVAILABLE))

    def test_district_score_is_unavailable_without_a_location(self):
        s = self.empty.scores["district_opportunity"]
        self.assertIsNone(s.score, "no location must not score 0")
        self.assertEqual(s.status, UNAVAILABLE)

    def test_district_score_distinguishes_thin_data_from_no_district(self):
        thin = engine().run(fixtures.district_only_user())
        s = thin.scores["district_opportunity"]
        self.assertIsNotNone(s.score)
        self.assertEqual(s.detail["match_method"], "EXACT_NAME")

    def test_no_gap_scores_high_not_middling(self):
        """A user with nothing left to learn must not be penalised for it."""
        lr = self.resolving.scores["learning_roadmap"]
        self.assertEqual(lr.detail["gap_state"], "NO_GAP")
        self.assertEqual(lr.score, 100.0)

    def test_startup_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(STARTUP_WEIGHTS.values()), 1.0, places=9)

    def test_startup_composite_excludes_unavailable_components(self):
        detail = self.empty.scores["startup_readiness"].detail
        self.assertIn("excluded_unavailable", detail)
        self.assertIn("district_opportunity", detail["excluded_unavailable"])
        self.assertLess(detail["weight_available"], 1.0)

    def test_scores_carry_evidence_when_applied(self):
        for key, s in self.resolving.scores.items():
            if s.status != APPLIED:
                continue
            with self.subTest(score=key):
                self.assertTrue(s.evidence, f"{key} is APPLIED with no evidence")

    def test_ai_readiness_uses_package006_ratings_not_invention(self):
        detail = self.resolving.scores["ai_readiness"].detail
        self.assertGreater(detail["skills_with_ai_rating"], 0)


# ═════════════════════════════════════════════ the ten recommendation sets
class RecommendationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = engine().run(
            fixtures.resolving_user(),
            articles=fixtures.research_articles(),
            candidates=fixtures.candidate_profiles())

    def test_all_ten_categories_are_produced(self):
        self.assertEqual(set(self.result.categories),
                         {c.key for c in RECOMMENDATION_CATEGORIES})
        self.assertEqual(len(RECOMMENDATION_CATEGORIES), 10)

    def test_every_recommendation_has_the_four_required_fields(self):
        """reason, supporting entities, confidence, timestamp — the brief's four."""
        rows = self.result.user_recommendations()
        self.assertTrue(rows)
        for row in rows:
            with self.subTest(item=row["item_id"]):
                self.assertTrue(row["reason"].strip(), "no reason")
                self.assertIn("supporting_entities", row)
                self.assertIsInstance(row["confidence"], int)
                self.assertTrue(row["generated_at"], "no timestamp")
                self.assertTrue(row["rule"], "no rule recorded")

    def test_graph_backed_recommendations_carry_real_evidence(self):
        for row in self.result.user_recommendations():
            if row["category"] in ("business_ideas", "research"):
                continue          # editorial sources; see the next test
            with self.subTest(item=row["item_id"]):
                self.assertTrue(row["supporting_entities"],
                                "a graph-backed recommendation with no evidence")

    def test_editorial_sources_do_not_borrow_a_confidence_score(self):
        """
        Idea-library and research rows have no confidence score in the source.

        Reporting 0 keeps editorial content distinguishable from researched
        content. Borrowing a number from elsewhere would blur exactly the line
        this platform exists to hold.
        """
        for row in self.result.user_recommendations():
            if row["item_id"].startswith(("idea:", "article:")):
                with self.subTest(item=row["item_id"]):
                    self.assertEqual(row["confidence"], 0)

    def test_mentors_returns_no_data_source_not_an_empty_list(self):
        cat = self.result.categories["mentors"]
        self.assertEqual(cat.status, NO_DATA_SOURCE)
        self.assertEqual(cat.recommendations, [])
        self.assertIn("No mentor data exists", cat.note)

    def test_events_returns_no_data_source(self):
        cat = self.result.categories["events"]
        self.assertEqual(cat.status, NO_DATA_SOURCE)
        self.assertIn("No event data exists", cat.note)

    def test_no_data_categories_never_emit_a_recommendation(self):
        """The whole point: an absent data source must not produce content."""
        for spec in RECOMMENDATION_CATEGORIES:
            if not spec.no_data_reason:
                continue
            for name, make in fixtures.ALL.items():
                r = engine().run(make(), articles=fixtures.research_articles(),
                                 candidates=fixtures.candidate_profiles())
                with self.subTest(category=spec.key, user=name):
                    self.assertEqual(r.categories[spec.key].recommendations, [])

    def test_sparse_categories_declare_their_sparseness(self):
        for key in ("courses", "markets"):
            with self.subTest(category=key):
                self.assertTrue(CATEGORIES_BY_KEY[key].sparse_note)
                self.assertIn("edge", self.result.categories[key].note.lower())

    def test_recommendations_are_ranked_descending(self):
        for key, cat in self.result.categories.items():
            scores = [r.match_score for r in cat.recommendations]
            with self.subTest(category=key):
                self.assertEqual(scores, sorted(scores, reverse=True))

    def test_the_match_floor_is_enforced(self):
        from user_intelligence.config import MIN_MATCH_SCORE
        for cat in self.result.categories.values():
            for r in cat.recommendations:
                self.assertGreaterEqual(r.match_score, MIN_MATCH_SCORE)

    def test_per_category_cap_is_enforced(self):
        from user_intelligence.config import MAX_PER_CATEGORY
        for key, cat in self.result.categories.items():
            with self.subTest(category=key):
                self.assertLessEqual(len(cat.recommendations), MAX_PER_CATEGORY)

    def test_no_duplicate_item_within_a_category(self):
        for key, cat in self.result.categories.items():
            ids = [r.item_id for r in cat.recommendations]
            with self.subTest(category=key):
                self.assertEqual(len(ids), len(set(ids)))

    def test_collaborators_never_includes_the_user_themselves(self):
        ctx = fixtures.resolving_user()
        candidates = fixtures.candidate_profiles() + [
            {"id": ctx.user_id, "name": "Me", "city": ctx.city,
             "skills": list(ctx.skills), "interests": list(ctx.interests)}]
        r = engine().run(ctx, candidates=candidates)
        ids = {rec.item_id for rec in r.categories["collaborators"].recommendations}
        self.assertNotIn(f"user:{ctx.user_id}", ids)

    def test_caller_supplied_categories_are_empty_without_input(self):
        """Research and collaborators read live tables the caller passes in."""
        r = engine().run(fixtures.resolving_user())
        for key in ("research", "collaborators"):
            with self.subTest(category=key):
                self.assertEqual(r.categories[key].recommendations, [])
                self.assertIn("supplied", r.categories[key].note)


# ══════════════════════════════════════════════════════════ reproducibility
class ReproducibilityTest(unittest.TestCase):
    def test_two_runs_produce_the_same_result_hash(self):
        ctx = fixtures.resolving_user
        a = engine().run(ctx(), articles=fixtures.research_articles(),
                         candidates=fixtures.candidate_profiles())
        b = engine().run(ctx(), articles=fixtures.research_articles(),
                         candidates=fixtures.candidate_profiles())
        self.assertEqual(a.result_hash(), b.result_hash())

    def test_hash_is_stable_across_a_fresh_snapshot(self):
        """A new process must agree with the old one, not just a new call."""
        ctx = fixtures.resolving_user
        a = IntelligenceEngine().run(ctx())
        b = IntelligenceEngine().run(ctx())
        self.assertEqual(a.result_hash(), b.result_hash())

    def test_hash_excludes_the_timestamp(self):
        a = engine().run(fixtures.resolving_user())
        b = engine().run(fixtures.resolving_user())
        # Same hash even though generated_at may differ by a second.
        self.assertEqual(a.result_hash(), b.result_hash())

    def test_hash_changes_when_the_profile_changes(self):
        base = engine().run(fixtures.resolving_user())
        changed = fixtures.resolving_user()
        changed.skills = tuple(list(changed.skills) + ["Python Programming"])
        self.assertNotEqual(base.result_hash(), engine().run(changed).result_hash())

    def test_recommendation_order_is_deterministic(self):
        a = engine().run(fixtures.resolving_user())
        b = engine().run(fixtures.resolving_user())
        for key in a.categories:
            with self.subTest(category=key):
                self.assertEqual([r.item_id for r in a.categories[key].recommendations],
                                 [r.item_id for r in b.categories[key].recommendations])

    def test_context_normalises_to_ordered_tuples(self):
        """A set here would make output differ between processes."""
        ctx = UserContext(user_id="u", skills=["b", "a", "a", ""])
        self.assertEqual(ctx.skills, ("a", "b"))
        self.assertIsInstance(ctx.skills, tuple)


# ════════════════════════════════════════════════════════ the output tables
class OutputTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = engine().run(
            fixtures.resolving_user(), articles=fixtures.research_articles(),
            candidates=fixtures.candidate_profiles()).tables()

    def test_all_five_tables_are_produced(self):
        self.assertEqual(set(self.tables), set(OUTPUT_TABLES))
        self.assertEqual(len(OUTPUT_TABLES), 5)

    def test_every_table_carries_user_rules_version_and_timestamp(self):
        for name, payload in self.tables.items():
            rows = payload if isinstance(payload, list) else [payload]
            for row in rows:
                with self.subTest(table=name):
                    self.assertEqual(row["user_id"], "fixture-resolving")
                    self.assertEqual(row["rules_version"], RULES_VERSION)
                    self.assertTrue(row["generated_at"])

    def test_recommendations_carry_the_unverified_notice(self):
        """All 2,299 knowledge rows are VST-NEEDS_REVIEW. Every rec must say so."""
        for row in self.tables["user_recommendations"]:
            self.assertIn("VST-NEEDS_REVIEW", row["unverified_notice"])

    def test_activity_summary_reports_what_is_missing(self):
        s = self.tables["user_activity_summary"]
        self.assertEqual(sorted(s["categories_without_data"]), ["events", "mentors"])
        self.assertEqual(sorted(s["inputs_unavailable"]),
                         ["assessment_results", "teams"])

    def test_activity_summary_counts_reconcile(self):
        s = self.tables["user_activity_summary"]
        self.assertEqual(s["total_recommendations"],
                         len(self.tables["user_recommendations"]))
        self.assertEqual(sum(c["count"] for c
                             in s["recommendations_by_category"].values()),
                         s["total_recommendations"])

    def test_all_tables_are_json_serialisable(self):
        json.dumps(self.tables, default=str)

    def test_learning_profile_includes_the_course_recommendations(self):
        self.assertIn("recommended_courses", self.tables["user_learning_profile"])


# ═════════════════════════════════════════════════════════ inputs and config
class ConfigurationTest(unittest.TestCase):
    def test_the_three_missing_inputs_are_declared_missing(self):
        for name in ("assessment_results", "teams"):
            with self.subTest(input=name):
                self.assertEqual(INPUTS[name].status, MISSING)
        self.assertEqual(INPUTS["idea_library"].status, "STATIC_FILE")

    def test_missing_inputs_stay_missing_until_applied_and_populated(self):
        """
        Was: "no migration defines assessment_results or teams".

        Step 2 Phase 8 added `frontend/migrations/010_missing_application_features.sql`,
        which creates both — so the old assertion is now false while the underlying
        claim is unchanged. A *written* migration is not a deployed, populated table,
        and the engine must keep reporting the input as unavailable until it is both.

        What is checked instead:
          - the migration exists (the shape has been agreed)
          - it seeds nothing (no fabricated mentor, event or assessment)
          - INPUTS still says MISSING
        """
        migration = (ROOT / "frontend" / "migrations"
                     / "010_missing_application_features.sql")
        if migration.exists():
            statements = "\n".join(line.split("--", 1)[0]
                                   for line in migration.read_text().lower().splitlines())
            self.assertNotIn("insert into", statements,
                             "a seeded row would make a NO_DATA_SOURCE category start "
                             "returning content that describes nobody")

        for name in ("assessment_results", "teams"):
            with self.subTest(input=name):
                self.assertEqual(
                    INPUTS[name].status, MISSING,
                    f"{name} is reported as available; a migration file alone does "
                    f"not make an input usable")

    def test_every_score_spec_has_rules_and_a_description(self):
        for s in SCORES:
            with self.subTest(score=s.key):
                self.assertTrue(s.rules)
                self.assertTrue(s.description)
                self.assertTrue(s.requires)

    def test_every_category_has_either_rules_or_a_no_data_reason(self):
        for c in RECOMMENDATION_CATEGORIES:
            with self.subTest(category=c.key):
                self.assertTrue(bool(c.rules) ^ bool(c.no_data_reason),
                                "a category must have rules or a stated reason "
                                "for having none — never both, never neither")

    def test_capabilities_are_computed_not_hardcoded(self):
        caps = engine().capabilities()
        self.assertEqual(len(caps["scores"]), len(SCORES))
        self.assertEqual(len(caps["categories"]), len(RECOMMENDATION_CATEGORIES))
        self.assertEqual(sorted(caps["categories_without_data"]),
                         ["events", "mentors"])

    def test_context_builder_handles_supabase_shaped_rows(self):
        ctx = from_supabase_rows(
            {"id": "u1", "name": "N", "city": "Medak", "skills": ["Welding"],
             "profile_complete": True},
            collaborator={"archetype": "Operator", "district": "Medak",
                          "top_sectors": ["Agriculture"]},
            connections=[{"id": "c1", "status": "accepted"},
                         {"id": "c2", "status": "pending"}],
            peers=[{"skills": ["Plumbing"]}])
        self.assertEqual(ctx.accepted_connection_ids, ("c1",))
        self.assertEqual(ctx.pending_connection_ids, ("c2",))
        self.assertEqual(ctx.collaborator_skills, ("Plumbing",))
        self.assertEqual(ctx.location_term, "Medak")


# ═══════════════════════════════════════════════════════════════ migration
class MigrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = (ROOT / "user_intelligence" / "migrations"
                    / "001_user_intelligence.sql")
        cls.sql = cls.path.read_text(encoding="utf-8")

    def test_migration_matches_the_configuration(self):
        r = subprocess.run(
            [sys.executable, "user_intelligence/generate_migration.py", "--check"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_all_five_tables_are_created_in_their_own_schema(self):
        for t in OUTPUT_TABLES:
            with self.subTest(table=t):
                self.assertIn(f"create table if not exists user_intelligence.{t}",
                              self.sql)

    def test_no_application_table_is_created_or_altered(self):
        statements = "\n".join(line.split("--", 1)[0]
                               for line in self.sql.lower().splitlines())
        for forbidden in ("create table if not exists public.",
                          "alter table public.", "drop table"):
            with self.subTest(statement=forbidden):
                self.assertNotIn(forbidden, statements)
        # The only permitted public references are FK targets and auth.uid().
        refs = set(re.findall(r"public\.\w+", statements))
        self.assertLessEqual(refs, {"public.profiles"},
                             f"unexpected public references: {refs}")

    def test_rls_restricts_rows_to_their_owner(self):
        for t in OUTPUT_TABLES:
            with self.subTest(table=t):
                self.assertIn(f"alter table user_intelligence.{t} "
                              f"enable row level security", self.sql)
        self.assertIn("auth.uid() = user_id", self.sql)

    def test_no_write_policy_is_granted(self):
        lowered = self.sql.lower()
        self.assertNotIn("for insert", lowered)
        self.assertNotIn("for update", lowered)
        self.assertNotIn("grant insert", lowered)

    def test_required_recommendation_fields_are_not_null(self):
        block = self.sql.split("create table if not exists "
                               "user_intelligence.user_recommendations")[1]
        block = block.split(");")[0]
        for column in ("reason", "confidence", "generated_at", "rule",
                       "unverified_notice", "match_score"):
            with self.subTest(column=column):
                line = next(l for l in block.splitlines() if l.strip().startswith(column))
                self.assertIn("not null", line,
                              f"{column} must be NOT NULL — the brief requires it")


# ══════════════════════════════════════════════════════════════════ safety
class SafetyTest(unittest.TestCase):
    def test_engine_never_queries_supabase(self):
        """Callers pass rows in; the engine holds no client."""
        offenders = []
        for py in sorted((ROOT / "user_intelligence").rglob("*.py")):
            text = py.read_text(encoding="utf-8")
            for token in ("create_client", "from supabase", "import supabase",
                          ".table(", "psycopg", "SUPABASE_SERVICE_ROLE_KEY"):
                if token in text:
                    offenders.append(f"{py.name}: {token}")
        self.assertEqual(offenders, [], f"database access in the engine: {offenders}")

    def test_engine_writes_nothing(self):
        """No file or database write anywhere in the package."""
        offenders = []
        for py in sorted((ROOT / "user_intelligence").rglob("*.py")):
            if py.name == "generate_migration.py":
                continue          # writes its own migration, deliberately
            text = py.read_text(encoding="utf-8")
            for token in ("write_text(", "open(", "os.remove", "shutil"):
                if token in text and "newline=" not in text.split(token)[1][:40]:
                    offenders.append(f"{py.name}: {token}")
        self.assertEqual(offenders, [],
                         f"unexpected write or non-CSV file access: {offenders}")

    def test_no_randomness_anywhere(self):
        """Reproducibility would be impossible with a single random call."""
        offenders = []
        for py in sorted((ROOT / "user_intelligence").rglob("*.py")):
            text = py.read_text(encoding="utf-8")
            for token in ("import random", "random.", "uuid4", "shuffle"):
                if token in text:
                    offenders.append(f"{py.name}: {token}")
        self.assertEqual(offenders, [], f"non-determinism: {offenders}")

    def test_no_ai_or_model_dependency(self):
        """The brief: rule-based only."""
        offenders = []
        for py in sorted((ROOT / "user_intelligence").rglob("*.py")):
            text = py.read_text(encoding="utf-8").lower()
            for token in ("openai", "anthropic", "transformers", "torch",
                          "sklearn", "embedding", "llm("):
                if token in text:
                    offenders.append(f"{py.name}: {token}")
        self.assertEqual(offenders, [], f"AI dependency found: {offenders}")

    def test_no_package_or_frontend_file_is_modified_by_this_step(self):
        changed = files_changed_by_commit("feat(v3.0): Step 1.5 — user intelligence engine")
        if changed is None:
            self.skipTest("Step 1.5's commit is not in this clone's history")
        offenders = [f for f in changed
                     if f.startswith(("packages/", "frontend/", "knowledge_graph/",
                                      "supabase/"))]
        self.assertEqual(offenders, [],
                         f"Step 1.5 modified protected paths: {offenders}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
