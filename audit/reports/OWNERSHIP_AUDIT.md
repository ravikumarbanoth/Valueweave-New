# Ownership Audit — ValueWeave v2.1 Phase 3

**Read-only audit.** Figures computed by `audit/run_audit.py`.

## Ownership matrix

19 entity types, each with exactly one declared owner.

| Entity type | Owner |
|---|---|
| `BusinessOpportunity` | P004 Industries |
| `Certification` | P006 Skills and Training |
| `ClimateZone` | P005 Agriculture |
| `Country` | P001 Geography |
| `Crop` | P005 Agriculture |
| `District` | P001 Geography |
| `ExportCountry` | P001 Geography |
| `FinancialInstitution` | P007 Government Schemes |
| `GovernmentScheme` | P007 Government Schemes |
| `Industry` | P004 Industries |
| `Institution` | P002 Education |
| `MSME` | P008 MSME |
| `Machinery` | P005 Agriculture |
| `Market` | P008 MSME |
| `RawMaterial` | P008 MSME |
| `Skill` | P006 Skills and Training |
| `Soil` | P005 Agriculture |
| `State` | P001 Geography |
| `TrainingProvider` | P006 Skills and Training |

### Types owned per package

| Package | Types owned |
|---|---|
| P001 Geography | 4 |
| P005 Agriculture | 4 |
| P006 Skills and Training | 3 |
| P008 MSME | 3 |
| P004 Industries | 2 |
| P007 Government Schemes | 2 |
| P002 Education | 1 |

**No entity type has two owners.** The Single Source of Truth rule holds at type level.

## Attribute ownership

87 enforceable owned attributes are registered and checked by graph check G7.

### Conflicting ownership: 2 attributes claimed by two packages

| Attribute | Claimed by |
|---|---|
| `ai_readiness` | P005 Agriculture, P008 MSME |
| `automation_level` | P005 Agriculture, P008 MSME |

`ai_readiness` and `automation_level` are claimed by both Package005 (as Machinery
attributes) and Package008 (as MSME attributes). **This is a genuine conflict, but a
benign one:** they describe different entity types that happen to share a column name.
A machine's automation level and a business's automation level are different facts.

**Recommendation:** disambiguate in the registry by qualifying the attribute name with
its entity type (`Machinery.automation_level` vs `MSME.automation_level`) rather than
transferring ownership. No data change required.

### Owned attributes appearing outside their owner

| Attribute | Owner | Also appears in |
|---|---|---|
| `district_name` | P001_Geography | P006 Skills and Training, P007 Government Schemes, P008 MSME |
| `scheme_name` | P007_Government_Schemes | P002 Education, P003 Healthcare, P005 Agriculture, P006 Skills and Training |
| `machinery_name` | P005_Agriculture | P008 MSME |

- `district_name` and `machinery_name` are **denormalised names beside a foreign key** —
  explicitly allowed, and on G7's allow-list.
- `scheme_name` in four non-owner packages is **the real issue**, and it is the
  ADR-003 problem below.

## Duplicate ownership: the scheme problem

| Package | Scheme rows |
|---|---|
| P002 Education | 25 |
| P003 Healthcare | 9 |
| P004 Industries | 18 |
| P005 Agriculture | 12 |
| P006 Skills and Training | 15 |
| P007 Government Schemes | 40 |
| **Total** | **119** |

119 scheme rows describing perhaps 90 distinct schemes. Package007 declares every
overlap in `also_in_package`, and `known_overlaps.csv` tracks it — but **declaring is not
resolving**, and nothing compares the copies.

### Declared overlaps

| Entity type | Canonical owner | Also in | Status | ADR |
|---|---|---|---|---|
| `GovernmentScheme` | P007_Government_Schemes | 5 pkg | **UNRESOLVED** | ADR-003 |
| `Industry` | P004_Industries | 3 pkg | **PARTIALLY_RESOLVED** | ADR-005 |
| `FinancialInstitution` | P007_Government_Schemes | 1 pkg | **ACCEPTED** | ADR-005 |
| `Machinery` | P005_Agriculture | 1 pkg | **ACCEPTED** | ADR-005 |
| `ExportCountry` | P001_Geography | 2 pkg | **UNRESOLVED** | ADR-005 |

Two remain **UNRESOLVED**: `GovernmentScheme` and `ExportCountry`.

## Entities sourced from a non-owner package

115 of 647 entities (18%) were extracted from a package that does not own their type:

| Entity type | Count |
|---|---|
| `Industry` | 53 |
| `Machinery` | 53 |
| `FinancialInstitution` | 9 |

This is **not a violation**. It is the graph recording where an entity was actually first
seen. `Industry` dominates because four packages maintain sector taxonomies;
`FinancialInstitution` and `Machinery` follow the declared overlaps.

It does mean the ownership registry describes *intent* while `source_package` describes
*reality*, and the two differ for 18% of entities.

## Recommended ownership transfers

| # | Entity type | From | To | Rationale | Effort |
|---|---|---|---|---|---|
| 1 | `GovernmentScheme` | 5 domain packages | **Package007** | Scheme parameters change every budget cycle; six copies will diverge. ADR-003 Option 1. | High — coordinated release across 5 packages |
| 2 | `Industry` | 4 packages | **Package004** | One sector taxonomy, referenced by the rest. Would collapse 17 orphan Industry nodes. | Medium |
| 3 | `Machinery` (non-agricultural) | Package008 free text | **New shared reference** | Package005 is agriculture-scoped by design; 54 machinery references cannot resolve. | Medium |
| 4 | `ExportCountry` | derived text | **Package001** | 29 entities parsed from destination strings; a real country dataset makes them foreign keys. | Low |
| 5 | `ai_readiness` / `automation_level` | shared | **qualify by entity type** | Registry-only fix; no data change. | Trivial |

## Recommendation: one authoritative package per entity type

The rule already holds at type level. What does not hold is **attribute-level discipline
for `GovernmentScheme`**, where five packages publish scheme attributes the registry
assigns to Package007.

**Ranked recommendation:**

1. **Resolve ADR-003 by adopting Option 1** (Package007 canonical). Domain packages keep
   their scheme datasets, mark them `DEPRECATED_REFERENCE`, and add a
   `package007_scheme_id` foreign key. One coordinated release against a permanent
   correctness risk.
2. **Consolidate `Industry` into Package004.** Cheaper than the scheme fix, and it
   directly reduces graph fragmentation.
3. **Do not transfer** `ai_readiness` / `automation_level` — qualify them instead.

Until item 1 lands, G7's declared-overlap mechanism prevents *new* undeclared duplication,
which is containment rather than a fix.
