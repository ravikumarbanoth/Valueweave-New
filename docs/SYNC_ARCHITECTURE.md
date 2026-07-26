# Sync Architecture — ValueWeave Platform v3.0, Step 1

**`knowledge_sync/` — the permanent synchronisation layer between the Git knowledge
repository and the Supabase application database.**

```
packages/ + knowledge_graph/          ← single source of truth
            │
            │  extract → transform → validate → detect → snapshot → apply
            ▼
Supabase schema `knowledge`           ← read-optimised cache, disposable
            │
            ▼
Next.js frontend (unchanged)
```

One direction. Never the other. Git wins every disagreement.

---

## 1. What this is, and what it is not

It is not an importer. An importer runs once and is deleted. This runs on every
package release, forever, and therefore has to answer questions an importer never
faces: what changed since last time, what happens when a row disappears, what
happens when the run fails halfway, and how do we undo it.

Seven modules, one per question:

| Module | File | Answers |
|---|---|---|
| Change detection | `changes.py` | What is new, changed, gone, or identical? |
| Validation | `validation.py` | Is it safe to write? |
| Transformation | `transform.py` | What does this CSV string mean in Postgres? |
| Synchronisation | `engine.py` | Apply it — or abort cleanly. |
| Logging | `logs.py` | What happened, and when? |
| Rollback | `rollback.py` | Undo the last run. |
| Metrics | `metrics.py` | How much, how fast, how complete? |

---

## 2. The decision that shaped everything: a separate Postgres schema

The brief lists eight target tables. **Three of them already exist.**

| Requested | Already in `public` | Conflict |
|---|---|---|
| `kg_skills` | `public.kg_skills` | admin CMS table, different columns, admin-writable |
| `kg_schemes` | `public.kg_schemes` | same |
| `kg_relationships` | `public.kg_relationships` | generic untyped edges, admin-writable, different keys |

The same brief also says: *"Do not touch … any existing application tables."*

Both instructions are satisfiable at once, but only by moving out of `public`:

```sql
create schema knowledge;
create table knowledge.kg_skills (...);   -- the requested name
                                          -- public.kg_skills untouched
```

**What this buys, beyond avoiding the collision:**

- **Rollback becomes total.** `drop schema knowledge cascade` removes every trace of
  the projection and cannot reach a user table. There is no version of that command
  in `public` that is safe to type.
- **Grants are per-schema.** `grant usage on schema knowledge to anon, authenticated`
  is one statement, and no write grant is issued to anyone.
- **The boundary is visible in every query.** `knowledge.kg_skills` versus
  `public.kg_skills` tells a reader which one they are looking at.

Two tables named `kg_skills` is admittedly a wart. It is a smaller wart than either
overwriting a live CMS table or renaming the tables the brief asked for. The
frontend integration plan (`SUPABASE_INTEGRATION.md`) already treats the CMS tables
as a separate layer with a different job, so the two coexist by design rather than
by accident.

---

## 3. Data flow, and where it stops

```
  extract        CSV → dicts, shaped to the spec, tagged with source
     │           only declared columns survive
     ▼
  transform      strings → typed values; sentinels → NULL; content hash
     │           ↳ ABORT on a malformed number or date
     ▼
  validate       7 checks across ALL tables at once
     │           ↳ ABORT on any error, before anything is written
     ▼
  detect         compare content hashes to the manifest
     │           → INSERT / UPDATE / DELETE / SKIP
     ▼
  snapshot       write what is about to change, plus pre-images
     │
     ▼
  apply          upsert + soft delete
     │           ↳ ABORT leaves the manifest un-advanced, so the run replays
     ▼
  manifest       written LAST
```

**Two abort points are before any write, and one is during.** The ordering is the
design:

**Validation runs across all eight tables before any of them is written.** It has
to — `kg_relationships` cannot be validated without `kg_entities` in hand. Writing
entities and then discovering the edges are broken would leave the target in a
state that is neither the old one nor the new one.

So a run is all-or-nothing. One bad foreign key anywhere aborts everything and the
target is untouched. **A partially synced projection is worse than a stale one:**
stale is merely old, partial is silently inconsistent, and only one of those is
obvious to a consumer.

