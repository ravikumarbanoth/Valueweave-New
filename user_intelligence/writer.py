#!/usr/bin/env python3
"""
User intelligence writer — engine output into the `user_intelligence` schema.

WHAT WAS MISSING
----------------
`IntelligenceEngine.run()` has always produced exactly the right rows:
`result.tables()` returns `{table: [rows]}` matching
`user_intelligence/migrations/001_user_intelligence.sql` column for column. What did
not exist was anything that put them in a database. `python3 -m user_intelligence run`
printed JSON to stdout, so the five tables stayed empty and `/dashboard` reported
`NOT_COMPUTED` for every user. Deployment preparation named this blocker B3; this
module is it.

DELIBERATELY THE SAME SHAPE AS knowledge_sync
---------------------------------------------
Adapter interface, `InMemoryTarget` for tests, `SupabaseTarget` for production,
allowlist guard before every write, JSONL run log. An operator who has debugged a
knowledge sync at an inconvenient hour already knows how this behaves, and a second
pattern for the same job would be a second set of failure modes to learn.

IDEMPOTENCY IS THE ENGINE'S, NOT OURS
-------------------------------------
`IntelligenceResult.result_hash()` covers every score, recommendation and piece of
evidence, and deliberately excludes `generated_at`. So "has anything changed for this
user?" is one string comparison against the `result_hash` already stored in
`user_activity_summary`. Re-running for an unchanged user writes nothing at all —
which is what makes it safe to run this on a schedule over every user.

THE ONE SUBTLETY: RECOMMENDATIONS SHRINK
----------------------------------------
The four profile tables are keyed `(user_id, rules_version)` — one row each, so an
upsert is complete by construction. `user_recommendations` is keyed
`(user_id, rules_version, category, item_id)` and holds many rows. If a user had 25
recommendations and now has 20, upserting 20 leaves 5 stale rows that no longer
correspond to anything the engine would produce. Those five are pruned explicitly.
Upsert alone would look correct and quietly accumulate garbage.
"""

import json
import os
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from user_intelligence import RULES_VERSION, __version__
from user_intelligence.config import OUTPUT_TABLES

TARGET_SCHEMA = "user_intelligence"

#: The column set each table is upserted on. Must match the unique constraints in
#: migrations/001_user_intelligence.sql — a mismatch turns an upsert into an insert
#: and the table grows a duplicate per run.
CONFLICT_KEYS = {
    "user_skill_profile": ("user_id", "rules_version"),
    "user_business_profile": ("user_id", "rules_version"),
    "user_learning_profile": ("user_id", "rules_version"),
    "user_activity_summary": ("user_id", "rules_version"),
    "user_recommendations": ("user_id", "rules_version", "category", "item_id"),
}

#: Tables holding exactly one row per (user, rules_version).
SINGLE_ROW_TABLES = tuple(t for t in OUTPUT_TABLES if t != "user_recommendations")

STATE_DIR = Path(__file__).resolve().parent / "state"
LOG_PATH = STATE_DIR / "writer_log.jsonl"

#: Retry schedule in seconds. Three attempts, not ten: a Supabase write either
#: succeeds, hits a transient network fault that clears in a second or two, or is
#: wrong in a way more attempts will not fix.
RETRY_DELAYS = (1.0, 4.0)


class WriterError(RuntimeError):
    pass


# ══════════════════════════════════════════════════════════════════ adapters
class Target(ABC):
    """The four operations writing per-user intelligence needs."""

    schema = TARGET_SCHEMA

    def _assert_target(self, table):
        """
        Allowlist, not denylist.

        The engine's brief forbids touching `auth.users`, `profiles`, `connections`
        and every other application table. Encoding that as a denylist would
        silently permit the next table someone adds; this permits exactly five.
        """
        if table not in OUTPUT_TABLES:
            raise WriterError(
                f"refusing to write to {table!r}: not one of the "
                f"{len(OUTPUT_TABLES)} tables this engine owns "
                f"({', '.join(OUTPUT_TABLES)}). Application and user tables are "
                f"unreachable from here by construction.")

    @abstractmethod
    def upsert(self, table, rows, conflict): ...

    @abstractmethod
    def prune_recommendations(self, user_id, rules_version, keep_item_ids): ...

    @abstractmethod
    def stored_result_hash(self, user_id, rules_version): ...

    @abstractmethod
    def count(self, table): ...

    def delete_user(self, user_id, rules_version=None):
        raise NotImplementedError


