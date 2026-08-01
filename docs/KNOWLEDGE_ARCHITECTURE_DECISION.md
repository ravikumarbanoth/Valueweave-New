# One knowledge architecture

Decided against the live production schema dump, not against the migrations.

---

## What the live database actually contains

30 tables in `public`, 70 RLS policies, and **no `knowledge` schema at all**.

| | |
|---|---|
| `public.profiles` with `is_admin` | ✅ present — both deployment preflights pass |
| `public.is_valueweave_admin()` | ✅ present — 16 CMS policies depend on it |
| `public.is_admin()` | ✅ present — 20 application policies depend on it |
| `knowledge` schema | ❌ absent |
| `user_intelligence` schema | ❌ absent |
| `kg_vocabulary_map` (either schema) | ❌ absent — migration 009 never succeeded |
| `kg_entity_registry` | ❌ absent — confirms 009's FK target was never built |
| migration-tracking table | ❌ none — migrations are applied by hand |

The dump is schema-only, so it says nothing about row counts. Every decision
below is safe under either answer, and the one place where the count matters is
guarded at runtime rather than guessed at.

---

## The collision, precisely

Three names exist in both systems:

| Name | `public` (CMS) | `knowledge` (projection) |
|---|---|---|
| `kg_skills` | 22 cols, uuid PK, `rich_text`, `faq_json`, SEO, publish workflow | 29 cols, `sync_row_key` PK, provenance, confidence |
| `kg_schemes` | same shape | same shape |
| `kg_relationships` | uuid edges, admin-authored | 865 derived edges |

This is exactly why the projection was given its own schema, and the live dump
confirms that reasoning was right: putting it in `public` would have collided
with three tables carrying different columns, different RLS and a different
purpose.

Verified by execution: with both deployed side by side in a replica of the live
schema, `public.kg_skills` (22 columns) and `knowledge.kg_skills` (29 columns)
coexist as distinct objects, and applying the deployment leaves the `public`
schema **byte-identical** — same 30 tables, same 70 policies, same column
fingerprint.

---

## The decision

> **`knowledge.*` is canonical. The CMS is demoted to an editorial override.**

**Why the projection wins.** It is derived from Git, which the architecture
already declares the single source of truth. Every row names the package and row
it came from. CI keeps it current. It holds 647 entities and 865 relationships
today.

**Why the CMS is not simply deleted.** Two reasons, and only one of them is
caution:

1. A human deliberately publishing a record should beat a projection. That is a
   real editorial capability, not a duplicate — it is just one nothing is
   currently using.
2. The repository states nothing populates these tables. That is a claim about
   the code, not about the database, and the dump cannot confirm it. Dropping a
   table on the strength of it would be destroying content I cannot see.

So the frontend prefers the graph and falls back to nothing else; the CMS
overrides only if it has rows; and retirement is a separate, guarded step.

### What that means per section

| Section | Canonical source | Rows available |
|---|---|---|
| `/skills` | graph — `Skill` | 45 |
| `/schemes` | graph — `GovernmentScheme` | 40 |
| `/resources` | graph — `TrainingProvider` + `FinancialInstitution` + `Institution` | 112 |
| `/roadmaps` | **none** | 0 |
| `/districts`, `/knowledge/*` | graph (already) | 647 total |
| `/district-opportunity-index` | CMS — genuinely CMS-only | — |

`/resources` was the real gap. It had 112 matching entities in the graph and read
only the empty CMS table, so it had never displayed a single row. It is now
bridged, and because those three entity types live at three different detail
URLs, the link is resolved per row rather than from one base path — the previous
code hardcoded `graphType === "GovernmentScheme" ? "scheme" : "skill"`, which
silently resolved everything that was not a scheme to "skill".

`/roadmaps` is the one section with no research behind it. A roadmap is an
ordered sequence of costed steps and the graph projects nothing of the kind;
assembling one out of unrelated entities would be fabricating a guide nobody
wrote. That page now says "Not available yet" and points to what does exist.

---

## What was removed, and what deliberately was not

**Removed — a second definition of "deploy the knowledge layer."**
`scripts/first_deploy.sh` applied the two migrations itself, so the greenfield
path and `sql/deploy_knowledge.sql` could disagree about what a deployed
knowledge layer is. It now invokes the same generated script an operator runs in
the SQL Editor. A test fails if it goes back to applying migrations directly.

**Removed — internal vocabulary from four public pages.** They told readers their
content would appear "after admins publish them from the Roadmaps CMS" or "once
the knowledge base is synced". Named internal tools a student cannot reach, and
an implied wait with no end.

**Not removed — `lib/static-knowledge.js`.** Still serves 56 indexed detail URLs.
Dead-looking, not dead.

**Not removed — migration 009.** It is un-appliable (it references
`kg_entity_registry`, which no migration creates) and the live schema proves it
never ran. But two tests assert its brokenness as the reason 011 exists, and
`first_deploy.sh` runs it deliberately so the failure is on the record. Deleting
it would erase the explanation for the repair.

**Not dropped — six CMS tables.** `kg_district_profiles` and `kg_relationships`
back the public `/district-opportunity-index` and the `/admin/opportunity-mapping`
editor writes to the latter. `kg_roadmaps`/`kg_roadmap_steps` have no equivalent.
`kg_industry_sectors`/`kg_collaborator_types` are controlled vocabularies for the
admin UI. None is a duplicate.

---

## Retiring the three duplicates

`sql/retire_cms_knowledge_tables.sql` — **opt-in, run after the sync, never
automatically.**

It drops `public.kg_skills`, `public.kg_schemes` and `public.kg_resources`, and
nothing else. Before dropping anything it counts rows in all three and **aborts
the whole transaction if any is non-empty**, naming the table and telling you to
move the content into the research packages in Git instead.

Verified both ways against the live replica:

| State | Result |
|---|---|
| all three empty | dropped; 30 → 27 tables; projection intact; the six KEEP tables intact |
| `kg_schemes` holds 1 row | **aborted**; 30 tables still present; the row preserved |

It uses `drop table … restrict`, not `cascade`: a surviving dependency should
stop the drop rather than be swept up by it.

**Pair it with the frontend change in that order.** Dropping these breaks
`/admin/skills`, `/admin/schemes` and `/admin/resources`, which edit them. Run
the SQL first — if it aborts, the tables have content and those screens must
stay. If it succeeds, remove the three admin routes in the same deploy.

---

## One change the live schema forced

`PHASE 1` of the deployment used to be `create or replace function
public.is_valueweave_admin()`. The dump shows that function already exists with
**sixteen policies** written in terms of it — the access-control rule on every
CMS table.

`create or replace` would have swapped the body those policies evaluate for one
this script cannot diff against the deployed version. The two are believed
identical; "believed identical" is not a reason to rewrite a live access-control
predicate.

PHASE 1 now creates it **only if absent**. Verified both ways: against the live
replica it reports `already exists — left untouched` and the function's OID is
unchanged (17318 before and after) with all 70 policies intact; with the function
dropped, it creates it and the deployment completes.
