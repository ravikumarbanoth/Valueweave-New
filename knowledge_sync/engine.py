#!/usr/bin/env python3
"""
Module 4 — Synchronisation. The engine that runs the other six.

    extract -> transform -> validate -> detect changes -> snapshot -> apply
                                 │
                                 └── abort here on any error, before the snapshot

FOUR MODES
----------
  DRY_RUN      plan and report, write nothing. Needs no credentials.
  INCREMENTAL  apply only what changed since the manifest. The default.
  FULL         treat every row as new. For a first load, or recovery from drift.
  ROLLBACK     handled by rollback.py; the engine exposes it for one entry point.

THE ORDERING RULE THAT MATTERS
------------------------------
Validation runs across *all* tables before *any* table is written. It has to:
kg_relationships cannot be validated without kg_entities, and writing entities
before discovering that the edges are broken would leave the target in a state
that is neither the old one nor the new one.

So the engine is all-or-nothing at the run level. One bad foreign key anywhere
aborts everything, and the target is untouched. A partially-synced projection is
worse than a stale one: stale is merely old, partial is silently inconsistent,
and only one of those is obvious to a consumer.

WHY THE MANIFEST IS WRITTEN LAST
--------------------------------
If the manifest were written first and the apply then failed, the next run would
believe the failed rows were already synced and skip them forever. Written last,
a crashed run simply replays.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from knowledge_sync import changes as changes_mod
from knowledge_sync import metrics as metrics_mod
from knowledge_sync import rollback as rollback_mod
from knowledge_sync import validation as validation_mod
from knowledge_sync.adapters import InMemoryTarget, utcnow
from knowledge_sync.config import TABLE_SPECS, spec as get_spec
from knowledge_sync.extract import extract
from knowledge_sync.logs import SyncLog
from knowledge_sync.transform import transform


class SyncMode(str, Enum):
    DRY_RUN = "dry-run"
    INCREMENTAL = "incremental"
    FULL = "full"
    ROLLBACK = "rollback"


class SyncAborted(RuntimeError):
    """Raised when a run stops before writing. Carries the report."""

    def __init__(self, message, report=None, errors=None):
        super().__init__(message)
        self.report = report
        self.errors = errors or []


class SyncEngine:
    def __init__(self, target=None, specs=TABLE_SPECS, manifest=None,
                 state_dir=None, quiet=False):
        self.target = target if target is not None else InMemoryTarget()
        self.specs = tuple(specs)
        self.quiet = quiet
        self.state_dir = state_dir
        self.manifest = manifest if manifest is not None else changes_mod.Manifest(
            path=(state_dir and f"{state_dir}/manifest.json") or None)

    # ------------------------------------------------------------------ run
    def run(self, mode=SyncMode.DRY_RUN, tables=None, version=None):
        mode = SyncMode(mode)
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + \
            "-" + uuid.uuid4().hex[:6]
        version = version or run_id
        specs = [s for s in self.specs if not tables or s.name in set(tables)]
        if not specs:
            raise SyncAborted(f"no tables matched {tables!r}")

        log = SyncLog(run_id, mode.value, quiet=self.quiet,
                      path=(state_dir_path(self.state_dir, "sync_log.jsonl")))
        if not self.quiet:
            print(f"ValueWeave knowledge sync — {mode.value}")
            print(f"  run {run_id}  ·  {len(specs)} table(s)  ·  target "
                  f"{type(self.target).__name__}")

        # ------------------------------------------------ extract + transform
        extracted, transform_errors = {}, []
        with log.phase("extract + transform"):
            for spec in specs:
                rows = extract(spec)
                rows, errs = transform(spec, rows, version)
                extracted[spec.name] = rows
                transform_errors.extend(errs)
                log.event("extract", f"{spec.name}: {len(rows)} rows",
                          table=spec.name, rows=len(rows))
            for err in transform_errors:
                log.error(str(err), table=err.table, row_key=err.row_key)

        if transform_errors:
            log.persist("ABORTED_TRANSFORM")
            raise SyncAborted(
                f"{len(transform_errors)} transform error(s); nothing was written",
                errors=transform_errors)

        # ----------------------------------------------------------- validate
        with log.phase("validate"):
            report = validation_mod.validate(specs, extracted)
            for f in report.findings:
                (log.error if f.severity == validation_mod.ERROR else log.event)(
                    *( (f.detail,) if f.severity == validation_mod.ERROR
                       else ("warning", f"{f.check} {f.table}: {f.detail}") ),
                    **({"table": f.table, "row_key": f.row_key}
                       if f.severity == validation_mod.ERROR else {}))
            log.event("validate",
                      f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)")

        if not report.ok:
            log.persist("ABORTED_VALIDATION", {"validation": report.to_dict()})
            raise SyncAborted(
                f"{len(report.errors)} validation error(s); nothing was written",
                report=report)

        # ---------------------------------------------------- detect changes
        with log.phase("detect changes"):
            all_changes = changes_mod.detect_all(
                extracted, self.manifest, full=(mode is SyncMode.FULL))
            for name, ch in sorted(all_changes.items()):
                log.table_result(name, **{k: v for k, v in ch.summary().items()
                                          if k != "table"})

        totals = changes_mod.totals(all_changes)
        packages = {src.package for s in specs for src in s.sources}

        # --------------------------------------------------------- dry run?
        if mode is SyncMode.DRY_RUN:
            m = metrics_mod.build(run_id, mode.value, version, all_changes, extracted,
                                  report, log.duration, packages)
            m["applied"] = False
            snapshot = rollback_mod.write_snapshot(
                run_id, all_changes, self.manifest.data,
                directory=state_dir_path(self.state_dir, "snapshots"))
            log.event("dry-run", f"plan written to {snapshot.name}; nothing applied")
            record = log.persist("DRY_RUN", m)
            return SyncResult(run_id, mode, m, report, all_changes, record,
                              applied=False, snapshot=str(snapshot))

        # ---------------------------------------------------------- snapshot
        with log.phase("snapshot"):
            snapshot = rollback_mod.write_snapshot(
                run_id, all_changes, self.manifest.data, target=self.target,
                directory=state_dir_path(self.state_dir, "snapshots"))
            log.event("snapshot", str(snapshot.name))

        # ------------------------------------------------------------- apply
        now = utcnow()
        with log.phase("apply"):
            try:
                for spec in specs:
                    ch = all_changes[spec.name]
                    if ch.inserts or ch.updates:
                        self.target.upsert(spec.name, ch.inserts + ch.updates)
                    if ch.deletes:
                        self.target.soft_delete(spec.name, ch.deletes, now)
            except Exception as exc:                                # noqa: BLE001
                log.error(f"apply failed: {type(exc).__name__}: {exc}")
                log.persist("ABORTED_APPLY")
                raise SyncAborted(
                    f"apply failed ({exc}). The manifest was NOT advanced, so the "
                    f"next run replays this one. Snapshot: {snapshot.name}") from exc

        # ---------------------------------------------- manifest, written last
        with log.phase("commit manifest"):
            for spec in specs:
                self.manifest.record(spec.name, extracted[spec.name])
            self.manifest.stamp(version)
            path = self.manifest.save()
            log.event("manifest", f"{self.manifest.row_count()} rows recorded in "
                                  f"{path.name}")

        m = metrics_mod.build(run_id, mode.value, version, all_changes, extracted,
                              report, log.duration, packages)
        m["applied"] = True
        m["coverage"] = metrics_mod.coverage(self.target, specs, extracted)
        record = log.persist("SUCCESS", m)
        if not self.quiet:
            print(f"\n  {totals.get('insert', 0)} inserted, "
                  f"{totals.get('update', 0)} updated, "
                  f"{totals.get('delete', 0)} soft-deleted, "
                  f"{totals.get('skip', 0)} unchanged  ·  {log.duration}s")
        return SyncResult(run_id, mode, m, report, all_changes, record,
                          applied=True, snapshot=str(snapshot))

    # ------------------------------------------------------------- rollback
    def rollback(self, run_id, dry_run=False):
        result = rollback_mod.rollback(
            run_id, self.target, dry_run=dry_run,
            directory=state_dir_path(self.state_dir, "snapshots"))
        if not dry_run:
            rollback_mod.restore_manifest(
                run_id,
                manifest_path=state_dir_path(self.state_dir, "manifest.json"),
                directory=state_dir_path(self.state_dir, "snapshots"))
        return result


class SyncResult:
    def __init__(self, run_id, mode, metrics, report, all_changes, log_record,
                 applied, snapshot):
        self.run_id = run_id
        self.mode = mode
        self.metrics = metrics
        self.report = report
        self.changes = all_changes
        self.log_record = log_record
        self.applied = applied
        self.snapshot = snapshot

    @property
    def ok(self):
        return self.report.ok

    def to_dict(self):
        return {"run_id": self.run_id, "mode": self.mode.value,
                "applied": self.applied, "snapshot": self.snapshot,
                "metrics": self.metrics, "validation": self.report.to_dict()}


def state_dir_path(state_dir, leaf):
    from pathlib import Path
    if state_dir is None:
        return None if leaf == "manifest.json" else None
    return Path(state_dir) / leaf