class InMemoryTarget(Target):
    """
    Fixture target. Faithful enough to exercise every path, and inspectable.

    Every test runs against this, which is why the suite needs no credentials and
    why the retry, prune and idempotency paths are actually covered rather than
    merely written.
    """

    def __init__(self, seed=None, fail_on=None, fail_times=0):
        self.rows = defaultdict(list)     # table -> [row]
        self.calls = []
        #: (table, op) pairs that should raise.
        self.fail_on = fail_on or set()
        #: How many times a fail_on entry raises before succeeding. Lets a test
        #: distinguish "retries and recovers" from "retries and gives up".
        self.fail_times = fail_times
        self._failures = defaultdict(int)
        for table, rows in (seed or {}).items():
            self.rows[table] = [dict(r) for r in rows]

    def _maybe_fail(self, table, op):
        if (table, op) not in self.fail_on:
            return
        if self.fail_times and self._failures[(table, op)] >= self.fail_times:
            return
        self._failures[(table, op)] += 1
        raise WriterError(f"injected failure: {op} on {table}")

    def upsert(self, table, rows, conflict):
        self._assert_target(table)
        self._maybe_fail(table, "upsert")
        self.calls.append(("upsert", table, len(rows)))
        existing = self.rows[table]
        for row in rows:
            key = tuple(row.get(c) for c in conflict)
            for i, old in enumerate(existing):
                if tuple(old.get(c) for c in conflict) == key:
                    existing[i] = dict(row)
                    break
            else:
                existing.append(dict(row))
        return len(rows)

    def prune_recommendations(self, user_id, rules_version, keep_item_ids):
        self._assert_target("user_recommendations")
        self._maybe_fail("user_recommendations", "prune")
        keep = set(keep_item_ids)
        before = len(self.rows["user_recommendations"])
        self.rows["user_recommendations"] = [
            r for r in self.rows["user_recommendations"]
            if not (r.get("user_id") == user_id
                    and r.get("rules_version") == rules_version
                    and r.get("item_id") not in keep)
        ]
        removed = before - len(self.rows["user_recommendations"])
        self.calls.append(("prune", "user_recommendations", removed))
        return removed

    def stored_result_hash(self, user_id, rules_version):
        for r in self.rows["user_activity_summary"]:
            if r.get("user_id") == user_id and r.get("rules_version") == rules_version:
                return r.get("result_hash")
        return None

    def count(self, table):
        self._assert_target(table)
        return len(self.rows[table])

    def delete_user(self, user_id, rules_version=None):
        n = 0
        for table in OUTPUT_TABLES:
            keep = []
            for r in self.rows[table]:
                match = r.get("user_id") == user_id and (
                    rules_version is None or r.get("rules_version") == rules_version)
                if match:
                    n += 1
                else:
                    keep.append(r)
            self.rows[table] = keep
        self.calls.append(("delete_user", user_id, n))
        return n


