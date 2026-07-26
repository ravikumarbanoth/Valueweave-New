# Supabase Integration Architecture — ValueWeave v3.0

**Phase 3 deliverable.** Where each kind of data lives, why, and the contract between
Git and Postgres.

---

## 1. The rule

> **Git is canonical. Supabase holds a derived projection. The projection is disposable.**

This is not a new principle — it is ADR-001 applied one layer further out. `knowledge_graph/`
is already a derived projection of `packages/`, rebuildable from scratch, creating no
knowledge of its own. Supabase becomes the third layer in that same chain:

```
packages/          researched, provenance-complete, hand-curated   ← source of truth
    ↓  build_graph.py            (derived, idempotent, in Git)
knowledge_graph/   647 entities, 865 relationships
    ↓  sync_to_supabase.py       (derived, idempotent, NOT in Git)
Supabase kg_*      the read path the frontend already knows how to use
```

If Postgres and Git disagree, **Git wins and the projection is rebuilt**. Nothing of value
is lost by dropping and rebuilding the projection tables, and the sync must be written so
that this is true.

---

## 2. The four-way split

| Class | Lives in | Written by | Read by | Examples |
|---|---|---|---|---|
| **A. Canonical knowledge** | Git (`packages/`) | Researchers, Knowledge Engine | build tools, sync | 2,299 rows, 77 datasets, provenance columns |
| **B. Projected knowledge** | Supabase `kg_*` | **sync only** | frontend, RLS-public | 647 entities, 865 edges, projected scheme/skill rows |
| **C. User data** | Supabase | users, app | frontend, RLS-scoped | `profiles`, `opportunities`, `connections`, `collaborator_profiles` |
| **D. API-only** | Neither — computed | — | admin, analysts | fuzzy search ranking, path traversal, merge proposals, stewardship queue |

### What syncs, and what does not

| Package data | Rows | Syncs? | Reason |
|---|---:|---|---|
| Entity registry | 647 | **Yes** | Every page that shows an entity needs it |
| Relationship registry | 865 | **Yes** | Every "related to" section traverses it |
| Aliases | 150 | **Yes** | Needed for lookup by surface form |
| `government_schemes` | 40 | **Yes** | Backfills the empty `kg_schemes` |
| `skills` | 45 | **Yes** | Backfills the empty `kg_skills` |
| `training_providers`, `institutions` | 25, 66 | **Yes** | Backfills `kg_resources` |
| `msme_businesses`, business opportunities | 40, 45 | **Yes** | Business Explorer, Idea Library links |
| Districts, states | 61, 2 | **Yes** | District pages, dashboard rails |
| Crops, soils, climate zones, machinery, raw materials | 45/10/8/69/21 | **Entities only** | The 30+ agronomic attribute columns have no UI. Sync the node, leave the detail in Git and reachable by link. |
| `district_scheme_mapping` (305 rows), eligibility, application process, required documents | ~500 | **No** | Deep detail. Reachable via the API or the CSV. Syncing them triples the projection for pages that do not exist. |
| Provenance columns (all 6, every row) | — | **Partially** | `data_source`, `source_url`, `confidence_score`, `verification_status` sync onto entities — the UI must show them (R2). `collection_date` and `notes` do not. |

**Roughly 1,000 of 2,299 rows sync.** The rest stay in Git and are reachable through the
API for admin and analyst use. That is the honest boundary: sync what a page renders,
not everything that exists.

### What must never sync

- **The stewardship ledger.** `stewardship/review_ledger.csv` is an append-only audit
  trail of human decisions. It belongs in Git, in version control, where an edit is a
  visible commit.
- **Merge proposals.** `knowledge_graph/resolution/merge_proposals.csv` is a work queue
  for a human, not application data.
- **The source registry.** 605 sources with collector/parser routing is operational
  metadata for the Knowledge Engine.
- **Audit reports.** `audit/` is a point-in-time snapshot.

---

## 3. Existing tables: extend, project, or leave alone

