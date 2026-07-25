# Changelog — Package005_Agriculture

All notable changes to this package. Released versions are immutable; corrections ship as new
versions. Format follows [Keep a Changelog](https://keepachangelog.com/); this package uses
semantic versioning.

## [1.0.0] — 2026-07-24

First release. Promotes Package005 from an empty placeholder to a Stable 16-dataset agriculture
knowledge base.

### Added

**Reference taxonomies (Layer 1)**

- `crop_categories.csv` — 24 categories spanning botanical groups (12), production systems (4:
  organic, protected, hydroponics, aquaponics) and allied activities (8: forest produce,
  sericulture, apiculture, mushroom, fisheries, livestock, poultry, dairy). The
  `category_group` column distinguishes the three kinds.
- `soil_types.csv` — 10 soil classes from the ICAR-NBSS&LUP national classification, retaining
  all four problem-soil classes (saline, acidic, alkaline, clay).
- `climate_zones.csv` — 8 agro-climatic zones derived from the ICAR-CRIDA framing.

**Core entity (Layer 2)**

- `crops.csv` — 45 crops across all 12 crop-bearing categories, 25 columns covering season,
  duration, water requirement, soil preference, rainfall, temperature range, indicative yield,
  state and district footprint, organic viability, export potential, processing potential and
  mechanization level.

**Relational mappings (Layer 3)**

- `crop_soil_mapping.csv` — 90 mappings; every crop carries its optimal soil plus a documented
  alternative, scored 0–100 and banded Optimal / Suitable / Marginal.
- `crop_climate_mapping.csv` — 90 mappings; every crop against two zones with yield potential,
  risk level, and the specific `primary_climatic_risk` that matters in that zone.

**Domain layers (Layers 4–11)**

- `farm_machinery.csv` — 16 machinery types with automation level, AI readiness and applicable
  subsidy scheme.
- `agri_processing_opportunities.csv` — 17 value-add enterprise types with licence requirements
  and linked scheme.
- `farmer_producer_organizations.csv` — 5 collective organisation models.
- `agriculture_training.csv` — 7 training and extension provider categories.
- `agriculture_schemes.csv` — 12 central government schemes with eligibility and benefit.
- `crop_disease_management.csv` — 10 diseases and pests with chemical and biological control
  plus AI-detection feasibility.
- `market_linkages.csv` — 6 market channel types from APMC to export.
- `export_opportunities.csv` — 8 export segments with destination countries, quality
  requirements and certifications.
- `ai_precision_agriculture.csv` — the 10 named precision-agriculture technologies with Indian
  adoption level, AI readiness and binding constraint.

**Cross-package spine (Layer 12)**

- `agri_business_mapping.csv` — 30 mappings tracing crop → processing → Package004 business
  opportunity → Package006 skill.

**Release artifacts**

- `schemas/schema_catalog.json` — canonical PK/FK/column reference with per-dataset limitations.
- `metadata/*.metadata.json` — 16 per-dataset metadata files.
- `reports/*.collection_report.md` — 16 per-dataset collection reports.
- `registry/dataset_registry.csv` — release registry.
- `package_manifest.json`, `VERSION`, `validation_report.md`, `validation_summary.json`.
- `docs/METHODOLOGY.md`, `docs/USAGE.md`, `docs/DATA_DICTIONARY.md`, `docs/IMPORT_GUIDE.md`.
- `validate.py` — re-runnable 10-check validation engine.
- `enrich_datasets.py`, `regen_mappings.py`, `build_artifacts.py`, `build_docs.py` — generators,
  retained so the package is reproducible from source.

### Cross-package integration

- **Package006_Skills_and_Training** — hard foreign key on `package006_skill_id`. All 30
  `agri_business_mapping` rows carry real `skill_id` UUIDs read from the released `skills.csv`,
  across 4 distinct skills.
- **Package004_Industries** — hard foreign key on `package004_opportunity_name`. 17 of 30 rows
  resolve to exact opportunity names read from the released Package004 CSVs; 13 carry the bare
  sentinel because Package004 v1.0.0 has no counterpart.
- **Package001_Geography** — soft link only. `crops.major_districts` holds district names as
  free text where publicly attributable; no `dist_id` foreign key is asserted because
  per-district attribution is incomplete for 13 of 45 crops.
- **Package007_Government_Schemes / Package008_MSME** — not yet released; no links asserted.

### Validation

388 records, 6,062 cells, **0 violations** across 10 checks (structural, primary key,
provenance completeness, confidence integer/range/ceiling, bare-sentinel discipline,
verification-status enum, uniform collection date, in-package foreign keys with denormalised
name agreement, cross-package foreign keys, no blank cells).

Two real defects were caught by the checks before release:

1. **Sentinel-discipline breach (V5)** — a `crops.csv` note contained the literal token
   `PENDING_VERIFICATION` in prose, which would have corrupted naive sentinel counting. Note
   rewritten.
2. **Foreign key drift (V8)** — expanding `crops.csv` from 35 to 45 rows renumbered every
   `crop_id` above `crop-004`, silently invalidating all three mapping datasets. Caught by the
   denormalised-name check; mappings regenerated from the new IDs rather than hand-patched.

### Provenance

- Confidence range **50–78** against an **85** policy ceiling (never reached). The ceiling
  records that WebFetch to `.gov.in` / `.nic.in` / `.ac.in` is blocked by this environment's
  egress policy, so no row rests on a primary-source page read — the same constraint that
  applied to Package004 and Package006.
- Sentinel rate **2.18%** (132 of 6,062 cells), concentrated in costs (84 cells),
  not-applicable concepts, absent geographic footprint and unresolvable cross-package links.
  Eleven of sixteen datasets contain zero sentinels.
- All 388 rows are `VST-NEEDS_REVIEW`. **No row has had human data-steward sign-off.**

### Deliberately not asserted

- **No cost or investment figure anywhere.** `farm_machinery.investment_inr` and
  `annual_maintenance_inr` (all 16 rows), `agri_processing_opportunities.investment_band` and
  `capacity_indicative` (all 17 rows), and `ai_precision_agriculture.approximate_cost_inr` (all
  10 rows) are sentinelled. Equipment and plant prices are manufacturer- and model-dependent
  with no single official public figure; a plausible number would be fabrication.
  Package004_Industries carries sourced investment detail for the overlapping food-processing
  opportunities — that is the correct source.
- **No value-add percentages.** `agri_business_mapping` carries a qualitative
  `value_add_stage` label instead.
- **No zone-level yield tonnages.** `crop_climate_mapping.yield_potential` is an ordinal rating,
  because tonnage cannot be asserted at zone level without district qualification.

### Known limitations

- `avg_yield_tons_per_ha` is an indicative national average and is **not comparable across
  crops** with different harvested products (cotton is lint not seed cotton; turmeric is dry,
  ginger fresh; coconut is sentinelled because its unit is nuts per palm).
- `suitability_score` is ordinal and comparable within a crop only.
- Scheme benefit amounts change by budget cycle and state top-up; re-verify at the portal.
- Chemical treatments are named actives, not doses, and are subject to current CIB&RC label
  approval.
- The 8-zone climate model is a screening tool, not the 127-zone NARP classification.
- The 8 allied categories (livestock, poultry, dairy, fisheries, sericulture, apiculture,
  mushroom, forest produce) appear in `crop_categories.csv` but have **no dedicated entity
  datasets** in this release.

---

## [Unreleased] — planned for 1.1.0

- Dedicated entity datasets for the 8 allied categories — the largest gap in v1.0.0.
- Populate the 13 sentinelled Package004 opportunity links as Package004 expands its coverage.
- Package007_Government_Schemes and Package008_MSME foreign keys once those packages release.
- Convert `crops.major_districts` from free text to a hard Package001 `dist_id` foreign key,
  contingent on district-level crop statistics.
- Equipment and processing investment figures, contingent on DIC / MSME project profile access
  — this would clear 84 of the 132 sentinel cells.
- Human data-steward review to move rows from `VST-NEEDS_REVIEW` to `VST-VERIFIED`.

---

## [0.0.0] — 2026-07-20

- Placeholder `README.md` reserving Package005 for agriculture knowledge assets. No data.
