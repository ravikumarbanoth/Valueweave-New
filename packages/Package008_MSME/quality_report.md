# Quality Report — Package008_MSME v1.0.0

What this package is fit for and where it is not. Read before building on it.

## Headline

| Dimension | Assessment |
|---|---|
| **Structural integrity** | Strong. 13 checks, 0 violations, 18/18 datasets clean. |
| **Referential integrity** | Strong. 10 FK sets into 6 packages, 213 resolved, 0 unresolved. |
| **Normalization discipline** | Strong, and mechanically enforced. V13 fails the build on any restated upstream attribute. |
| **Provenance completeness** | Strong. 6 mandatory columns on all 477 rows. |
| **Coverage breadth** | Adequate. 40 businesses across 18 of 24 categories. |
| **Coverage depth** | Good. Every business has scheme, skill, machinery and investment rows (V11). |
| **Numeric completeness** | Weak by design. No rupee figure, no percentage, no payback period. |
| **Human review** | None. All rows `VST-NEEDS_REVIEW`. |

## What this package is fit for

- **Business discovery and shortlisting.** Filter 40 businesses by category, model, udyam class, difficulty, risk, technology level, export potential and district suitability — all closed-domain columns enforced by V12.
- **Requirement checklists.** Machinery, raw materials, licences and skills per business, each as its own queryable row.
- **Scheme matching.** 57 mappings, every one resolving to a real Package007 scheme.
- **Cross-domain navigation.** The point of the layer: crop -> business -> scheme -> skill -> district in one join path, with none of those domains duplicated.
- **Comparative screening.** `investment_intelligence` compares businesses against each other on capex intensity, ROI category, scalability and risk.

## What this package is NOT fit for

- **Telling an entrepreneur what a business costs.** No rupee figure exists anywhere. `udyam_classification` gives the statutory band; that is all.
- **Financial modelling or underwriting.** `investment_intelligence` has no return percentage and no payback period — every field is ordinal.
- **Deciding scheme eligibility.** `scheme_mapping` says a scheme is relevant to a business *type*, not that a given applicant qualifies.
- **Exhaustive district guidance.** 32 rows, not 2,440. Absence of a pair is not evidence of unsuitability.
- **Complete category coverage.** Several categories have no business at all.

## Business catalogue composition

**40 businesses** across **18 of 24 categories**.

| Category | Businesses |
|---|---|
| Food Processing | 7 |
| Engineering | 5 |
| Information Technology | 5 |
| Logistics and Warehousing | 3 |
| Electric Vehicles | 2 |
| Healthcare | 2 |
| Industrial Automation | 2 |
| Recycling and Circular Economy | 2 |
| Renewable Energy | 2 |
| Textiles and Apparel | 2 |
| Agriculture and Allied | 1 |
| Artificial Intelligence | 1 |
| Chemical | 1 |
| Creative Industries | 1 |
| Education and Training | 1 |
| Manufacturing | 1 |
| Robotics | 1 |
| Tourism and Hospitality | 1 |

The 6 categories with no business in v1.0.0 hold classification value for future additions but currently have nothing pointing at them. That is the clearest coverage gap in the release.

### By Udyam classification

| Class | Businesses |
|---|---|
| Micro | 25 |
| Small | 14 |
| Medium | 1 |

The skew toward Micro and Small is deliberate and reflects reality: Udyam registrations are overwhelmingly micro enterprises, and a knowledge base aimed at first-time entrepreneurs should reflect that rather than over-representing what is rare.

### By business model

| Model | Businesses |
|---|---|
| Manufacturing Unit | 16 |
| Service Centre | 7 |
| Battery and E-Waste Recycling | 2 |
| Cold Storage Facility | 2 |
| IT Services Firm | 2 |
| Job Work / Ancillary Unit | 2 |
| Repair and Maintenance Centre | 2 |
| Cloud Kitchen | 1 |
| Drone Service Provider | 1 |
| Food Processing Unit | 1 |
| Software Product Company | 1 |
| Solar EPC Contractor | 1 |
| Systems Integrator | 1 |
| Warehouse and Distribution | 1 |

## The normalization achievement, and what it cost

This is the first package in the programme where non-duplication was a stated hard requirement and the first where it is enforced in code rather than prose:

| Upstream domain | Package008 holds | Package008 does NOT hold |
|---|---|---|
| Government schemes | 57 relationship rows with relevance, stage, support nature | Any benefit, eligibility, portal, ministry or amount |
| Skills | 53 relationship rows with role, criticality, who needs it | Any NSQF level, duration or training route |
| Crops | 22 crop references across two datasets | Any season, yield, soil type or water requirement |
| Districts | 32 suitability rows with a named documented basis | Any population, area, literacy or coordinate |
| Industries | 19 opportunity references with a typed relationship | Any Package004 investment or machinery detail |
| Institutions | 13 talent-flow rows | Any established year, affiliation or type |

**The cost: Package008 is not independently useful.** Ask it what a scheme pays and it cannot tell you — only which scheme to look up. That is the correct trade (one authoritative copy beats six that drift) but it means any consumer application must load the upstream packages. `docs/IMPORT_GUIDE.md` section 5 shows how to join without re-materialising the duplication.

## Risk register

| Risk | Severity | Mitigation in place | Residual |
|---|---|---|---|
| Consumers re-denormalise upstream attributes into their own tables | High | V13 here; import guide section 5 | Cannot be enforced downstream |
| Upstream id renamed in a future release | Medium | V9 fails the build on any unresolved id | Requires `validate.py` to be run |
| Investment sentinel read as 'cheap' or 'low risk' | Medium | Stated in six places | Depends on consumers reading docs |
| Ordinal fields mistaken for measurements | Medium | Closed domains; no numeric-looking values | Column names could still mislead |
| Category coverage gaps read as 'no opportunity exists' | Low | Stated here and in the manifest | — |
| No human review | Medium | Every row `VST-NEEDS_REVIEW` | Unresolved |

## Recommended next actions, in priority order

1. **Source investment bands from DIC and MSME-DI project profiles.** The single largest gap between this package and entrepreneur-facing use. MSME-DI publishes project profiles free of charge — they are the right primary source.
2. **Feed the seven unmatched skill requirements back to Package006** as a concrete coverage request. They are already documented as sentinel rows with the requirement described.
3. **Human data-steward review of the 40 business rows.** Highest value per hour, since everything else hangs off them.
4. **Expand toward full category coverage.**
5. **Propose a general industrial machinery reference** (or an expanded Package005 `farm_machinery`) so the 54 sentinelled machinery references can resolve.

## Reproducing this report

```bash
python3 validate.py && python3 build_docs.py
```
