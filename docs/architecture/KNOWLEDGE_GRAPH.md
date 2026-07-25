# Knowledge Graph — ValueWeave Platform v2

## What it is

647 entities and 865 relationships extracted from eight Stable packages. It
creates no domain knowledge (ADR-001) — every node and edge points back at the package
row it came from.

```
Citizen profile
   ↓
Skill ──REQUIRES_SKILL── MSME ──SUPPORTED_BY_SCHEME── GovernmentScheme
   │                      │  │                              │
TRAINED_BY          PROCESSES │ USES_MACHINERY          FUNDED_BY
   │                      │  │        │                     │
TrainingProvider        Crop │    Machinery        FinancialInstitution
                             │
                   GENERATES_EMPLOYMENT
                             │
                          District ──LOCATED_IN── State ──LOCATED_IN── Country
```

## Build and validate

```bash
python3 knowledge_graph/build_graph.py             # extract
python3 knowledge_graph/ownership/build_ownership.py
python3 knowledge_graph/validate_graph.py          # 10 checks, exit 0 required
python3 knowledge_graph/resolution/resolver.py     # merge proposals
```

Idempotent: same packages in, same graph and same identifiers out.

## Current state

| Metric | Value |
|---|---|
| Entities | 647 |
| Relationships | 865 |
| Entity types | 19 populated / 19 registered |
| Relationship types | 15 populated / 19 registered |
| Connectivity | 78.05% (142 orphans) |
| Validation | PASS, 0 violations |
| Unresolved endpoints logged | 132 |
| Pending merge proposals | 1 |

## What the graph revealed that no package could

Building it surfaced five things that were invisible from inside any single package:

**1. Package006's certification vocabulary does not match its own skill vocabulary.**
`certifications.related_skill_names` contains "Two-Wheeler Servicing" where `skills.csv`
says "Two-Wheeler Mechanic". Result: `CERTIFIED_BY` has zero edges and all 30
certifications are orphans. A single-package validator cannot see this because both
columns are internally valid.

**2. `Agriculture & Allied` and `Agriculture and Allied` were two nodes.** Package005 and
Package008 spell the same industry differently. The query "AI tools used in Agriculture"
silently returned nothing until slug normalisation collapsed them.

**3. Package002 has carried an unused `district` column all along.** No package linked
universities to geography. The graph turned it into 66 `LOCATED_IN` edges.

**4. Six packages hold scheme data with no reconciliation.** Known before, but the graph
makes the cost concrete: a scheme benefit updated in Package007 leaves five copies stale
with nothing detecting it. See ADR-003.

**5. 142 entities have no relationships at all** — 30 certifications, 22 training
providers, 21 schemes, 17 industries. Each is a real upstream gap, now enumerable.

## Reading the sparsity honestly

78.05% connectivity is not a defect to hide. The graph is derived, so it can only be as
connected as the packages are. Every orphan is a specific, addressable upstream gap
rather than a mystery, and `relationships/unresolved_endpoints.csv` names 132 cases
where a mapping row exists but its endpoint does not resolve, with the reason for each.

A denser graph would require either enriching packages (correct) or inferring edges
(fabrication).

## Files

| Path | Contents |
|---|---|
| `entities/entities.csv` | The Global Entity Registry |
| `entities/entity_types.csv` | 19 registered types with owner and count |
| `entities/aliases.csv` | 150 alternate surface forms |
| `entities/cross_package_sightings.csv` | Same entity seen in more than one package |
| `relationships/relationships.csv` | The Global Relationship Graph |
| `relationships/relationship_types.csv` | 19 registered edge types |
| `relationships/unresolved_endpoints.csv` | Mapping rows whose endpoints do not resolve, with reasons |
| `ownership/` | Ownership registry, attribute ownership, declared overlaps |
| `resolution/` | Resolver and pending merge proposals |
