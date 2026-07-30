#!/usr/bin/env python3
"""
Deployment integration tests — Operational Completion Sprint.

Covers the three things the sprint built: the user-intelligence writer, the eight
deployment scripts, and migration 011's repair of the vocabulary crosswalk.

WHAT "INTEGRATION" MEANS HERE, AND WHAT IT DOES NOT
---------------------------------------------------
These run the real engine against the real knowledge graph and the real writer,
end to end, with no mocking of the layer under test. What they do not do is reach
a Postgres — there is none in this environment and there never has been, which is
precisely why `InMemoryTarget` exists and why every failure path can be exercised
at all.

The parts that genuinely need a database — `\\copy`, `alter table set schema`, the
`do $$ ... $$` block in 011 — are verified structurally: the SQL is parsed for the
guards that make it idempotent, and the scripts for the checks that make them
safe. Claiming otherwise would be claiming coverage this suite does not have.

Four groups, matching the sprint's brief:

  1. Fresh deployment       first run against an empty target
  2. Incremental            second run writes nothing; changed input writes again
  3. Rollback               reversal paths and the scripted ladder
  4. Health verification    what the health check and verifier actually assert
"""

import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(ROOT))

from user_intelligence import RULES_VERSION                            # noqa: E402
from user_intelligence.config import OUTPUT_TABLES                     # noqa: E402
from user_intelligence.context import UserContext                      # noqa: E402
from user_intelligence.engine import IntelligenceEngine                # noqa: E402
from user_intelligence.writer import (CONFLICT_KEYS, InMemoryTarget,   # noqa: E402
                                      IntelligenceWriter, SupabaseTarget,
                                      UserWriteResult, WriterError, make_target)

ENGINE = None


def engine():
    """One snapshot for the whole module — loading it per test is pointless."""
    global ENGINE
    if ENGINE is None:
        ENGINE = IntelligenceEngine()
    return ENGINE


def writer(target=None, **kwargs):
    kwargs.setdefault("log_path", None)
    kwargs.setdefault("sleep", lambda _s: None)
    return IntelligenceWriter(engine(), target or InMemoryTarget(), **kwargs)


RESOLVING = UserContext(user_id="u-resolving", city="Hyderabad, Telangana",
                        skills=["Welding", "Food Processing", "Tailoring"],
                        interests=["Manufacturing"])
THIN = UserContext(user_id="u-resolving", city="Adilabad",
                   skills=["Quidditch Coaching"], interests=[])
OTHER = UserContext(user_id="u-other", city="Guntur", skills=["Welding"], interests=[])


def read(path):
    return Path(path).read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════ 1. fresh deployment
