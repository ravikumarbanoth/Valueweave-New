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


# ══════════════════════════════════════════ 6. consolidated deployment SQL
class ConsolidatedDeploymentTest(unittest.TestCase):
    """
    Guards on sql/deploy_knowledge.sql and the generator that writes it.

    The script itself was executed against a real PostgreSQL 16 while it was
    written — clean, partial and re-run, with the object counts and the grant
    matrix checked each time. None of that can run here, so what these tests
    protect is the set of properties that would silently rot: that the checked-in
    file still matches the migrations, and that the invariants which took a real
    database to discover are still stated in the SQL.
    """

    DEPLOY = ROOT / "sql" / "deploy_knowledge.sql"
    VERIFY = ROOT / "sql" / "verify_knowledge_schema.sql"
    BUILDER = SCRIPTS / "build_deployment_sql.py"

    def test_checked_in_sql_is_not_stale(self):
        """Regenerate and compare. This is the whole reason the file is generated.

        If someone edits a migration, the consolidated script must be rebuilt or
        it becomes a second, wrong source of truth — and the drift is invisible
        until a deployment produces a schema the sync does not recognise.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location("bds", self.BUILDER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(
            mod.build(), read(self.DEPLOY),
            "sql/deploy_knowledge.sql is stale — a migration changed under it. "
            "Run: python3 scripts/build_deployment_sql.py")

    def test_exactly_one_transaction(self):
        """One outer begin/commit, and no nested ones left behind by a migration.

        011 ships with its own `begin;`/`commit;`. Nested transaction control
        inside a larger batch either errors or commits early depending on the
        client, so the generator strips them and wraps everything once. A second
        `begin;` reappearing means that stripping silently stopped working.
        """
        lines = [l.strip().lower() for l in read(self.DEPLOY).splitlines()]
        self.assertEqual(lines.count("begin;"), 1, "expected exactly one `begin;`")
        self.assertEqual(lines.count("commit;"), 1, "expected exactly one `commit;`")
        self.assertLess(lines.index("begin;"), lines.index("commit;"))

    def test_preflight_checks_both_prerequisites(self):
        """profiles AND profiles.is_admin.

        The column check is not decoration. public.is_valueweave_admin() reads
        p.is_admin, PostgreSQL validates a `language sql` body at CREATE time, and
        the column comes from frontend/migrations/001_research_articles.sql rather
        than the base schema. Without this check the script dies forty lines in
        with `column p.is_admin does not exist` — which is what it did the first
        time it was run against a database.
        """
        sql = read(self.DEPLOY)
        # Anchor on the phase banner. Anchoring on the CREATE broke the moment
        # PHASE 1 became create-if-absent; the banner is the stable boundary.
        head = sql[:sql.index("PHASE 1 ·")]
        self.assertIn("to_regclass('public.profiles')", head)
        self.assertIn("is_admin", head,
                      "preflight does not check profiles.is_admin")
        self.assertEqual(head.count("raise exception"), 2,
                         "expected two preflight aborts, one per prerequisite")

    def test_admin_function_precedes_the_policy_that_calls_it(self):
        sql = read(self.DEPLOY)
        self.assertLess(
            sql.index("create function public.is_valueweave_admin()"),
            sql.index("sync runs admin read"),
            "the policy on knowledge.sync_runs is created before the function it "
            "calls — this is the ordering bug the consolidated script exists to fix")

    def test_no_destructive_statement_reaches_an_application_table(self):
        """`drop policy if exists` is expected. Anything that loses data is not."""
        banned = re.compile(
            r"^\s*(drop\s+(table|schema|column)|truncate|delete\s+from)\b",
            re.IGNORECASE | re.MULTILINE)
        found = banned.findall(read(self.DEPLOY))
        self.assertEqual(found, [], f"destructive statement in the deployment SQL: {found}")


class ServiceRoleGrantTest(unittest.TestCase):
    """
    The sync's own privileges, in the migrations rather than only in the
    consolidated copy.

    Supabase's service_role has BYPASSRLS, and an earlier comment in
    001_knowledge_schema.sql concluded from that it "bypasses grants and RLS
    alike" and granted it nothing. Only half is true: BYPASSRLS exempts a role
    from row-level security, not from GRANT checks — PostgreSQL exempts only
    superusers from those, and the service role is deliberately not one. Supabase's
    default grants cover `public`; a schema created by a migration gets none.

    Measured against PostgreSQL 16: with the grants absent, the sync's first
    statement fails with `permission denied for schema knowledge`, on SELECT as
    well as INSERT — after a deployment where tables, indexes, policies and the
    verifier's verdict all looked perfect.
    """

    KNOWLEDGE = ROOT / "knowledge_sync/migrations/001_knowledge_schema.sql"
    VOCAB = ROOT / "frontend/migrations/011_repair_vocabulary_crosswalk.sql"
    INTEL = ROOT / "user_intelligence/migrations/001_user_intelligence.sql"

    def test_knowledge_schema_grants_the_sync_usage_and_writes(self):
        sql = read(self.KNOWLEDGE)
        self.assertRegex(sql, r"grant usage on schema knowledge to[^;]*service_role")
        self.assertRegex(sql, r"grant[^;]*insert[^;]*on all tables in schema knowledge"
                              r"[^;]*service_role")
        self.assertRegex(sql, r"grant usage on all sequences in schema knowledge"
                              r"[^;]*service_role",
                         "kg_vocabulary_map has a sequence; an insert needs USAGE on it")

    def test_knowledge_withholds_delete_from_the_sync(self):
        """Soft delete is the contract, and the grant is what enforces it.

        knowledge_sync/adapters.py contains no hard delete — removal is
        `sync_deleted_at = now()`. Granting DELETE would mean a bug in the sync
        could destroy the projection instead of marking it.
        """
        for stmt in re.findall(r"^grant[^;]*service_role[^;]*;", read(self.KNOWLEDGE),
                               re.IGNORECASE | re.MULTILINE | re.DOTALL):
            if "schema knowledge" in stmt or "on all tables" in stmt:
                self.assertNotRegex(
                    stmt, r"\bdelete\b",
                    "DELETE granted to service_role on `knowledge`; the sync "
                    "soft-deletes and must not be able to hard-delete")

    def test_vocabulary_repair_grants_the_sync_too(self):
        sql = read(self.VOCAB)
        self.assertRegex(sql, r"grant usage on schema knowledge to[^;]*service_role")
        self.assertRegex(sql, r"grant[^;]*insert[^;]*knowledge\.kg_vocabulary_map"
                              r"[^;]*service_role")

    def test_user_intelligence_grants_delete_because_the_writer_uses_it(self):
        """The one place DELETE is correct, and it is asymmetric on purpose.

        user_intelligence/writer.py hard-deletes a user's stale recommendations
        before rewriting them. `knowledge` never does.
        """
        sql = read(self.INTEL)
        self.assertRegex(sql, r"grant usage on schema user_intelligence to"
                              r"[^;]*service_role")
        self.assertRegex(sql, r"grant[^;]*delete[^;]*in schema user_intelligence"
                              r"[^;]*service_role")
        self.assertIn(".delete()", read(ROOT / "user_intelligence/writer.py"),
                      "the DELETE grant above is justified by the writer; if the "
                      "writer no longer deletes, withdraw the grant")

    def test_no_write_is_granted_to_a_browser_role(self):
        """anon and authenticated read. Nothing else, in any of the three."""
        for path in (self.KNOWLEDGE, self.VOCAB, self.INTEL):
            for stmt in re.findall(r"^grant[^;]*;", read(path),
                                   re.IGNORECASE | re.MULTILINE | re.DOTALL):
                if re.search(r"\b(anon|authenticated)\b", stmt) \
                        and "service_role" not in stmt:
                    self.assertNotRegex(
                        stmt, r"\b(insert|update|delete|truncate|all privileges)\b",
                        f"{path.name} grants a write to a browser role: {stmt!r}")


class VerifierContractTest(unittest.TestCase):
    """sql/verify_knowledge_schema.sql — the one file an operator runs on prod."""

    VERIFY = ROOT / "sql" / "verify_knowledge_schema.sql"

    def test_is_strictly_read_only(self):
        """It is handed to an operator to run against production, twice.

        The brief that asked for it was explicit: no CREATE, ALTER, INSERT,
        UPDATE, DELETE, DROP, GRANT, REVOKE or TRUNCATE.
        """
        banned = re.compile(
            r"^\s*(create|alter|insert|update|delete|drop|grant|revoke|truncate)\b",
            re.IGNORECASE | re.MULTILINE)
        found = banned.findall(read(self.VERIFY))
        self.assertEqual(found, [], f"verifier is not read-only: {found}")

    def test_checks_the_service_role_grant(self):
        """Because its absence is invisible in every other block.

        Tables, indexes, policies and row counts can all be perfect while the
        sync cannot write a single row.
        """
        sql = read(self.VERIFY)
        self.assertIn("service_role", sql)
        self.assertIn("has_schema_privilege", sql)
        verdict = sql[sql.index("7 · Verdict"):]
        self.assertIn("service_role", verdict,
                      "the verdict can say SCHEMA COMPLETE while the sync is "
                      "unable to write")


class ExposurePreflightUrlTest(unittest.TestCase):
    """
    The workflow's exposure preflight must not paste SUPABASE_URL into a URL raw.

    It did, and the run failed with PGRST125 "Invalid request URL" — HTTP 404,
    which reads like a missing table and is actually a malformed path. PostgREST
    routes a table as ONE path segment; a trailing slash in the secret produces
    `//rest/v1/kg_entities`, which is four.

        secret                          PostgREST receives      segments
        https://x.supabase.co           /kg_entities                   1
        https://x.supabase.co/          //rest/v1/kg_entities          4
        https://x.supabase.co/rest/v1   /rest/v1/kg_entities           3

    A trailing slash is invisible in the GitHub secrets UI, so the fix
    normalises rather than only rejecting.
    """

    WORKFLOW = ROOT / ".github" / "workflows" / "knowledge-sync.yml"
    HEALTH = SCRIPTS / "health_check.sh"

    @staticmethod
    def _strip_comments(script):
        """Drop whole-line `#` comments.

        The absence assertions below would otherwise fire on the comment that
        quotes the old broken expression to explain why it went — and that
        explanation is the most useful thing in the step. Only full-line
        comments are removed: the `#` characters that remain are sed delimiters
        inside quoted expressions, never at the start of a line.
        """
        return "\n".join(l for l in script.splitlines()
                          if not l.lstrip().startswith("#"))

    @classmethod
    def setUpClass(cls):
        import yaml                                              # noqa: PLC0415
        doc = yaml.safe_load(read(cls.WORKFLOW))
        steps = doc["jobs"]["sync"]["steps"]
        # Located by what it does, not what it is called. Matching the step name
        # broke the moment the step was renamed from "Preflight — is the
        # knowledge schema exposed?" to "Check — …", and a StopIteration in
        # setUpClass is a far worse failure than the one it was guarding.
        cls.preflight = next(
            s["run"] for s in steps
            if "kg_entities?select=global_entity_id" in (s.get("run") or ""))
        cls.code = cls._strip_comments(cls.preflight)

    def test_url_is_not_built_from_the_raw_secret(self):
        self.assertNotIn('"$SUPABASE_URL/rest/v1', self.code,
                         "the secret is concatenated without normalisation")

    def test_trailing_slash_and_rest_suffix_are_stripped(self):
        self.assertIn("*/rest/v1) base=", self.code,
                      "a /rest/v1 suffix in the secret is not stripped")
        self.assertIn('${base%"${base##*[!/]}"}', self.code,
                      "trailing slashes in the secret are not stripped")

    def test_pgrst125_is_diagnosed_by_name(self):
        """Otherwise it falls through to "Unexpected HTTP 404", which is what
        happened and told the operator nothing."""
        self.assertIn("PGRST125", self.preflight)
        idx = self.preflight.index("PGRST125")
        self.assertIn("SUPABASE_URL", self.preflight[idx:idx + 800],
                      "the PGRST125 branch must point at the secret's shape")

    def test_the_final_url_is_printed_with_the_project_ref_masked(self):
        self.assertIn("Final request URL", self.preflight)
        self.assertRegex(self.preflight, r"sed -E 's#\(https://\)\[\^./\]\+#",
                         "the project ref must be masked before printing")

    def test_health_check_normalises_the_same_way(self):
        """It runs in the Verify step of the same workflow and had the same bug.

        Left unfixed it would report CRITICAL "not exposed" for what is really a
        typo in an environment variable, sending someone to the wrong setting.
        """
        src = self._strip_comments(read(self.HEALTH))
        self.assertNotIn('"$NEXT_PUBLIC_SUPABASE_URL/rest/v1', src)
        self.assertIn("PGRST125", src)


class LiveSchemaCompatibilityTest(unittest.TestCase):
    """
    Facts about the production database, from the schema dump the operator
    supplied, that the deployment has to respect.

    The dump is the authority here — not the migrations, which describe what
    *should* have been applied rather than what was. Two things it settles:
    `public.is_valueweave_admin()` already exists with sixteen CMS policies
    depending on it, and the `knowledge` schema does not exist at all.
    """

    DEPLOY = ROOT / "sql" / "deploy_knowledge.sql"
    RETIRE = ROOT / "sql" / "retire_cms_knowledge_tables.sql"

    def test_phase1_creates_only_if_absent(self):
        """It must not replace the predicate sixteen live policies evaluate.

        `create or replace` would swap the body out from under
        kg_district_profiles, kg_skills, kg_schemes, kg_resources, kg_roadmaps,
        kg_industry_sectors and kg_collaborator_types — the access-control rule
        on every CMS table — for a body this script cannot diff against the
        deployed one.
        """
        sql = read(self.DEPLOY)
        phase1 = sql[sql.index("PHASE 1 ·"):sql.index("PHASE 2 ·")]
        self.assertIn("to_regprocedure('public.is_valueweave_admin()')", phase1)
        self.assertNotIn("create or replace function public.is_valueweave_admin", phase1,
                         "PHASE 1 still replaces an existing function")
        self.assertIn("create function public.is_valueweave_admin()", phase1)

    def test_deployment_creates_nothing_in_public(self):
        """The whole point of the separate schema.

        Three of the projection's table names — kg_skills, kg_schemes,
        kg_relationships — already exist in `public` as CMS tables with different
        columns and different RLS. A `create table` landing in `public` would
        either collide or, worse, shadow one.
        """
        sql = read(self.DEPLOY)
        creates = re.findall(r"create table (?:if not exists )?([\w.]+)", sql, re.I)
        self.assertTrue(creates)
        for target in creates:
            self.assertRegex(
                target, r"^(knowledge|user_intelligence)\.",
                f"deployment creates {target} outside its own schemas")

    def test_retirement_script_refuses_to_destroy_content(self):
        sql = read(self.RETIRE)
        self.assertIn("raise exception", sql,
                      "the retirement script must abort on a non-empty table")
        self.assertRegex(sql, r"count\(\*\).*into\s+n",
                         "it must actually count rows before dropping")

    def test_retirement_script_leaves_live_tables_alone(self):
        """Only genuinely superseded tables may be dropped.

        kg_relationships is written by /admin/opportunity-mapping and read by
        /district-opportunity-index; kg_district_profiles backs that same public
        page; roadmaps have no equivalent in the graph at all. None of them is a
        duplicate, so none of them may appear in a DROP.
        """
        dropped = set(re.findall(r"drop table if exists public\.(\w+)", read(self.RETIRE)))
        self.assertEqual(dropped, {"kg_skills", "kg_schemes", "kg_resources"})
        for keep in ("kg_district_profiles", "kg_relationships", "kg_roadmaps",
                     "kg_roadmap_steps", "kg_industry_sectors", "kg_collaborator_types"):
            self.assertNotIn(keep, dropped)

    def test_retirement_uses_restrict_not_cascade(self):
        """A surviving dependency should stop the drop, not be swept up by it."""
        self.assertNotRegex(read(self.RETIRE), r"drop table[^;]*cascade")

    def test_greenfield_script_and_sql_editor_agree(self):
        """One definition of "deploy the knowledge layer", used by both paths.

        first_deploy.sh used to apply the two migrations itself, so it and
        sql/deploy_knowledge.sql could drift — and the SQL Editor path is the one
        an operator actually runs against production.
        """
        fd = read(SCRIPTS / "first_deploy.sh")
        self.assertIn("sql/deploy_knowledge.sql", fd)
        for migration in ("knowledge_sync/migrations/001_knowledge_schema.sql",
                          "user_intelligence/migrations/001_user_intelligence.sql"):
            self.assertNotIn(
                migration, fd,
                f"first_deploy.sh still applies {migration} directly, so it can "
                "disagree with sql/deploy_knowledge.sql")


if __name__ == "__main__":
    unittest.main(verbosity=2)