class SupabaseTarget(Target):
    """
    The real target. Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.

    The service role bypasses RLS, which is necessary here: `user_intelligence` is
    gated on `auth.uid() = user_id` with no admin exception, so a writer running as
    anyone else could not write another user's rows. It is also why `_assert_target`
    is checked before every call.

    The client is imported lazily so the module — and the whole test suite — works
    with no `supabase` package installed.
    """

    def __init__(self, url=None, service_role_key=None, client=None):
        self.url = url or os.environ.get("SUPABASE_URL")
        self.key = service_role_key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self._client = client
        if client is None and not (self.url and self.key):
            raise WriterError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required. For a dry "
                "run or a test use InMemoryTarget — neither needs credentials.")

    @property
    def client(self):
        if self._client is None:
            try:
                from supabase import create_client       # noqa: PLC0415
            except ImportError as exc:                   # pragma: no cover
                raise WriterError(
                    "the `supabase` package is not installed. It is an optional "
                    "dependency: everything except a live write works without it."
                ) from exc
            self._client = create_client(self.url, self.key)
        return self._client

    def _table(self, table):
        self._assert_target(table)
        return self.client.schema(self.schema).table(table)

    def upsert(self, table, rows, conflict):
        if not rows:
            return 0
        self._table(table).upsert(rows, on_conflict=",".join(conflict)).execute()
        return len(rows)

    def prune_recommendations(self, user_id, rules_version, keep_item_ids):
        q = (self._table("user_recommendations")
             .delete()
             .eq("user_id", user_id)
             .eq("rules_version", rules_version))
        if keep_item_ids:
            # PostgREST `not.in` takes a parenthesised list.
            joined = ",".join(f'"{i}"' for i in sorted(keep_item_ids))
            q = q.filter("item_id", "not.in", f"({joined})")
        resp = q.execute()
        return len(getattr(resp, "data", None) or [])

    def stored_result_hash(self, user_id, rules_version):
        resp = (self._table("user_activity_summary")
                .select("result_hash")
                .eq("user_id", user_id)
                .eq("rules_version", rules_version)
                .limit(1)
                .execute())
        rows = getattr(resp, "data", None) or []
        return rows[0].get("result_hash") if rows else None

    def count(self, table):
        resp = self._table(table).select("user_id", count="exact").execute()
        return getattr(resp, "count", None) or 0

    def delete_user(self, user_id, rules_version=None):
        n = 0
        for table in OUTPUT_TABLES:
            q = self._table(table).delete().eq("user_id", user_id)
            if rules_version is not None:
                q = q.eq("rules_version", rules_version)
            resp = q.execute()
            n += len(getattr(resp, "data", None) or [])
        return n


# ══════════════════════════════════════════════════════════════════ the writer
class UserWriteResult:
    """What happened for one user. `outcome` is the only field a caller must read."""

    #: Written because the result changed, or because nothing was stored before.
    WRITTEN = "WRITTEN"
    #: The engine produced a byte-identical result. Nothing was written.
    UNCHANGED = "UNCHANGED"
    #: Every retry failed. Nothing was written for this user.
    FAILED = "FAILED"

    def __init__(self, user_id, outcome, *, result_hash=None, rows_written=0,
                 rows_pruned=0, attempts=1, error=None, elapsed_ms=0):
        self.user_id = user_id
        self.outcome = outcome
        self.result_hash = result_hash
        self.rows_written = rows_written
        self.rows_pruned = rows_pruned
        self.attempts = attempts
        self.error = error
        self.elapsed_ms = elapsed_ms

    def as_dict(self):
        return {
            "user_id": self.user_id, "outcome": self.outcome,
            "result_hash": self.result_hash, "rows_written": self.rows_written,
            "rows_pruned": self.rows_pruned, "attempts": self.attempts,
            "error": self.error, "elapsed_ms": self.elapsed_ms,
        }

    def __repr__(self):
        return f"<UserWriteResult {self.user_id} {self.outcome} rows={self.rows_written}>"


