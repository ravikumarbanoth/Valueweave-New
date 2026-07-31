# Knowledge Architecture Audit

**ValueWeave v1.0 · Knowledge → Database → API → UI pipeline**

Every conclusion below was verified by executing something against the
repository. Nothing is assumed.

---

## The answer, first

> ### Are the Knowledge Packages connected to Supabase?
>
> **The connection exists in code and has never been executed.**
>
> A complete, tested import pipeline reads the package CSVs and writes them to
> Supabase. It is 12 modules, 8 table specs, a migration, a driver script and
> 114 tests. It works.
>
> **It has never once written to a database.** The only record of any run in the
> repository is two entries in `knowledge_sync/state/sync_log.jsonl`:
>
> ```
> RUN 20260727T033850Z-fe2a27   mode: 'dry-run'   applied: False
> RUN 20260727T093247Z-a04184   mode: 'dry-run'   applied: False
> ```
>
> `--target` defaults to `memory`. There was **no CI in this repository at
> all** — no `.github/workflows/` directory — so nothing was ever going to
> invoke it.
>
> That is the whole diagnosis. The production pages are not broken. They are
> correctly reporting an empty table.

---

## Step 1 · How the packages are stored

**Plain files in Git. No database involvement at rest.**

| Format | Files | Role |
|---|---:|---|
| `.csv` | 84 | the research itself — the source of truth |
| `.md` | 221 | documentation, provenance notes, manifests |
| `.json` | 121 | build artifacts, registries, checksums |
| `.py` | 15 | per-package build scripts |

| Package | Datasets | Rows |
|---|---:|---:|
| Package001_Geography | 5 | ~143 |
| Package002_Education | 4 | ~145 |
| Package003_Healthcare | 4 | ~150 |
| Package004_Industries | 5 | ~68 |
| Package005_Agriculture | 16 | ~404 |
| Package006_Skills_and_Training | 10 | ~301 |
| Package007_Government_Schemes | 15 | ~670 |
| Package008_MSME | 18 | ~495 |

Are they only CSV/JSON? **Yes, at rest.** Are they imported into Supabase?
**No — the importer exists and has not run.**

---

## The pipeline, as designed

```
packages/*/datasets/*.csv          84 CSV files, the source of truth
        │
        ├─ knowledge_graph/build_graph.py
        │     └→ entities.csv (647) + relationships.csv (865)
        │
        └─ knowledge_sync/  ─────────────── 8 TableSpecs, 12 source files
                 │  extract → transform → validate → plan → apply
                 ▼
          Supabase `knowledge` schema           ← NEVER REACHED
                 │
                 ▼
          frontend/lib/knowledge.js
                 │
                 ▼
          14 public routes
```

Verified: every one of the 12 source files the sync declares **exists and has
rows**. `tests/test_knowledge_pipeline.py` now asserts this on every run.

---

## Step 3 · Which package writes into which table

| Table | Reads from | Rows waiting |
|---|---|---:|
| `kg_entities` | `knowledge_graph/entities/entities.csv` | 647 |
| `kg_relationships` | `knowledge_graph/relationships/relationships.csv` | 865 |
| `kg_districts` | Package001 `district.csv` | 61 |
| `kg_skills` | Package006 `skills.csv` | 45 |
| `kg_schemes` | Package007 `government_schemes.csv` | 40 |
| `kg_businesses` | Package008 `msme_businesses.csv` **+ 4 Package004 files** | 85 |
| `kg_industries` | Package008 `msme_categories.csv` | 24 |
| `kg_agriculture` | Package005 `crops.csv` | 45 |
| | **Total** | **1,812** |

### Packages that are disconnected

* **Package003_Healthcare — completely disconnected.** It contributes **zero**
  entities to the graph and has no TableSpec. Its datasets exist; no builder
  reads them. No hospital, medical college or health scheme is reachable
  anywhere in the application, and running the import would not change that.
* **Package002_Education — half connected.** Its 66 Institution entities reach
  the graph, but it has no detail table, so an institution page shows a name and
  its links and nothing else.

Both are pinned by a test so that fixing either registers as a change.

---

## Step 7 · Does the knowledge graph exist in production?

**In Git: yes.** 647 entities, 865 typed relationships, 19 entity types, every
edge carrying provenance. Built deterministically by `build_graph.py` and
committed as CSV.

**In production: no.** It would live in `knowledge.kg_entities` and
`knowledge.kg_relationships`. Those tables are declared by
`knowledge_sync/migrations/001_knowledge_schema.sql` and have never been
populated by this repository.

---

## Step 8 · Do we need a knowledge layer?

**It already exists — designed, migrated and tested.** The architecture the
brief sketches is the architecture that is already here:

| The brief proposes | Already exists as |
|---|---|
| `knowledge_entities` | `knowledge.kg_entities` |
| `knowledge_relationships` | `knowledge.kg_relationships` |
| Import pipeline | `knowledge_sync/` + `scripts/run_sync.sh` |
| `knowledge_search_index` | **does not exist** — see below |

**Recommendation: do not build a new architecture.** Building a second knowledge
layer beside a complete and unused one would leave the platform with two, which
is the failure mode already recorded as backlog A1 (`public.kg_*` CMS tables vs
`knowledge.kg_*`).

The one component the brief names that genuinely does not exist is the **search
index**, and the audit found a concrete reason to want it — see
`SEARCH_PIPELINE_REPORT.md`.

---

## The three findings, ranked

**1 · The import has never run.** Nothing invoked it. Fixed in this sprint:
`.github/workflows/knowledge-sync.yml` runs it on every merge that touches the
research, weekly, and on demand. It cannot work until an operator adds three
repository secrets, and it fails loudly rather than half-running without them.

**2 · Running it will not fill the district pages.** Measured across all 61
districts:

| Incoming links | Districts |
|---|---:|
| 0 | **34** |
| 1–2 | 13 |
| 3+ | 14 |
| median | **0** |
| max | 17 (Hyderabad) |

Medak — the brief's example — has **exactly one** incoming edge. So the answer
to "why does Medak say we have not researched this yet" is **D (import never
happened) and B (relationships missing)**, in that order. Fixing D alone moves
Medak from nothing to one MSME.

**3 · Search misses content that exists.** `searchKnowledge()` runs `ilike` on
`canonical_name` and nothing else. Of the six terms the brief names, five return
results and **"Dairy" returns zero** — despite appearing in 11 package rows,
because it lives in descriptions and category names that the entity registry does
not carry.

---

## What the frontend can display without this connection

**Nothing from the packages.** Every knowledge surface reads
`lib/knowledge.js`, which reads the `knowledge` schema. Empty schema → empty
result → "This information is being prepared".

What still works without it: the opportunity marketplace, collaborator profiles,
research articles, the idea library and the editorial district narratives. All of
those are `public` tables or files in the repository, and none is package data.

---

**Companions:** `SUPABASE_SCHEMA_REPORT.md` · `PACKAGE_TO_DATABASE_MAPPING.md` ·
`SEARCH_PIPELINE_REPORT.md` · `DISTRICT_PIPELINE_REPORT.md` ·
`KNOWLEDGE_GRAPH_REPORT.md` · `IMPLEMENTATION_PLAN.md`
