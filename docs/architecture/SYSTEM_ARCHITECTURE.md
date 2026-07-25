# System Architecture — ValueWeave Platform v2

## The shape of the system

```
                        ┌──────────────────────────────┐
                        │   Future: API / AI surface   │   not built (see API_VISION.md)
                        └──────────────┬───────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
┌───────▼────────┐          ┌──────────▼─────────┐        ┌───────────▼──────────┐
│  query_engine/ │          │ Recommendation     │        │  source_registry/    │
│  traversal +   │          │ Engine (DESIGN     │        │  605 sources        │
│  named queries │          │ ONLY, not built)   │        │  469 organisations   │
└───────┬────────┘          └──────────┬─────────┘        └──────────────────────┘
        │                              │
        └──────────────┬───────────────┘
                       │
        ┌──────────────▼───────────────────────────────────┐
        │            knowledge_graph/                      │
        │  entities/        647 entities, 19 types          │
        │  relationships/   865 edges, 19 types             │
        │  ownership/      19 owned types, 5 declared overlaps│
        │  resolution/     alias + duplicate detection      │
        └──────────────────────┬───────────────────────────┘
                               │  DERIVED — creates nothing (ADR-001)
        ┌──────────────────────▼───────────────────────────┐
        │        packages/  — 8 Stable v1.0.0 packages     │
        │  P001 Geography      P005 Agriculture            │
        │  P002 Education      P006 Skills & Training      │
        │  P003 Healthcare     P007 Government Schemes     │
        │  P004 Industries     P008 MSME                   │
        │        ← SINGLE SOURCE OF TRUTH lives here →     │
        └──────────────────────────────────────────────────┘
                               ▲
        ┌──────────────────────┴───────────────────────────┐
        │   knowledge_engine/  — ABSENT (see ADR-006)      │
        │   No tracked source files in this repository.    │
        │   Treated as a contract, not a dependency.       │
        └──────────────────────────────────────────────────┘
```

## Layer responsibilities

### Packages — the source of truth

Eight Stable packages, each owning a domain, each self-validating (10 to 13 checks
apiece), each carrying six mandatory provenance columns on every row. Nothing above this
layer may assert a domain fact.

### Knowledge graph — derived integration

Extracts entities and relationships **from** the packages. Every entity carries
`source_package` and `package_local_id`; every edge carries
`provenance_package`, `provenance_dataset` and `provenance_row_id`. Check G4 verifies
that claimed local ids actually exist upstream.

Rebuild is idempotent: same input, same output, same identifiers (ADR-002).

### Query engine — traversal

Three layers, deliberately separated:

| Layer | Knows about | Replaceable by |
|---|---|---|
| `GraphStore` | That the graph is in CSV | A Postgres / DuckDB / property-graph implementation |
| `QueryEngine` | Graph topology only | — |
| `queries.py` | Domain vocabulary | — |

Moving to a real database means reimplementing `GraphStore` and nothing else.

### Source registry — collection inventory

605 distinct source URLs extracted from package citations, with trust score and
re-collection cadence derived from what each source actually publishes. `collector` and
`parser` are `PENDING_IMPLEMENTATION` on every row — see the next section.

## The Knowledge Engine gap

Platform v2 was specified on the premise that the Knowledge Engine is implemented.
**`knowledge_engine/` contains no tracked source files** — only `__pycache__`
directories whose names match the eight specified modules.

Consequences, and how v2 is designed around them:

- **No v2 component imports from it.** The graph builder, resolver, query engine and
  validators read package CSVs directly.
- **The source registry records the absence** rather than inventing module paths.
- **It is treated as a contract:** this document describes where it fits and what it
  must provide. When it is recovered or rebuilt, it slots in beneath the packages
  without changing anything above them.

See `governance/adr/ADR-006`.

## Data flow, end to end

```
external source
  → [collector]           ← ABSENT
  → [parser]              ← ABSENT
  → package CSV           ← 8 packages, validated, provenance-complete
  → build_graph.py        → entities.csv + relationships.csv
  → validate_graph.py     → 10 checks, exit 0 required
  → GraphStore            → QueryEngine → named queries
  → [API]                 ← NOT BUILT (API_VISION.md)
```

Two of the five stages are missing. Both are named rather than glossed.

## What runs today

```bash
python3 knowledge_graph/build_graph.py             # 647 entities, 865 edges
python3 knowledge_graph/ownership/build_ownership.py
python3 knowledge_graph/validate_graph.py          # PASS, 0 violations
python3 knowledge_graph/resolution/resolver.py     # 1 merge proposal
python3 source_registry/build_source_registry.py   # 605 sources
python3 query_engine/queries.py                    # 5 named queries + traversals
```

## Design decisions

| Decision | ADR |
|---|---|
| The graph is derived, not authored | ADR-001 |
| Deterministic slug identifiers | ADR-002 |
| Scheme ownership across six packages — **OPEN** | ADR-003 |
| Resolution proposes, never merges | ADR-004 |
| Declared overlaps are governed; undeclared are violations | ADR-005 |
| The Knowledge Engine is absent | ADR-006 |
