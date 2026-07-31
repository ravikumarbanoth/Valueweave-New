# Search Pipeline Report

**ValueWeave v1.0 · search box → results, traced**

---

## The trace

```
KnowledgeSearch.jsx          user types, 250 ms debounce, ≥2 characters
        │
        ▼
lib/knowledge.js  searchKnowledge(q, { entityType, limit })
        │                       no API route, no fetch — the browser queries
        │                       Supabase directly with the anon key
        ▼
supabase-js  .from("kg_entities")
             .select("*")
             .is("sync_deleted_at", null)
             .ilike("canonical_name", `%${q}%`)      ← the whole of the matching
             .eq("entity_type", type)                 (optional filter)
             .order("confidence_score", desc)
             .limit(24)
        │
        ▼
knowledge.kg_entities                                ← EMPTY: import never ran
        │
        ▼
[]  →  "Nothing matches "welding" yet"
```

There is **no API layer**. The frontend makes zero `fetch()` calls; it holds a
Supabase client scoped to the `knowledge` schema. That is deliberate — the
engines are Python with no deployment target, so they write to Supabase and the
frontend reads it with the client it already had.

---

## Why search returns nothing today

`knowledge.kg_entities` has no rows. The query is correct, the client is correct,
the table is empty. Nothing else is wrong at this level.

---

## What search will do once the import runs

Tested against `entities.csv` — the exact data the import would load — using the
same substring rule the query uses:

| Term | Matches | Examples |
|---|---:|---|
| Construction | **4** | Construction (Industry), Construction & Real Estate (Industry) |
| Electrician | **2** | Electrician (Domestic Wiring), Industrial Electrician (Skills) |
| Solar | **6** | Solar Panel Assembly Unit, Solar Rooftop EPC Contractor (MSMEs) |
| Bakery | **1** | Bakery Production (Skill) |
| Robot | **6** | ABB Robotics Certification, FANUC Certified Robot Operator |
| **Dairy** | **0** | — |

**Five of the brief's six terms work.** The sixth is a real defect.

---

## The Dairy defect

`searchKnowledge()` matches `canonical_name` and nothing else.
`knowledge.kg_entities` carries identity — id, type, name, package, confidence —
and no descriptive text at all. Descriptions live in the six per-type detail
tables and are never searched.

"Dairy" appears in **11 package rows**: a veterinary university, fodder and
livestock crop categories, an animal feed processing opportunity, the National
Livestock Mission. A user searching for it gets "Nothing matches "Dairy" yet",
which is a true statement about our index and a false impression of our research.

Every multi-word or descriptive query has the same problem. "Cold storage",
"food processing", "women entrepreneurs" — all present in the research, none in
an entity name.

### The fix, specified

This is the `knowledge_search_index` the audit brief hypothesises in Step 8, and
it is the one component of that proposal the platform genuinely lacks.

**Do not add a table.** Add a column, populated by the pipeline that already
runs:

1. **`frontend/migrations/012_entity_search_text.sql`** — forward migration,
   leaving 001 untouched:
   ```sql
   alter table knowledge.kg_entities add column if not exists search_text text;
   create index if not exists kg_entities_search_idx
     on knowledge.kg_entities using gin (to_tsvector('simple', coalesce(search_text,'')));
   ```
2. **`knowledge_sync/config.py`** — add `search_text` to the `kg_entities`
   columns and a transform that concatenates `canonical_name`, `entity_type`,
   the detail row's `description` and `category_name`. `generate_migration.py
   --check` must be re-run so the DDL and the spec stay in agreement.
3. **`lib/knowledge.js`** — `.ilike("search_text", …)` with `canonical_name` as
   the ordering tiebreak, so an exact name still wins.

**Effort: small. Risk: low** — additive column, no data moved, idempotency
unaffected because `sync_content_hash` already excludes `sync_*` columns only and
would legitimately change once per row on the first run after the change.

**Deliberately not implemented in this sprint.** It requires a migration and a
sync-spec change that should be proven against a real Postgres before merging,
and no environment reachable from here has one. Shipping a schema change verified
only against an in-memory target would be the same class of mistake this audit
was called to diagnose.

---

## What search does not claim to be

The Python `search/index.py` implements a four-mode ladder — EXACT → ALIAS →
PREFIX → FUZZY — with 27 tests. **The frontend does not use it** and does not
pretend to: it is a Python module with no deployment target. The UI does Postgres
substring matching and the copy says so.

Bridging the two would mean deploying a Python service, which is a larger
architectural decision than this audit's scope.

---

**Companions:** `KNOWLEDGE_ARCHITECTURE_AUDIT.md` · `IMPLEMENTATION_PLAN.md`
