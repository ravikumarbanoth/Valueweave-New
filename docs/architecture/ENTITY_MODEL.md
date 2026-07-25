# Entity Model — ValueWeave Platform v2

## The registry

647 entities across 19 populated types, extracted from 8 packages.

Every entity carries eleven fields, all mandatory and all validated:

| Field | Meaning | Check |
|---|---|---|
| `global_entity_id` | `vw:<type_slug>:<name_slug>` | G1 |
| `entity_type` | One of the registered types | G3 |
| `canonical_name` | The owning package's own name, verbatim | — |
| `source_package` | Which package owns this entity | G4 |
| `package_local_id` | The row key it was derived from | G4 |
| `status` | Registry status | G2 |
| `lifecycle_state` | One of seven states | G8 |
| `created_at` / `updated_at` | Build dates | G2 |
| `confidence_score` | Inherited from the source row, 0-100 | G9 |
| `verification_status` | Inherited from the source row | G2 |

Aliases live in a separate table (`aliases.csv`, 150 rows) rather than as a delimited
column, so alias lookup is an index rather than a scan.

## Registered types

| Type | Owner | Count | Description |
|---|---|---|---|
| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |\n| `{r['entity_type']}` | {r['owner_package'].replace('Package','P').replace('_',' ')} | {r['entity_count']} | {r['description']} |

## Identifier scheme

`vw:<entity_type_slug>:<canonical_name_slug>` — deterministic, readable, stable across
rebuilds. `vw:crop:turmeric`, `vw:skill:python-programming`,
`vw:governmentscheme:pradhan-mantri-kisan-samman-nidhi`.

Rationale and trade-offs in ADR-002. The key property is that a rebuild produces
identical ids, so a diff of `entities.csv` shows real change rather than churn.

## Cross-package sightings

When the same entity is seen in more than one package, the graph records **one node**
owned by the first package to declare it, plus a row in `cross_package_sightings.csv`
naming the other package and its local id. No duplicate node is created, and the second
sighting is not silently discarded.

## Orphans — 142 of 647 entities have no relationships

This is reported by check G10 as a **warning, not a failure**, and it is worth
understanding rather than fixing by fabrication:

| Type | Orphans | Why |
|---|---|---|
| Certification | 30 | Package006 certifications name skills in a **different vocabulary** than its own `skills.csv` — "Two-Wheeler Servicing" vs "Two-Wheeler Mechanic". No `CERTIFIED_BY` edge resolves. |
| TrainingProvider | 22 | Only 3 providers are linked to a skill by any package |
| GovernmentScheme | 21 | Schemes with no Package007 or Package008 mapping row |
| Industry | 17 | Sector labels with no member business or skill mapping |
| FinancialInstitution | 13 | Institutions not named in any scheme link |

Every one of these is a **real upstream gap**, not a graph defect. The Certification case
is the most actionable: it is a vocabulary reconciliation task inside a single package.

## What the model does not have

- **No entity attributes beyond the eleven registry fields.** Domain attributes stay in
  the owning package. Ask the graph *which* crop; ask Package005 *what season* it grows.
- **No temporal versioning.** An entity has one state, now. Historical states live in
  package version history.
- **No confidence propagation.** An entity's confidence is inherited from its source row,
  not recomputed from its edges.
