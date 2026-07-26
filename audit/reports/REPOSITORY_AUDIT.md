# Repository Audit — ValueWeave v2.1 Phase 1

**Read-only audit. No file was modified.** Every figure is computed by
`audit/run_audit.py` and stored in `audit/audit_findings.json`.

## Headline

| Check | Result | Verdict |
|---|---|---|
| Duplicate entity ids | 0 | Clean |
| Duplicate entity names within a type | 0 | Clean |
| Duplicate relationship triples | 0 | Clean |
| **Broken cross-package references** | **0 of 730 checked** | **Clean** |
| Weak (sentinel) references | 127 (17.4%) | Expected — documented upstream absences |
| Orphan entities | 142 | Known, traceable |
| Orphan relationships | 0 | Clean |
| Datasets not feeding the graph | **37 of 77** | **Largest finding** |
| Fully-sentinel columns | 23 | Intentional |
| Empty or constant columns | 241 | Mostly intentional |
| Python files scanned | 28 | — |
| `__pycache__` without source | 12 | Dead artifacts |

**Zero broken references across 730 cross-package reference cells** is the strongest
structural result in this audit. Eight packages referencing each other by id, and every
id resolves.

## Finding 1 — 37 datasets never reach the knowledge graph

**37 of 77 datasets (48%), holding 1,142 rows, contribute no entity and no edge.**

| Package | Datasets | Rows | Examples |
|---|---|---|---|
| P001 Geography | 3 | 75 | `mandal.csv`, `revenue_division_andhra_pradesh.csv`, `revenue_division_telangana.csv` |
| P002 Education | 3 | 75 | `education_boards_regulatory_bodies.csv`, `entrance_exams.csv`, `scholarships.csv` |
| P003 Healthcare | 4 | 146 | `government_health_insurance_schemes.csv`, `government_hospitals_telangana_andhra_pradesh.csv`, `medical_colleges_telangana_andhra_pradesh.csv`… |
| P004 Industries | 1 | 18 | `msme_entrepreneurship_support_schemes.csv` |
| P005 Agriculture | 7 | 87 | `agri_business_mapping.csv`, `agri_processing_opportunities.csv`, `agriculture_schemes.csv`… |
| P006 Skills and Training | 4 | 76 | `career_paths.csv`, `government_skill_schemes.csv`, `skill_categories.csv`… |
| P007 Government Schemes | 10 | 565 | `application_process.csv`, `district_scheme_mapping.csv`, `education_scheme_mapping.csv`… |
| P008 MSME | 5 | 100 | `business_models.csv`, `industry_mapping.csv`, `investment_intelligence.csv`… |

**This is an extraction gap, not dead data.** The datasets are valid, validated and
provenance-complete. `build_graph.py` simply does not read them. Package007 is the worst
case: 565 rows across 11 datasets — eligibility criteria, benefits, application process,
required documents — none of which the graph models.

Three sub-cases, needing different responses:

1. **Genuinely out of the current entity model** (mandal, revenue divisions, hospitals,
   medical colleges, entrance exams). The graph has no Mandal or Hospital entity type.
   Fix: extend the entity model, or accept the scope boundary explicitly.
2. **Modellable with existing types but unextracted** (Package007 scheme_benefits,
   eligibility_criteria, application_process). Fix: extend `build_graph.py`. This is the
   highest-value extraction work in v2.1.
