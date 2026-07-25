# Query Engine — ValueWeave Platform v2

No UI. No server. The architecture and interfaces are the deliverable, with a reference
implementation that runs so the interfaces are demonstrably real.

## Three layers

```python
GraphStore    # the ONLY class that knows the graph is in CSV
    ↓
QueryEngine   # traversal primitives, domain-agnostic
    ↓
Queries       # named business questions, domain vocabulary
```

Moving to Postgres, DuckDB or a property graph means reimplementing `GraphStore`. Nothing
above it changes. That separation is the main architectural claim of this module.

## Primitives

| Method | Purpose |
|---|---|
| `get(gid)` | Fetch one entity |
| `find(entity_type=, name_contains=, where=)` | Filter without traversing |
| `neighbours(gid, rel_type=, direction=, entity_type=)` | One hop; `direction` is `out`, `in` or `both` |
| `traverse(gid, path)` | Multi-hop along an explicit `[(rel_type, direction), …]` path |
| `shortest_path(from, to, max_hops=4)` | BFS ignoring direction |
| `rank(results, min_confidence=, sort_by=)` | Filter and sort; invents no scoring model |

`traverse` takes an **explicit** path rather than inferring one. A caller can read
exactly which edges a query walks — which matters when the answer will be shown to a
citizen making a livelihood decision.

## Provenance on every result

```python
r = queries.businesses_requiring_skill("Python")[0]
r.name                # 'Digital Marketing Agency'
r.min_confidence()    # 75  — a chain is only as strong as its weakest edge
r.provenance()
# [{'package': 'Package006_Skills_and_Training',
#   'dataset': 'skill_business_mapping.csv',
#   'row_id': '976c0303-…', 'relationship': 'REQUIRES_SKILL', 'confidence': '75'}]
```

**An answer that cannot cite its source is not an answer this platform gives.**

## The five named queries

All five run against the built graph:

| # | Question | Path |
|---|---|---|
| 1 | Businesses requiring Python | `Skill ←REQUIRES_SKILL← MSME\|BusinessOpportunity\|Industry` |
| 2 | Schemes supporting Millet Processing | `Subject →SUPPORTED_BY_SCHEME→ GovernmentScheme` |
| 3 | Skills needed for Solar EPC | `MSME →REQUIRES_SKILL→ Skill` |
| 4 | Districts suitable for Food Processing | `Industry → member MSMEs →GENERATES_EMPLOYMENT→ District` |
| 5 | AI tools used in Manufacturing | `Industry →USES_AI→ Industry` |

```bash
python3 query_engine/queries.py
```

Query 2 does not require the caller to know which package owns "Millet Processing" — the
resolver tries MSME, then Crop, then BusinessOpportunity. That is the graph earning its
place.

## Surface forms are resolved, never string-matched

Queries call `Resolver.resolve()`, which tries exact canonical, then registered alias,
then unique prefix, then conservative fuzzy — and **returns None rather than guessing**
when two candidates are equally plausible.

`"PM-KISAN"` resolves through the alias index. `"Python"` resolves by unique prefix to
`Python Programming`. `"Manufacturing"` resolves to `Manufacturing`, not
`Manufacturing (General)` — an exact full-name match beats one that only matches after
parenthetical stripping.

## Cross-package traversal

`full_business_context(name)` returns skills, schemes, machinery, raw materials, crops
processed, districts, export countries and banks for one business — spanning six packages
in one call. No single package can answer it.

## Deliberately absent

- **No query language.** A DSL is premature before the access patterns are known.
- **No caching.** 647 entities load in milliseconds.
- **No write path.** The graph is derived; writes go to packages (ADR-001).
- **No pagination or auth.** Those belong to the API layer (`API_VISION.md`).