**The manifest is written last.** If it were written first and the apply then
failed, the next run would believe the failed rows were already synced and skip
them forever. Written last, a crashed run simply replays. A test asserts this
(`test_failed_apply_does_not_advance_the_manifest`).

---

## 4. Change detection: why a manifest, not a query

The obvious design is to ask Supabase what it holds and diff against that. It is
worse in three specific ways:

| Problem | Consequence |
|---|---|
| Requires a live connection to *plan* | Dry run stops working offline; the framework becomes untestable without credentials |
| Depends on the target's round-tripping | A numeric read back as a string looks like a change on every run |
| Ratifies drift | A hand-edited row becomes the baseline instead of a discrepancy to correct |

The manifest — `{table: {row_key: content_hash}}` — is a record of what *this
framework* last wrote. Comparing against it makes the sync reproducible, plannable
offline, and treats tampering as a change to correct rather than a state to
preserve.

**The content hash excludes the `sync_*` columns.** Otherwise `sync_synced_at`
would move on every run and every row would report as updated forever.

---

## 5. Deletion is soft, always

A row that disappears from a package is marked `sync_deleted_at`, never removed.

Package releases are immutable and versioned. A row vanishing almost always means a
dataset was regenerated, not that a fact stopped being true — Package005's crop
renumbering during v1.0.0 is exactly that case. Soft delete keeps the row queryable
for anything already referencing it, and makes the removal reversible without a
restore.

Rolling back an insert **also** soft-deletes rather than removing: the row existed
for some period and something may have referenced it. `purge` exists for the
operator who genuinely wants a row gone, and no sync path calls it.

---

## 6. Sentinels become NULL, and record which sentinel

Building this surfaced something the platform did not have written down: **there is
more than one sentinel.**

| Sentinel | Cells | Meaning |
|---|---:|---|
| `PENDING_VERIFICATION` | 2,456 | a fact could not be sourced |
| `PENDING_GEOCODING` | 272 | Package001 coordinates not yet resolved |

`SENTINELS` is an explicit set, not a `PENDING_*` pattern — a pattern would also
swallow legitimate uppercase values like `PMEGP`, `NABARD`, `CGTMSE` and
`DEPRECATED_REFERENCE`.

Each becomes `NULL`, and the column-to-sentinel mapping is stored in
`sync_pending_fields` as JSONB. Zero would be a fabricated measurement; the literal
string would make every consumer re-implement the check; a bare NULL would lose
*why*. `PENDING_GEOCODING` on a latitude means something different to a reader than
`PENDING_VERIFICATION` on a benefit amount, and the UI can now say which.

Two more type findings came out of the same pass, both recorded in `transform.py`:

- **`minimum_investment` is prose, not a number.** All 45 non-empty Package004
  values are sourced narrative — *"Rs 3,50,000 total project cost per the official
  KVIC/PMEGP profile; smaller informal starts are plausible but not quantified"*.
  The column name implies a measure. Coercing it would discard the sourcing that
  makes it trustworthy.
- **`collection_date` is not always a date.** Nine Package004 rows carry
  `"2026-07-22; 2026-07-24 (v2 enrichment)"`, following the multi-source cell
  convention. Parsing to a single date would silently drop the second collection
  pass. Stored verbatim as text: a cache that reinterprets its source is no longer
  a cache.

---

## 7. Validation: severity is the real design

Seven checks. What matters is which ones abort.

| Check | Severity | Rationale |
|---|---|---|
| V1 Schema | ERROR | An undeclared column would silently widen the projection |
| V2 Keys | ERROR | A duplicate key means one row overwrites another |
| V3 Required | ERROR | |
| V4 Foreign keys | ERROR | A dangling reference is invisible to consumers |
| V5 Confidence | ERROR | |
| V6 Ownership — **undeclared** | ERROR | |
| V6 Ownership — **declared** | WARNING | Governed by `known_overlaps.csv` and an ADR |
| V7 Verification status | ERROR | |
| `VST-NEEDS_REVIEW` | **not a finding** | True of all 2,299 rows; flagging it flags everything |

The split is not about how serious a problem sounds. It is about whether writing the
row would make the target **wrong**.

