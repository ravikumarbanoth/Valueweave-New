# Operations Guide — Knowledge Sync

For whoever is on the other end of a failed sync at an inconvenient hour.

---

## 0. Read this first

**Nothing here has ever run against a real Supabase.** No credentials exist in the
environment this was built in. Every code path is exercised against
`InMemoryTarget` — faithfully, including the failure paths — but an in-memory dict
is not Postgres.

Treat the first production run as a rehearsal with a real audience: §2 walks it
through one table at a time, and the whole thing is reversible.

---

## 1. Prerequisites

| | |
|---|---|
| Python | 3.11+, standard library only for everything except a live sync |
| `supabase` package | Only for `--target supabase`. Imported lazily; the tests never need it. |
| `SUPABASE_URL` | The project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | **Service role.** Bypasses RLS. |

### The key

The service role key bypasses RLS entirely. It is the only credential in the
platform that can write to the `knowledge` schema, and the only reason it exists.

- CI secret or server-side environment variable **only**
- Never in a `NEXT_PUBLIC_*` variable, a client component, or a committed file
- Never in a local shell history: use a `.env` the shell sources, and gitignore it

If it leaks, rotate it in Supabase. Nothing else in the platform holds it, so
rotation breaks nothing but the sync.

---

## 2. First run

Do it in this order. Each step is verifiable and reversible.

```bash
# 1 — plan. No credentials. Expect 1,812 rows, 0 errors, 4 governed warnings.
python3 -m knowledge_sync plan

# 2 — confirm the DDL matches the specs
python3 knowledge_sync/generate_migration.py --check

# 3 — apply the schema
psql "$DATABASE_URL" -f knowledge_sync/migrations/001_knowledge_schema.sql
psql "$DATABASE_URL" -c "\dt knowledge.*"        # expect 9 tables

# 4 — sync ONE small table first
python3 -m knowledge_sync sync --table kg_schemes --target supabase
psql "$DATABASE_URL" -c "select count(*) from knowledge.kg_schemes;"   # 40

# 5 — spot-check a row, including provenance
psql "$DATABASE_URL" -c \
  "select scheme_id, scheme_name, confidence_score, verification_status,
          sync_source_package, sync_pending_fields
     from knowledge.kg_schemes limit 3;"

# 6 — if that looks right, the rest
python3 -m knowledge_sync sync --target supabase

# 7 — prove idempotency: this must report 0 inserted, 0 updated
python3 -m knowledge_sync sync --target supabase
```

Step 7 is the one that matters. If the second run reports updates, something is
round-tripping differently through Postgres than through the hash, and that needs
understanding before the sync goes on a schedule.

### Expected first-run figures

| Table | Rows |
|---|---:|
| `kg_relationships` | 865 |
| `kg_entities` | 647 |
| `kg_businesses` | 85 |
| `kg_districts` | 61 |
| `kg_skills` | 45 |
| `kg_agriculture` | 45 |
| `kg_schemes` | 40 |
| `kg_industries` | 24 |
| **Total** | **1,812** |

---

## 3. Routine operation

```bash
python3 -m knowledge_sync status              # manifest, tables, last run
python3 -m knowledge_sync plan                # what would change
python3 -m knowledge_sync sync                # apply
python3 -m knowledge_sync history --limit 10  # recent runs
python3 -m knowledge_sync snapshots           # rollback points
```

**Steady state is `plan` reporting all-skip.** Anything else means a package
changed, and the change should be traceable to a commit.

---

## 4. The manifest

`knowledge_sync/state/manifest.json` — `{table: {row_key: content_hash}}` from the
last successful sync.

**It is deliberately not committed.** A manifest in the repository would describe
whichever machine last ran a sync, and a second environment would plan against a
baseline that was never true for it. It belongs to a deployment.

| Situation | Effect | Action |
|---|---|---|
| Missing | Next run is a full insert | None. Upserts are idempotent. |
| Stale (target ahead) | Rows re-sent | None; harmless |
| Stale (target behind) | Rows wrongly skipped | `sync --full` |
| Corrupt JSON | Sync fails to start | Delete it; next run is a full insert |

In CI, persist it between runs (cache keyed on the branch) or accept a full sync
each time — at 1,812 rows and ~0.1 s of framework time, full is not expensive.

---

## 5. Troubleshooting

### `ABORTED: N transform error(s)`

A cell will not convert. Every bad cell is listed with its table, column, row key
and value.

```
kg_districts.population = '12,00,000' in row 'abc-123': not an integer
```

**Fix the package**, not the sync. If the column has legitimately changed type,
change the hint in `knowledge_sync/transform.py` and say why in a comment — the
existing entries for `minimum_investment` and `collection_date` are the model.

### `ABORTED: N validation error(s)`

