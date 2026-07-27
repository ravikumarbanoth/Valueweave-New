# Graph Compiler Report

**`knowledge_graph/build_graph.py` analysed completely** · 839 lines · commit `2e86f4e`

No package data, frontend or graph output was modified. One test file was added
(`tests/test_graph_compiler.py`) and registered — Workstream 6's explicit deliverable.

---

## 0. Headline

**Coverage is 39 of 77 datasets, not 42.** The brief's figure and my own Phase 2 figure
were both wrong, in opposite directions:

| Source | Claimed | Why it was wrong |
|---|---:|---|
| Phase 2 report | 35 / 77 | Missed Package004's four **dynamically** loaded datasets |
| This mission's brief | 42 / 77 | — |
| **Measured** | **39 / 77** | 35 literal `read()` paths + 4 from the `P4_FILES` loop |

A checker that only greps for string literals reports Package004 as unread. The new
regression test parses **both** loading styles, which is why its manifest can be trusted
where the earlier count could not.

### The three findings that matter

> **1 · The compiler has no dataset registry.** Every dataset is a hardcoded `read()` in
> the script body. Adding a dataset means editing 839 lines of procedural code, and
> forgetting to is invisible — nothing in the build output, the graph summary or the test
> suite said 38 datasets were being skipped.
>
> **2 · The `UNRESOLVED` diagnostic is correct, and four call sites defeat it.**
> `edge()` logs every unresolvable endpoint. Four callers pre-check with `and E(...)`,
> so `edge()` is never reached and nothing is logged. That is the entire explanation for
> 27 silently-lost mappings — not a missing mechanism, a bypassed one.
>
> **3 · `CERTIFIED_BY` is not an unused type — it is a producer that fails 100% of the
> time.** 122 attempts, 0 edges, all 122 logged with a diagnostic the author wrote
> explaining exactly why. My Phase 2 report called it "registered but no producer." It
> has a producer; the producer cannot resolve its inputs.

---

## 1. Architecture as it stands

```
839 lines, module-level procedural. Three phases execute at import.

lines  39– 133   Configuration   OWNER (19 types), ENTITY_TYPE_DESC,
                                 RELATIONSHIP_TYPE_DESC (19 types)
lines 135– 267   Helpers         slug(), read(), maybe(), Registry, edge(),
                                 conf(), vst()
lines 270– 422   PHASE 1         Entities — one hardcoded block per package
lines 425– 752   PHASE 2         Relationships — one hardcoded block per shape
lines 755– 839   PHASE 3         Write 8 output files + graph_summary.json
```

### What is well built

| | |
|---|---|
| **Entity identity** | `vw:<type_slug>:<name_slug>`, deterministic, stable across rebuilds |
| **Entity de-duplication** | `Registry` keys on `(type, slug)`; a second sighting becomes provenance, not a duplicate node. **This is why there are 0 duplicate entities** |
| **Edge de-duplication** | `EDGE_KEYS` on `(from, type, to)`. **This is why there are 0 duplicate edges** |
| **Closed type sets** | An unregistered entity or relationship type aborts the build. `sys.exit`, not a warning |
| **Sentinel discipline** | `conf()` and `vst()` treat `PENDING_VERIFICATION` as absent rather than as data |
| **Unresolved logging** | `edge()` appends to `UNRESOLVED` instead of dropping — the design is right |

**The compiler is not sloppy.** Every structural invariant the Phase 2 validation checked
— no duplicates, no self-loops, no dangling endpoints, no unregistered types — holds *by
construction* because of the four rows above.

### What is missing

| # | Gap | Consequence |
|---|---|---|
| **A1** | **No dataset registry** | 38 datasets skipped with no signal anywhere |
| **A2** | **Procedural, executes at import** | No builder can be unit-tested in isolation; `import build_graph` rebuilds the graph |
| **A3** | **No coverage metric** | `graph_summary.json` reports entities and edges, never *datasets read* |
| **A4** | **`read()` is fatal** | 35 hard dependencies; renaming any dataset kills the build with `sys.exit` |
| **A5** | **No attribute channel** | A dataset can contribute an entity or an edge. `eligibility_criteria.csv` (55 rows) can contribute neither, so it is unreachable by design |
| **A6** | **Metrics are `print()`** | Per-shape counts are human-readable and machine-invisible |

**A5 is the one that blocks the 77/77 goal**, and §4 addresses it.

---

## 2. The four bypassed guards — exact locations

`edge()` logs an unresolvable endpoint:

```python
def edge(rtype, from_id, to_id, ...):
    if not from_id or not to_id:
        UNRESOLVED.append({... "reason": "endpoint did not resolve ..."})
        return
```

Four callers make sure it never sees one:

