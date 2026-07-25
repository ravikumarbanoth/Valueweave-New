# ValueWeave Platform v2 — Knowledge Graph Foundation

**Version 2.0.0 · Released 2026-07-25 · Validation PASS (0 violations, 10 checks)**

The architectural layer above the eight Stable packages. Not a package — it creates no
domain knowledge and owns no facts.

| | |
|---|---|
| Entities | 647 across 19 types |
| Relationships | 865 across 15 populated types |
| Connectivity | 78.05% (142 orphans, all traceable to upstream gaps) |
| Sources tracked | 605 URLs across 469 organisations |
| Ownership | 19 owned types, 99 enforceable attributes, 5 declared overlaps |
| ADRs | 6 (2 open) |
| Human review | **None. Every row is `VST-NEEDS_REVIEW`.** |

## Run it

```bash
python3 knowledge_graph/build_graph.py              # extract from 8 packages
python3 knowledge_graph/ownership/build_ownership.py
python3 knowledge_graph/validate_graph.py           # 10 checks, exit 0 required
python3 knowledge_graph/resolution/resolver.py      # merge proposals
python3 source_registry/build_source_registry.py
python3 query_engine/queries.py                     # the 5 named queries
```

Order matters — the validator reads the ownership registry, so ownership builds first.

## Layout

```
knowledge_graph/
├── entities/          Global Entity Registry + types + aliases + cross-package sightings
├── relationships/     Global Relationship Graph + types + unresolved endpoints
├── ownership/         Single-source-of-truth registry + declared overlaps
├── resolution/        Entity Resolution Engine + pending merge proposals
├── build_graph.py     extraction from the 8 packages
└── validate_graph.py  10 checks (G1-G10)

query_engine/
├── engine.py          GraphStore / QueryEngine / Result
└── queries.py         the named business questions

source_registry/       605 sources with trust score and re-collection cadence
governance/            policy, stewardship lifecycle, 6 ADRs
docs/architecture/     10 architecture documents
```

## Start here

| Document | For |
|---|---|
| `docs/architecture/SYSTEM_ARCHITECTURE.md` | How the layers fit together |
| `docs/architecture/KNOWLEDGE_GRAPH.md` | What the graph is and what it revealed |
| `docs/architecture/OWNERSHIP_POLICY.md` | Who owns what, and how it is enforced |
| `governance/DATA_GOVERNANCE.md` | The rules, each marked enforced or not |
| `docs/architecture/ROADMAP_V2.md` | What is next and what is deliberately not |

## Two things to know before building on this

**1. The graph is derived (ADR-001).** It creates nothing. To add a fact, add it to the
owning package and rebuild. Every entity and edge traces to a specific package row, and
check G4 verifies those references actually resolve.

**2. Nothing has been human-reviewed.** All 647 entities and all 2,269 underlying package
rows carry `VST-NEEDS_REVIEW`. Machine validation confirms structure, references,
provenance and ownership — it confirms no fact. This is the largest gap in the platform
and no amount of further engineering closes it.

## Open decisions

| ADR | Issue | Status |
|---|---|---|
| ADR-003 | Six packages hold government scheme data; copies will drift | **Open — decision required** |
| ADR-006 | `knowledge_engine/` contains no tracked source files | **Open — recovery required** |