3. **Deliberately superseded** (Package005 `agri_business_mapping` was superseded by
   Package008's richer mapping). Fix: none needed; document the supersession.

## Finding 2 — 23 fully-sentinel columns

Every cell is `PENDING_VERIFICATION`:

| Dataset | Column | Rows |
|---|---|---|
| `Package001_Geography/district.csv` | `lgd_district_code` | 61 |
| `Package001_Geography/district.csv` | `district_gdp_inr_cr` | 61 |
| `Package001_Geography/district.csv` | `primary_industry_sector_id` | 61 |
| `Package001_Geography/revenue_division_telangana.csv` | `lgd_code` | 75 |
| `Package001_Geography/state.csv` | `state_gdp_inr_cr` | 2 |
| `Package001_Geography/state.csv` | `lgd_state_code` | 2 |
| `Package004_Industries/construction_skilled_trade_services.csv` | `district_suitability_summary` | 11 |
| `Package004_Industries/digital_technology_livelihoods.csv` | `minimum_investment` | 12 |
| `Package004_Industries/digital_technology_livelihoods.csv` | `working_capital_summary` | 12 |
| `Package004_Industries/digital_technology_livelihoods.csv` | `estimated_setup_time_summary` | 12 |
| `Package004_Industries/digital_technology_livelihoods.csv` | `seasonal_factors_summary` | 12 |
| `Package004_Industries/digital_technology_livelihoods.csv` | `sustainability_summary` | 12 |
| `Package004_Industries/food_agro_processing_micro_enterprises.csv` | `estimated_setup_time_summary` | 13 |
| `Package004_Industries/food_agro_processing_micro_enterprises.csv` | `ai_tools_summary` | 13 |
| `Package005_Agriculture/agri_processing_opportunities.csv` | `investment_band` | 17 |
| `Package005_Agriculture/agri_processing_opportunities.csv` | `capacity_indicative` | 17 |
| `Package005_Agriculture/ai_precision_agriculture.csv` | `approximate_cost_inr` | 10 |
| `Package005_Agriculture/farm_machinery.csv` | `investment_inr` | 16 |
| `Package005_Agriculture/farm_machinery.csv` | `annual_maintenance_inr` | 16 |
| `Package007_Government_Schemes/district_scheme_mapping.csv` | `district_specific_variation` | 305 |
| `Package008_MSME/business_models.csv` | `typical_lead_time_to_revenue` | 15 |
| `Package008_MSME/market_channels.csv` | `typical_payment_cycle` | 11 |
| `Package008_MSME/msme_businesses.csv` | `investment_range` | 40 |

**All 23 are intentional and documented.** They cluster in exactly the places the
packages refused to fabricate: monetary values (investment, cost, maintenance),
timelines (payment cycle, lead time to revenue, setup time) and per-district variation.
Package008's `investment_range` being sentinel on all 40 rows is stated in six places in
that package's own docs.

**No action recommended.** These columns are honest gaps, and removing them would delete
the record that the gap exists.

## Finding 3 — naming inconsistencies

| Issue | Detail |
|---|---|
| Primary key column naming | Package002/003/004 use bare `id`; Package005-008 use `<entity>_id`. Both internally consistent. |
| Primary key value format | UUIDs in Package001-004, human-readable prefixed ids in Package005-008 |
| Ampersand vs "and" | 1 pattern found; slug normalisation already collapses it so no node splits |

**Cosmetic, not structural.** Cross-package joins work regardless. Retrofitting either
convention would break every released package's immutability guarantee for no functional
gain. Recommendation: **document the convention split, change nothing.**

## Finding 4 — dead files and code

| Item | Count | Assessment |
|---|---|---|
| `__pycache__` directories with no source | 12 | **Dead. Safe to delete.** All under `knowledge_engine/` |
| Placeholder package directories | 1 | `Package005_Agriculture`-era stubs: Package006_Skills |
| Empty directories inside packages | 7 | Package006_Skills_and_Training/docs, Package006_Skills_and_Training/evidence, Package006_Skills_and_Training/imports, Package006_Skills_and_Training/metadata |
| Possibly-unused Python functions | 4 files flagged | Mostly false positives: module-level scripts and library methods called externally |

`Package006_Skills` (empty) is superseded by `Package006_Skills_and_Training` and is
already noted in the package index.

## Finding 5 — documentation completeness

Every package was checked for 11 expected artifacts (README, CHANGELOG, VERSION,
manifest, validation report, 4 docs, schema catalog, dataset registry).

| Package | Missing |
|---|---|
| P001 Geography | `validation_report.md`, `docs/METHODOLOGY.md`, `docs/USAGE.md`, `docs/DATA_DICTIONARY.md`, `docs/IMPORT_GUIDE.md` |
| P002 Education | `validation_report.md`, `docs/DATA_DICTIONARY.md`, `docs/IMPORT_GUIDE.md` |
| P003 Healthcare | `docs/DATA_DICTIONARY.md`, `docs/IMPORT_GUIDE.md` |
| P004 Industries | `docs/DATA_DICTIONARY.md`, `docs/IMPORT_GUIDE.md` |
| P006 Skills and Training | `README.md`, `CHANGELOG.md`, `VERSION`, `package_manifest.json`, `docs/METHODOLOGY.md`, `docs/USAGE.md`, `docs/DATA_DICTIONARY.md`, `docs/IMPORT_GUIDE.md`, `schemas/schema_catalog.json`, `registry/dataset_registry.csv` |

Packages 001-004 predate the documentation standard that Packages 005-008 established.
This is version drift, not neglect — and correcting it would mean modifying released
immutable packages.

## What is genuinely clean

- Zero duplicate entity ids, names or relationship triples
- Zero broken cross-package references
- Zero orphan relationships
- Zero graph validation violations (10 checks)
- Zero package validation violations (10-13 checks per package)

## Recommended actions

| # | Action | Effort | Risk |
|---|---|---|---|
| 1 | Extend `build_graph.py` to extract Package007's 565 unmodelled rows | Medium | Low — additive |
| 2 | Delete 12 orphan `__pycache__` directories | Trivial | None |
| 3 | Document the id-convention split rather than retrofitting | Trivial | None |
| 4 | Decide: extend entity model for Hospital/Mandal, or declare the boundary | Decision | None |
| 5 | Leave all 23 sentinel columns alone | — | — |