| Line | Guard | Dataset | Rows lost, unlogged |
|---:|---|---|---:|
| 450 | `if d and d != PV and E("District", d):` | `universities…csv` | 8 |
| **505** | `if sk and opp and E("BusinessOpportunity", opp):` | `skill_business_mapping.csv` | **27** |
| 541 | `if sn and opp and E("BusinessOpportunity", opp):` | `industry_scheme_mapping.csv` | ~5 |
| 692 | `if catname and E("Industry", catname):` | `education_support_mapping.csv` | ~4 |

Roughly **44 mapping rows fail to join and are recorded nowhere.**
`unresolved_endpoints.csv` holds 132 rows, all from call sites that pass through
`edge()` — so the file **looks complete** while missing about a quarter of the real
failures.

**A failure log that is partially complete is worse than none**, because its
completeness is the only reason to consult it. The fix is to delete four guards and let
`edge()` do the job it already does — a subtractive change, verifiable by the
`unresolved_endpoints.csv` row count rising from 132 to ~176 with the emitted edge count
unchanged.

### The contrast that proves the point

Line 659 does it correctly:

```python
sid = E("Skill", part)
if sid:
    edge("CERTIFIED_BY", sid, ...)
else:
    UNRESOLVED.append({... "reason": "Package006 certifications use descriptive skill
                       labels rather than the canonical skill_name vocabulary ..."})
```

All 122 failures logged, each with a written explanation. **The author knew.** The same
care applied at four other sites would have made the `skill_business_mapping` loss
visible from the first build.

---

## 3. Diagnostics (Workstream 5)

### 3.1 Unused foreign keys — 21 populated, 1 empty

Columns in **consumed** datasets that look like foreign keys and are never read:

| Populated | Dataset | Column | Opportunity |
|---:|---|---|---|
| **40/40** | `msme_businesses.csv` | `business_model_id` | **`BusinessModel`: 15 entities + 40 edges** |
| **40/40** | `msme_businesses.csv` | `business_model_name` | ↑ |
| 32/32 | `district_business_mapping.csv` | `package001_dist_id` | Stronger key than the name currently used |
| 14/14 | `agriculture_business_mapping.csv` | `package005_processing_opportunity_id` | Joins `agri_processing_opportunities.csv` **14/14** |
| 13/13 | `education_support_mapping.csv` | `entity_name` | |
| 12/14 | `agriculture_scheme_mapping.csv` | `package005_scheme_id` / `_name` | ADR-003 domain schemes |
| 12/12 | `industry_scheme_mapping.csv` | `package004_dataset` | |
| 9/12 | `skill_scheme_mapping.csv` | `package006_scheme_id` / `_name` | |
| 4/12 | `skill_scheme_mapping.csv` | `package006_certification_id` / `_name` | Second route to `CERTIFIED_BY` |
| 3/12 | `skill_scheme_mapping.csv` | `package006_provider_name` | |
| 10/64 | `machinery_mapping.csv` | `package005_machinery_name` | |
| 10/10 | `ai_precision_agriculture.csv` | `technology_name` | |
| 1/2 | `state.csv` | `industrial_policy_name` | |
| **0/61** | `district.csv` | `primary_industry_sector_id` | **Empty — correctly ignored** |

**`business_model_id` at 40/40 is the best of these.** `business_models.csv` (15 rows,
ignored) joins perfectly: *Manufacturing Unit · Job Work / Ancillary Unit · Trading
Business · Service Centre · Cloud Kitchen · Cold Storage · Warehouse and Distribution.*
A new entity type, 15 entities, 40 edges, from two files already in the repository.

**`district.primary_industry_sector_id` is the useful negative.** It is exactly the
`Industry → District` key that would revive `RI3-VIA_DISTRICT`, and it is **0 of 61
populated**. The builder is right to skip it, and a diagnostic that flagged it without
checking population would have sent someone on a two-day chase. **An unused FK column is
only a finding once it is known to hold data.**

### 3.2 Duplicate entity builders — none

`Registry.add()` keys on `(entity_type, slug(canonical_name))`. A second producer of the
same entity appends to `collisions` and writes `cross_package_sightings.csv`. Multiple
call sites can produce the same node safely, by design.

### 3.3 Relationship conflicts — none

`EDGE_KEYS` on `(from, type, to)`. Two datasets asserting the same edge yield one row,
first writer winning the provenance. **Worth flagging for Phase 2's Wave 1**: R5
(`agri_business_mapping`) and the repaired M1 path both emit
`BusinessOpportunity -REQUIRES_SKILL-> Skill`. The de-duplication is silent, so the
second source's provenance is discarded without a note.

### 3.4 Unreachable datasets — 55 rows that no channel can carry

