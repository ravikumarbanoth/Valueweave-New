#!/usr/bin/env python3
"""
Module 6 — Rollback.

Restores the target to the state recorded by a previous sync, using the snapshot
that sync wrote before it changed anything.

WHAT A SNAPSHOT CONTAINS, AND WHY THAT IS ENOUGH
------------------------------------------------
Before applying changes, the engine writes `state/snapshots/<run_id>.json`: for
every table, the rows that were about to be inserted or updated, plus the row
keys about to be soft-deleted, plus the previous manifest.

That is sufficient because the projection is *derived*. Rolling back does not
need the old row bodies for anything the sync did not touch — those are still
there, unmodified. It needs only to undo the three things the run did:

    inserted   -> soft delete (never hard delete: see below)
    updated    -> restore the pre-image, which the snapshot holds
    deleted    -> restore, clearing sync_deleted_at

**A rolled-back insert is soft-deleted, not removed.** The row existed in the
target for some period and something may have referenced it. Soft delete makes
the rollback itself reversible and leaves the audit trail intact, which a DELETE
would not. `purge` in the CLI exists for the operator who genuinely wants the row
gone, and rollback never calls it.

THE HONEST LIMIT
----------------
Rollback restores what the *framework* changed. It cannot restore a row someone
edited by hand in the Supabase console between two syncs — that edit is not in
any snapshot, and the next sync would overwrite it anyway. This is why projected
rows are read-only in the admin UI. The limit is stated here rather than
discovered later.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent / "state"
SNAPSHOT_DIR = STATE_DIR / "snapshots"


class RollbackError(RuntimeError):
    pass


def snapshot_path(run_id, directory=None):
    return Path(directory or SNAPSHOT_DIR) / f"{run_id}.json"


def write_snapshot(run_id, all_changes, previous_manifest, target=None, directory=None):
    """
    Capture what is about to change, before it changes.

    When a target is supplied, the *current* row bodies for the rows about to be
    updated are read back and stored as pre-images. Without a target — a dry run
    — the snapshot still records the plan, so it can be inspected.
    """
    payload = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "previous_manifest": previous_manifest,
        "tables": {},
    }
    for name, changes in all_changes.items():
        pre_images = {}
        if target is not None and changes.updates:
            existing = getattr(target, "rows", {}).get(name, {})
            for row in changes.updates:
                key = row["sync_row_key"]
                if key in existing:
                    pre_images[key] = dict(existing[key])
        payload["tables"][name] = {
            "inserted_keys": [r["sync_row_key"] for r in changes.inserts],
            "updated_keys": [r["sync_row_key"] for r in changes.updates],
            "deleted_keys": list(changes.deletes),
            "pre_images": pre_images,
        }
    path = snapshot_path(run_id, directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


def list_snapshots(directory=None):
    d = Path(directory or SNAPSHOT_DIR)
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob("*.json"), reverse=True):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        out.append({
            "run_id": data.get("run_id", p.stem),
            "created_at": data.get("created_at"),
            "path": str(p),
            "tables": {t: {k: len(v) for k, v in d2.items() if isinstance(v, list)}
                       for t, d2 in data.get("tables", {}).items()},
        })
    return out


def rollback(run_id, target, directory=None, dry_run=False):
    """Undo one run. Returns a report of exactly what was reversed."""
    path = snapshot_path(run_id, directory)
    if not path.exists():
        available = [s["run_id"] for s in list_snapshots(directory)]
        raise RollbackError(
            f"no snapshot for run {run_id!r}. Available: {available or 'none'}")

    data = json.loads(path.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    result = {"run_id": run_id, "dry_run": dry_run, "snapshot": str(path), "tables": {}}

    for table, entry in sorted(data.get("tables", {}).items()):
        inserted = entry.get("inserted_keys", [])
        pre_images = entry.get("pre_images", {})
        deleted = entry.get("deleted_keys", [])

        plan = {
            "soft_delete_reverted_inserts": len(inserted),
            "restored_pre_images": len(pre_images),
            "undeleted": len(deleted),
        }
        if not dry_run:
            if inserted:
                target.soft_delete(table, inserted, now)
            if pre_images:
                target.upsert(table, list(pre_images.values()))
            if deleted:
                target.restore(table, deleted)
        result["tables"][table] = plan

    result["manifest_restored_to"] = data.get("previous_manifest", {}).get("version")
    return result


def restore_manifest(run_id, manifest_path=None, directory=None):
    """Put the manifest back to its pre-run state, so the next sync plans correctly."""
    path = snapshot_path(run_id, directory)
    if not path.exists():
        raise RollbackError(f"no snapshot for run {run_id!r}")
    data = json.loads(path.read_text(encoding="utf-8"))
    previous = data.get("previous_manifest")
    if previous is None:
        raise RollbackError(f"snapshot {run_id!r} carries no previous manifest")
    out = Path(manifest_path) if manifest_path else STATE_DIR / "manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(previous, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    return out