| Check | Usual cause |
|---|---|
| `V1-SCHEMA` | A column was added or removed upstream. Update the spec. |
| `V2-KEY` | Two rows share a key. Usually a duplicated source row. |
| `V3-REQUIRED` | A required cell is empty. |
| `V4-FOREIGN_KEY` | An edge points at a missing entity. **Rebuild the graph first** — `python3 knowledge_graph/build_graph.py`. |
| `V5-CONFIDENCE` | Out of 0–100. |
| `V6-OWNERSHIP` **error** | An *undeclared* cross-package overlap. Either it is a mistake, or it needs declaring in `known_overlaps.csv` with an ADR. |
| `V7-VERIFICATION` | An unregistered `VST-*` value. |

### `WARNING V6-OWNERSHIP … governed by ADR-005`

Expected. Four of them, covering 115 entity rows. Declared in
`known_overlaps.csv`. No action.

### `cannot reach Supabase`

`SupabaseTarget` refuses to construct without both env vars — by design, so a run
fails at the start rather than halfway through. Check them, then check the project
is reachable.

### Apply failed partway

Some tables written, **manifest not advanced**. Re-run: it replays. Verify with
`plan` first if you want to see what it will do.

### The second run reports updates

The hash disagrees with what came back from Postgres. Check whether a numeric
column is round-tripping as a string, or a date as a timestamp. This is the
failure mode most likely to appear on first contact with a real database and is
the reason step 7 of §2 exists.

---

## 6. Rolling back

```bash
python3 -m knowledge_sync snapshots
python3 -m knowledge_sync rollback <run_id> --dry-run   # always first
python3 -m knowledge_sync rollback <run_id>
```

**What rollback can do:** undo inserts (soft delete), restore updated rows from
their pre-images, un-delete soft-deleted rows, and restore the previous manifest.

**What it cannot do:** restore a row someone edited by hand in the Supabase
console. That edit is in no snapshot, and the next sync would overwrite it anyway.
This is why no write policy is granted on any table — the situation should be
impossible rather than merely discouraged.

Only the most recent run should normally be rolled back. Rolling back an older run
while newer ones stand will produce a state that matches no version of Git.

### Complete reset

```sql
drop schema knowledge cascade;
```

Then re-apply the migration and `sync --full`. Safe by construction: the schema
contains nothing but the projection, and the projection is derived from Git.

---

## 7. Monitoring

Read from `knowledge_sync/state/sync_log.jsonl` (one JSON object per run) or from
`knowledge.sync_runs`.

| Watch | Alert when |
|---|---|
| `outcome` | anything other than `SUCCESS` or `DRY_RUN` |
| `rows_soft_deleted` | unexpectedly large — usually a renamed dataset, not retired facts |
| `validation_errors` | `> 0` |
| `coverage[*].complete` | `false` on any table — a page will render a gap |
| `pending_rate_pct` | rising; currently 1.26% |
| Time since last `SUCCESS` | longer than the release cadence |

`coverage` is the one that catches silent partial failure: it compares rows in the
target against rows Git produces, per table.

---

## 8. Runbooks

**A package was released.** CI runs `plan` on the PR and `sync` on merge. Manually:
`plan`, read it, `sync`.

**A scheme's benefit figure is wrong in the app.** Fix it in
`packages/Package007_Government_Schemes/datasets/government_schemes.csv`, run the
package validator, commit, merge. The sync propagates it. **Never edit the row in
Supabase** — the next sync would revert it, and the fix would be lost from Git.

**A dataset was renamed.** `plan` will show every row as a delete plus an insert,
because `sync_row_key` includes the dataset name for multi-source tables. Expected.
Apply it; the old rows soft-delete and the new ones insert.

**Rotating the service role key.** Rotate in Supabase, update the CI secret, run
`plan --target supabase` to confirm connectivity. Nothing else holds the key.

**Restoring the database from a backup.** The manifest now describes a state the
target no longer has. Run `sync --full`.

---

## 9. Quick reference

```bash
# no credentials needed
python3 -m knowledge_sync plan
python3 -m knowledge_sync status
python3 -m knowledge_sync history
python3 -m knowledge_sync snapshots
python3 knowledge_sync/generate_migration.py --check
python3 -m unittest tests.test_knowledge_sync        # 64 tests

# credentials needed
python3 -m knowledge_sync sync   --target supabase
python3 -m knowledge_sync sync   --target supabase --full
python3 -m knowledge_sync sync   --target supabase --table kg_schemes
python3 -m knowledge_sync rollback <run_id> --target supabase
```

**Companion documents:** `SYNC_ARCHITECTURE.md` (design and its reasoning),
`SUPABASE_SCHEMA.md` (tables, columns, RLS), `SYNC_WORKFLOW.md` (the four modes).