class IntelligenceWriter:
    """
    Computes intelligence for a user and writes it to the `user_intelligence` schema.

    Args:
        engine:  a built `IntelligenceEngine`. Passed in rather than constructed
                 because loading the knowledge snapshot takes real time and one
                 writer run covers many users.
        target:  a `Target`. Defaults to `InMemoryTarget` — nothing writes to a
                 real database unless a caller asks for it explicitly.
        force:   write even when the result hash is unchanged. For a rules bump
                 where the hash moves anyway, or to repair a partial write.
    """

    def __init__(self, engine, target=None, *, force=False, log_path=LOG_PATH,
                 sleep=time.sleep):
        self.engine = engine
        self.target = target if target is not None else InMemoryTarget()
        self.force = force
        self.log_path = Path(log_path) if log_path else None
        self._sleep = sleep

    # ── one user ────────────────────────────────────────────────────────────
    def write_user(self, context):
        started = time.perf_counter()
        result = self.engine.run(context)
        result_hash = result.result_hash()
        user_id = context.user_id

        if not self.force:
            stored = self._attempt(
                lambda: self.target.stored_result_hash(user_id, RULES_VERSION),
                what=f"read stored hash for {user_id}")
            if stored.error:
                return self._finish(UserWriteResult(
                    user_id, UserWriteResult.FAILED, result_hash=result_hash,
                    attempts=stored.attempts, error=stored.error,
                    elapsed_ms=self._ms(started)))
            if stored.value == result_hash:
                return self._finish(UserWriteResult(
                    user_id, UserWriteResult.UNCHANGED, result_hash=result_hash,
                    attempts=stored.attempts, elapsed_ms=self._ms(started)))

        tables = result.tables()
        written = 0
        pruned = 0
        attempts = 1

        # Recommendations first, then the profile tables, then the summary last.
        #
        # The summary holds `result_hash`, which is what the next run compares
        # against. Writing it last means a failure part-way leaves the stored hash
        # stale, so the next run retries the whole user rather than believing it
        # succeeded — the same reason knowledge_sync advances its manifest last.
        order = ["user_recommendations", *SINGLE_ROW_TABLES]
        order.remove("user_activity_summary")
        order.append("user_activity_summary")

        for table in order:
            rows = tables.get(table) or []
            rows = rows if isinstance(rows, list) else [rows]

            if rows:
                step = self._attempt(
                    lambda t=table, r=rows: self.target.upsert(t, r, CONFLICT_KEYS[t]),
                    what=f"upsert {table} for {user_id}")
                attempts = max(attempts, step.attempts)
                if step.error:
                    return self._finish(UserWriteResult(
                        user_id, UserWriteResult.FAILED, result_hash=result_hash,
                        rows_written=written, rows_pruned=pruned, attempts=attempts,
                        error=step.error, elapsed_ms=self._ms(started)))
                written += step.value or 0

            # Prune runs even when `rows` is empty, and that is the whole point.
            #
            # A user whose skills stop resolving — a district correction, a
            # crosswalk change — legitimately drops to zero recommendations. An
            # earlier version of this loop skipped a table with no rows, so those
            # users kept every stale recommendation forever while the writer
            # reported success. Zero is a result, not an absence of one.
            if table == "user_recommendations":
                keep = [r["item_id"] for r in rows]
                step = self._attempt(
                    lambda k=keep: self.target.prune_recommendations(
                        user_id, RULES_VERSION, k),
                    what=f"prune recommendations for {user_id}")
                attempts = max(attempts, step.attempts)
                if step.error:
                    return self._finish(UserWriteResult(
                        user_id, UserWriteResult.FAILED, result_hash=result_hash,
                        rows_written=written, attempts=attempts, error=step.error,
                        elapsed_ms=self._ms(started)))
                pruned += step.value or 0

        return self._finish(UserWriteResult(
            user_id, UserWriteResult.WRITTEN, result_hash=result_hash,
            rows_written=written, rows_pruned=pruned, attempts=attempts,
            elapsed_ms=self._ms(started)))

    # ── many users ──────────────────────────────────────────────────────────
    def write_many(self, contexts, *, stop_after_failures=None):
        """
        Write for many users. One user's failure does not stop the rest.

        `stop_after_failures` aborts the run once that many users have failed —
        for a scheduled job, a systemic fault (credentials rotated, schema
        dropped) should stop early rather than fail ten thousand times and fill
        the log.
        """
        results = []
        failures = 0
        for context in contexts:
            res = self.write_user(context)
            results.append(res)
            if res.outcome == UserWriteResult.FAILED:
                failures += 1
                if stop_after_failures and failures >= stop_after_failures:
                    break
        return WriteRun(results, stopped_early=bool(
            stop_after_failures and failures >= stop_after_failures))

    # ── retry ───────────────────────────────────────────────────────────────
    class _Step:
        __slots__ = ("value", "error", "attempts")

        def __init__(self, value=None, error=None, attempts=1):
            self.value = value
            self.error = error
            self.attempts = attempts

    def _attempt(self, fn, *, what):
        """
        Run `fn`, retrying transient failures with backoff.

        Three attempts total. A Supabase write either succeeds, hits a blip that
        clears in a second, or is wrong in a way more attempts cannot fix — and a
        long retry ladder on a per-user loop turns one bad credential into an hour
        of waiting.
        """
        last = None
        for attempt in range(1, len(RETRY_DELAYS) + 2):
            try:
                return self._Step(value=fn(), attempts=attempt)
            except Exception as exc:            # noqa: BLE001 — adapters raise anything
                last = f"{what}: {type(exc).__name__}: {exc}"
                if attempt <= len(RETRY_DELAYS):
                    self._sleep(RETRY_DELAYS[attempt - 1])
        return self._Step(error=last, attempts=len(RETRY_DELAYS) + 1)

    # ── logging ─────────────────────────────────────────────────────────────
    def _finish(self, result):
        if self.log_path:
            record = {
                "at": datetime.now(timezone.utc).isoformat(),
                "engine_version": __version__,
                "rules_version": RULES_VERSION,
                "target": type(self.target).__name__,
                **result.as_dict(),
            }
            try:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, sort_keys=True) + "\n")
            except OSError:
                # A log that cannot be written must not fail a write that
                # succeeded. The outcome is still returned to the caller.
                pass
        return result

    @staticmethod
    def _ms(started):
        return int((time.perf_counter() - started) * 1000)


