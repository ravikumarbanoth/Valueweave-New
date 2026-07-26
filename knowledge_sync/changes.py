#!/usr/bin/env python3
"""
Module 1 — Change Detection.

Compares the rows Git currently produces against the manifest written by the last
successful sync, and classifies each row: INSERT, UPDATE, DELETE, or SKIP.

WHY A MANIFEST AND NOT A QUERY AGAINST SUPABASE
-----------------------------------------------
Asking the target what it holds seems more direct, and is worse in three ways.
It requires a live connection to *plan* a sync, which makes dry-run useless
offline and untestable without credentials. It makes the plan depend on the
target's round-tripping — a numeric column read back as a string would look like
a change on every run. And it silently ratifies drift: if someone hand-edited a
row, comparing against the target treats the edit as the baseline.

The manifest is a committed record of what this framework last wrote. Comparing
against it means the sync is reproducible, plannable offline, and detects
tampering as a change to be corrected rather than a state to preserve.

DELETION IS SOFT, ALWAYS
------------------------
A row that disappears from a package is marked `sync_deleted_at` rather than
removed. Package data is versioned and immutable; a row vanishing usually means a
dataset was regenerated, not that the fact stopped being true. Soft delete keeps
the row queryable for anything already referencing it and makes the removal
reversible without a restore. `purge_deleted()` exists for when a real delete is
wanted, and it is never called by a sync.
"""

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent / "state"

INSERT, UPDATE, DELETE, SKIP = "INSERT", "UPDATE", "DELETE", "SKIP"


@dataclass
class TableChanges:
    table: str
    inserts: list = field(default_factory=list)
    updates: list = field(default_factory=list)
    deletes: list = field(default_factory=list)   # row keys, not rows
    skips: int = 0

    @property
    def total(self):
        return len(self.inserts) + len(self.updates) + len(self.deletes)

    @property
    def has_work(self):
        return self.total > 0

    def summary(self):
        return {"table": self.table, "insert": len(self.inserts),
                "update": len(self.updates), "delete": len(self.deletes),
                "skip": self.skips}


class Manifest:
    """What the last successful sync wrote: {table: {row_key: content_hash}}."""

    def __init__(self, path=None, data=None):
        self.path = Path(path) if path else STATE_DIR / "manifest.json"
        if data is not None:
            self.data = data
        elif self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.data = {"version": None, "synced_at": None, "tables": {}}

    @property
    def tables(self):
        return self.data.setdefault("tables", {})

    def hashes(self, table):
        return self.tables.get(table, {})

    def record(self, table, rows):
        self.tables[table] = {r["sync_row_key"]: r["sync_content_hash"] for r in rows}

    def stamp(self, version):
        self.data["version"] = version
        self.data["synced_at"] = datetime.now(timezone.utc).replace(
            microsecond=0).isoformat()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
        return self.path

    def row_count(self):
        return sum(len(v) for v in self.tables.values())


def detect(table, rows, manifest, full=False):
    """
    Classify every row for one table.

    `full=True` treats every row as an insert regardless of the manifest — the
    mode for rebuilding a target from empty, or recovering from drift.
    """
    changes = TableChanges(table=table)
    previous = {} if full else dict(manifest.hashes(table))

    for row in rows:
        key = row["sync_row_key"]
        old = previous.pop(key, None)
        if old is None:
            changes.inserts.append(row)
        elif old != row["sync_content_hash"]:
            changes.updates.append(row)
        else:
            changes.skips += 1

    # Anything left in `previous` was synced before and Git no longer produces it.
    changes.deletes = sorted(previous)
    return changes


def detect_all(tables, manifest, full=False):
    return {name: detect(name, rows, manifest, full=full)
            for name, rows in tables.items()}


def totals(all_changes):
    c = Counter()
    for ch in all_changes.values():
        c["insert"] += len(ch.inserts)
        c["update"] += len(ch.updates)
        c["delete"] += len(ch.deletes)
        c["skip"] += ch.skips
    return dict(c)
