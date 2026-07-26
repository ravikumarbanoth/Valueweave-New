#!/usr/bin/env python3
"""
Platform v3.0 Step 1 — knowledge synchronisation framework tests.

Every test runs against `InMemoryTarget`. **No Supabase credentials are needed
and no network call is made**, which is the point: a sync framework whose tests
require a live database is a framework whose failure modes are discovered in
production.

Three groups:

  * Unit tests per module, against small hand-built fixtures where the expected
    answer is obvious by inspection.
  * Integration tests of the whole pipeline against the real repository, which is
    the only way to know the framework survives contact with actual package data.
  * Safety tests, which assert the framework *cannot* do the things the brief
    forbids — reach a user table, hard-delete, or advance the manifest after a
    failed apply.
"""

import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from knowledge_sync import changes as changes_mod                    # noqa: E402
from knowledge_sync import metrics as metrics_mod                    # noqa: E402
from knowledge_sync import rollback as rollback_mod                  # noqa: E402
from knowledge_sync import validation as validation_mod              # noqa: E402
from knowledge_sync.adapters import (InMemoryTarget, SupabaseTarget,  # noqa: E402
                                     TargetError)
from knowledge_sync.changes import Manifest                          # noqa: E402
from knowledge_sync.config import (SENTINELS, SYNC_COLUMNS,          # noqa: E402
                                   TABLE_SPECS, TARGET_SCHEMA, spec)
from knowledge_sync.engine import SyncAborted, SyncEngine, SyncMode  # noqa: E402
from knowledge_sync.extract import extract                           # noqa: E402
from knowledge_sync.transform import (TransformError, coerce,        # noqa: E402
                                      content_hash, transform)


def fixture_row(key="k1", name="Alpha", extra=None):
    row = {
        "sync_row_key": key, "sync_source_package": "PkgX",
        "sync_source_dataset": "d.csv", "sync_source_row_id": key,
        "sync_pending_fields": {}, "sync_deleted_at": None,
        "sync_version": "v1", "sync_synced_at": "2026-01-01T00:00:00Z",
        "name": name,
    }
    row.update(extra or {})
    row["sync_content_hash"] = content_hash(row)
    return row


# ─────────────────────────────────────────────────────────── transformation
class TransformTest(unittest.TestCase):
    def test_sentinel_becomes_null_and_is_recorded(self):
        for sentinel in SENTINELS:
            with self.subTest(sentinel=sentinel):
                value, found = coerce("t", "k", "population", sentinel)
                self.assertIsNone(value, "a sentinel must not reach the target as text")
                self.assertEqual(found, sentinel, "which sentinel applied must be kept")

    def test_sentinel_is_never_coerced_to_zero(self):
        """Zero is a measurement. 'We could not source this' is not."""
        value, _ = coerce("t", "k", "population", "PENDING_VERIFICATION")
        self.assertIsNotNone(value is None or value != 0)
        self.assertIsNone(value)

    def test_empty_string_is_null_in_numbers_but_kept_in_text(self):
        self.assertEqual(coerce("t", "k", "population", ""), (None, None))
        self.assertEqual(coerce("t", "k", "description", ""), ("", None))

    def test_malformed_number_raises_rather_than_nulling(self):
        """Coercing '12,00,000' to NULL would silently discard a real figure."""
        with self.assertRaises(TransformError):
            coerce("t", "k", "population", "12,00,000")

    def test_malformed_date_raises(self):
        with self.assertRaises(TransformError):
            coerce("t", "k", "derived_at", "26 July 2026")

    def test_collection_date_is_text_not_date(self):
        """Package004 writes '2026-07-22; 2026-07-24 (v2 enrichment)'."""
        value, _ = coerce("t", "k", "collection_date",
                          "2026-07-22; 2026-07-24 (v2 enrichment)")
        self.assertEqual(value, "2026-07-22; 2026-07-24 (v2 enrichment)")

    def test_minimum_investment_is_text_not_numeric(self):
        """All 45 Package004 values are sourced prose, not a measure."""
        value, _ = coerce("t", "k", "minimum_investment",
                          "Rs 3,50,000 per the KVIC/PMEGP profile")
        self.assertTrue(value.startswith("Rs 3,50,000"))

    def test_content_hash_ignores_sync_bookkeeping(self):
        """Otherwise every run reports every row as updated."""
        a = fixture_row()
        b = dict(a, sync_synced_at="2030-01-01T00:00:00Z", sync_version="v99")
        self.assertEqual(content_hash(a), content_hash(b))

    def test_content_hash_changes_when_data_changes(self):
        self.assertNotEqual(content_hash(fixture_row(name="Alpha")),
                            content_hash(fixture_row(name="Beta")))

    def test_transform_collects_all_errors_not_just_the_first(self):
        s = spec("kg_districts")
        rows = [{"sync_row_key": f"k{i}", "sync_source_package": "p",
                 "sync_source_dataset": "d", "sync_source_row_id": f"k{i}",
                 "population": "not-a-number"} for i in range(3)]
        _, errors = transform(s, rows, "v1")
        self.assertEqual(len(errors), 3)