The ownership check earns its keep by following graph check G7: 115 entity rows are
held by a non-owner, and all 115 are declared in `known_overlaps.csv` under ADR-005.
Warning on each would produce 115 lines an operator learns to scroll past — and then
an *undeclared* overlap slips through unnoticed. Declared cases collapse to **4
summary warnings** naming the ADR; an undeclared one is an **error**.

---

## 8. Adapters, and why the tests need no credentials

```python
class Target(ABC):
    def upsert(self, table, rows): ...
    def soft_delete(self, table, row_keys, at): ...
    def fetch_keys(self, table): ...
    def count(self, table): ...
```

| Implementation | Used by |
|---|---|
| `InMemoryTarget` | **all 64 tests**, `plan`, rehearsal |
| `SupabaseTarget` | production only |

Not an abstraction for hypothetical future backends — one for testability. A sync
framework whose tests need a live database is one whose tests do not run in CI and
whose failure modes are found in production. `InMemoryTarget` also supports injected
failures (`fail_on`), which is how the abort and rollback paths are tested at all.

The `supabase` client is imported lazily, so the whole framework — including the
full suite — runs with the package uninstalled.

### The safety rule is an allowlist

```python
def _assert_target(self, table):
    if table not in BY_NAME:
        raise TargetError(...)
```

The brief names nine application tables that must never be touched. Encoding that
as a denylist would silently permit a tenth. Instead, only the eight tables this
framework owns are reachable; a typo raises instead of writing somewhere it should
not. A test asserts every table the brief names is refused.

---

## 9. Measured behaviour

Against the real repository, `InMemoryTarget`:

| | |
|---|---|
| Rows extracted | **1,812** across 8 tables |
| Transform errors | 0 |
| Validation errors | 0 (4 governed warnings) |
| First sync | 1,812 inserted, ~0.09 s, ~21,000 rows/s |
| Second sync | **0 inserted, 0 updated, 1,812 skipped** |
| Coverage | 8/8 tables complete |
| Rollback | 1,812 live → 0 live, 1,812 retained soft-deleted |
| Sentinel rate | 1.26% of cells |

Per table: `kg_entities` 647, `kg_relationships` 865, `kg_businesses` 85 (five
datasets unioned), `kg_districts` 61, `kg_skills` 45, `kg_agriculture` 45,
`kg_schemes` 40, `kg_industries` 24.

---

## 10. Honest limits

| Limit | Detail |
|---|---|
| **Never run against a live Supabase** | No credentials exist in this environment. Every path is exercised against `InMemoryTarget`, which is faithful but is not Postgres. The first production run should be `plan`, then `sync --table kg_schemes`, then the rest. |
| Rollback cannot undo a hand edit | It restores what the *framework* changed. A row edited in the Supabase console is in no snapshot — and the next sync would overwrite it anyway. This is why no write policy is granted. |
| No transactional guarantee across tables | The engine aborts before writing on any validation error, but a failure *during* apply can leave earlier tables written. The manifest is not advanced, so a re-run repairs it. True cross-table atomicity needs a single Postgres transaction, which the REST client does not expose. |
| `kg_businesses` unions two shapes | Package008 keys on `business_id`, Package004 on `id`; both columns exist and one is null per row, discriminated by `business_kind`. Honest, and slightly awkward. |
| The manifest is per-deployment | Not committed. A fresh environment plans a full insert, which is correct. |

---

## 11. Files

```
knowledge_sync/
  config.py               8 TableSpecs — the only place a table is declared
  extract.py              CSV → rows
  transform.py            types, sentinels, content hash
  validation.py           7 checks
  changes.py              manifest + INSERT/UPDATE/DELETE/SKIP
  adapters.py             InMemoryTarget, SupabaseTarget, the allowlist
  engine.py               orchestration, 4 modes
  logs.py                 console + JSONL
  metrics.py              counts, coverage, pending rate
  rollback.py             snapshots, restore
  cli.py / __main__.py    plan | sync | rollback | status | history | snapshots
  generate_migration.py   DDL generated from the specs
  migrations/001_knowledge_schema.sql
  state/                  manifest, snapshots, log (gitignored)
```

Adding a ninth table is a `TableSpec` and a regenerated migration. No module
hard-codes a table name.

**Companion documents:** `SUPABASE_SCHEMA.md`, `SYNC_WORKFLOW.md`,
`OPERATIONS_GUIDE.md`.
