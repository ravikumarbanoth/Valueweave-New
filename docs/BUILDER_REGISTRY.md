# Builder Registry

**Workstream 2** · Registration spec for all 36 ignored datasets

Each entry gives entity types, relationship types, foreign keys, validation, and expected
graph contribution. **Join rates are measured, not estimated.**

---

## 0. Summary

| Stage | Datasets | Rows | Entities | Edges | New types | Days |
|---|---:|---:|---:|---:|---|---:|
| **A** relationship builders | 8 | 465 | **+54** | **~490** | `TrainingCentre`, `BusinessModel`, `RevenueDivision` | 1.5 |
| **B** entity builders | 9 | 220 | **+130** | ~180 | `Hospital`, `RegulatoryBody`, `Exam`, `Agency` | 2.0 |
| **C** attribute channel | 15 | 393 | 0 | ~37 | — | 1.5 |
| **D** modelling decisions | 4 | 109 | +23 | ~30 | — | 1.0 |
| | **36** | **1,187** | **+207** | **~737** | 7 | **6.0** |

**Coverage 39/77 → 75/77.** The last two are header-only; §5.

---

## 1. Stage A — relationship builders · 1.5 days

### A1 · `Package007/district_scheme_mapping.csv` — **the priority**

| | |
|---|---|
| Rows | **305** (5 schemes × 61 districts) |
| Entities | none new |
| Relationship | **`GovernmentScheme -AVAILABLE_IN-> District`** — new type |
| Foreign keys | `scheme_id` → `government_schemes.scheme_id` · `package001_dist_id` → `district.dist_id` |
| **Join rate** | **305/305 and 305/305 — both 100%** |
| Validation | Both FKs must resolve; unresolved rows to `unresolved_endpoints.csv` |
| Contribution | **305 edges. Every district gains its first scheme edge. Revives `RS2-VIA_DISTRICT`, dead since the graph was first built** |

Also carries `district_level_agency`, `application_channel` and
`district_specific_variation` — per-district operational detail that belongs on the edge
as `notes`, making a scheme recommendation actionable rather than merely correct.

**Four of the five schemes are currently orphans**: MGNREGS, PMAY-G, PM-KISAN, AB PM-JAY.

### A2 · `Package008/business_models.csv` + the FK already in a consumed file

| | |
|---|---|
| Rows | 15 |
| Entity | **`BusinessModel`** — new type, 15 entities |
| Relationship | **`MSME -USES_BUSINESS_MODEL-> BusinessModel`** — new type |
| Foreign key | `msme_businesses.business_model_id` → `business_models.business_model_id` |
| **Join rate** | **40/40 — 100%** |
| Contribution | **15 entities + 40 edges** |

Models: *Manufacturing Unit · Job Work / Ancillary Unit · Trading Business · Service
Centre · Repair and Maintenance Centre · Cloud Kitchen · Cold Storage Facility ·
Warehouse and Distribution* (+7).

**The FK sits in `msme_businesses.csv`, which the builder already opens** and reads at
20% of columns. This is the clearest case in the repository of research paid for and left
on the floor.

### A3 · `Package005/agri_business_mapping.csv`

| | |
|---|---|
| Rows | 30 · **78% of business columns are FKs** — the densest mapping table found |
| Relationships | `Crop -PROCESSED_BY-> BusinessOpportunity` · `BusinessOpportunity -REQUIRES_SKILL-> Skill` · `Crop -REQUIRES_SKILL-> Skill` |
| Foreign keys | `crop_name` **30/30** · `package006_skill_name` **30/30** · `package004_opportunity_name` **17/30** |
| Contribution | **64 edges** |

**The 13 excluded rows carry `PENDING_VERIFICATION` in the opportunity name and must
produce no edge.** Emitting a guess there would break the sentinel discipline the whole
platform rests on.

Raises businesses-with-a-skill-edge from **2 of 45 to 19 of 45.**

### A4 · `Package008/industry_mapping.csv`

19 rows · `MSME -RELATED_TO-> BusinessOpportunity` ·
`package004_opportunity_name` **19/19** · **19 edges**.

### A5 · `Package006/training_centres.csv`

22 rows · **`TrainingCentre`** new type, 22 entities ·
`TrainingCentre -LOCATED_IN-> District` via `district_name` **22/22** · **22 edges**.