# ────────────────────────────────────────────────────────── change detection
class ChangeDetectionTest(unittest.TestCase):
    def setUp(self):
        self.manifest = Manifest(data={"version": None, "tables": {}})

    def test_first_run_is_all_inserts(self):
        rows = [fixture_row("a"), fixture_row("b")]
        ch = changes_mod.detect("t", rows, self.manifest)
        self.assertEqual(len(ch.inserts), 2)
        self.assertEqual((len(ch.updates), len(ch.deletes), ch.skips), (0, 0, 0))

    def test_unchanged_rows_are_skipped(self):
        rows = [fixture_row("a")]
        self.manifest.record("t", rows)
        ch = changes_mod.detect("t", rows, self.manifest)
        self.assertEqual(ch.skips, 1)
        self.assertFalse(ch.has_work)

    def test_changed_row_is_an_update(self):
        self.manifest.record("t", [fixture_row("a", name="Alpha")])
        ch = changes_mod.detect("t", [fixture_row("a", name="Renamed")], self.manifest)
        self.assertEqual(len(ch.updates), 1)
        self.assertEqual(len(ch.inserts), 0)

    def test_vanished_row_is_a_delete(self):
        self.manifest.record("t", [fixture_row("a"), fixture_row("b")])
        ch = changes_mod.detect("t", [fixture_row("a")], self.manifest)
        self.assertEqual(ch.deletes, ["b"])

    def test_full_mode_ignores_the_manifest(self):
        rows = [fixture_row("a")]
        self.manifest.record("t", rows)
        ch = changes_mod.detect("t", rows, self.manifest, full=True)
        self.assertEqual(len(ch.inserts), 1)
        self.assertEqual(ch.skips, 0)

    def test_manifest_round_trips(self):
        with tempfile.TemporaryDirectory() as d:
            m = Manifest(path=Path(d) / "m.json")
            m.record("t", [fixture_row("a")])
            m.stamp("v1")
            m.save()
            again = Manifest(path=Path(d) / "m.json")
            self.assertEqual(again.data["version"], "v1")
            self.assertEqual(again.row_count(), 1)

    def test_missing_manifest_means_never_synced(self):
        with tempfile.TemporaryDirectory() as d:
            m = Manifest(path=Path(d) / "absent.json")
            self.assertIsNone(m.data["version"])
            self.assertEqual(m.row_count(), 0)