| Table | Verdict | Change |
|---|---|---|
| `profiles` | **Extend** | Add resolved-skill entity ids and a home-district entity id. Original columns untouched. |
| `opportunities` | **Extend** | Add resolved industry/district entity ids. Nullable, additive. |
| `connections` | **Unchanged** | Skill gap is computed from the two joined profiles. Nothing to store. |
| `collaborator_profiles` | **Extend** | Resolve `top_sectors` to Industry ids. |
| `founder_matches` | **Unchanged** | Already an admin-computed score. Knowledge adds explanation at render time, not a column. |
| `kg_schemes` | **Project into** | Backfill 40 rows with `source = 'package'` |
| `kg_skills` | **Project into** | Backfill 45 rows with `source = 'package'` |
| `kg_resources` | **Project into** | Backfill from providers + institutions |
| `kg_district_profiles` | **Project into** | Backfill 61, preserving any admin editorial |
| `kg_roadmaps`, `kg_roadmap_steps` | **Unchanged** | No package counterpart. Stays admin-authored. |
| `kg_industry_sectors`, `kg_collaborator_types` | **Project into** | 78 industries; collaborator types stay admin-authored |
| `kg_relationships` | **Repurpose** | See §4 — this is the one genuinely awkward table |
| All analytics tables | **Unchanged** | `search_events` gains rows from unified search, no schema change |
| `platform_settings` | **Unchanged** | Add sync config keys as rows, not columns |

**Nothing is dropped. Nothing is renamed. Every change is additive.**

---

## 4. The `kg_relationships` problem

`kg_relationships` already exists with `source_type`/`source_id`/`source_external_id` →
`target_type`/`target_id`/`target_external_id`, plus `relationship_type`, `weight`, and a
seven-column uniqueness constraint. It is generic, untyped and admin-writable.

The knowledge graph's 865 edges are none of those things: they are typed against a
registry of 19 relationship types with declared endpoint types, they carry provenance
(package, dataset, row id), and graph check G6 fails the build if an endpoint type is
wrong.

Overloading one table for both loses exactly what makes the graph trustworthy.

**Decision: two tables with distinct jobs.**

| Table | Holds | Written by | Typed? | Provenance? |
|---|---|---|---|---|
| `kg_relationships` *(existing)* | Admin-authored editorial links, and **user-scoped** edges (user ↔ entity) | admin, app | No | No |
| `kg_graph_edges` *(new)* | The 865 projected graph edges | **sync only** | Yes | Yes |

Reusing `kg_relationships` for both would mean either dropping provenance from graph edges
or adding six columns that are null for every admin row. Two tables is the smaller lie.

---

## 5. The sync contract

`scripts/sync_to_supabase.py` — a new script, sitting beside `build_graph.py`, obeying
the same rules the rest of the platform already follows.

### Properties, in priority order

1. **One-way.** Git → Postgres. The sync never reads application state to decide what to
   write. There is no merge, no conflict resolution, no "newer wins".
2. **Idempotent.** Running it twice changes nothing the second time. Verified the way
   `test_graph_integrity.py::test_rebuild_is_idempotent` verifies the graph — compare the
   result to itself across two runs, not to the last commit.
3. **Never touches admin rows.** Every projected row carries `source = 'package'`. Rows
   with `source = 'admin'` are invisible to the sync. This is the mechanical guarantee
   behind risk R6.
4. **Aborts rather than partially writes.** Same discipline as the package generators:
   an unresolvable reference stops the run. A half-synced projection is worse than a
   stale one.
5. **Provenance travels.** `source_package`, `source_dataset`, `source_row_id`,
   `confidence_score`, `verification_status` land on every projected row. A projected row
   that cannot say where it came from is not written.
6. **Reports drift.** Before writing, it compares row counts and a content hash per table
   and prints what will change. `--check` exits non-zero on drift without writing — that
   is the CI mode.

### Invocation

```bash
python3 scripts/sync_to_supabase.py --check     # CI: exit 1 on drift, write nothing
python3 scripts/sync_to_supabase.py --dry-run   # print the plan
python3 scripts/sync_to_supabase.py --apply     # write
python3 scripts/sync_to_supabase.py --apply --only kg_schemes
```

Credentials: `SUPABASE_SERVICE_ROLE_KEY`, server-side only, never `NEXT_PUBLIC_*`. The
sync is the only thing in the system that holds it.

### Trigger

CI, on push to `main` touching `packages/**` or `knowledge_graph/**`. Not on a timer —
package data changes by commit, so the commit is the correct trigger. A nightly `--check`
catches manual database edits.

### Ordering

```
1. kg_entity_registry      (nodes first — edges reference them)
2. kg_entity_aliases
3. kg_graph_edges          (endpoints must already exist)
4. kg_schemes / kg_skills / kg_resources / kg_district_profiles / kg_industry_sectors
5. kg_vocabulary_map       (crosswalks)
6. refresh materialised views
```

Whole thing in one transaction where the client allows; otherwise entities and edges must
share one, because a partially-written edge set breaks every "related to" section.

---

## 6. Reads: which client, which page

