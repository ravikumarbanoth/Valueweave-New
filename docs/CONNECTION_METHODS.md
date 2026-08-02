# Which Supabase connection string CI should use

**Answer: the Session Pooler.**

```
postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

Set that as the `DATABASE_URL` repository secret. No workflow change is needed —
the sync already reads `DATABASE_URL`, and the code now recognises all three
endpoint shapes.

---

## Why the direct connection fails

```
db.<project-ref>.supabase.co:5432  →  Network is unreachable
```

That host publishes an **AAAA record only**. Supabase moved direct connections to
IPv6-only when it stopped bundling a dedicated IPv4 address with every project;
IPv4 for the direct endpoint is now a paid add-on.

**GitHub-hosted runners have no IPv6 route.** The runner resolves the AAAA
record, tries to open the socket, and the kernel rejects it because there is no
route to an IPv6 destination.

The error is worth reading closely: *"Network is unreachable"* is a socket-layer
failure. Nothing reached Postgres, so nothing checked a password, so this is not
a credentials problem — which is exactly why the earlier run misdiagnosed it as
a missing schema. `psql` returned nothing, and an empty result was
indistinguishable from `to_regclass(...) is null`.

---

## The three methods compared

| | **Direct** | **Session pooler** | **Transaction pooler** |
|---|---|---|---|
| Host | `db.<ref>.supabase.co` | `aws-0-<region>.pooler.supabase.com` | `aws-0-<region>.pooler.supabase.com` |
| Port | 5432 | **5432** | 6543 |
| Username | `postgres` | `postgres.<ref>` | `postgres.<ref>` |
| IP family | **IPv6 only** (IPv4 = paid add-on) | IPv4 | IPv4 |
| Reachable from GitHub Actions | ❌ **no** | ✅ yes | ✅ yes |
| Connection lifetime | whole session | whole session | returned to the pool per transaction |
| Prepared statements | yes | yes | **no** |
| `SET`, `LISTEN`, advisory locks, temp tables | yes | yes | no |
| Intended for | long-lived servers | long-lived clients needing IPv4 | serverless, many short connections |

### Why session and not transaction

Both are IPv4 and both would connect. Session mode is the right one here, and
the reason is specific rather than aesthetic.

`knowledge_sync/adapters.py` upserts through `psycopg`'s `executemany()`.
psycopg 3 defaults to `prepare_threshold=5`, so it promotes a repeated statement
to a **server-side prepared statement**. Measured against PostgreSQL 16:

```
default (prepare_threshold=5)    prepared=1  rows_written=40
prepare_threshold=None           prepared=0  rows_written=40
```

In transaction mode the connection goes back to the pool after each transaction,
so the backend holding `_pg3_0` is not the one that runs the next statement, and
the sync fails with `prepared statement "_pg3_0" does not exist`. Session mode
keeps one backend for the whole connection, so preparing is both correct and
faster.

The workload also suits session mode on its own terms: one connection, opened
once, ~1,812 upserts, closed. Transaction pooling exists to multiplex many
short-lived clients — the opposite shape.

### Transaction pooler works too, automatically

If you set the 6543 string anyway, `PostgresTarget.connection_mode()` detects the
port and connects with `prepare_threshold=None`. That costs nothing measurable
at this volume. You will see it in the log:

```
[target] PostgresTarget -> postgresql://aws-0-….pooler.supabase.com:6543/postgres
         schema=knowledge mode=transaction-pooler prepared-statements=off
```

---

## If you want to keep the direct connection

It needs an **IPv4 address for the project** — the paid add-on under
Project Settings → Add-ons. That is the only infrastructure change that makes
`db.<ref>.supabase.co` reachable from a GitHub-hosted runner.

Two alternatives, for completeness, both worse here:

* **A self-hosted runner on an IPv6-capable network.** Solves it, and adds a
  machine to maintain for one nightly job.
* **An IPv6-to-IPv4 proxy in front of the database.** More moving parts than the
  pooler Supabase already runs for you.

The pooler is free, already provisioned, and needs one secret changed. There is
no good reason to pay for or build the alternatives.

---

## What the log will tell you

The transport banner prints before anything connects:

```
==> Transport
    target:   postgres
    database: postgresql://postgres.****:****@aws-0-ap-south-1.pooler.supabase.com:5432/postgres
```

and the adapter states the mode it detected:

```
[target] PostgresTarget -> postgresql://aws-0-ap-south-1.pooler.supabase.com:5432/postgres
         schema=knowledge mode=session-pooler [Exposed schemas does not apply]
```

If `mode=direct` appears in a CI run, the connection is about to fail and the
log now says why.

---

## Unrelated, and still true

The **Exposed schemas** setting governs PostgREST — the browser's path to the
data. It has no bearing on any of the above: none of these three methods goes
through PostgREST. Both settings are needed, for different readers:

* `DATABASE_URL` via the session pooler → CI can **write** the projection.
* `knowledge` in Exposed schemas → the website can **read** it.
