# Data Stewardship Audit — ValueWeave v2.1 Phase 4

**Read-only audit.** Figures computed by `audit/run_audit.py`.

## The headline number

| Metric | Value |
|---|---|
| Total package rows | **2299** |
| Rows awaiting review | **2299** |
| Rows verified | **0** |
| Verified percentage | **0.0%** |
| Graph entities awaiting review | 647 of 647 |
| Stewards assigned | **0** |

**Nothing in this knowledge base has been reviewed by a human.** Not one row of 2299.
Every row across all eight packages carries `VST-NEEDS_REVIEW`, and no steward role is
filled. This is the largest single gap in the platform and no further engineering
reduces it.

## Workload by package

| Package | Rows | Awaiting review | Verified | Avg confidence | Range |
|---|---|---|---|---|---|
| P001 Geography | 138 | 138 | 0 | 82.2 | 55-90 |
| P002 Education | 141 | 141 | 0 | 77.9 | 58-92 |
| P003 Healthcare | 146 | 146 | 0 | 85.8 | 78-88 |
| P004 Industries | 63 | 63 | 0 | 74.4 | 55-85 |
| P005 Agriculture | 388 | 388 | 0 | 72.2 | 50-78 |
| P006 Skills and Training | 291 | 291 | 0 | 67.3 | 50-80 |
| P007 Government Schemes | 655 | 655 | 0 | 71.6 | 60-78 |
| P008 MSME | 477 | 477 | 0 | 67.9 | 57-78 |
| **Total** | **2299** | **2299** | **0** | — | — |

## Review priority: leverage, not volume

Reviewing 2,299 rows in package order is the wrong strategy. Reviewing in **graph-degree
order** is far better, because degree measures how much of the graph depends on a row
being right.

**128 entities have degree ≥ 5.** The top 40 alone carry
**643 of 1730 edge endpoints — 37.2% of the entire graph.**

### Top 25 by review priority

| # | Degree | Type | Entity | Package | Conf |
|---|---|---|---|---|---|
| 1 | 39 | FinancialInstitution | Scheduled Commercial Banks | P008 MSME | 75 |
| 2 | 34 | State | Telangana | P001 Geography | 85 |
| 3 | 29 | State | Andhra Pradesh | P001 Geography | 80 |
| 4 | 27 | Soil | Loamy | P005 Agriculture | 77 |
| 5 | 22 | MSME | Spice Grinding and Packing Unit | P008 MSME | 74 |
| 6 | 21 | Soil | Red Soil | P005 Agriculture | 77 |
| 7 | 20 | ClimateZone | Semi-arid | P005 Agriculture | 75 |
| 8 | 20 | GovernmentScheme | Pradhan Mantri MUDRA Yojana | P007 Government Schemes | 77 |
| 9 | 19 | ClimateZone | Sub-tropical | P005 Agriculture | 76 |
| 10 | 19 | MSME | Dal Milling Unit | P008 MSME | 73 |
| 11 | 19 | MSME | Fruit Pulp and Beverage Unit | P008 MSME | 69 |
| 12 | 18 | District | Hyderabad | P001 Geography | 88 |
| 13 | 18 | GovernmentScheme | Prime Minister's Employment Generation Progr | P007 Government Schemes | 76 |
| 14 | 18 | Industry | Manufacturing | P004 Industries | 55 |
| 15 | 17 | ClimateZone | Tropical | P005 Agriculture | 77 |
| 16 | 17 | MSME | Cold-Pressed Oil Unit | P008 MSME | 72 |
| 17 | 17 | MSME | Rice Milling Unit | P008 MSME | 73 |
| 18 | 15 | Crop | Rice | P005 Agriculture | 78 |
| 19 | 15 | MSME | Garment Manufacturing Unit | P008 MSME | 73 |
| 20 | 13 | ClimateZone | Dry | P005 Agriculture | 74 |
| 21 | 13 | Crop | Turmeric | P005 Agriculture | 77 |
| 22 | 13 | GovernmentScheme | Credit Guarantee Fund Trust for Micro and Sm | P007 Government Schemes | 74 |
| 23 | 13 | MSME | Custom Software Development Firm | P008 MSME | 74 |
| 24 | 12 | Crop | Chickpea | P005 Agriculture | 77 |
| 25 | 12 | Industry | Agriculture & Allied | P004 Industries | 56 |

Note what the list is made of: reference entities. `Scheduled Commercial Banks`,
`Telangana`, `Loamy` soil, `Semi-arid` climate. **An error in one of these propagates to
dozens of query answers**; an error in a leaf entity affects one.

## Suggested review workflow

```
Select entity by degree rank
   ↓
Open its source row (source_package + package_local_id)
   ↓
Check every provenance field against the cited source_url
   ↓
   ├── Accurate  → verification_status = VST-VERIFIED, record reviewer + date
   ├── Wrong     → correct in the OWNING package, new patch version
   └── Unverifiable → leave VST-NEEDS_REVIEW, note why in the notes column
   ↓
Rebuild graph, re-run validation
```

**Review at the package row, never at the graph entity.** The graph is derived (ADR-001);
editing it would be overwritten on the next rebuild.

## Estimated effort

Assumptions stated so they can be challenged: 6 minutes per row for a domain-literate
reviewer with the source portal open; 20% needing correction at 15 minutes each.

| Scope | Rows | Base hours | Correction hours | Total |
|---|---|---|---|---|
| **Tier 1** — top 40 by degree | 40 | 4 | 2 | **~6 h** |
| **Tier 2** — all degree ≥ 5 | 128 | 13 | 6 | **~19 h** |
| **Tier 3** — all connected entities | 505 | 50 | 25 | **~76 h** |
| **Tier 4** — every package row | 2299 | 230 | 115 | **~345 h** |

**Tier 1 is six hours and covers 37.2% of graph edge endpoints.** That is the single
highest-return activity available anywhere in this repository.

Tier 4 is roughly 43 working days for one person — real, but not prohibitive, and it
is the precondition for the API and recommendation engine.

## Lifecycle observation

All entities are `PUBLISHED`, yet none passed through `REVIEWED` or `APPROVED`. The
lifecycle model in `governance/DATA_STEWARDSHIP.md` defines seven states; the platform
uses two of them (`PUBLISHED`, and `ARCHIVED` never). The middle states are unreachable
because no steward exists to perform the transitions.

**The state machine is not wrong — it is unstaffed.**

## Recommendations

| # | Action | Effort |
|---|---|---|
| 1 | **Assign one Package Steward per package** — 8 named people, or 1 person 8 times | Decision |
| 2 | **Execute Tier 1 review (top 40 entities)** | ~6 h |
| 3 | Record reviewer identity and date; move accepted rows to `VST-VERIFIED` | Included |
| 4 | Re-run the audit; `verified_pct` becomes a tracked metric | Trivial |
| 5 | Then Tier 2 (128 entities, ~19 h) before any API work | ~19 h |
