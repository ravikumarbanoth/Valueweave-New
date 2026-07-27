# Dataset Coverage Report

**Workstream 1** · All 77 datasets classified · `build_graph.py` @ `2e86f4e`

---

## 0. Summary

| Class | Datasets | Rows | Definition |
|---|---:|---:|---|
| **Consumed** | **13** | 542 | Read, and ≥50% of business columns used |
| **Partially consumed** | **26** | 570 | Read, but <50% of business columns used |
| **Ignored** | **36** | 1,187 | Present and populated; the builder never opens the file |
| **Unused** | **2** | **0** | Header-only — nothing to consume |
| | **77** | **2,299** | |

**Datasets the builder opens: 39 of 77 (50.6%).**

Two corrections to figures in circulation:

| Source | Claimed | Error |
|---|---:|---|
| Phase 2 report | 35 | Missed Package004's four dynamically loaded files |
| This mission's brief | 42 | — |
| **Measured here** | **39** | 35 literal + 4 from the `P4_FILES` loop |

### Column consumption is the sharper story

Only **13 of the 39 datasets the builder opens** use half or more of their business
columns. The other 26 are opened for two or three fields and the rest is discarded.

```
Package004 opportunity datasets    2–3 of 30 columns    7–10%
district.csv                       4 of 28             14%
universities…csv                   3 of 16             19%
msme_businesses.csv                4 of 20             20%
```

**The well-consumed datasets are the mapping tables** (50–83%) — they are mostly foreign
keys, so reading the keys is reading the dataset. **The under-consumed ones are the
entity tables**, where the builder takes a name and an id and leaves the research behind.

`china_inspired_adapted_opportunities.csv` has 30 business columns describing an
opportunity — investment, revenue, risk, licensing, market. The compiler reads **two**:
the name, and the category.

---

## 1. Consumed — 13 datasets, 542 rows

Read, with ≥50% of business columns used.

| Package | Dataset | Rows | Cols used | % | FK cols |
|---|---|---:|---|---:|---:|
| P006 | `skill_business_mapping.csv` | 30 | 5/6 | **83%** | 4 |
| P008 | `scheme_mapping.csv` | 57 | 6/8 | 75% | 5 |
| P008 | `skill_mapping.csv` | 53 | 6/8 | 75% | 5 |
| P008 | `agriculture_business_mapping.csv` | 14 | 6/8 | 75% | 7 |
| P005 | `crop_soil_mapping.csv` | 90 | 5/7 | 71% | 5 |
| P006 | `industry_skill_mapping.csv` | 40 | 5/7 | 71% | 4 |
| P008 | `raw_material_mapping.csv` | 33 | 7/11 | 64% | 6 |
| P008 | `district_business_mapping.csv` | 32 | 6/10 | 60% | 6 |
| P005 | `crop_climate_mapping.csv` | 90 | 5/9 | 56% | 5 |
| P007 | `agriculture_scheme_mapping.csv` | 14 | 5/9 | 56% | 7 |
| P008 | `education_support_mapping.csv` | 13 | 5/9 | 56% | 6 |
| P008 | `machinery_mapping.csv` | 64 | 5/10 | 50% | 6 |
| P007 | `industry_scheme_mapping.csv` | 12 | 4/8 | 50% | 5 |

**Every one is a mapping table.** Not a single entity table reaches 50%.

---

## 2. Partially consumed — 26 datasets, 570 rows

Read, but most of the research is discarded.

| Package | Dataset | Rows | Used | % | What is left behind |
|---|---|---:|---|---:|---|
| P004 | `china_inspired_adapted_opportunities.csv` | 9 | 2/30 | **7%** | investment, revenue, risk, licensing |
| P004 | `construction_skilled_trade_services.csv` | 11 | 3/30 | 10% | ↑ |
| P004 | `digital_technology_livelihoods.csv` | 12 | 3/30 | 10% | ↑ |
| P004 | `food_agro_processing_micro_enterprises.csv` | 13 | 3/30 | 10% | ↑ |
| P001 | `district.csv` | 61 | 4/28 | 14% | population, area, GDP, mandal count |
| P005 | `farm_machinery.csv` | 16 | 2/12 | 17% | cost, power, suitability |
| P002 | `universities…csv` | 66 | 3/16 | 19% | NAAC grade, type, established |
| P005 | `climate_zones.csv` | 8 | 2/10 | 20% | rainfall, temperature |
| P005 | `ai_precision_agriculture.csv` | 10 | 2/10 | 20% | technology, adoption |
| P008 | `msme_businesses.csv` | 40 | 4/20 | 20% | **`business_model_id` (40/40)**, investment |
| P005 | `soil_types.csv` | 10 | 2/9 | 22% | pH, drainage |
| P008 | `market_channels.csv` | 11 | 2/9 | 22% | reach, commission |
| P008 | `ai_business_tools.csv` | 12 | 2/9 | 22% | complexity, relevance |
| P006 | `skills.csv` | 45 | 5/22 | 23% | NSQF level, demand, automation risk |
| P007 | `financial_institutions.csv` | 12 | 2/8 | 25% | type, coverage |
| P008 | `msme_categories.csv` | 24 | 2/8 | 25% | description |
| P006 | `training_providers.csv` | 25 | 2/8 | 25% | **`skills_offered_summary`**, pathways |
| P001 | `state.csv` | 2 | 4/16 | 25% | policy, capital |
| P007 | `government_schemes.csv` | 40 | 5/19 | 26% | **`jurisdiction`**, ministry, benefit |
| P005 | `crops.csv` | 45 | 5/19 | 26% | season, yield, duration |
| P005 | `crop_categories.csv` | 24 | 2/7 | 29% | description |
| P006 | `certifications.csv` | 30 | 3/9 | 33% | NSQF level, cost, recognition |
| P005 | `export_opportunities.csv` | 8 | 3/7 | 43% | volume, value |
| P008 | `export_opportunities.csv` | 12 | 4/9 | 44% | ↑ |
| P008 | `financial_support.csv` | 12 | 4/9 | 44% | interest, tenure |
| P007 | `skill_scheme_mapping.csv` | 12 | 5/11 | 45% | **6 unused FK columns** |

