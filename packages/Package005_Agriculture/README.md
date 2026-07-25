# Package005_Agriculture v1.0.0

**ValueWeave.in Agriculture Intelligence and Agri-Business Knowledge Base**

| | |
|---|---|
| **Version** | 1.0.0 (Stable) |
| **Release date** | 2026-07-24 |
| **Datasets** | 16 |
| **Records** | 388 |
| **Validation** | PASS — 0 violations across 10 checks |
| **Confidence range** | 50–78 (policy ceiling 85) |
| **Sentinel rate** | 2.18% of cells (`PENDING_VERIFICATION`) |
| **Verification status** | `VST-NEEDS_REVIEW` — pending human data-steward sign-off |

## Purpose

Package005 models Indian agriculture as a connected graph rather than a list of crops. It
links land and climate to crop choice, crop choice to machinery and processing, processing to
business opportunity and skill, and the whole chain to the government schemes and market
channels that make it viable:

```
Geography → Climate → Soil → Crop → Farmer Institution → Machinery → Technology
     → Processing → Market → Export → Business → Scheme → Skill → AI Readiness
```

Crop selection is weighted to national significance plus Telangana and Andhra Pradesh
relevance, consistent with the rest of the knowledge base. The schema extends to any state
without modification.

## Datasets

Datasets are grouped into twelve layers. Load them in the order below — it is the dependency
order, and it is also recorded in `package_manifest.json` as `import_order`.

### Layer 1 — Reference taxonomies

| Dataset | Records | PK | Purpose |
|---|---|---|---|
| `crop_categories.csv` | 24 | `category_id` | Crop groups, production systems and allied activities |
| `soil_types.csv` | 10 | `soil_id` | Soil classes with pH band, texture and suitability |
| `climate_zones.csv` | 8 | `climate_zone_id` | Agro-climatic zones with rainfall and temperature bands |

### Layer 2 — Core entity

| Dataset | Records | PK | Purpose |
|---|---|---|---|
| `crops.csv` | 45 | `crop_id` | Agronomic and commercial profile per crop |

### Layer 3 — Relational mappings

| Dataset | Records | PK | Purpose |
|---|---|---|---|
| `crop_soil_mapping.csv` | 90 | `mapping_id` | Crop → soil suitability, scored 0–100 |
| `crop_climate_mapping.csv` | 90 | `mapping_id` | Crop → climate zone yield potential and dominant risk |

### Layers 4–11 — Domain layers

| Dataset | Records | PK | Layer |
|---|---|---|---|
| `farm_machinery.csv` | 16 | `machinery_id` | Capital and technology |
| `agri_processing_opportunities.csv` | 17 | `opportunity_id` | Value addition |
| `farmer_producer_organizations.csv` | 5 | `fpo_id` | Institutions |
| `agriculture_training.csv` | 7 | `training_id` | Institutions |
| `agriculture_schemes.csv` | 12 | `scheme_id` | Government support |
| `crop_disease_management.csv` | 10 | `disease_id` | Crop protection |
| `market_linkages.csv` | 6 | `linkage_id` | Market access |
| `export_opportunities.csv` | 8 | `opportunity_id` | Export |
| `ai_precision_agriculture.csv` | 10 | `technology_id` | AI and technology readiness |

### Layer 12 — Cross-package spine

| Dataset | Records | PK | Purpose |
|---|---|---|---|
| `agri_business_mapping.csv` | 30 | `mapping_id` | Crop → processing → Package004 opportunity → Package006 skill |

## Cross-package integration

| Package | Link type | Status |
|---|---|---|
| **Package001_Geography** | Soft (free-text district names in `crops.major_districts`) | No `dist_id` FK asserted — per-district attribution is incomplete |
| **Package004_Industries** | Hard FK on `package004_opportunity_name` | 17 of 30 resolve; 13 sentinelled (no Package004 counterpart in v1.0.0) |
| **Package006_Skills_and_Training** | Hard FK on `package006_skill_id` | All 30 resolve, across 4 distinct skill UUIDs |
| **Package007_Government_Schemes** | Planned | `agriculture_schemes.csv` is the agriculture slice to reconcile |
| **Package008_MSME** | Planned | `agri_processing_opportunities.csv` is the join surface |

Cross-package foreign keys are real values read out of the released packages, not descriptive
text. They are re-checked on every validation run.

## What this package does not assert

Being explicit about the gaps is part of the deliverable:

- **No cost or investment figures.** Every `investment_inr`, `annual_maintenance_inr`,
  `investment_band` and `approximate_cost_inr` field is the bare `PENDING_VERIFICATION`
  sentinel. Equipment and plant prices are set by manufacturer and model, and no single
  official public figure exists. A plausible-looking number here would be fabrication.
  Package004_Industries already carries sourced investment detail for the overlapping
  food-processing opportunities — use that, not an estimate from here.
