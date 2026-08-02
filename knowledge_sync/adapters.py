#!/usr/bin/env python3
"""
Target adapters — where synced rows actually go.

Three implementations behind one interface:

  InMemoryTarget   the fixture. Holds rows in a dict, records every call.
                   Every test in tests/test_knowledge_sync.py runs against it,
                   which is why the suite needs no Supabase credentials.

  SupabaseTarget   over PostgREST, with the service role key.

  PostgresTarget   over the PostgreSQL wire protocol, with DATABASE_URL.

WHY THERE ARE TWO REAL ONES
---------------------------
They differ in one way that turned out to matter: SupabaseTarget speaks to
PostgREST, and PostgREST will not serve a schema that is not listed in its
`db-schemas` allowlist — the Dashboard's "Exposed schemas" setting. It validates
that before it authenticates anything, so an unlisted schema returns PGRST106 to
every caller, including one holding the service role key. There is no key, grant
or policy that routes around a server configuration.

That is correct for the browser. It is a strange gate for an import: the sync is
an operator process running in CI with the database's own credentials, and it was
being blocked by a setting that exists to control what the public API exposes. A
deployment that has created every table, index, policy and grant would still
import nothing until somebody ticked a checkbox.

PostgresTarget writes over the Postgres protocol instead, using DATABASE_URL —
already a required secret, and until now used only for a psql table check. It is
not affected by Exposed schemas at all.

Exposing the schemas is still necessary for the frontend, which reads through
PostgREST with the anon key. It is no longer necessary in order to populate the
tables, and those two things should not have been coupled.

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

    def describe(self):
        """One line naming this target and its destination, safe to log.

        Asked for after the default transport changed: a shell variable says
        which target was *intended*, and only the constructed object can say
        which one is actually about to write. Implementations must never include
        a credential — see the masking in each.
        """
        return f"{type(self).__name__} (no destination)"


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

    def describe(self):
        return "InMemoryTarget -> in-process dict (nothing is persisted)"

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

    def describe(self):
        host = (self.url or "").split("//", 1)[-1].split("/", 1)[0] or "(unset)"
        return (f"SupabaseTarget -> PostgREST at {_mask_host(host)} "
                f"schema={self.schema} "
                f"[subject to API > Exposed schemas]")

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


class PostgresTarget(Target):
    """
    The other real target. Writes over the PostgreSQL wire protocol.

    Same interface, same allowlist, same soft-delete semantics as SupabaseTarget
    — the only difference is the transport, and therefore what can block it. See
    the module docstring for why that difference matters.

    `psycopg` is imported lazily, inside `conn`, for the same reason the Supabase
    SDK is: the test suite and every dry run must work without it installed.

    Autocommit, deliberately. It matches SupabaseTarget statement-for-statement,
    so a partial failure leaves the same state either way and the engine's
    manifest-written-last design replays it identically. Wrapping the whole sync
    in one transaction would be a different — arguably better — contract, but it
    would be a different contract, and this class exists to be a drop-in.
    """

    #: Supavisor's transaction-mode port. Supabase publishes the transaction
    #: pooler on 6543 and the session pooler on 5432, both on *.pooler.supabase.com.
    TRANSACTION_POOLER_PORT = 6543

    def __init__(self, dsn=None, connection=None):
        self.dsn = dsn or os.environ.get("DATABASE_URL")
        self._conn = connection
        if connection is None and not self.dsn:
            raise TargetError(
                "DATABASE_URL is required for --target postgres. For a dry run "
                "or a test, use InMemoryTarget instead — no credentials needed.")

    def _endpoint(self):
        """(host, port, dbname) from the DSN, or ('(unparseable)', None, ...).

        Never raises: it is used by describe(), which has to work on a DSN too
        broken to connect with — that is exactly when someone needs to read it.
        """
        from urllib.parse import urlsplit, parse_qs                # noqa: PLC0415
        try:
            u = urlsplit(self.dsn or "")
            host = u.hostname or parse_qs(u.query).get("host", [""])[0] \
                or "(local socket)"
            try:
                port = u.port
            except ValueError:
                port = None
            return host, port, (u.path or "").lstrip("/") or "(default)"
        except Exception:                                          # noqa: BLE001
            return "(unparseable)", None, "(unknown)"

    def connection_mode(self):
        """Which Supabase connection method this DSN points at.

        It decides one thing that matters: whether server-side prepared
        statements are safe. Measured, not assumed — psycopg3 defaults to
        prepare_threshold=5 and does create a named prepared statement for the
        upsert this class issues (verified against PostgreSQL 16).

        Under Supavisor TRANSACTION mode the connection returns to the pool
        after every transaction, so the backend holding `_pg3_0` is not the one
        that runs the next statement, and the sync dies on
        `prepared statement "_pg3_0" does not exist`. Session mode and a direct
        connection both keep one backend for the whole session, where preparing
        is correct and faster.
        """
        host, port, _ = self._endpoint()
        if port == self.TRANSACTION_POOLER_PORT:
            return "transaction-pooler"
        if "pooler.supabase.com" in host:
            return "session-pooler"
        if host.startswith("db.") and host.endswith(".supabase.co"):
            return "direct"
        return "other"

    def describe(self):
        """Host, port, database and connection mode. Never the password.

        Parsed rather than split on punctuation, because a Postgres password may
        legally contain '@' and ':' and a naive split puts part of it in the log.

        The mode is here because it is the difference between a run that works
        and one that cannot reach the host at all — a direct connection resolves
        to IPv6 only, and GitHub's hosted runners have no IPv6 route.
        """
        host, port, db = self._endpoint()
        mode = self.connection_mode()
        prep = " prepared-statements=off" if mode == "transaction-pooler" else ""
        port_s = f":{port}" if port else ""
        return (f"PostgresTarget -> postgresql://{host}{port_s}/{db} "
                f"schema={self.schema} mode={mode}{prep} "
                f"[Exposed schemas does not apply]")

    @staticmethod
    def _psycopg():
        """The one place the driver is imported, so the message is the same
        wherever it is missing. Importing `psycopg.sql` directly inside each
        method bypassed this and leaked a raw ModuleNotFoundError."""
        try:
            import psycopg                                 # noqa: PLC0415
            from psycopg import sql                        # noqa: PLC0415
            from psycopg.types.json import Jsonb           # noqa: PLC0415
        except ImportError as exc:                         # pragma: no cover
            raise TargetError(
                "the `psycopg` package is not installed. It is an optional "
                "dependency: everything except a live sync works without it. "
                "Install with: pip install -r requirements-sync.txt") from exc
        return psycopg, sql, Jsonb

    @property
    def conn(self):
        if self._conn is None:
            psycopg, _, _ = self._psycopg()
            kwargs = {"autocommit": True}
            if self.connection_mode() == "transaction-pooler":
                # Not an optimisation toggle — a correctness requirement. See
                # connection_mode(). Costs nothing at this volume: 1,812 rows
                # apply in well under a second either way.
                kwargs["prepare_threshold"] = None
            self._conn = psycopg.connect(self.dsn, **kwargs)
        return self._conn

    def _qualified(self, table):
        # Allowlist BEFORE the driver import, so a forbidden table is refused
        # even where psycopg is not installed — and so the refusal never depends
        # on a dependency being present.
        self._assert_target(table)
        _, sql, _ = self._psycopg()
        return sql.Identifier(self.schema, table)

    @classmethod
    def _adapt(cls, value):
        """Only one conversion is needed, and it is measured rather than guessed.

        Across all 1,812 rows the engine produces, the value types are str, int,
        float, None and dict — and dict occurs in exactly one column,
        `sync_pending_fields`, which is jsonb. psycopg adapts the first four
        natively; a bare dict it would reject.
        """
        if isinstance(value, dict):
            _, _, Jsonb = cls._psycopg()
            return Jsonb(value)
        return value

    def upsert(self, table, rows):
        self._assert_target(table)          # before the early return, and before psycopg
        if not rows:
            return 0
        _, sql, _ = self._psycopg()
        ident = self._qualified(table)

        # Grouped by column set. Every table the engine writes has exactly one
        # (verified across all eight), so this is normally a single group — but
        # a heterogeneous batch would otherwise produce a statement whose
        # placeholders did not match its rows.
        groups = {}
        for row in rows:
            groups.setdefault(tuple(row.keys()), []).append(row)

        written = 0
        with self.conn.cursor() as cur:
            for cols, batch in groups.items():
                updatable = [c for c in cols if c != "sync_row_key"]
                stmt = sql.SQL(
                    "insert into {tbl} ({cols}) values ({vals}) "
                    "on conflict (sync_row_key) do update set {sets}"
                ).format(
                    tbl=ident,
                    cols=sql.SQL(", ").join(map(sql.Identifier, cols)),
                    vals=sql.SQL(", ").join(sql.Placeholder() * len(cols)),
                    sets=sql.SQL(", ").join(
                        sql.SQL("{c} = excluded.{c}").format(c=sql.Identifier(c))
                        for c in updatable),
                )
                cur.executemany(
                    stmt, [[self._adapt(r[c]) for c in cols] for r in batch])
                written += len(batch)
        return written

    def soft_delete(self, table, row_keys, at):
        return self._set_deleted_at(table, row_keys, at)

    def restore(self, table, row_keys):
        return self._set_deleted_at(table, row_keys, None)

    def _set_deleted_at(self, table, row_keys, at):
        self._assert_target(table)
        if not row_keys:
            return 0
        _, sql, _ = self._psycopg()
        keys = list(row_keys)
        with self.conn.cursor() as cur:
            cur.execute(
                sql.SQL("update {tbl} set sync_deleted_at = %s "
                        "where sync_row_key = any(%s)").format(
                            tbl=self._qualified(table)),
                (at, keys))
        return len(keys)

    def fetch_keys(self, table):
        _, sql, _ = self._psycopg()
        with self.conn.cursor() as cur:
            cur.execute(
                sql.SQL("select sync_row_key, sync_content_hash from {tbl} "
                        "where sync_deleted_at is null").format(
                            tbl=self._qualified(table)))
            return dict(cur.fetchall())

    def count(self, table, include_deleted=False):
        _, sql, _ = self._psycopg()
        clause = sql.SQL("") if include_deleted else sql.SQL(
            " where sync_deleted_at is null")
        with self.conn.cursor() as cur:
            cur.execute(sql.SQL("select count(*) from {tbl}").format(
                tbl=self._qualified(table)) + clause)
            return cur.fetchone()[0]

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None


def _mask_host(host):
    """Hide the project ref in a Supabase hostname, keep the shape."""
    parts = host.split(".")
    if len(parts) > 2:
        parts[0] = "****"
    return ".".join(parts)


def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