The frontend keeps using the two clients it already has. No new pattern.

| Surface | Client | Caching |
|---|---|---|
| Server components (`/skills`, `/schemes`, `/district/[slug]`) | `lib/supabase-server.js` | `export const revalidate = 300` — already the convention |
| Client components (`/dashboard`, `/ideas`) | `lib/supabase-browser.js` | none today; see `DATABASE_EXTENSION_PLAN.md` §caching |
| Anon reads with no cookie (`getKgEntities`) | `lib/knowledge-graph.js` anon client | `revalidate` |

**A new `lib/knowledge.js`** mirrors `lib/knowledge-graph.js` for the projected tables —
same shape, same silent-failure behaviour (`catch { return [] }`), same naming. An engineer
who knows the existing file will recognise the new one immediately.

---

## 7. When the Python API *is* the right answer

Three cases, all off the user request path:

| Use | Why not Supabase |
|---|---|
| **Fuzzy search** | `SearchEngine`'s two-route fuzzy matching (token blend + typo floor) is not expressible in Postgres `ilike`. Postgres `pg_trgm` is a close substitute for the typo route; see the note below. |
| **Multi-hop traversal** | `QueryEngine.traverse()` and `shortest_path()` are recursive. Supabase can do it with a recursive CTE, but the logic already exists and is tested. |
| **Stewardship & admin analytics** | `/admin/stewardship`, `/admin/knowledge-graph`. Admin-only, low-traffic, and a failure degrades an internal dashboard rather than a user page. |

**Deployment, when it happens.** The v2.2 API is a stdlib `http.server`, explicitly a
scaffold with **no authentication** — its own reference says *"Do not expose this on a
public interface."* Deploying it requires, in order: a real WSGI/ASGI server, an auth
layer, rate limiting, and a private network path or an allowlist. That is a project, and
it is why v3.0 puts nothing user-facing behind it.

**On search specifically.** Postgres full-text plus `pg_trgm` covers exact, prefix and
typo-tolerant matching well enough for the app's search box, and it joins natively against
`profiles` and `opportunities`. Recommend Postgres for the user-facing search and keep the
Python `SearchEngine` as the admin/analyst tool and the reference for expected behaviour.
`DATABASE_EXTENSION_PLAN.md` §5 gives the index DDL.

---

## 8. Row Level Security

Projected tables adopt the policy shape the `kg_*` tables already use — no new pattern:

```sql
-- read: published rows to everyone, everything to admins
create policy "<table> public read"
  on public.<table> for select
  using (status = 'published' or public.is_valueweave_admin());

-- write: nobody through the API. The sync uses the service role, which bypasses RLS.
create policy "<table> admin write"
  on public.<table> for all
  using (public.is_valueweave_admin())
  with check (public.is_valueweave_admin());
```

Two things worth being explicit about:

- **Projected rows are `status = 'published'` on arrival.** They come from released
  packages; there is no draft state upstream. But they are *not* verified — every row is
  `VST-NEEDS_REVIEW`, and `verification_status` syncs so the UI can say so (R2).
- **The service role key bypasses RLS entirely.** It exists only in CI, only for the sync.
  It must never appear in a `NEXT_PUBLIC_*` variable, a client component, or a route
  handler.

---

## 9. Failure modes

| Failure | Effect | Handling |
|---|---|---|
| Sync fails mid-run | Partial projection | Transactional; abort and roll back. Last good projection stays served. |
| Sync never runs after a package change | Stale projection | `--check` in CI fails the build. A nightly check alerts. |
| Admin edits a projected row | Overwritten on next sync | Prevented: projected rows are read-only in the admin UI and carry `source = 'package'`. |
| Supabase down | Knowledge sections empty | Same failure mode the app already has for every page. `catch { return [] }` and an empty state — no new behaviour. |
| Crosswalk resolves to a deleted entity | Broken link | FK from the crosswalk to the entity registry, `on delete restrict`. The sync aborts rather than orphan a link. |
| Projection and Git disagree | Wrong data shown | Git wins. Drop and rebuild — cheap by construction. |

---

## 10. What this architecture explicitly does not do

- **No write path from the app into `packages/`.** Users cannot edit knowledge. Corrections
  go through the package release process and the stewardship ledger. This preserves ADR-001.
- **No real-time subscriptions on projected tables.** Package data changes by commit, not
  by the second.
- **No Supabase Edge Functions.** Nothing here needs server-side compute that Next.js
  server components cannot do.
- **No replacement of any existing table.** Thirty tables keep working exactly as they do.