**Not duplicates of `training_providers.csv`** — zero name overlap. Centres are physical
sites ("Government ITI, Mancherial"); providers are accrediting networks ("Industrial
Training Institutes (ITI) — Telangana"). A `PART_OF` link between them is real but needs
curation: the `affiliation` column names NCVT/SBTET/MSDE, which are not provider rows.

### A6 · `Package005/agri_processing_opportunities.csv`

17 rows · 17 `BusinessOpportunity` entities ·
FK `agriculture_business_mapping.package005_processing_opportunity_id` **14/14**.

**Ownership check required.** Package004 owns `BusinessOpportunity`. These 17 are
agri-processing opportunities that may duplicate Package004 rows — dedup on
`(type, slug)` handles it automatically, and any collision must be recorded in
`cross_package_sightings.csv` and reviewed before merge.

### A7 · `Package007/education_scheme_mapping.csv`

7 rows · `GovernmentScheme -SUPPORTS-> Institution` ·
`package002_record_name` **0/4 joined on a first pass** — needs the Step 0 matching
ladder. **Lowest-yield item in Stage A**; do it last or defer.

### A8 · `Package001/revenue_division_telangana.csv`

75 rows · **`RevenueDivision`** new type · `RevenueDivision -PART_OF-> District` via
`dist_ref`.

**Modelling decision, not a mechanical registration.** Adds a geographic tier below
district. Worth it only if a user-facing surface needs sub-district granularity — and the
AP half is header-only, so half the states would be covered. **Recommend deferring** to
the same wave that collects `revenue_division_andhra_pradesh.csv`.

---

## 2. Stage B — entity builders · 2 days

### B1–B3 · Package003 Healthcare — 137 entities

Full design in `PACKAGE003_INTEGRATION_PLAN.md`. Summary:

| Dataset | Rows | Type | Note |
|---|---:|---|---|
| `government_hospitals…csv` | 55 | **`Hospital`** new | `bed_capacity`, `specialties` justify a distinct type |
| `medical_colleges…csv` | 58 | `Institution` | **Package002 owns it** — ADR-006 + `also_in_package` |
| `medical_regulatory_bodies…csv` | 24 | **`RegulatoryBody`** new | ~8 will be orphans; accept or cap |
| `government_health_insurance_schemes.csv` | 9 | *(none)* | ADR-003 — Package007 is canonical |

~203 district edges from `district` columns, which are **free text** and must resolve
through the Step 0 ladder with `NO_COUNTERPART` where they do not.

### B4 · `Package002/education_boards_regulatory_bodies.csv`

21 rows → the same **`RegulatoryBody`** type as B3. Registering both together avoids
creating two types for one concept — the mistake `AI Tooling:` pseudo-industries already
made.

### B5 · `Package002/entrance_exams.csv`

29 rows → new **`Exam`** type. `Exam -REQUIRED_FOR-> Institution` is plausible and the FK
is weak. **Register the entities; defer the edges.**

### B6 · `Package007/implementing_agencies.csv`

20 rows → **`Agency`**, or fold into `Institution`. `GovernmentScheme -IMPLEMENTED_BY->`
via `scheme_id`. Decide the type before registering — a second organisation type with
unclear boundaries is how `Institution` and `RegulatoryBody` start to drift.

### B7–B9 · ADR-003 domain schemes — 52 rows, **0 new entities**

`Package002/scholarships.csv` (25) · `Package006/government_skill_schemes.csv` (15) ·
`Package005/agriculture_schemes.csv` (12)

**These must not create `GovernmentScheme` entities.** All three carry
`package007_scheme_id` and are part of the 79 domain rows ADR-003 resolved — 21
`DEPRECATED_REFERENCE`, 58 `DOMAIN_CANONICAL`.

| Row type | Action |
|---|---|
| `DEPRECATED_REFERENCE` | Emit **no** entity; optionally an alias on the Package007 scheme |
| `DOMAIN_CANONICAL` | Emit the entity — no Package007 counterpart exists |

**Registering these naively is the single most likely way to corrupt the graph** in this
whole registry: it would double-count schemes and silently break `G11-SCHEME_OWNERSHIP`.
The crosswalk in `governance/ownership/scheme_crosswalk.csv` is the authority.

---

## 3. Stage C — attribute channel · 1.5 days

**Blocked until the compiler can attach attributes** (`COMPILER_ARCHITECTURE.md` §4).
No entities, no edges — except C6.

| # | Dataset | Rows | Enriches | Attributes |
|---|---|---:|---|---|
| C1 | `eligibility_criteria.csv` | 55 | `GovernmentScheme` | criterion type, value, mandatory |
| C2 | `scheme_benefits.csv` | 51 | `GovernmentScheme` | benefit type, amount, unit |
| C3 | `ai_skill_mapping.csv` | 45 | `Skill` | automation risk, AI impact, human advantage |
| C4 | `application_process.csv` | 43 | `GovernmentScheme` | step order, channel, timeline |
| C5 | `investment_intelligence.csv` | 40 | `MSME` | capex, opex, payback |
| **C6** | `scheme_ai_recommendations.csv` | 37 | `GovernmentScheme` | **+ ~37 `RELATED_TO` scheme→scheme edges** via `suggested_next_scheme_id` |
| C7 | `skill_categories.csv` | 24 | `Skill` | **fixes the 42-of-45 mis-categorisation** |
| C8 | `scheme_categories.csv` | 24 | `GovernmentScheme` | category |
| C9 | `msme_entrepreneurship_support_schemes.csv` | 18 | ADR-003 | as B7–B9 |
| C10 | `career_paths.csv` | 15 | `Skill` | **could yield `PREDECESSOR_OF`/`SUCCESSOR_OF`** — both registered, both unused |
| C11 | `required_documents.csv` | 15 | `GovernmentScheme` | document list |
| C12 | `license_compliance.csv` | 14 | `MSME` | licences, authority |
| C13 | `startup_ecosystem.csv` | 12 | mixed | incubators, funding |
| C14 | `crop_disease_management.csv` | 10 | `Crop` | disease, treatment |
| C15 | `scheme_application_status.csv` | 8 | `GovernmentScheme` | status semantics |

**C7 is the highest-value attribute item.** 42 of 45 skills are currently labelled *"Soft
Skills & Communication"* — including Python, Welding and CNC — because one `category_id`
repeats across 42 rows. `RC2-PROVIDER_IN_DISTRICT` falls back to recommending *"a
certification in the same category as your gap skill"*, so today it can offer a
beautician certification to someone whose gap skill is Python. The category data exists;
the compiler has no channel to carry it.

**C1, C2, C4 and C11 together (164 rows) make schemes actionable.** A recommendation that
names the eligibility rule, the benefit amount, the application channel and the documents
needed is a different product from one that names a scheme.

---

## 4. Stage D — modelling decisions · 1 day

| Dataset | Rows | Question |
|---|---:|---|
| `Package001/revenue_division_telangana.csv` | 75 | New geographic tier? AP half is empty |
| `Package005/agriculture_training.csv` | 7 | `TrainingProvider`, or attributes? |
| `Package005/market_linkages.csv` | 6 | `Market`, or attributes of an existing one? |
| `Package005/farmer_producer_organizations.csv` | 5 | New type for 5 rows? |

**Each is a decision, not a task.** Creating a type for 5 rows is how the graph acquired
6 `AI Tooling:` pseudo-industries that can never be located or required — 10 orphans
created by typing something as the nearest available type rather than the right one.

**Default recommendation: fold into existing types where a plausible one exists; create a
type only where the attributes genuinely differ.**

---

## 5. The last two datasets

`Package001/mandal.csv` and `Package001/revenue_division_andhra_pradesh.csv` are
**header-only**. No registration can consume an empty file.

**The compiler's honest ceiling is 75/77 (97%).** Reaching 77/77 needs collection, not
registration, and is tracked in `KNOWLEDGE_COLLECTION_QUEUE.md` W5-D4. Registering two
empty files as no-ops to hit a round number would make the coverage metric a lie.

---

## 6. New types this registry introduces

| Type | Datasets | Entities | Owner | Justification |
|---|---|---:|---|---|
| `BusinessModel` | A2 | 15 | P008 | FK joins 40/40; distinct attributes |
| `TrainingCentre` | A5 | 22 | P006 | Physical sites; zero overlap with providers |
| `Hospital` | B1 | 55 | P003 | `bed_capacity`, `specialties` ≠ `Institution` |
| `RegulatoryBody` | B3, B4 | 45 | P003/P002 | Neither institution nor hospital |
| `Exam` | B5 | 29 | P002 | Distinct |
| `Agency` | B6 | 20 | P007 | **Decide first** — may fold into `Institution` |
| `RevenueDivision` | A8 | 75 | P001 | **Defer** — AP half missing |

**Relationship types:** `AVAILABLE_IN`, `USES_BUSINESS_MODEL`, `PROCESSED_BY`,
`SUPPORTS`, `IMPLEMENTED_BY`, `REQUIRED_FOR`.

Every one must be added to `RELATIONSHIP_TYPE_DESC` **before** any builder emits it —
the compiler aborts on an unregistered type, which is the behaviour that keeps the type
set meaningful.

---

## 7. Registration order

```
A1  district_scheme_mapping     305 edges, revives a dead rule   ← first
A2  business_models              15 entities + 40 edges
A3  agri_business_mapping        64 edges, 2->19 businesses w/ skills
A4  industry_mapping             19 edges
A5  training_centres             22 entities + 22 edges
A6  agri_processing              17 entities (check ownership)
─── Stage A: 47/77 ──────────────────────────────────────────────
B1–B4  healthcare + reg bodies   158 entities
B5–B6  exams, agencies            49 entities (decide types)
B7–B9  ADR-003 domain schemes      0 entities — honour the crosswalk
─── Stage B: 56/77 ──────────────────────────────────────────────
C   attribute channel (needs the compiler change first)
─── Stage C: 71/77 ──────────────────────────────────────────────
D   modelling decisions
─── Stage D: 75/77 — the ceiling ────────────────────────────────
```

**Prerequisite for all of it:** delete the four bypass guards
(`GRAPH_COMPILER_REPORT.md` §2). Registering 36 datasets into a compiler that hides a
quarter of its join failures means every new failure is as invisible as the last, and
`unresolved_endpoints.csv` will still look complete.

**Verification after each stage:** rebuild, `validate_graph.py` clean, orphan count not
increased, `unresolved_endpoints.csv` reviewed — a rise there is the builder working, not
failing.
