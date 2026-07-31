# Implementation Plan

**ValueWeave v1.0 · what the audit found, what was built, what remains**

---

## Was implementation required?

The brief's Step 9 triggers *"if Knowledge Packages → Supabase has NO
connection"*. The audit found something narrower and more awkward:

> **The connection exists, is complete, is tested, and has never been invoked.**

So building an import pipeline would have been building a second one. What was
genuinely missing was the thing that *calls* it — and after that, two defects
that would still be there on the day it runs.

---

## Built in this sprint

### `.github/workflows/knowledge-sync.yml`

There was **no CI in this repository at all** — no `.github/` directory. A
complete pipeline and nothing to run it.

| | |
|---|---|
| Runs on | every merge to `main` touching `packages/`, `knowledge_graph/`, `knowledge_sync/`, `governance/vocabulary/`, `scripts/` |
| Also | weekly (Mon 03:00 UTC), and on demand |
| Manual default | **plan only** — the first thing anyone tries is the safe thing |
| Concurrency | serialised; two syncs against one database make the idempotency check meaningless |
| Steps | tests → preflight → plan → apply → verify → upload run log |

Three decisions worth stating:

* **It fails loudly without secrets.** A workflow that silently skips its apply
  step is indistinguishable from one that worked, and that ambiguity is exactly
  what this audit spent its time resolving.
* **It applies, it does not only plan.** Guarded by a test, because a plan-only
  workflow is green and delivers nothing.
* **Verification uses the anon key.** The service-role key can read a schema
  that is not exposed to the browser — verifying with it would report a healthy
  deployment while every page rendered empty.

### `tests/test_knowledge_pipeline.py` — 15 tests

Holds the audit's findings so they cannot silently regress:

* every one of the 12 declared source files exists, has rows, and has its key
  column — nothing checked this, and a renamed dataset would have failed at
  import time in CI after a merge;
* the workflow exists, applies, fails without secrets, and never takes the
  service-role key from anywhere but a secret;
* the measured coverage — 647 entities, 865 edges, 27 of 61 districts linked, the
  five search terms that work and the one that does not — asserted as floors.

Three of these tests were wrong on first run and were fixed rather than loosened.
One had the wrong premise (Package004's rows reach `kg_businesses` under
Package008's ownership, so `owner_package` was the wrong axis); two used regexes
where a greedy `\s*` let a negative lookahead pass. Line-based checks replaced
both.

---

## Required before the pipeline can run

**An operator must add three repository secrets** — Settings → Secrets and
variables → Actions:

| Secret | Used for |
|---|---|
| `DATABASE_URL` | migrations and verification |
| `SUPABASE_URL` | the sync's writes |
| `SUPABASE_SERVICE_ROLE_KEY` | the sync's writes |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | exposure check (optional but recommended) |

> `SUPABASE_SERVICE_ROLE_KEY` bypasses RLS. Actions secrets or a server-side
> environment variable only — never a `NEXT_PUBLIC_*` variable, never a committed
> file, never local shell history.

Then, once:

```bash
scripts/first_deploy.sh          # migrations (009 fails, 011 repairs), crosswalk
#   MANUAL: expose `knowledge` and `user_intelligence` in the Supabase dashboard
scripts/run_user_intelligence.sh --from-db --apply
scripts/verify_deployment.sh
```

Exposing the schemas is the one step no script takes: it is a dashboard toggle
and a decision about what becomes publicly readable.

---

## What remains, in priority order

### 1 · Search beyond entity names — small

`searchKnowledge()` matches `canonical_name` only. "Dairy" returns zero despite
11 package rows mentioning it. Specified in full in `SEARCH_PIPELINE_REPORT.md`:
a `search_text` column on `kg_entities`, populated by the sync, plus a forward
migration `012`.

**Not built here on purpose.** It is a migration plus a sync-spec change, and it
should be proven against a real Postgres before merging. Verifying a schema
change only against an in-memory target would repeat the mistake this audit was
called to diagnose.

### 2 · 305 scheme→district edges — small, highest product impact

`packages/Package007_Government_Schemes/datasets/district_scheme_mapping.csv`
holds 305 verified pairs. `build_graph.py` does not read it. Result: **zero**
scheme→district edges and two dead recommendation rules.

This is the single change that most improves district pages, and it needs no new
research.

### 3 · 410 further recoverable edges — medium

Identified at 100% both-endpoint verification in
`RELATIONSHIP_RECOVERY_REPORT.md`. Would lift `GENERATES_EMPLOYMENT` (32),
`TRAINED_BY` (3) and `SELLS_TO` (12) off the floor. No new research.

### 4 · Package003_Healthcare — medium

Zero entities. Datasets exist; no builder reads them. An entire package is dark.

### 5 · Project the unread Package006/007 datasets — small each

`eligibility_criteria.csv` (55 rows) is the most visible: scheme pages currently
say "we have not published this yet" for eligibility that is researched and
sitting in Git.

---

## The honest sequencing

Running the import is **necessary and not sufficient**. It moves 27 of 61
districts from nothing to something and leaves 34 exactly as they are, because
the limiting factor is edges, not rows.

Items 2 and 3 need no new research and would do more for how the product reads
than item 1 does. The correct order is: **run the import** (so the platform stops
lying about being unprepared), then **fix the edges** (so the pages are worth
reading), then **widen search** (so people can find any of it).

---

## Not verified from this environment

No credential here reaches a database — `frontend/.env.local` holds
placeholders — and `api.vercel.com`, `vercel.com` and `valueweave.in` all return
HTTP 000. So:

* the workflow has never fired;
* no row has been written by this sprint;
* no production page has been observed.

Everything above is verified against the repository. Nothing is verified against
production, and nothing here should be read as claiming otherwise.

---

**Companions:** `KNOWLEDGE_ARCHITECTURE_AUDIT.md` · `SUPABASE_SCHEMA_REPORT.md` ·
`PACKAGE_TO_DATABASE_MAPPING.md` · `SEARCH_PIPELINE_REPORT.md` ·
`DISTRICT_PIPELINE_REPORT.md` · `KNOWLEDGE_GRAPH_REPORT.md`
