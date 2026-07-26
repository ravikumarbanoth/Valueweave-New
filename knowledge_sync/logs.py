#!/usr/bin/env python3
"""
Module 5 — Logging. An append-only record of every sync run.

Two outputs, because two audiences read them:

  console   an operator watching a run, wanting to know what is happening
  JSONL     `knowledge_sync/state/sync_log.jsonl`, one object per run, for the
            question "what changed on the 14th, and who ran it?"

Append-only and one-object-per-line for the same reason the stewardship ledger is
append-only: a log that a later run can rewrite is not evidence of anything. JSONL
survives a crash mid-write with at most one truncated line, which a JSON array
does not.

Errors are recorded with the row key that produced them. A log saying "42 rows
failed" without saying which is a log that costs more to act on than it saves.
"""

import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent / "state"
LOG_PATH = STATE_DIR / "sync_log.jsonl"


class SyncLog:
    def __init__(self, run_id, mode, path=None, quiet=False):
        self.run_id = run_id
        self.mode = mode
        self.path = Path(path) if path else LOG_PATH
        self.quiet = quiet
        self.started_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self._t0 = time.perf_counter()
        self.events = []
        self.errors = []
        self.tables = {}

    # ----------------------------------------------------------------- write
    def event(self, kind, message, **fields):
        entry = {"kind": kind, "message": message, **fields}
        self.events.append(entry)
        if not self.quiet:
            print(f"  {kind:<10} {message}")
        return entry

    def error(self, message, table="", row_key="", **fields):
        entry = {"message": message, "table": table, "row_key": row_key, **fields}
        self.errors.append(entry)
        if not self.quiet:
            print(f"  ERROR      {table}{f' [{row_key}]' if row_key else ''}: {message}")
        return entry

    def table_result(self, table, **fields):
        self.tables[table] = fields
        if not self.quiet:
            print(f"  {table:<20} " + "  ".join(f"{k}={v}" for k, v in fields.items()))

    @contextmanager
    def phase(self, name):
        t0 = time.perf_counter()
        if not self.quiet:
            print(f"\n[{name}]")
        try:
            yield
        finally:
            self.event("phase", name, seconds=round(time.perf_counter() - t0, 3))

    # ---------------------------------------------------------------- finish
    @property
    def duration(self):
        return round(time.perf_counter() - self._t0, 3)

    def to_dict(self, outcome, metrics=None):
        return {
            "run_id": self.run_id,
            "mode": self.mode,
            "outcome": outcome,
            "started_at": self.started_at,
            "finished_at": datetime.now(timezone.utc).replace(
                microsecond=0).isoformat(),
            "duration_seconds": self.duration,
            "tables": self.tables,
            "errors": self.errors[:100],
            "error_count": len(self.errors),
            "metrics": metrics or {},
        }

    def persist(self, outcome, metrics=None):
        record = self.to_dict(outcome, metrics)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
        return record


def read_log(path=None, limit=20):
    """Most recent runs, newest first."""
    path = Path(path) if path else LOG_PATH
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            # A truncated final line from an interrupted write. Skip it rather
            # than fail: the rest of the log is still readable, which is the
            # whole reason for JSONL over a JSON array.
            continue
    return list(reversed(out))[:limit]