Two rows deserve attention:

**`msme_businesses.csv`** discards `business_model_id`, populated **40 of 40**, which
joins `business_models.csv` perfectly. A new entity type and 40 edges, from a column in a
file the builder already opens.

**`skill_scheme_mapping.csv`** has **11 FK columns and uses 5**, leaving
`package006_certification_id`, `package006_provider_name` and
`package006_scheme_id` unread — a second route to `CERTIFIED_BY`, the type that
currently fails 122 times out of 122.

---

## 3. Ignored — 36 datasets, 1,187 rows

Present, populated, never opened. Grouped by the channel each needs.

### 3a · Needs a relationship builder — 8 datasets, 465 rows

| Package | Dataset | Rows | Contribution |
|---|---|---:|---|
| **P007** | **`district_scheme_mapping.csv`** | **305** | **305 scheme→district edges. Both FKs join 100%. Revives `RS2-VIA_DISTRICT`** |
| P005 | `agri_business_mapping.csv` | 30 | 64 edges: crop→business, business→skill, crop→skill |
| P006 | `training_centres.csv` | 22 | 22 entities + 22 district edges |
| P008 | `industry_mapping.csv` | 19 | 19 MSME→business edges, 19/19 join |
| P005 | `agri_processing_opportunities.csv` | 17 | 17 entities; FK joins `agriculture_business_mapping` 14/14 |
| P008 | `business_models.csv` | 15 | **15 entities + 40 edges** via `msme_businesses.business_model_id` |
| P007 | `education_scheme_mapping.csv` | 7 | scheme→institution |
| P001 | `revenue_division_telangana.csv` | 75 | Needs a `RevenueDivision` type — a modelling decision |

### 3b · Needs an entity builder — 9 datasets, 220 rows

| Package | Dataset | Rows | Type |
|---|---|---:|---|
| P003 | `medical_colleges…csv` | 58 | `Institution` (Package002 owns; ADR-006) |
| P003 | `government_hospitals…csv` | 55 | **`Hospital`** — new type |
| P002 | `entrance_exams.csv` | 29 | New type |
| P002 | `scholarships.csv` | 25 | ADR-003 domain schemes |
| P003 | `medical_regulatory_bodies…csv` | 24 | **`RegulatoryBody`** — new type |
| P002 | `education_boards_regulatory_bodies.csv` | 21 | ↑ same type |
| P007 | `implementing_agencies.csv` | 20 | Agency type or `Institution` |
| P006 | `government_skill_schemes.csv` | 15 | ADR-003 domain schemes |
| P005 | `agriculture_schemes.csv` | 12 | ADR-003 domain schemes |

Four of these carry `package007_scheme_id` and are the ADR-003 domain rows: 21
`DEPRECATED_REFERENCE`, 58 `DOMAIN_CANONICAL`. **Registering them naively would
double-count schemes** — the crosswalk must be honoured.

### 3c · Needs the attribute channel — 15 datasets, 393 rows

The compiler has no way to attach these. They are not edges and not entities.