class FreshDeploymentTest(unittest.TestCase):
    """First write into an empty target — the state a first deployment is in."""

    def setUp(self):
        self.target = InMemoryTarget()
        self.writer = writer(self.target)

    def test_first_write_populates_every_output_table(self):
        result = self.writer.write_user(RESOLVING)
        self.assertEqual(result.outcome, UserWriteResult.WRITTEN)
        for table in OUTPUT_TABLES:
            with self.subTest(table=table):
                self.assertGreater(
                    self.target.count(table), 0,
                    f"{table} is empty after a write — /dashboard reads it")

    def test_written_rows_carry_the_rules_version(self):
        """Rows are keyed (user_id, rules_version). Missing it means reading zero."""
        self.writer.write_user(RESOLVING)
        for table in OUTPUT_TABLES:
            for row in self.target.rows[table]:
                with self.subTest(table=table):
                    self.assertEqual(row.get("rules_version"), RULES_VERSION)

    def test_conflict_keys_match_the_migration(self):
        """
        An upsert on the wrong columns silently becomes an insert, and the table
        grows a duplicate set per run. Checked against the SQL, not assumed.
        """
        sql = read(ROOT / "user_intelligence" / "migrations" / "001_user_intelligence.sql")
        for table, keys in CONFLICT_KEYS.items():
            with self.subTest(table=table):
                block = sql.split(f"create table if not exists user_intelligence.{table}")[1]
                block = block.split(");")[0]
                if table == "user_recommendations":
                    self.assertIn("unique (" + ", ".join(keys) + ")", block)
                else:
                    self.assertIn("primary key (" + ", ".join(keys) + ")", block)

    def test_summary_is_written_last(self):
        """
        `user_activity_summary` holds the result hash the next run compares against.
        Written last, so a partial failure leaves it stale and the user is retried
        rather than assumed done — the same reason the sync advances its manifest last.
        """
        self.writer.write_user(RESOLVING)
        upserts = [c[1] for c in self.target.calls if c[0] == "upsert"]
        self.assertEqual(upserts[-1], "user_activity_summary")

    def test_engine_output_matches_what_is_written(self):
        result = engine().run(RESOLVING)
        self.writer.write_user(RESOLVING)
        self.assertEqual(len(result.user_recommendations()),
                         self.target.count("user_recommendations"))

    def test_writer_refuses_tables_it_does_not_own(self):
        """Allowlist. The brief forbids touching profiles, connections, auth.users."""
        for table in ("profiles", "connections", "auth.users", "opportunities"):
            with self.subTest(table=table):
                with self.assertRaises(WriterError):
                    self.target.upsert(table, [{"id": 1}], ("id",))

    def test_supabase_target_refuses_to_construct_without_credentials(self):
        env = {k: v for k, v in os.environ.items()
               if k not in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")}
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(WriterError):
                SupabaseTarget()

    def test_make_target_defaults_to_memory(self):
        self.assertIsInstance(make_target(None), InMemoryTarget)
        self.assertIsInstance(make_target("memory"), InMemoryTarget)
        with self.assertRaises(WriterError):
            make_target("postgres")


# ═══════════════════════════════════════════════ 2. incremental deployment
class IncrementalDeploymentTest(unittest.TestCase):
    """
    The property that makes a scheduled run safe: recomputing an unchanged user
    writes nothing. Without it, a nightly job rewrites every row every night and
    a rollback point means nothing.
    """

    def setUp(self):
        self.target = InMemoryTarget()
        self.writer = writer(self.target)

    def test_second_run_writes_nothing(self):
        first = self.writer.write_user(RESOLVING)
        self.assertEqual(first.outcome, UserWriteResult.WRITTEN)
        before = len(self.target.calls)

        second = self.writer.write_user(RESOLVING)
        self.assertEqual(second.outcome, UserWriteResult.UNCHANGED)
        self.assertEqual(second.rows_written, 0)
        upserts_after = [c for c in self.target.calls[before:] if c[0] == "upsert"]
        self.assertEqual(upserts_after, [], "an unchanged user was rewritten")

    def test_idempotency_uses_the_engine_result_hash(self):
        self.writer.write_user(RESOLVING)
        stored = self.target.stored_result_hash(RESOLVING.user_id, RULES_VERSION)
        self.assertEqual(stored, engine().run(RESOLVING).result_hash())

    def test_force_rewrites_an_unchanged_user(self):
        self.writer.write_user(RESOLVING)
        forced = writer(self.target, force=True).write_user(RESOLVING)
        self.assertEqual(forced.outcome, UserWriteResult.WRITTEN)

    def test_changed_input_writes_again(self):
        self.writer.write_user(RESOLVING)
        changed = self.writer.write_user(THIN)      # same user_id, different profile
        self.assertEqual(changed.outcome, UserWriteResult.WRITTEN)

    def test_shrinking_recommendations_prunes_stale_rows(self):
        """
        The bug this test was written for.

        A user whose skills stop resolving legitimately drops to zero
        recommendations. An earlier writer skipped a table with no rows, so those
        users kept every stale recommendation forever while the run reported
        success. Zero is a result, not an absence of one.
        """
        self.writer.write_user(RESOLVING)
        before = self.target.count("user_recommendations")
        self.assertGreater(before, 0)

        result = self.writer.write_user(THIN)
        after = self.target.count("user_recommendations")

        self.assertEqual(len(engine().run(THIN).user_recommendations()), 0,
                         "fixture assumption: the thin profile yields no recommendations")
        self.assertEqual(after, 0, "stale recommendations survived a drop to zero")
        self.assertEqual(result.rows_pruned, before)

    def test_pruning_does_not_touch_another_user(self):
        self.writer.write_user(RESOLVING)
        self.writer.write_user(OTHER)
        other_before = sum(1 for r in self.target.rows["user_recommendations"]
                           if r["user_id"] == OTHER.user_id)
        self.writer.write_user(THIN)          # drops u-resolving to zero
        other_after = sum(1 for r in self.target.rows["user_recommendations"]
                          if r["user_id"] == OTHER.user_id)
        self.assertEqual(other_before, other_after)

    def test_batch_reports_each_outcome(self):
        run = self.writer.write_many([RESOLVING, OTHER])
        self.assertEqual(run.written, 2)
        self.assertTrue(run.ok)
        again = self.writer.write_many([RESOLVING, OTHER])
        self.assertEqual(again.unchanged, 2)
        self.assertEqual(again.written, 0)

    def test_one_users_failure_does_not_stop_the_batch(self):
        target = InMemoryTarget(fail_on={("user_recommendations", "upsert")},
                                fail_times=99)
        run = writer(target).write_many([RESOLVING, OTHER])
        self.assertEqual(len(run.results), 2, "the batch stopped at the first failure")
        self.assertFalse(run.ok)

    def test_stop_after_failures_aborts_a_systemic_fault(self):
        target = InMemoryTarget(fail_on={("user_recommendations", "upsert")},
                                fail_times=99)
        run = writer(target).write_many([RESOLVING, OTHER, THIN],
                                        stop_after_failures=1)
        self.assertTrue(run.stopped_early)
        self.assertEqual(len(run.results), 1)

    def test_transient_failure_is_retried_and_recovers(self):
        target = InMemoryTarget(fail_on={("user_recommendations", "upsert")},
                                fail_times=2)
        result = writer(target).write_user(RESOLVING)
        self.assertEqual(result.outcome, UserWriteResult.WRITTEN)
        self.assertEqual(result.attempts, 3)

    def test_persistent_failure_gives_up_and_reports_why(self):
        target = InMemoryTarget(fail_on={("user_recommendations", "upsert")},
                                fail_times=99)
        result = writer(target).write_user(RESOLVING)
        self.assertEqual(result.outcome, UserWriteResult.FAILED)
        self.assertEqual(result.attempts, 3)
        self.assertIn("user_recommendations", result.error)

    def test_a_failed_write_does_not_advance_the_stored_hash(self):
        """Otherwise the next run believes a partial write succeeded."""
        target = InMemoryTarget(fail_on={("user_recommendations", "upsert")},
                                fail_times=99)
        writer(target).write_user(RESOLVING)
        self.assertIsNone(target.stored_result_hash(RESOLVING.user_id, RULES_VERSION))

    def test_writer_log_is_appended_and_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "writer_log.jsonl"
            w = IntelligenceWriter(engine(), InMemoryTarget(), log_path=log,
                                   sleep=lambda _s: None)
            w.write_user(RESOLVING)
            w.write_user(RESOLVING)
            lines = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
            self.assertEqual(len(lines), 2)
            self.assertEqual([l["outcome"] for l in lines],
                             [UserWriteResult.WRITTEN, UserWriteResult.UNCHANGED])
            for entry in lines:
                self.assertEqual(entry["rules_version"], RULES_VERSION)


# ═══════════════════════════════════════════════════════════ 3. rollback
class RollbackTest(unittest.TestCase):

    def test_delete_user_removes_every_table(self):
        target = InMemoryTarget()
        w = writer(target)
        w.write_user(RESOLVING)
        w.write_user(OTHER)
        removed = target.delete_user(RESOLVING.user_id)
        self.assertGreater(removed, 0)
        for table in OUTPUT_TABLES:
            remaining = [r for r in target.rows[table]
                         if r.get("user_id") == RESOLVING.user_id]
            self.assertEqual(remaining, [], f"{table} kept rows for a deleted user")
        self.assertGreater(target.count("user_activity_summary"), 0,
                           "deleting one user removed another")

    def test_recompute_after_delete_restores_identical_state(self):
        """Level 4 rollback is safe because every row is reproducible."""
        target = InMemoryTarget()
        w = writer(target)
        w.write_user(RESOLVING)
        before = target.stored_result_hash(RESOLVING.user_id, RULES_VERSION)
        target.delete_user(RESOLVING.user_id)
        w.write_user(RESOLVING)
        self.assertEqual(target.stored_result_hash(RESOLVING.user_id, RULES_VERSION),
                         before)

    def test_rollback_script_documents_all_five_levels(self):
        src = read(SCRIPTS / "rollback.sh")
        for level in ("frontend", "sync", "knowledge", "intelligence", "point-in-time"):
            with self.subTest(level=level):
                self.assertIn(level, src)

    def test_rollback_script_does_not_automate_the_destructive_level(self):
        """
        Level 5 destroys user data. It is documented and deliberately not scripted:
        it needs a decision, not a command.
        """
        src = read(SCRIPTS / "rollback.sh")
        self.assertNotRegex(src, r"drop\s+schema\s+(if\s+exists\s+)?public")
        self.assertIn("not scripted", src)

    def test_destructive_levels_require_confirmation(self):
        src = read(SCRIPTS / "rollback.sh")
        for block in src.split("  knowledge)")[1:]:
            self.assertIn("confirm ", block.split(";;")[0])

    def test_knowledge_rollback_reloads_the_crosswalk(self):
        """
        The crosswalk lives in `knowledge` after migration 011, so dropping that
        schema drops it too. A rebuild that forgot it would leave a working
        projection where nothing resolves.
        """
        src = read(SCRIPTS / "rollback.sh")
        knowledge_block = src.split("  knowledge)")[1].split(";;")[0]
        self.assertIn("load_crosswalk.sh", knowledge_block)
        self.assertIn("011_repair_vocabulary_crosswalk.sql", knowledge_block)


# ═══════════════════════════════════════════════ 4. health verification
class HealthVerificationTest(unittest.TestCase):

    def test_health_check_runs_and_reports_degraded_without_env(self):
        proc = subprocess.run([str(SCRIPTS / "health_check.sh")],
                              capture_output=True, text=True, cwd=ROOT,
                              env={**os.environ, "DATABASE_URL": "",
                                   "NEXT_PUBLIC_SUPABASE_URL": "",
                                   "PRODUCTION_URL": ""})
        self.assertEqual(proc.returncode, 1,
                         "no environment should be degraded (1), not healthy or critical")

    def test_health_check_emits_valid_json(self):
        """A monitor parses this. Hand-rolled JSON that is subtly invalid fails late."""
        proc = subprocess.run([str(SCRIPTS / "health_check.sh"), "--json"],
                              capture_output=True, text=True, cwd=ROOT,
                              env={**os.environ, "DATABASE_URL": "",
                                   "NEXT_PUBLIC_SUPABASE_URL": "",
                                   "PRODUCTION_URL": ""})
        payload = json.loads(proc.stdout)
        self.assertIn(payload["status"], ("healthy", "degraded", "critical"))
        for key in ("checked_at", "findings", "ok", "warnings", "critical"):
            self.assertIn(key, payload)
        for finding in payload["findings"]:
            self.assertIn(finding["severity"], ("OK", "WARN", "CRITICAL"))

    def test_health_check_uses_the_anon_key_for_exposure(self):
        """
        Service role bypasses both RLS and the exposed-schemas setting, so a check
        using it would pass while every real user saw nothing. This is the whole
        reason the script exists.
        """
        src = read(SCRIPTS / "health_check.sh")
        self.assertIn("NEXT_PUBLIC_SUPABASE_ANON_KEY", src)
        self.assertIn("Accept-Profile: knowledge", src)
        exposure = src.split("schema exposure")[1].split("# ── 3")[0]
        self.assertNotIn("SERVICE_ROLE", exposure)

    def test_verifier_checks_all_seven_required_areas(self):
        src = read(SCRIPTS / "verify_deployment.sh")
        for area in ("Schema", "Migration 011", "Crosswalk loaded", "Knowledge synced",
                     "Dashboard data", "Search returns results", "Recommendations"):
            with self.subTest(area=area):
                self.assertIn(area, src)

    def test_verifier_expects_the_real_row_counts(self):
        """Counts come from the sync's own specs, so a drift fails here first."""
        from knowledge_sync.config import TABLE_SPECS
        src = read(SCRIPTS / "verify_deployment.sh")
        expected = {"kg_entities": 647, "kg_relationships": 865, "kg_districts": 61,
                    "kg_skills": 45, "kg_schemes": 40, "kg_businesses": 85,
                    "kg_industries": 24, "kg_agriculture": 45}
        declared = {s.name for s in TABLE_SPECS}
        for table, count in expected.items():
            with self.subTest(table=table):
                self.assertIn(table, declared)
                self.assertIn(f'"{table} {count}"', src)

    def test_verifier_distinguishes_known_gaps_from_failures(self):
        """
        Empty is often correct here. A verifier that failed on a documented data
        gap would be switched off within a week.
        """
        src = read(SCRIPTS / "verify_deployment.sh")
        self.assertIn("KNOWN GAP", src)
        self.assertIn("scheme->district", src)


# ══════════════════════════════════════════ 5. scripts and the migration
class ScriptContractTest(unittest.TestCase):

    REQUIRED = ("first_deploy.sh", "load_crosswalk.sh", "run_graph_build.sh",
                "run_sync.sh", "run_user_intelligence.sh", "verify_deployment.sh",
                "health_check.sh", "rollback.sh")

    def test_every_required_script_exists_and_is_executable(self):
        for name in self.REQUIRED:
            with self.subTest(script=name):
                path = SCRIPTS / name
                self.assertTrue(path.exists(), f"missing script {name}")
                self.assertTrue(path.stat().st_mode & stat.S_IXUSR,
                                f"{name} is not executable")

    def test_every_script_parses(self):
        for path in sorted(SCRIPTS.glob("*.sh")):
            with self.subTest(script=path.name):
                proc = subprocess.run(["bash", "-n", str(path)],
                                      capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_every_script_uses_strict_mode(self):
        """Without `set -e`, a failed psql is a skipped step that reports success."""
        self.assertIn("set -Eeuo pipefail", read(SCRIPTS / "_common.sh"))
        for name in self.REQUIRED:
            with self.subTest(script=name):
                self.assertIn("_common.sh", read(SCRIPTS / name))

    def test_scripts_that_write_require_credentials_explicitly(self):
        for name in ("run_sync.sh", "load_crosswalk.sh"):
            with self.subTest(script=name):
                self.assertIn("need_env", read(SCRIPTS / name))

    def test_no_script_hardcodes_a_credential(self):
        pattern = re.compile(r"(eyJ[A-Za-z0-9_-]{20,}|postgres(ql)?://[^\s\"']*:[^\s\"']+@)")
        for path in sorted(SCRIPTS.glob("*.sh")):
            with self.subTest(script=path.name):
                self.assertIsNone(pattern.search(read(path)),
                                  f"{path.name} appears to contain a credential")

    def test_intelligence_script_defaults_to_not_writing(self):
        """A mistyped command should compute and report, not write to production."""
        src = read(SCRIPTS / "run_user_intelligence.sh")
        self.assertIn('TARGET="memory"', src)
        self.assertIn("--apply", src)


class MigrationRepairTest(unittest.TestCase):
    """Migration 011. Structural checks — there is no Postgres in this environment."""

    @classmethod
    def setUpClass(cls):
        cls.sql = read(ROOT / "frontend" / "migrations"
                       / "011_repair_vocabulary_crosswalk.sql")
        cls.original = read(ROOT / "frontend" / "migrations"
                            / "009_vocabulary_crosswalk.sql")
        #: Executable statements only.
        #:
        #: The header explains at length which foreign key it removes and why, so
        #: an assertion over the raw file would fail on the documentation — and the
        #: documentation is the most useful part of a repair migration. Assertions
        #: about what the migration *does* must read what Postgres reads.
        cls.stmts = "\n".join(
            line.split("--", 1)[0] for line in cls.sql.splitlines()).strip()

    def test_009_is_unchanged(self):
        """History is preserved. The repair moves forward, it does not rewrite."""
        self.assertIn("references public.kg_entity_registry", self.original,
                      "009 was modified — the sprint required a forward migration")

    def test_011_creates_the_table_in_the_knowledge_schema(self):
        """`lib/knowledge.js` queries it through a knowledge-scoped client."""
        self.assertIn("create table if not exists knowledge.kg_vocabulary_map", self.sql)
        js = read(ROOT / "frontend" / "lib" / "knowledge.js")
        self.assertIn('KNOWLEDGE_SCHEMA = "knowledge"', js)
        self.assertIn('.from("kg_vocabulary_map")', js)

    def test_011_does_not_recreate_the_unbuildable_foreign_key(self):
        self.assertNotIn("kg_entity_registry", self.stmts,
                         "011 re-introduces the reference that made 009 unapplyable")
        table = self.stmts.split(
            "create table if not exists knowledge.kg_vocabulary_map")[1]
        self.assertNotIn("references", table.split(");")[0])

    def test_011_explains_the_defect_it_repairs(self):
        """A repair migration nobody can read is a repair nobody can review."""
        self.assertIn("kg_entity_registry", self.sql,
                      "011 does not say which reference it removes")

    def test_011_keeps_the_coherence_constraint(self):
        """The invariant the dropped FK was reaching for."""
        self.assertIn("kg_vocab_resolution_is_coherent", self.sql)
        self.assertIn("kg_vocab_resolution_is_coherent", self.original)

    def test_011_is_idempotent(self):
        for guard in ("create schema if not exists",
                      "create table if not exists",
                      "create index if not exists",
                      "drop policy if exists",
                      "on conflict"):
            with self.subTest(guard=guard):
                self.assertIn(guard, self.sql)

    def test_011_is_transactional(self):
        """A half-repaired crosswalk resolves some terms and not others."""
        self.assertTrue(self.stmts.startswith("begin;"),
                        "the first statement is not begin;")
        self.assertIn("commit;", self.stmts)

    def test_011_does_not_drop_the_public_table(self):
        """Dropping in a repair migration makes the rollback irreversible."""
        self.assertNotRegex(self.stmts, r"drop\s+table\s+(if\s+exists\s+)?public\.")
        self.assertIn("comment on table public.kg_vocabulary_map", self.sql)

    def test_011_grants_read_and_no_write(self):
        self.assertIn("enable row level security", self.stmts)
        self.assertIn("for select", self.stmts)
        self.assertNotIn("for insert", self.stmts)
        self.assertNotIn("for all", self.stmts)

    def test_crosswalk_csvs_match_the_expected_load(self):
        """The loader asserts 202 rows. Verified against the files it reads."""
        import csv as _csv
        total = 0
        for kind, expected in (("district", 33), ("sector", 22), ("skill", 147)):
            path = ROOT / "governance" / "vocabulary" / f"{kind}_crosswalk.csv"
            with open(path, newline="", encoding="utf-8") as f:
                rows = list(_csv.DictReader(f))
            with self.subTest(kind=kind):
                self.assertEqual(len(rows), expected)
            total += len(rows)
        self.assertEqual(total, 202)
        self.assertIn("EXPECTED_TOTAL=202", read(SCRIPTS / "load_crosswalk.sh"))

    def test_loader_columns_match_the_csv_header(self):
        """A column-order mismatch in \\copy loads data into the wrong fields."""
        import csv as _csv
        with open(ROOT / "governance" / "vocabulary" / "skill_crosswalk.csv",
                  newline="", encoding="utf-8") as f:
            header = next(_csv.reader(f))
        loader = read(SCRIPTS / "load_crosswalk.sh")
        copy_line = [l for l in loader.splitlines() if "\\copy _vw_stage" in l][0]
        columns = re.search(r"_vw_stage\(([^)]*)\)", copy_line).group(1)
        declared = [c.strip() for c in columns.split(",")]
        self.assertEqual(declared, header,
                         "the \\copy column list does not match the CSV header")


if __name__ == "__main__":
    unittest.main(verbosity=2)