`eligibility_criteria.csv` (55), `scheme_benefits.csv` (51), `application_process.csv`
(43), `required_documents.csv` (15) describe **properties of a scheme**, not links
between entities. The compiler emits entities and edges only, so these are unreachable
however they are registered.

**This is the architectural blocker to 77/77**, not an oversight — see §4.

### 3.5 Ignored CSV files — 38

36 populated, 2 header-only (`mandal.csv`, `revenue_division_andhra_pradesh.csv`).
Full classification in `DATASET_COVERAGE.md`; per-dataset registration specs in
`BUILDER_REGISTRY.md`.

---

## 4. Reaching 77/77 needs a third contribution channel

The goal as stated cannot be met by registration alone, and the reason is worth being
precise about rather than quietly redefining the target.

| Channel | Exists | Datasets it can carry |
|---|:---:|---:|
| **Entity** | ✅ | ~30 |
| **Relationship** | ✅ | ~28 |
| **Attribute** — enrich an existing node | ❌ | **~19** |

Nineteen datasets carry per-entity detail and no relationship:
eligibility, benefits, application process, required documents, investment figures,
licence and compliance, AI-impact scoring, career paths.

**They are the most useful content in the repository for an actual user** — a scheme
recommendation is far more actionable with its eligibility rule and application channel
attached — and the compiler has no way to attach them.

**`COMPILER_ARCHITECTURE.md` §4 specifies the attribute channel.** With it, 77/77 is
reachable and honest: every dataset contributes an entity, an edge, or an attribute.
Without it, the ceiling is ~58/77 and the remaining 19 would have to be registered as
no-ops to hit the number — which would make the metric a lie.

**Revised target: 77/77 with three channels, of which ~19 are attribute-only.**

---

## 5. Regression protection — implemented

`tests/test_graph_compiler.py` · **11 tests** · registered in `run_all.py` ·
suite now **458**.

| Group | Protects |
|---|---|
| `DatasetRegistrationTest` | **A new dataset must be registered.** Fails on any CSV in `packages/*/datasets/` absent from the manifest; also catches stale entries and overlapping sets |
| `ManifestFidelityTest` | The manifest must match the builder — parses `build_graph.py` for **both** literal and `P4_FILES` loading, and verifies `EMPTY` files are still empty |
| `CoverageTest` | Coverage floor of 39; the set of silent packages is pinned to `Package003_Healthcare` |
| `CompilerInvariantTest` | `edge()` still logs unresolved endpoints; type sets stay closed; edges stay de-duplicated |

**Verified to fail for the right reason.** Dropping an unregistered CSV into
`Package008_MSME/datasets/` produces:

```
AssertionError: dataset(s) present in packages/ but absent from the compiler registry
  Package008_MSME/datasets/__probe_new_dataset.csv
```

and the suite returns to green when it is removed. A guard that has never been seen to
fail is a guard nobody should trust.

`test_consumed_manifest_matches_the_builder_source` is the one that keeps the rest
honest: it is what would have caught the 35-vs-39 error in my own Phase 2 report.

---

## 6. Recommendations, in order

| # | Change | Effort | Why first |
|---|---|---:|---|
| **1** | **Delete the four bypass guards** | **1 h** | Subtractive. Makes ~44 hidden failures visible before anything is added |
| **2** | Extract the `DATASETS` registry | 4 h | Turns "add a dataset" from an 839-line edit into a table row |
| **3** | Add the attribute channel | 6 h | Unblocks 19 datasets and the 77/77 goal |
| **4** | Wrap phases in functions; guard `__main__` | 3 h | Makes builders unit-testable |
| **5** | Emit `dataset_coverage.json` | 2 h | Coverage becomes a build output, not an audit finding |
| **6** | Register the 36 ignored datasets | 3 d | The actual work, safe only after 1–5 |

**Change 1 before change 6, without exception.** Registering 36 datasets into a compiler
that hides a quarter of its join failures means every new failure is as invisible as the
last — and `unresolved_endpoints.csv` will still look complete.

### One refactor risk worth naming

`build_graph.py` executes at import, so `tests/test_graph_integrity.py` and the
idempotency test both depend on running it as a script. Wrapping the phases in functions
(change 4) must keep `python3 knowledge_graph/build_graph.py` byte-identical in output.
**The acceptance test is a rebuild producing an identical graph modulo `BUILD_DATE`** —
`COMPILER_ARCHITECTURE.md` §7 specifies it, and no refactor should be merged without it.

---

**Companion documents:** `DATASET_COVERAGE.md` · `BUILDER_REGISTRY.md` ·
`COMPILER_ARCHITECTURE.md` · `REGRESSION_TEST_PLAN.md`