| Package | Dataset | Rows | Enriches |
|---|---|---:|---|
| P007 | `eligibility_criteria.csv` | 55 | `GovernmentScheme` |
| P007 | `scheme_benefits.csv` | 51 | `GovernmentScheme` |
| P006 | `ai_skill_mapping.csv` | 45 | `Skill` — automation risk, AI impact |
| P007 | `application_process.csv` | 43 | `GovernmentScheme` |
| P008 | `investment_intelligence.csv` | 40 | `MSME` |
| P007 | `scheme_ai_recommendations.csv` | 37 | `GovernmentScheme` (also ~37 scheme→scheme edges) |
| P006 | `skill_categories.csv` | 24 | `Skill` — **and would fix the 42/45 mis-categorisation** |
| P007 | `scheme_categories.csv` | 24 | `GovernmentScheme` |
| P004 | `msme_entrepreneurship_support_schemes.csv` | 18 | ADR-003 |
| P006 | `career_paths.csv` | 15 | Skill sequencing — could yield `PREDECESSOR_OF` |
| P007 | `required_documents.csv` | 15 | `GovernmentScheme` |
| P008 | `license_compliance.csv` | 14 | `MSME` |
| P008 | `startup_ecosystem.csv` | 12 | Ecosystem attributes |
| P005 | `crop_disease_management.csv` | 10 | `Crop` |
| P007 | `scheme_application_status.csv` | 8 | `GovernmentScheme` |

**This group is why 77/77 needs a third channel.** These 393 rows are the most
*actionable* content in the repository — eligibility rules, application channels,
required documents — and the compiler is structurally unable to attach any of it.

### 3d · Low-value or needs a modelling decision — 4 datasets, 109 rows

`P005/agriculture_training.csv` (7) · `P005/market_linkages.csv` (6) ·
`P005/farmer_producer_organizations.csv` (5) · `P003/government_health_insurance_schemes.csv` (9)

The last is ADR-003-governed; the first three need entity types whose value is unproven.

---

## 4. Unused — 2 datasets, 0 rows

| Package | Dataset | Rows |
|---|---|---:|
| P001 | `mandal.csv` | **0** — header only |
| P001 | `revenue_division_andhra_pradesh.csv` | **0** — header only |

Nothing to consume. Tracked in `KNOWLEDGE_COLLECTION_QUEUE.md` W5-D4.
`revenue_division_telangana.csv` has 75 rows, so the AP half is a collection gap rather
than a design choice.

---

## 5. Coverage by package

| Package | Datasets | Consumed | Partial | Ignored | Unused | **Opened** |
|---|---:|---:|---:|---:|---:|---:|
| P001_Geography | 5 | 0 | 2 | 1 | **2** | 2/5 (40%) |
| P002_Education | 4 | 0 | 1 | 3 | 0 | 1/4 (25%) |
| **P003_Healthcare** | **4** | **0** | **0** | **4** | **0** | **0/4 (0%)** |
| P004_Industries | 5 | 0 | 4 | 1 | 0 | 4/5 (80%) |
| P005_Agriculture | 16 | 2 | 7 | 7 | 0 | 9/16 (56%) |
| P006_Skills | 10 | 2 | 3 | 5 | 0 | 5/10 (50%) |
| P007_Government_Schemes | 15 | 2 | 3 | 10 | 0 | 5/15 (33%) |
| P008_MSME | 18 | 7 | 6 | 5 | 0 | 13/18 (72%) |
| **Total** | **77** | **13** | **26** | **36** | **2** | **39/77** |

**Package003_Healthcare: 0 of 4.** 146 researched rows, Stable v1.0.0, entirely
invisible. `PACKAGE003_INTEGRATION_PLAN.md` covers it; the regression test pins it as the
only silent package so the day it changes, the suite says so.

**Package007: 5 of 15 (33%)** — the worst ratio among contributing packages, and it owns
the single most valuable ignored dataset (305 rows).

**Package008: 13 of 18 (72%)** — the best, and it is why MSME is the only richly
connected entity type in the graph.

---

## 6. Path to 77/77

| Stage | Registers | Coverage | Effort |
|---|---:|---:|---:|
| Baseline | — | **39/77 (51%)** | — |
| **A** · relationship builders (3a) | +8 | **47/77 (61%)** | 1.5 d |
| **B** · entity builders (3b) | +9 | **56/77 (73%)** | 2 d |
| **C** · attribute channel (3c) | +15 | **71/77 (92%)** | 1.5 d |
| **D** · modelling decisions (3d) | +4 | **75/77 (97%)** | 1 d |
| **E** · collect mandal + AP divisions | +2 | **77/77 (100%)** | *collection* |

**Stage A is the highest value: 8 datasets, ~465 rows, ~470 edges, no new entity type
and no research.**

**Stage E is not a compiler task.** Two datasets are header-only, so 77/77 is unreachable
by the compiler alone — the honest ceiling for registration work is **75/77 (97%)**, and
claiming 100% would require registering two empty files as no-ops.

Per-dataset specifications — entity types, relationship types, foreign keys, validation
and expected contribution — are in **`BUILDER_REGISTRY.md`**.

---

## 7. How this stays true

`tests/test_graph_compiler.py` holds the manifest and **fails when a dataset appears in
`packages/*/datasets/` that is in none of the three sets.** It parses `build_graph.py`
for both literal and `P4_FILES` loading, so the `CONSUMED` set cannot drift from what the
compiler actually reads.

That check is what would have caught the 35-vs-39 discrepancy in the Phase 2 report, and
it is why the figures here can be trusted where the earlier ones could not.
