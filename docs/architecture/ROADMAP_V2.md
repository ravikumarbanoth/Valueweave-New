# Roadmap — ValueWeave Platform v2 and beyond

## Where the platform is

```
Package Repository  ──►  Knowledge Repository  ──►  Knowledge Graph  ──►  Recommendation
     (v1, done)            (v1, 8 packages)          (v2.0.0, DONE)       (designed only)
                                                            │
                                                            ▼
                                            Decision Support  ──►  AI-ready infrastructure
                                              (not started)          (not started)
```

**v2.0.0 delivers the third box.** The fourth is designed and deliberately unbuilt.

## Delivered in v2.0.0

| Module | Delivered |
|---|---|
| 1 Global Entity Registry | 647 entities, 19 types, deterministic ids |
| 2 Relationship Registry | 865 edges, 19 types, provenance per edge |
| 3 Ownership Registry | 19 owned types, 99 enforceable attributes, 5 declared overlaps |
| 4 Entity Resolution | Alias, canonical naming, duplicate detection, cross-package linking |
| 5 Query Engine | 3-layer architecture, 5 named queries, provenance on every result |
| 6 Recommendation Engine | **Design only**, as specified |
| 7 Source Registry | 605 sources, 469 organisations, trust and cadence |
| 8 Data Governance | 6 ADRs, governance and stewardship docs |
| 9 Data Stewardship | 7-state lifecycle, validated by G8 |
| 10 Documentation | 10 architecture documents |

Plus a 10-check graph validator that generalises Package008's ownership rule to all eight
packages.

## v2.1 — close the gaps the graph exposed

Ordered by value per unit of effort.

| # | Item | Effort | Why it is first |
|---|---|---|---|
| 1 | **Fix Package006 certification vocabulary** | Low | 30 orphan entities, `CERTIFIED_BY` at zero edges. Aligning `related_skill_names` with `skills.csv` is a one-package change that adds ~30 edges and removes 30 orphans. |
| 2 | **Human review of the ~170 core rows** | High | 40 MSMEs, 40 schemes, 45 crops, 45 skills carry most connectivity. This is the gate on everything downstream. |
| 3 | **Decide ADR-003** (scheme ownership) | Decision | Six packages hold scheme data; copies will drift. |
| 4 | **Recover `knowledge_engine/`** (ADR-006) | Unknown | No tracked source files exist. Weakens every package's reproducibility claim. |
| 5 | **Link training providers to skills** | Medium | 22 orphan providers; `TRAINED_BY` has 3 edges. |
| 6 | **Structured scheme predecessor links** | Medium | Would populate `SUCCESSOR_OF` / `PREDECESSOR_OF`, currently zero. |
| 7 | **Country reference dataset in Package001** | Low | Turns 29 parsed `ExportCountry` entities into real foreign keys. |

Target: connectivity above 85% (from 78.05%), zero open ADRs.

## v2.2 — make the graph queryable at scale

- Replace the `GraphStore` CSV implementation with DuckDB or Postgres. **Only that class
  changes** — the separation is already in place.
- Graph metrics: centrality to find the entities most worth reviewing first.
- Incremental rebuild rather than full extraction.

## v3.0 — recommendation, once its preconditions hold

Blocked on v2.1 items 1-3 plus some outcome signal. `RECOMMENDATION_ENGINE.md` states the
four preconditions and why building before them would produce a system that looks
authoritative and is not.

Interim: ship **explained traversal** (`full_business_context`, already working) rather
than scored ranking.

## v4.0 — API and AI surface

Blocked on human review above all. `API_VISION.md` lists seven requirements; the first
three are done, and items 4-6 gate whether the data should be exposed at all.

## Deliberately not on the roadmap

| Not doing | Why |
|---|---|
| Package009 and beyond | The brief is explicit; the gap is depth, not breadth |
| Inferred edges | The graph is derived (ADR-001); inference is fabrication |
| Automatic entity merging | ADR-004 |
| Confidence recomputation from graph structure | A well-connected wrong fact is still wrong |
| A query DSL | Premature before access patterns are known |

## The honest summary

The architecture is sound and every layer runs. What the platform lacks is not
engineering — it is **647 entities and 2,269 package rows that no human has
verified**, and a decision about who owns scheme data.

Both are cheap relative to what has been built, and everything downstream depends on
them.
