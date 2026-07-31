# Knowledge Graph Report

**ValueWeave v1.0 · does the graph exist in production?**

---

## Answer

**In Git: yes, completely. In production: no, not one row.**

| | Git | Production |
|---|---:|---|
| Entities | **647** | 0 |
| Relationships | **865** | 0 |
| Entity types | 19 | — |
| Relationship types | 15 | — |
| Provenance on every edge | yes | — |

---

## How it is stored

**In Git — two CSV files, built deterministically.**

```
packages/*/datasets/*.csv
        │  knowledge_graph/build_graph.py
        ▼
knowledge_graph/entities/entities.csv        647 rows
knowledge_graph/relationships/relationships.csv   865 rows
```

Entity ids are `vw:<type>:<name-slug>` — `vw:district:medak`,
`vw:skill:welding`. Deterministic, so a URL slug reconstructs an id with no
lookup, which is why detail pages need one query rather than two.

`validate_graph.py` runs 11 structural checks on every build.

**In production — two tables that have never been filled.**

`knowledge.kg_entities` and `knowledge.kg_relationships`, declared by
`knowledge_sync/migrations/001_knowledge_schema.sql`, with soft-delete
(`sync_deleted_at`), provenance columns and no write policy at all. Correct, and
empty.

---

## Entity types

| Type | Count | Reachable at |
|---|---:|---|
| Industry | 78 | `/knowledge?type=industry` |
| Machinery | 69 | `?type=machinery` |
| Institution | 66 | `?type=institution` |
| District | 61 | `?type=district` |
| BusinessOpportunity | 45 | `?type=business` |
| Crop | 45 | `?type=crop` |
| Skill | 45 | `?type=skill` |
| GovernmentScheme | 40 | `?type=scheme` |
| MSME | 40 | `?type=msme` |
| Certification | 30 | `?type=certification` |
| ExportCountry | 29 | `?type=export` |
| TrainingProvider | 25 | `?type=provider` |
| FinancialInstitution | 21 | `?type=bank` |
| RawMaterial | 21 | `?type=material` |
| Market | 11 | `?type=market` |
| Soil | 10 | `?type=soil` |
| ClimateZone | 8 | `?type=climate` |
| State | 2 | `?type=state` |
| Country | 1 | `?type=country` |

All 19 have a route. Five of them did not until the previous sprint.

---

## Relationship types — and the two that are missing

| Type | Edges |
|---|---:|
| RELATED_TO | 190 |
| LOCATED_IN | 121 |
| SUPPORTED_BY_SCHEME | 92 |
| PART_OF | 90 |
| REQUIRES_SKILL | 86 |
| EXPORTS_TO | 68 |
| USES_MACHINERY | 64 |
| SUPPORTED_BY_BANK | 36 |
| USES_RAW_MATERIAL | 33 |
| GENERATES_EMPLOYMENT | **32** |
| USES_AI | 16 |
| SELLS_TO | **12** |
| FUNDED_BY | 12 |
| PROCESSES | 10 |
| TRAINED_BY | **3** |

The three in bold are the platform's ceiling:

* **`GENERATES_EMPLOYMENT` — 32 edges across 61 districts.** This is the edge
  `getDistrictKnowledge()` traverses. 34 districts have none.
* **`TRAINED_BY` — 3 edges.** The "Skills to learn" rail and every training
  section are near-empty for almost everybody.
* **`SELLS_TO` — 12 edges.** "Where you could sell" resolves for a handful of
  businesses.

And one that does not exist at all:

* **scheme → district: 0 edges.** `packages/Package007_Government_Schemes/
  datasets/district_scheme_mapping.csv` holds **305 verified pairs** and
  `build_graph.py` does not read it. Two recommendation rules
  (`RS2-VIA_DISTRICT`, `RI3-VIA_DISTRICT`) are structurally dead as a result.

---

## What is missing, in order

1. **The projection.** 647 + 865 rows sitting in Git. Closed by the workflow
   added in this sprint, pending three repository secrets.
2. **305 scheme→district edges** already researched and unread. A builder change,
   no new research.
3. **410 further recoverable edges** identified at 100% both-endpoint
   verification in `RELATIONSHIP_RECOVERY_REPORT.md`. Also no new research.
4. **Package003_Healthcare**, which produces zero entities because no builder
   reads it.

Items 2 and 3 matter more than item 1 for how the product *feels*: item 1 makes
the pages non-empty, items 2 and 3 make them worth reading.

---

**Companions:** `KNOWLEDGE_ARCHITECTURE_AUDIT.md` · `DISTRICT_PIPELINE_REPORT.md` ·
`IMPLEMENTATION_PLAN.md`
