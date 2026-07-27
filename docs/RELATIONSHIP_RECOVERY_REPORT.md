# Relationship Recovery Report

**Workstreams 1 & 2** · Every relationship implied by existing package data

---

## 0. Summary

| | |
|---|---:|
| Datasets in the repository | **77** |
| Consumed by `build_graph.py` | **35** |
| **Not consumed** | **42** (1,232 rows) |
| Unconsumed datasets carrying foreign keys | **23** (901 rows) |
| **Edges recoverable at 100% both-endpoint verification** | **410** |
| New records required | **0** |
| New entities created | 22 (`TrainingCentre`, from an existing dataset) |

**The packages were built with cross-package foreign keys already in place.** Six
distinct FK conventions appear across the unconsumed datasets:

```
package001_dist_id · dist_ref          -> Package001 districts
package002_record_id · _record_name    -> Package002 institutions
package004_opportunity_id · _name      -> Package004 opportunities
package006_skill_id · _skill_name      -> Package006 skills
package007_scheme_id                   -> Package007 schemes
crop_id · business_id · category_id    -> intra-package
```

They were designed for exactly this. The builder reads almost none of them.

---

## 1. The single largest finding

### `Package007_Government_Schemes/datasets/district_scheme_mapping.csv`

```
305 rows · 5 schemes × 61 districts

columns: mapping_id, scheme_id, scheme_short_name, package001_dist_id, dist_ref,
         district_name, state_scope, district_level_agency, application_channel,
         district_specific_variation, + 6 provenance columns
```

| Check | Result |
|---|---|
| `package001_dist_id` joins to `Package001/district.csv` | **305 of 305** |
| `scheme_id` joins to `Package007/government_schemes.csv` | **305 of 305** |
| Distinct districts covered | **61 of 61** |
| Read by `build_graph.py` | **No** |

Five schemes, each mapped to all 61 districts: **PMEGP · MGNREGS · PMAY-G · PM-KISAN ·
AB PM-JAY**. Four of those five are currently **orphan entities**.

This dataset is the exact edge shape that `RS2-VIA_DISTRICT` traverses. **The rule has
been dead since the graph was first built, and the data to revive it has been sitting
in `packages/` the whole time.**

It also carries `district_level_agency`, `application_channel` and
`district_specific_variation` — per-district operational detail that would make a scheme
recommendation genuinely actionable rather than merely correct.

---

## 2. Dataset registration inventory (WS2)

### Consumed — 35 datasets

Package001 (2) · Package002 (1) · Package005 (9) · Package006 (5) · Package007 (5) ·
Package008 (13). Package004's five opportunity datasets are read dynamically at
`build_graph.py:305`.

**Package003_Healthcare: 0 of 4 consumed.** Covered by `PACKAGE003_INTEGRATION_PLAN.md`;
out of scope for Wave 1.

### Not consumed — 42 datasets, 1,232 rows

**Group A — carry foreign keys and yield edges now (6 datasets, 443 rows)**

| Rows | Dataset | Yields |
|---:|---|---|
| **305** | `P007/district_scheme_mapping.csv` | **R1** — 305 edges |
| 30 | `P005/agri_business_mapping.csv` | **R4, R5, R6** — 64 edges |
| 22 | `P006/training_centres.csv` | **R2** — 22 edges + 22 entities |
| 19 | `P008/industry_mapping.csv` | **R3** — 19 edges |
| 45 | `P006/ai_skill_mapping.csv` | Attributes, not edges — §4 |
| 24 | `P006/skill_categories.csv` | Attributes — and see §5 |

**Group B — carry `package007_scheme_id`, already governed by ADR-003 (5 datasets, 79 rows)**

`P002/scholarships.csv` (25) · `P004/msme_entrepreneurship_support_schemes.csv` (18) ·
`P006/government_skill_schemes.csv` (15) · `P005/agriculture_schemes.csv` (12) ·
`P003/government_health_insurance_schemes.csv` (9)

These are the 79 domain scheme rows ADR-003 resolved: 21 `DEPRECATED_REFERENCE`, 58
`DOMAIN_CANONICAL`. **Not new schemes** — registering them naively would double-count.
The `DOMAIN_CANONICAL` rows are the interesting ones (a domain scheme with no Package007
counterpart), and they are Wave 2 work.

**Group C — scheme detail, attributes rather than edges (6 datasets, 269 rows)**

`P007/eligibility_criteria.csv` (55) · `P007/scheme_benefits.csv` (51) ·
`P007/application_process.csv` (43) · `P007/scheme_ai_recommendations.csv` (37) ·
`P007/implementing_agencies.csv` (20) · `P007/required_documents.csv` (15)

These enrich a scheme node rather than connecting it. **Except**
`scheme_ai_recommendations.csv`, which carries `suggested_next_scheme_id` and
`related_scheme_ids` — a genuine `GovernmentScheme -> GovernmentScheme` shape worth ~37
edges in Wave 2.

**Group D — Package003 healthcare (4 datasets, 146 rows)** — separate plan.

**Group E — no foreign keys, need collection or modelling (21 datasets, ~295 rows)**

Includes `P008/business_models.csv` (15), `P008/startup_ecosystem.csv` (12),
`P005/farmer_producer_organizations.csv` (5), `P002/entrance_exams.csv` (29).
`mandal.csv` and `revenue_division_andhra_pradesh.csv` are **header-only, 0 rows**.

---

## 3. The 410 recoverable edges

Every row below was verified with **both endpoints** resolving to an existing entity.

