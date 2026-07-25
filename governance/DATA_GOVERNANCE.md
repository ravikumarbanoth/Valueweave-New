# Data Governance — ValueWeave Platform v2

The rules that keep eight independently-released packages coherent as one knowledge
graph. Every rule here is either enforced by a check or explicitly marked as unenforced.

**Enforcement status is stated on every rule.** A governance document whose rules nothing
checks is a wish list.

## 1. Entity naming rules

| Rule | Enforced by |
|---|---|
| `global_entity_id` matches `vw:<entity_type_slug>:<canonical_name_slug>` | G1 |
| The id prefix matches the row's `entity_type` | G1 |
| `entity_type` is one of the 19 registered types | G3 |
| Canonical name is the owning package's own name for the entity, verbatim | Not enforced — extraction convention |
| Alternate surface forms are registered as aliases, never as new entities | Not enforced — reviewed at merge proposal |

Slug normalisation: ASCII fold, lowercase, `&` to `and`, non-alphanumerics to hyphens,
80-character cap. See ADR-002.

## 2. Ownership rules

| Rule | Enforced by |
|---|---|
| Each entity type has exactly one owner package | `ownership_registry.csv` |
| A non-owner may hold a foreign key to an owned entity | G7 (allows) |
| A non-owner may hold a denormalised name beside that key | G7 (allow-list) |
| A non-owner may NOT publish an owned distinctive attribute | **G7 (fails build)** |
| Known duplication must be declared in `known_overlaps.csv` with an ADR | **G7 (undeclared fails, declared warns)** |

Only *distinctive* attributes are enforceable. Generic column names (`jurisdiction`,
`ownership`, `established_year`, `capacity`, `risk_level`) are excluded — see ADR-005.

## 3. Validation rules

Graph checks, all run by `knowledge_graph/validate_graph.py`:

| Check | Enforces |
|---|---|
| G1 | Entity identity: unique, well-formed, type-consistent |
| G2 | All 11 registry fields present and non-empty |
| G3 | Entity type is registered |
| G4 | `package_local_id` actually exists in the claimed package |
| G5 | Both edge endpoints exist; no self-loops |
| G6 | Edge type registered; endpoints match declared types |
| G7 | Ownership — undeclared attribute duplication fails |
| G8 | `lifecycle_state` is a registered state |
| G9 | Confidence is an integer 0-100 |
| G10 | Orphan report (warning, not failure) |

Package-level validation remains each package's own responsibility. Package008 runs 13
checks, Package007 runs 12, Package005 runs 10. The graph does not re-run them.

## 4. Data steward roles

| Role | Responsibility | Currently assigned |
|---|---|---|
| **Package Steward** | Owns one package: accuracy, currency, release | **None** |
| **Graph Steward** | Owns entity resolution decisions and merge proposals | **None** |
| **Ownership Arbiter** | Decides contested ownership; owns ADR-003 | **None** |
| **Source Steward** | Owns the source registry and re-collection cadence | **None** |

**No role is filled.** All 647 entities and every package row carry
`VST-NEEDS_REVIEW`. Nothing in this knowledge base has had human sign-off. This is the
single largest quality gap in the platform and no amount of machine validation closes it.

## 5. Review workflow

```
Contributor change
   -> package validation (package's own checks)
   -> graph rebuild + validate_graph.py
   -> if G7 flags undeclared duplication: declare it with an ADR, or reference instead
   -> if merge_proposals.csv changes: Graph Steward decides accept / reject
   -> review
   -> merge to main
```

Merge proposals are never auto-applied (ADR-004).

## 6. Version policy

| Layer | Scheme | Immutable once released |
|---|---|---|
| Package | `PackageNNN_Domain_vMAJOR.MINOR.PATCH` | Yes |
| Graph | `vMAJOR.MINOR.PATCH`, currently 2.0.0 | Regenerated, not versioned in place |

Graph version bumps:

- **Patch** — rebuild against unchanged packages; entity and edge counts stable
- **Minor** — a package minor release adds entities or edges; new entity or relationship type registered
- **Major** — identifier scheme change, entity type removal, or ownership reassignment

## 7. Deprecation policy

Entities are never deleted. They transition to `ARCHIVED` (see lifecycle below) and
retain their `global_entity_id` so external references keep resolving. A superseded
entity should carry a `SUCCESSOR_OF` edge to its replacement — the relationship type is
registered for this purpose and currently carries zero edges, because scheme renames are
recorded as prose in package `notes` rather than structured links.

## 8. Contribution guide

To add a fact to the knowledge graph, **add it to the owning package**. The graph is
derived (ADR-001) and creates nothing.

1. Identify the owner in `knowledge_graph/ownership/ownership_registry.csv`
2. Add the row to that package, with full provenance
3. Run the package's own validator
4. Rebuild: `python3 knowledge_graph/build_graph.py`
5. Validate: `python3 knowledge_graph/validate_graph.py`
6. If G7 fails, you have restated an attribute someone else owns — reference their id

## 9. Release process

```bash
python3 knowledge_graph/build_graph.py            # extract entities + relationships
python3 knowledge_graph/ownership/build_ownership.py
python3 knowledge_graph/validate_graph.py         # 10 checks; exit 0 required
python3 knowledge_graph/resolution/resolver.py    # refresh merge proposals
python3 source_registry/build_source_registry.py
python3 query_engine/queries.py                   # smoke-test the named queries
```

Order matters: the validator reads the ownership registry, so ownership builds first.

## 10. Current governance state, stated plainly

| Item | State |
|---|---|
| Graph validation | PASS, 0 violations across 10 checks |
| Entities | 647 across 19 types |
| Relationships | 865 across 15 types |
| Connectivity | 78.05% (142 orphans) |
| Sources tracked | 605 across 469 organisations |
| Open ADRs | ADR-003 (scheme ownership), ADR-006 (missing engine) |
| Pending merge proposals | 1 |
| Stewards assigned | 0 |
| Rows with human sign-off | 0 |