# ───────────────────────────────────────────────────────────────── adapters
class AdapterTest(unittest.TestCase):
    def test_writing_to_an_unknown_table_is_refused(self):
        """The allowlist, not a denylist: a typo cannot reach a user table."""
        t = InMemoryTarget()
        for forbidden in ("profiles", "auth.users", "connections", "kg_typo"):
            with self.subTest(table=forbidden):
                with self.assertRaises(TargetError):
                    t.upsert(forbidden, [fixture_row()])

    def test_every_user_table_named_in_the_brief_is_unreachable(self):
        t = InMemoryTarget()
        for table in ("auth.users", "profiles", "connections", "messages", "teams",
                      "projects", "idea_library", "bookmarks", "notifications",
                      "assessment_results", "opportunities", "collaborator_profiles"):
            with self.subTest(table=table):
                with self.assertRaises(TargetError):
                    t.upsert(table, [])
                with self.assertRaises(TargetError):
                    t.soft_delete(table, ["x"], "now")

    def test_upsert_then_count(self):
        t = InMemoryTarget()
        t.upsert("kg_skills", [fixture_row("a"), fixture_row("b")])
        self.assertEqual(t.count("kg_skills"), 2)

    def test_soft_delete_keeps_the_row(self):
        t = InMemoryTarget()
        t.upsert("kg_skills", [fixture_row("a")])
        t.soft_delete("kg_skills", ["a"], "2026-01-01T00:00:00Z")
        self.assertEqual(t.count("kg_skills"), 0)
        self.assertEqual(t.count("kg_skills", include_deleted=True), 1,
                         "a soft delete must not remove the row")

    def test_restore_undoes_a_soft_delete(self):
        t = InMemoryTarget()
        t.upsert("kg_skills", [fixture_row("a")])
        t.soft_delete("kg_skills", ["a"], "2026-01-01T00:00:00Z")
        t.restore("kg_skills", ["a"])
        self.assertEqual(t.count("kg_skills"), 1)

    def test_supabase_target_refuses_to_construct_without_credentials(self):
        """Fail at construction, not halfway through a write."""
        import os
        saved = {k: os.environ.pop(k, None)
                 for k in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")}
        try:
            with self.assertRaises(TargetError):
                SupabaseTarget()
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v


# ─────────────────────────────────────────────────────────────── validation
class ValidationTest(unittest.TestCase):
    def test_clean_tables_pass(self):
        s = spec("kg_skills")
        rows, _ = transform(s, extract(s), "v1")
        report = validation_mod.validate([s], {"kg_skills": rows})
        self.assertTrue(report.ok, [str(f) for f in report.errors[:5]])

    def test_duplicate_row_key_is_an_error(self):
        s = spec("kg_skills")
        rows, _ = transform(s, extract(s), "v1")
        report = validation_mod.validate([s], {"kg_skills": rows[:1] + rows[:1]})
        self.assertFalse(report.ok)
        self.assertTrue(any(f.check == "V2-KEY" for f in report.errors))

    def test_missing_required_column_is_an_error(self):
        s = spec("kg_skills")
        rows, _ = transform(s, extract(s), "v1")
        rows[0]["skill_name"] = ""
        report = validation_mod.validate([s], {"kg_skills": rows})
        self.assertTrue(any(f.check == "V3-REQUIRED" for f in report.errors))

    def test_broken_foreign_key_is_an_error(self):
        ents = spec("kg_entities")
        rels = spec("kg_relationships")
        e_rows, _ = transform(ents, extract(ents), "v1")
        r_rows, _ = transform(rels, extract(rels), "v1")
        r_rows[0]["to_entity"] = "vw:crop:does-not-exist"
        report = validation_mod.validate([ents, rels],
                                         {"kg_entities": e_rows,
                                          "kg_relationships": r_rows})
        self.assertFalse(report.ok)
        self.assertTrue(any(f.check == "V4-FOREIGN_KEY" for f in report.errors))

    def test_out_of_range_confidence_is_an_error(self):
        s = spec("kg_skills")
        rows, _ = transform(s, extract(s), "v1")
        rows[0]["confidence_score"] = 150
        report = validation_mod.validate([s], {"kg_skills": rows})
        self.assertTrue(any(f.check == "V5-CONFIDENCE" for f in report.errors))

    def test_unknown_verification_status_is_an_error(self):
        s = spec("kg_skills")
        rows, _ = transform(s, extract(s), "v1")
        rows[0]["verification_status"] = "VST-PROBABLY-FINE"
        report = validation_mod.validate([s], {"kg_skills": rows})
        self.assertTrue(any(f.check == "V7-VERIFICATION" for f in report.errors))

    def test_needs_review_is_not_a_finding(self):
        """All 2,299 rows are unreviewed. Flagging that would flag everything."""
        s = spec("kg_skills")
        rows, _ = transform(s, extract(s), "v1")
        self.assertTrue(any(r["verification_status"] == "VST-NEEDS_REVIEW"
                            for r in rows))
        report = validation_mod.validate([s], {"kg_skills": rows})
        self.assertTrue(report.ok)

    def test_declared_overlap_warns_but_undeclared_errors(self):
        ents = spec("kg_entities")
        rows, _ = transform(ents, extract(ents), "v1")
        clean = validation_mod.validate([ents], {"kg_entities": rows})
        self.assertTrue(clean.ok, "declared overlaps must not fail the build")
        self.assertTrue(clean.warnings, "but they must still be reported")

        rows[0]["entity_type"] = "Crop"
        rows[0]["source_package"] = "Package002_Education"   # undeclared
        dirty = validation_mod.validate([ents], {"kg_entities": rows})
        self.assertFalse(dirty.ok)
        self.assertTrue(any(f.check == "V6-OWNERSHIP" for f in dirty.errors))


# ─────────────────────────────────────────────────────────────── the engine
class EngineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.target = InMemoryTarget()
        self.engine = SyncEngine(target=self.target, state_dir=self.dir, quiet=True,
                                 manifest=Manifest(path=self.dir / "manifest.json"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_dry_run_writes_nothing(self):
        result = self.engine.run(SyncMode.DRY_RUN)
        self.assertFalse(result.applied)
        self.assertEqual(self.target.calls, [], "a dry run must not touch the target")
        self.assertGreater(result.metrics["rows_from_source"], 1000)

    def test_dry_run_still_produces_a_plan(self):
        result = self.engine.run(SyncMode.DRY_RUN)
        self.assertTrue(Path(result.snapshot).exists())

    def test_incremental_first_run_inserts_everything(self):
        result = self.engine.run(SyncMode.INCREMENTAL)
        self.assertTrue(result.applied)
        self.assertEqual(result.metrics["rows_inserted"],
                         result.metrics["rows_from_source"])
        self.assertEqual(result.metrics["rows_updated"], 0)

    def test_second_run_is_a_no_op(self):
        """Idempotency: the property that makes a scheduled sync safe."""
        self.engine.run(SyncMode.INCREMENTAL)
        second = self.engine.run(SyncMode.INCREMENTAL)
        self.assertEqual(second.metrics["rows_inserted"], 0)
        self.assertEqual(second.metrics["rows_updated"], 0)
        self.assertEqual(second.metrics["rows_skipped"],
                         second.metrics["rows_from_source"])

    def test_full_mode_rewrites_everything(self):
        self.engine.run(SyncMode.INCREMENTAL)
        full = self.engine.run(SyncMode.FULL)
        self.assertEqual(full.metrics["rows_inserted"], full.metrics["rows_from_source"])

    def test_coverage_is_complete_after_a_sync(self):
        result = self.engine.run(SyncMode.INCREMENTAL)
        for table, c in result.metrics["coverage"].items():
            with self.subTest(table=table):
                self.assertTrue(c["complete"], f"{table}: {c}")

    def test_single_table_sync(self):
        result = self.engine.run(SyncMode.INCREMENTAL, tables=["kg_schemes"])
        self.assertEqual(self.target.count("kg_schemes"), 40)
        self.assertEqual(self.target.count("kg_skills"), 0)
        self.assertEqual(result.metrics["tables_processed"], 1)

    def test_validation_failure_aborts_before_writing(self):
        """All-or-nothing: a partial projection is worse than a stale one."""
        broken = list(TABLE_SPECS)
        rels = spec("kg_relationships")
        engine = SyncEngine(target=self.target, state_dir=self.dir, quiet=True,
                            specs=[rels],       # entities absent -> FKs unresolvable
                            manifest=Manifest(path=self.dir / "m2.json"))
        with self.assertRaises(SyncAborted):
            engine.run(SyncMode.INCREMENTAL)
        self.assertEqual(self.target.calls, [])

    def test_failed_apply_does_not_advance_the_manifest(self):
        """Otherwise the next run skips the rows that failed, forever."""
        target = InMemoryTarget(fail_on={("kg_skills", "upsert")})
        manifest = Manifest(path=self.dir / "m3.json")
        engine = SyncEngine(target=target, state_dir=self.dir, quiet=True,
                            specs=[spec("kg_skills")], manifest=manifest)
        with self.assertRaises(SyncAborted):
            engine.run(SyncMode.INCREMENTAL)
        self.assertIsNone(manifest.data["version"])
        self.assertEqual(manifest.row_count(), 0)

    def test_a_deleted_source_row_is_soft_deleted(self):
        engine = SyncEngine(target=self.target, state_dir=self.dir, quiet=True,
                            specs=[spec("kg_schemes")],
                            manifest=Manifest(path=self.dir / "m4.json"))
        engine.run(SyncMode.INCREMENTAL)
        engine.manifest.tables["kg_schemes"]["ghost-row"] = "deadbeef"
        result = engine.run(SyncMode.INCREMENTAL)
        self.assertEqual(result.metrics["rows_soft_deleted"], 1)

    def test_run_is_logged(self):
        self.engine.run(SyncMode.INCREMENTAL)
        log = self.dir / "sync_log.jsonl"
        self.assertTrue(log.exists())
        record = json.loads(log.read_text().splitlines()[-1])
        self.assertEqual(record["outcome"], "SUCCESS")
        self.assertIn("metrics", record)


# ───────────────────────────────────────────────────────────────── rollback
class RollbackTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.target = InMemoryTarget()
        self.engine = SyncEngine(target=self.target, state_dir=self.dir, quiet=True,
                                 specs=[spec("kg_schemes")],
                                 manifest=Manifest(path=self.dir / "manifest.json"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_rollback_of_inserts_soft_deletes_them(self):
        result = self.engine.run(SyncMode.INCREMENTAL)
        self.assertEqual(self.target.count("kg_schemes"), 40)
        self.engine.rollback(result.run_id)
        self.assertEqual(self.target.count("kg_schemes"), 0)
        self.assertEqual(self.target.count("kg_schemes", include_deleted=True), 40,
                         "rollback must not hard-delete")

    def test_rollback_dry_run_changes_nothing(self):
        result = self.engine.run(SyncMode.INCREMENTAL)
        before = self.target.count("kg_schemes")
        self.engine.rollback(result.run_id, dry_run=True)
        self.assertEqual(self.target.count("kg_schemes"), before)

    def test_rollback_restores_the_previous_manifest(self):
        result = self.engine.run(SyncMode.INCREMENTAL)
        self.assertIsNotNone(self.engine.manifest.data["version"])
        self.engine.rollback(result.run_id)
        restored = Manifest(path=self.dir / "manifest.json")
        self.assertIsNone(restored.data["version"],
                          "after rollback the next run must replay")

    def test_rollback_of_an_unknown_run_fails_clearly(self):
        with self.assertRaises(rollback_mod.RollbackError) as ctx:
            self.engine.rollback("20990101T000000Z-nope")
        self.assertIn("no snapshot", str(ctx.exception))

    def test_snapshot_captures_pre_images_for_updates(self):
        first = self.engine.run(SyncMode.INCREMENTAL)
        key = next(iter(self.target.rows["kg_schemes"]))
        self.target.rows["kg_schemes"][key]["scheme_name"] = "EDITED"
        self.engine.manifest.tables["kg_schemes"][key] = "stale-hash"
        second = self.engine.run(SyncMode.INCREMENTAL)
        snap = json.loads(Path(second.snapshot).read_text())
        self.assertIn(key, snap["tables"]["kg_schemes"]["pre_images"])
        self.assertEqual(
            snap["tables"]["kg_schemes"]["pre_images"][key]["scheme_name"], "EDITED")
        self.engine.rollback(second.run_id)
        self.assertEqual(self.target.rows["kg_schemes"][key]["scheme_name"], "EDITED",
                         "rollback must restore the pre-image")
        self.assertNotEqual(first.run_id, second.run_id)


# ────────────────────────────────────────────────────────────────── metrics
class MetricsTest(unittest.TestCase):
    def test_metrics_reconcile_with_the_changes(self):
        with tempfile.TemporaryDirectory() as d:
            engine = SyncEngine(target=InMemoryTarget(), state_dir=Path(d), quiet=True,
                                manifest=Manifest(path=Path(d) / "m.json"))
            m = engine.run(SyncMode.INCREMENTAL).metrics
            self.assertEqual(m["rows_inserted"] + m["rows_updated"],
                             m["rows_synchronised"])
            per = sum(t["source_rows"] for t in m["by_table"].values())
            self.assertEqual(per, m["rows_from_source"])

    def test_pending_rate_is_computed_from_real_sentinels(self):
        with tempfile.TemporaryDirectory() as d:
            engine = SyncEngine(target=InMemoryTarget(), state_dir=Path(d), quiet=True,
                                manifest=Manifest(path=Path(d) / "m.json"))
            m = engine.run(SyncMode.DRY_RUN).metrics
            self.assertGreater(m["pending_cells"], 0,
                               "the packages do contain sentinels")
            self.assertLess(m["pending_rate_pct"], 100)


# ──────────────────────────────────────────────────── configuration + schema
class ConfigurationTest(unittest.TestCase):
    def test_all_eight_tables_the_brief_names_are_present(self):
        expected = {"kg_districts", "kg_skills", "kg_schemes", "kg_businesses",
                    "kg_industries", "kg_agriculture", "kg_entities",
                    "kg_relationships"}
        self.assertEqual({s.name for s in TABLE_SPECS}, expected)

    def test_every_source_file_exists(self):
        for s in TABLE_SPECS:
            for src in s.sources:
                with self.subTest(table=s.name, source=src.dataset):
                    self.assertTrue(src.path.exists(), f"missing {src.path}")

    def test_entities_are_specified_before_relationships(self):
        """Extraction order matters: relationship FKs resolve against entities."""
        names = [s.name for s in TABLE_SPECS]
        self.assertLess(names.index("kg_entities"), names.index("kg_relationships"))

    def test_target_schema_is_not_public(self):
        """kg_skills, kg_schemes and kg_relationships already exist in public."""
        self.assertEqual(TARGET_SCHEMA, "knowledge")
        self.assertNotEqual(TARGET_SCHEMA, "public")

    def test_the_three_colliding_names_are_still_used(self):
        """The separate schema exists so the brief's names could be honoured."""
        names = {s.name for s in TABLE_SPECS}
        for colliding in ("kg_skills", "kg_schemes", "kg_relationships"):
            self.assertIn(colliding, names)


class MigrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / "knowledge_sync" / "migrations" / "001_knowledge_schema.sql"
        cls.sql = cls.path.read_text(encoding="utf-8")

    def test_migration_matches_the_specs(self):
        import subprocess
        r = subprocess.run(
            [sys.executable, "knowledge_sync/generate_migration.py", "--check"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_table_is_created_in_the_knowledge_schema(self):
        for s in TABLE_SPECS:
            with self.subTest(table=s.name):
                self.assertIn(f"create table if not exists {TARGET_SCHEMA}.{s.name}",
                              self.sql)

    def test_no_public_table_is_created_or_altered(self):
        lowered = self.sql.lower()
        for forbidden in ("create table if not exists public.",
                          "alter table public.", "drop table"):
            with self.subTest(statement=forbidden):
                self.assertNotIn(forbidden, lowered)

    def test_no_write_policy_is_granted(self):
        """Writes are impossible for anon/authenticated by absence of a policy."""
        self.assertNotIn("for insert", self.sql.lower())
        self.assertNotIn("for update", self.sql.lower())
        self.assertNotIn("grant insert", self.sql.lower())

    def test_rls_is_enabled_on_every_table(self):
        for s in TABLE_SPECS:
            with self.subTest(table=s.name):
                self.assertIn(
                    f"alter table {TARGET_SCHEMA}.{s.name} enable row level security",
                    self.sql)

    def test_soft_delete_column_exists_everywhere(self):
        self.assertEqual(self.sql.count("sync_deleted_at              timestamptz"),
                         len(TABLE_SPECS))


# ─────────────────────────────────────────────────────────────────── safety
class SafetyTest(unittest.TestCase):
    """Assertions that the framework CANNOT do what the brief forbids."""

    def test_no_module_references_a_user_table(self):
        forbidden = ("profiles", "auth.users", "connections", "opportunities",
                     "collaborator_profiles", "idea_library", "bookmarks",
                     "assessment_results")
        offenders = []
        for py in sorted((ROOT / "knowledge_sync").rglob("*.py")):
            text = py.read_text(encoding="utf-8")
            for name in forbidden:
                # Mentioning a table in a comment explaining why it is off limits
                # is fine; a string that could become a query is not.
                if f'"{name}"' in text or f"'{name}'" in text:
                    offenders.append(f"{py.name}: {name}")
        self.assertEqual(offenders, [], f"user table names appear as literals: {offenders}")

    def test_no_sql_statement_touches_a_user_table(self):
        """
        Comments are stripped first, deliberately.

        The generated file names its sources in comments, and one of those is
        `china_inspired_adapted_opportunities.csv`. A naive substring search
        flags that as a reference to the `opportunities` table, which would make
        this test fail on a file that is entirely safe — and a safety test that
        cries wolf gets deleted. What matters is the executable SQL.
        """
        raw = (ROOT / "knowledge_sync" / "migrations"
               / "001_knowledge_schema.sql").read_text().lower()
        statements = "\n".join(
            line.split("--", 1)[0] for line in raw.splitlines()).strip()

        for name in ("profiles", "auth.users", "connections", "opportunities",
                     "idea_library", "bookmarks", "assessment_results", "teams",
                     "messages", "projects"):
            with self.subTest(table=name):
                self.assertNotIn(name, statements)

        # Only two `public.` references are permitted, and both are read-only
        # helpers the platform already owns.
        import re
        public_refs = set(re.findall(r"public\.\w+", statements))
        self.assertLessEqual(public_refs, {"public.is_valueweave_admin"},
                             f"unexpected public schema references: {public_refs}")

    def test_every_created_object_lives_in_the_knowledge_schema(self):
        import re
        raw = (ROOT / "knowledge_sync" / "migrations"
               / "001_knowledge_schema.sql").read_text().lower()
        statements = "\n".join(line.split("--", 1)[0] for line in raw.splitlines())
        created = re.findall(r"create table (?:if not exists )?([\w.]+)", statements)
        self.assertTrue(created)
        for obj in created:
            with self.subTest(object=obj):
                self.assertTrue(obj.startswith("knowledge."),
                                f"{obj} is created outside the knowledge schema")

    def test_sync_columns_cannot_collide_with_package_columns(self):
        prefixed = [c for c in SYNC_COLUMNS if c.startswith("sync_")]
        self.assertEqual(len(prefixed), len(SYNC_COLUMNS))
        for s in TABLE_SPECS:
            for c in s.columns:
                with self.subTest(table=s.name, column=c):
                    self.assertFalse(c.startswith("sync_"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
