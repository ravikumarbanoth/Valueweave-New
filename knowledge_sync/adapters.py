#!/usr/bin/env python3
"""
Target adapters — where synced rows actually go.

Two implementations behind one interface:

  InMemoryTarget   the fixture. Holds rows in a dict, records every call.
                   Every test in tests/test_knowledge_sync.py runs against it,
                   which is why the suite needs no Supabase credentials.

  SupabaseTarget   the real one. Uses the service role key and writes only to the
                   `knowledge` schema.

WHY AN ADAPTER AT ALL
---------------------
Not for hypothetical future backends — for testability. A sync framework whose
tests need a live database is a framework whose tests do not run in CI, and one
whose failure modes are only discovered in production. The interface is four
methods because that is all a one-way projection needs; there is no query
builder, no ORM, and no read path beyond what rollback requires.

THE SAFETY RULE, ENFORCED IN CODE
---------------------------------
`_assert_target()` rejects any table not declared in config.TABLE_SPECS and any
schema other than `knowledge`. The brief lists nine application tables that must
never be touched; rather than encoding that denylist — which would silently allow
a tenth — this is an allowlist of the eight tables the framework owns. A typo
raises instead of writing somewhere it shouldn't.
"""

import os
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timezone

from knowledge_sync.config import BY_NAME, TARGET_SCHEMA


class TargetError(RuntimeError):
    pass


class Target(ABC):
    """The four operations a one-way projection needs."""

    schema = TARGET_SCHEMA

    def _assert_target(self, table):
        """Allowlist, not denylist. A table this framework does not own is refused."""
        if table not in BY_NAME:
            raise TargetError(
                f"refusing to write to {table!r}: not one of the {len(BY_NAME)} tables "
                f"this framework owns ({', '.join(sorted(BY_NAME))}). User and "
                f"application tables are unreachable from here by construction.")

    @abstractmethod
    def upsert(self, table, rows): ...

    @abstractmethod
    def soft_delete(self, table, row_keys, at): ...

    @abstractmethod
    def fetch_keys(self, table): ...

    @abstractmethod
    def count(self, table): ...

    def restore(self, table, row_keys):
        """Undo a soft delete. Used only by rollback."""
        raise NotImplementedError


class InMemoryTarget(Target):
    """Fixture target. Faithful enough to test every code path, and inspectable."""

    def __init__(self, seed=None, fail_on=None):
        self.rows = defaultdict(dict)          # table -> {row_key: row}
        self.calls = []                        # every operation, in order
        #: (table, operation) that should raise — for testing abort/rollback paths.
        self.fail_on = fail_on or set()
        for table, rows in (seed or {}).items():
            for r in rows:
                self.rows[table][r["sync_row_key"]] = dict(r)

    def _maybe_fail(self, table, op):
        if (table, op) in self.fail_on:
            raise TargetError(f"injected failure: {op} on {table}")

    def upsert(self, table, rows):
        self._assert_target(table)
        self._maybe_fail(table, "upsert")
        self.calls.append(("upsert", table, len(rows)))
        for r in rows:
            self.rows[table][r["sync_row_key"]] = dict(r)
        return len(rows)

    def soft_delete(self, table, row_keys, at):
        self._assert_target(table)
        self._maybe_fail(table, "soft_delete")
        self.calls.append(("soft_delete", table, len(row_keys)))
        n = 0
        for key in row_keys:
            row = self.rows[table].get(key)
            if row is not None and row.get("sync_deleted_at") is None:
                row["sync_deleted_at"] = at
                n += 1
        return n

    def restore(self, table, row_keys):
        self._assert_target(table)
        self.calls.append(("restore", table, len(row_keys)))
        n = 0
        for key in row_keys:
            row = self.rows[table].get(key)
            if row is not None and row.get("sync_deleted_at") is not None:
                row["sync_deleted_at"] = None
                n += 1
        return n

    def fetch_keys(self, table):
        self._assert_target(table)
        return {k: v.get("sync_content_hash") for k, v in self.rows[table].items()
                if v.get("sync_deleted_at") is None}

    def count(self, table, include_deleted=False):
        self._assert_target(table)
        rows = self.rows[table].values()
        if include_deleted:
            return len(rows)
        return sum(1 for r in rows if r.get("sync_deleted_at") is None)


class SupabaseTarget(Target):
    """
    The real target. Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.

    The service role bypasses RLS, which is why this class is the only thing in
    the platform that holds that key, why it lives server-side and in CI only, and
    why `_assert_target` is checked before every write.

    The client is imported lazily so that the entire framework — including the
    full test suite — imports and runs with no `supabase` package installed.
    """

    def __init__(self, url=None, service_role_key=None, client=None):
        self.url = url or os.environ.get("SUPABASE_URL")
        self.key = service_role_key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self._client = client
        if client is None and not (self.url and self.key):
            raise TargetError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required. "
                "For a dry run or a test, use InMemoryTarget instead — no "
                "credentials are needed for either.")

    @property
    def client(self):
        if self._client is None:
            try:
                from supabase import create_client       # noqa: PLC0415
            except ImportError as exc:                   # pragma: no cover
                raise TargetError(
                    "the `supabase` package is not installed. It is an optional "
                    "dependency: everything except a live sync works without it."
                ) from exc
            self._client = create_client(self.url, self.key)
        return self._client

    def _table(self, table):
        self._assert_target(table)
        return self.client.schema(self.schema).table(table)

    def upsert(self, table, rows):
        if not rows:
            return 0
        self._table(table).upsert(rows, on_conflict="sync_row_key").execute()
        return len(rows)

    def soft_delete(self, table, row_keys, at):
        if not row_keys:
            return 0
        (self._table(table)
            .update({"sync_deleted_at": at})
            .in_("sync_row_key", list(row_keys))
            .execute())
        return len(row_keys)

    def restore(self, table, row_keys):
        if not row_keys:
            return 0
        (self._table(table)
            .update({"sync_deleted_at": None})
            .in_("sync_row_key", list(row_keys))
            .execute())
        return len(row_keys)

    def fetch_keys(self, table):
        resp = (self._table(table)
                .select("sync_row_key,sync_content_hash")
                .is_("sync_deleted_at", "null")
                .execute())
        return {r["sync_row_key"]: r["sync_content_hash"] for r in (resp.data or [])}

    def count(self, table, include_deleted=False):
        q = self._table(table).select("sync_row_key", count="exact")
        if not include_deleted:
            q = q.is_("sync_deleted_at", "null")
        return q.execute().count or 0


def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