- **Yields are indicative national averages**, not district figures, and are not comparable
  across crops with different harvested products (lint vs seed cotton, dry vs fresh rhizome,
  nuts per palm for coconut).
- **Scheme benefits change by budget cycle** and by state top-up. Re-verify against the
  scheme portal before relying on any amount.
- **Named chemical actives are not dose recommendations.** Pesticide legality and dosage are
  governed by current CIB&RC label approval.
- **The eight-zone climate model is a screening tool**, not the 127-zone NARP agro-ecological
  classification.
- **Allied categories have no entity datasets yet.** Livestock, poultry, dairy, fisheries,
  sericulture, apiculture and mushroom appear in `crop_categories.csv` but have no dedicated
  datasets in v1.0.0. They are the primary v1.1.0 target.

## Provenance model

Every row in every dataset carries six mandatory provenance columns:

| Column | Meaning |
|---|---|
| `data_source` | The authoritative body the fact is attributed to |
| `source_url` | Public URL for that body or scheme |
| `collection_date` | `2026-07-24`, uniform across the package |
| `confidence_score` | Integer 0–100, capped at 85 by policy |
| `verification_status` | `VST-NEEDS_REVIEW` |
| `notes` | Caveats and sourcing remarks |

### Confidence bands

| Band | Tier |
|---|---|
| 70–85 | Tier 1 — ICAR institutes, Ministry of Agriculture, statutory commodity boards, named scheme portals |
| 60–69 | Tier 2 — state departments, NABARD, MoFPI programme literature |
| 55–59 | Tier 3 — sector associations, published research aggregates |
| 50–54 | Tier 4 — forward-looking technology assessment (`ai_precision_agriculture` only, disclosed in-row) |

The 85 ceiling is a standing acknowledgement that WebFetch to `.gov.in` / `.nic.in` /
`.ac.in` domains is blocked in this environment, so no row rests on a primary-source page
read. The observed range is 50–78. The floor of 50 occurs only in
`ai_precision_agriculture`, where rows describe research-stage technology — there the low
score is the honest signal, not a defect.

### Sentinel discipline

`PENDING_VERIFICATION` appears only as a complete, bare cell value. It is never appended to
other text, never embedded in prose, and never substitutes for a numeric `confidence_score`.
A sentinel means no public source was found for that specific fact — not that the fact is
unknowable. Check V5 in `validate.py` enforces this, and it caught one real breach during
this release (a note whose prose contained the literal token).

## Validation

```bash
cd packages/Package005_Agriculture
python3 validate.py
```

Ten checks run on every invocation:

| Check | Enforces |
|---|---|
| V1 | Structural — every row matches its header's column count |
| V2 | Primary key unique and non-empty |
| V3 | All six provenance columns present on every dataset |
| V4 | `confidence_score` is an integer, 0–100, ≤ 85 ceiling |
| V5 | `PENDING_VERIFICATION` only as a bare exact string |
| V6 | `verification_status` drawn from the allowed enum |
| V7 | Uniform `collection_date` across the package |
| V8 | In-package FKs resolve, and denormalised name columns agree with their FK |
| V9 | Cross-package FKs resolve against Package004 and Package006 |
| V10 | No silently blank cells — a gap must be the sentinel |

Exit code 0 means release-clean. Machine-readable results land in
`validation_summary.json`; the narrative report is `validation_report.md`.

## Repository layout

```
Package005_Agriculture/
├── datasets/                  16 released CSVs
├── metadata/                  16 per-dataset metadata JSON files
├── reports/                   16 per-dataset collection reports
├── schemas/schema_catalog.json  canonical PK/FK/column reference
├── registry/dataset_registry.csv release registry
├── docs/
│   ├── METHODOLOGY.md         how the data was collected and scored
│   ├── USAGE.md               query patterns and join recipes
│   ├── DATA_DICTIONARY.md     every column in every dataset
│   └── IMPORT_GUIDE.md        load order and DDL guidance
├── package_manifest.json      package-level manifest
├── validation_report.md       narrative validation report
├── validation_summary.json    machine-readable validation output
├── validate.py                re-runnable validation engine
├── enrich_datasets.py         generator for the 5 profile datasets
├── regen_mappings.py          generator for the 3 mapping datasets
├── build_artifacts.py         generator for schemas/metadata/registry/reports
├── CHANGELOG.md
├── VERSION
└── README.md
```

The generator scripts are kept in the package deliberately: the datasets are reproducible
from source, and a reviewer can see exactly what was asserted and what was left sentinelled.

## Versioning

Released versions are immutable. Corrections and additions ship as new versions under
`Package005_Agriculture_vMAJOR.MINOR.PATCH`. See `CHANGELOG.md` for history and
`package_manifest.json` → `planned_next_release` for the v1.1.0 target.