| # | Edges | Shape | Source | Join |
|---|---:|---|---|---|
| **R1** | **305** | `GovernmentScheme -AVAILABLE_IN-> District` | `P007/district_scheme_mapping` | `scheme_id` + `package001_dist_id`, **100%** |
| **R2** | **22** | `TrainingCentre -LOCATED_IN-> District` | `P006/training_centres` | `district_name`, **100%** |
| **R3** | **19** | `MSME -RELATED_TO-> BusinessOpportunity` | `P008/industry_mapping` | `package004_opportunity_name`, **19 of 19** |
| **R4** | **17** | `Crop -PROCESSED_BY-> BusinessOpportunity` | `P005/agri_business_mapping` | both names, 17 of 30 † |
| **R5** | **17** | `BusinessOpportunity -REQUIRES_SKILL-> Skill` | `P005/agri_business_mapping` | both names, 17 of 30 † |
| **R6** | **30** | `Crop -REQUIRES_SKILL-> Skill` | `P005/agri_business_mapping` | **30 of 30** |
| | **410** | | | |

† The 13 excluded rows carry `PENDING_VERIFICATION` in `package004_opportunity_name`.
**They produce no edge.** The sentinel is honoured rather than guessed past — which is
the whole reason the sentinel exists.

### R5 is the important one

**Businesses with a skill edge goes from 2 to 19 of 45** — a 9.5× improvement in the
single connection the recommendation engine most depends on, from a dataset that has
been in `packages/Package005_Agriculture/` since it was assembled.

`agri_business_mapping.csv` is the best-connected unconsumed dataset in the repository:
30 rows, and **`crop_name`, `package006_skill_name` and `package004_opportunity_name` all
join at 100%** where populated. It was built to be a three-way bridge and has never been
read.

### R2 creates entities, and they are not duplicates

`training_centres.csv` (22) and `training_providers.csv` (25) share **zero** names:

| `training_centres` | `training_providers` |
|---|---|
| Government ITI, Mancherial | Industrial Training Institutes (ITI) — Telangana |
| Government Polytechnic for Women, Secunderabad | Polytechnic Colleges (SBTET) — Telangana |
| SynchroServe Pradhan Mantri Kaushal Kendra | Pradhan Mantri Kaushal Kendra (PMKK) Network |

**Centres are physical sites; providers are the networks that accredit them.** A genuine
`TrainingCentre -PART_OF-> TrainingProvider` relationship exists and is a curation task —
the centres' `affiliation` column names accrediting bodies (NCVT, SBTET, MSDE) that are
not provider rows, so it cannot be joined automatically. Wave 2.

---

## 4. What was examined and deliberately excluded

| Dataset | Rows | Why no edge |
|---|---:|---|
| `P006/ai_skill_mapping.csv` | 45 | `will_ai_replace`, `automation_potential` are **attributes of a skill**, not relationships. Modelling "Skill is at risk from AI" as an edge would require an `AI` entity that means nothing |
| `P008/investment_intelligence.csv` | 40 | `business_id` joins, but the payload is capital figures — attributes |
| `P007/eligibility_criteria.csv` | 55 | Eligibility is a predicate over a user, not an edge between two entities |
| `P004/*_opportunities.csv` `related_businesses_summary` | 63 | **Free-text prose**, not a foreign key. Parsing it would be inference |
| `P001/revenue_division_telangana.csv` | 75 | Would need a `RevenueDivision` entity type. Real, and a modelling decision rather than a recovery |
| `P002/entrance_exams.csv` | 29 | No FK to any existing type |

**`related_businesses_summary` is the closest call.** It appears in four Package004
datasets and reads like a relationship. It is prose — *"related to dairy processing and
cold-chain logistics"* — and extracting edges from it would be exactly the speculative
inference the mission's rules forbid. If those relationships matter, the fix is a
structured column in Package004, not a parser.

---

## 5. Two builder defects that must be fixed first

### Defect 1 — mapping losses are dropped silently

```python
# build_graph.py:501
if sk and opp and E("BusinessOpportunity", opp):
    edge("REQUIRES_SKILL", ...)
```

`E(...)` returns nothing for 23 of 25 business names. No exception, no warning, **no row
in `unresolved_endpoints.csv`** — 27 of 30 researched mappings vanish.

The certification path logs **all 122** of its failures to the same file.
`unresolved_endpoints.csv` therefore holds 132 rows and **looks complete**.

**The inconsistency is the defect.** A failure log that reports some losses and hides
others is worse than none, because it invites trust it has not earned. Fix before Stage
A, or the six new registrations will fail the same way.

### Defect 2 — `training_centres.csv` is not registered at all

22 rows with a populated `district_id`, never opened. Not a resolution failure — the file
is simply absent from the builder.

---

## 6. Effect

| Metric | Before | After | Δ |
|---|---:|---:|---|
| Edges | 865 | **1,275** | **+47%** |
| Entities | 647 | 669 | +22 |
| Edges per entity | 1.34 | **1.91** | +43% |
| Distinct edge shapes | 27 | **32** | +5 |
| **Districts reaching a scheme in 1 hop** | **0 of 61** | **61 of 61** | **∞** |
| **Businesses with a skill edge** | **2 of 45** | **19 of 45** | **9.5×** |
| Schemes with a district edge | 0 of 40 | 5 of 40 | +5 |
| Orphan entities | 142 | **138** | **−4** |
| Structurally dead rules | 2 | **1** | −1 |

### Read the orphan row honestly

**−4.** Relationship recovery connects entities that already had edges; it does not reach
entities nobody references. Those are cleared by entity resolution
(`ENTITY_MATCHING_RULES.md`), and the largest block — 30 orphan certifications — is
**23 of 30 blocked on skills Package006 v1.1 has not collected**.

Phase 1 projected 142 → ~18 after Wave 1. **That was optimistic and this report
supersedes it.** The recovery's value is reach, not orphan reduction: one dead rule
revived, every district given a scheme, and the business-to-skill connection improved
9.5× — all without collecting a single record.
