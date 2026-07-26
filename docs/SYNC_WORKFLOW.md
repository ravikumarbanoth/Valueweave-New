# Sync Workflow — ValueWeave Platform v3.0

The four modes, what each does, and when to reach for it.

```bash
python3 -m knowledge_sync plan                    # dry run — writes nothing
python3 -m knowledge_sync sync                    # incremental
python3 -m knowledge_sync sync --full             # rebuild
python3 -m knowledge_sync rollback <run_id>       # undo
```

---

## 1. The modes

| Mode | Writes | Credentials | Use when |
|---|---|---|---|
| **Dry run** | nothing | none | Always, before anything else |
| **Incremental** | changed rows only | Supabase | The default; every package release |
| **Full** | every row | Supabase | First load, or recovery from drift |
| **Rollback** | reverses one run | Supabase | Something went wrong |

### Dry run

```bash
python3 -m knowledge_sync plan
python3 -m knowledge_sync plan --table kg_schemes --json
```

Runs extract → transform → validate → detect, writes a snapshot of the plan, and
stops. Needs no credentials, so it works on a laptop and in CI on every pull
request that touches `packages/`.

A dry run that reports validation errors is the framework doing its job. Fix the
package, not the sync.

### Incremental

```bash
python3 -m knowledge_sync sync --target supabase
```

Compares content hashes against the manifest and applies only the difference.
Rows whose hash is unchanged are skipped entirely — measured on the real
repository, a second consecutive run reports **0 inserted, 0 updated, 1,812
skipped**.

That idempotency is what makes a scheduled sync safe: running it twice is
indistinguishable from running it once.

### Full

```bash
python3 -m knowledge_sync sync --full --target supabase
```

Ignores the manifest and treats every row as new. Two legitimate uses: the first
load into an empty schema, and recovery when the manifest and the target have
diverged — after a restore, or after someone edited rows by hand.

Not a substitute for incremental. It rewrites 1,812 rows to change three.

### Rollback

```bash
python3 -m knowledge_sync rollback 20260726T084404Z-e784ac --dry-run
python3 -m knowledge_sync rollback 20260726T084404Z-e784ac
```

Reverses exactly one run using its snapshot:

| The run did | Rollback does |
|---|---|
| inserted a row | soft-deletes it |
| updated a row | restores the pre-image |
| soft-deleted a row | un-deletes it |

It also restores the previous manifest, so the next sync replays the run rather
than believing it succeeded.

**Rolling back an insert soft-deletes rather than removes.** The row existed for
some period and something may have referenced it; soft delete makes the rollback
itself reversible.

---

## 2. What a run does, step by step

```
extract        1,812 rows from 12 CSVs across 8 tables
   ↓           only declared columns survive
transform      strings → typed values; 2 sentinels → NULL; content hash
   ↓           ABORT on a malformed number or date
validate       7 checks, across ALL tables at once
   ↓           ABORT on any error — nothing has been written yet
detect         compare hashes to the manifest → INSERT/UPDATE/DELETE/SKIP
   ↓
snapshot       write the plan + pre-images to state/snapshots/<run_id>.json
   ↓
apply          upsert changed rows; soft-delete vanished ones
   ↓           ABORT leaves the manifest un-advanced → the run replays
manifest       written LAST
```

Two abort points precede any write. That is deliberate: **a partially synced
projection is worse than a stale one.** Stale is merely old; partial is silently
inconsistent, and only one of those is visible to a consumer.

---

## 3. Reading the output

```
[detect changes]
  kg_agriculture       insert=45  update=0  delete=0  skip=0
  kg_businesses        insert=85  update=0  delete=0  skip=0
  ...
  1812 inserted, 0 updated, 0 soft-deleted, 0 unchanged  ·  0.086s
```

| Signal | Means |
|---|---|
| `insert` on an established table | New package rows — expected after a release |
| `update` | A row's content changed |
| `delete` | Git no longer produces a row that was synced before |
| `skip` high, others zero | Nothing changed. The normal steady state. |
| `WARNING V6-OWNERSHIP` | A declared, governed overlap. 4 of these are expected. |
| `ERROR` anything | The run stopped. Nothing was written. |

**A large unexpected `delete` count is the one to stop on.** It usually means a
dataset was renamed or a key column changed, not that facts were retired. Run
`plan` and read the list before applying.

---

## 4. When to run it

| Trigger | Mode |
|---|---|
| PR touching `packages/**` or `knowledge_graph/**` | `plan` — fail the PR on validation errors |
| Merge to `main` touching those paths | `sync` |
| First deploy of a new environment | apply the migration, then `sync --full` |
| Nightly | `plan`; alert if it reports changes, since that means a sync was missed |
| After a database restore | `sync --full` |

The trigger is a **commit**, not a timer. Package data changes when someone
releases a package, so that is when the projection should move.

---

## 5. CI

```yaml
# .github/workflows/knowledge-sync.yml  (illustrative — not committed)
on:
  pull_request:
    paths: ['packages/**', 'knowledge_graph/**', 'knowledge_sync/**']
  push:
    branches: [main]
    paths: ['packages/**', 'knowledge_graph/**']

jobs:
  plan:
    steps:
      - run: python3 -m knowledge_sync plan            # no credentials
      - run: python3 knowledge_sync/generate_migration.py --check
      - run: python3 -m unittest tests.test_knowledge_sync

  sync:
    if: github.ref == 'refs/heads/main'
    needs: plan
    steps:
      - run: python3 -m knowledge_sync sync --target supabase
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
```

The plan job needs no secrets, so it can run on pull requests from forks. Only the
sync job holds the service role key, and only on `main`.

---

## 6. Failure modes

| Failure | Behaviour | Recovery |
|---|---|---|
| Malformed number or date | Abort before writing; every bad cell listed | Fix the package |
| Validation error | Abort before writing; findings listed | Fix the package, or the spec if the schema legitimately changed |
| Apply fails mid-run | Some tables written, **manifest not advanced** | Re-run. It replays. |
| Credentials missing | `SupabaseTarget` refuses to construct | Set the env vars |
| Wrong data synced | Target holds it | `rollback <run_id>` |
| Manifest lost | Next run plans a full insert | Correct. Upserts are idempotent. |
| Manifest stale vs target | Rows skipped that should sync | `sync --full` |
| Someone hand-edited a row | Next sync overwrites it | Expected. No write policy exists, so this should be impossible. |

The recurring shape: **the framework prefers to stop than to write something it is
unsure about.** A stale projection is visible and recoverable. A wrong one is
neither.

---

## 7. Adding a ninth table

1. Add a `TableSpec` to `knowledge_sync/config.py`
2. `python3 knowledge_sync/generate_migration.py`
3. `python3 -m knowledge_sync plan`
4. Apply the regenerated migration
5. `python3 -m knowledge_sync sync --table <new_table>`

No module hard-codes a table name, so steps 1 and 2 are the whole code change.
`test_all_eight_tables_the_brief_names_are_present` will need updating — which is
the point: adding a table should be a visible decision.

---

## 8. What the framework will not do

- **Write to a user table.** `_assert_target` is an allowlist of the eight tables
  it owns. A test asserts every table the brief protects is refused.
- **Hard-delete.** No sync path removes a row.
- **Write back to Git.** One direction only.
- **Resolve a conflict.** There is no conflict to resolve: Git wins by
  construction.
- **Advance the manifest after a failed apply.** Tested.