class WriteRun:
    """Aggregate of one `write_many`. What a scheduled job reports."""

    def __init__(self, results, *, stopped_early=False):
        self.results = list(results)
        self.stopped_early = stopped_early

    def _count(self, outcome):
        return sum(1 for r in self.results if r.outcome == outcome)

    @property
    def written(self):
        return self._count(UserWriteResult.WRITTEN)

    @property
    def unchanged(self):
        return self._count(UserWriteResult.UNCHANGED)

    @property
    def failed(self):
        return self._count(UserWriteResult.FAILED)

    @property
    def rows_written(self):
        return sum(r.rows_written for r in self.results)

    @property
    def rows_pruned(self):
        return sum(r.rows_pruned for r in self.results)

    @property
    def ok(self):
        return self.failed == 0 and not self.stopped_early

    def as_dict(self):
        return {
            "users": len(self.results), "written": self.written,
            "unchanged": self.unchanged, "failed": self.failed,
            "rows_written": self.rows_written, "rows_pruned": self.rows_pruned,
            "stopped_early": self.stopped_early, "ok": self.ok,
            "failures": [r.as_dict() for r in self.results
                         if r.outcome == UserWriteResult.FAILED],
        }

    def summary(self):
        parts = [
            f"{len(self.results)} user(s)",
            f"{self.written} written",
            f"{self.unchanged} unchanged",
            f"{self.failed} failed",
            f"{self.rows_written} row(s) upserted",
        ]
        if self.rows_pruned:
            parts.append(f"{self.rows_pruned} stale row(s) pruned")
        if self.stopped_early:
            parts.append("STOPPED EARLY")
        return " · ".join(parts)


def make_target(kind, **kwargs):
    """`"memory"` or `"supabase"`. Memory is the default everywhere."""
    if kind in (None, "memory"):
        return InMemoryTarget(**kwargs)
    if kind == "supabase":
        return SupabaseTarget(**kwargs)
    raise WriterError(f"unknown target {kind!r}: use 'memory' or 'supabase'")
