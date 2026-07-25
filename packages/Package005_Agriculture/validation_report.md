# Validation Report — Package005_Agriculture v1.0.0

**Result: PASS** · 0 violations · 16 datasets · 388 records · 6062 cells

Validated 2026-07-24 by `validate.py` (in-package, re-runnable). Machine-readable output in `validation_summary.json`.

## Checks run

| Check | Enforces | Result |
|---|---|---|
| V1 Structural | Every row matches its header's column count | PASS |
| V2 Primary key | First column unique and non-empty in all 16 datasets | PASS |
| V3 Provenance | All six provenance columns present on every dataset | PASS |
| V4 Confidence | Integer, 0–100, ≤ 85 policy ceiling | PASS |
| V5 Sentinel | `PENDING_VERIFICATION` only as a bare exact string | PASS |
| V6 Verification | `verification_status` in the allowed enum | PASS |
| V7 Collection date | Uniform `2026-07-24` package-wide | PASS |
| V8 In-package FK | FKs resolve; denormalised names agree with their FK | PASS |
| V9 Cross-package FK | Package004 and Package006 references resolve | PASS |
| V10 Empty cells | No silently blank cells — a gap must be the sentinel | PASS |

## Per-dataset results

| Dataset | Records | Cols | PK unique | Confidence | Avg | Sentinel cells | Blank |
|---|---|---|---|---|---|---|---|
| `crop_categories.csv` | 24 | 13 | ✓ | 57–78 | 72.1 | 0 | 0 |
| `soil_types.csv` | 10 | 15 | ✓ | 72–78 | 75.5 | 0 | 0 |
| `climate_zones.csv` | 8 | 16 | ✓ | 72–77 | 74.9 | 0 | 0 |
| `crops.csv` | 45 | 25 | ✓ | 66–78 | 74.4 | 25 | 0 |
| `crop_soil_mapping.csv` | 90 | 13 | ✓ | 65–78 | 73.5 | 0 | 0 |
| `crop_climate_mapping.csv` | 90 | 15 | ✓ | 65–78 | 73.4 | 0 | 0 |
| `farm_machinery.csv` | 16 | 18 | ✓ | 62–72 | 67.9 | 50 | 0 |
| `agri_processing_opportunities.csv` | 17 | 18 | ✓ | 62–70 | 66.9 | 34 | 0 |
| `farmer_producer_organizations.csv` | 5 | 12 | ✓ | 68–75 | 71.6 | 0 | 0 |
| `agriculture_training.csv` | 7 | 13 | ✓ | 64–77 | 71.1 | 0 | 0 |
| `agriculture_schemes.csv` | 12 | 13 | ✓ | 69–78 | 73.2 | 0 | 0 |
| `crop_disease_management.csv` | 10 | 14 | ✓ | 65–76 | 72.4 | 0 | 0 |
| `market_linkages.csv` | 6 | 12 | ✓ | 66–76 | 70.0 | 0 | 0 |
| `export_opportunities.csv` | 8 | 13 | ✓ | 71–77 | 74.1 | 0 | 0 |
| `ai_precision_agriculture.csv` | 10 | 16 | ✓ | 50–66 | 58.2 | 10 | 0 |
| `agri_business_mapping.csv` | 30 | 15 | ✓ | 62–74 | 69.0 | 13 | 0 |
| **package** | **388** | — | ✓ | **50–78** | — | **132** (2.18%) | **0** |

## Cross-package foreign key integrity (V9)

Both external FK sets were resolved by reading the released packages directly, not by matching on remembered names. They are re-checked on every validation run, so a rename upstream fails the build rather than silently breaking.

| Reference | Target | Resolved | Sentinel | Unresolved |
|---|---|---|---|---|
| `agri_business_mapping.package006_skill_id` | Package006 `skills.csv` `skill_id` | 30 | 0 | **0** |
| `agri_business_mapping.package004_opportunity_name` | Package004 `name` / `adapted_indian_concept` | 17 | 13 | **0** |

The 13 sentinelled Package004 links are not failures. Package004 v1.0.0 has no counterpart opportunity for rice milling, dal milling, jaggery, cold storage, essential-oil distillation, animal feed, vermicompost or cashew shelling. Pointing them at the nearest loosely-similar row would have produced a wrong FK, which is worse than an absent one: it silently corrupts every join that uses it. They become populatable when Package004 expands.

## In-package foreign key integrity (V8)

| Reference | Target | Rows | Result |
|---|---|---|---|
| `crops.category_id` | `crop_categories.category_id` | 45 | PASS |
| `crop_soil_mapping.crop_id` | `crops.crop_id` | 90 | PASS |
| `crop_soil_mapping.soil_id` | `soil_types.soil_id` | 90 | PASS |
| `crop_climate_mapping.crop_id` | `crops.crop_id` | 90 | PASS |
| `crop_climate_mapping.climate_zone_id` | `climate_zones.climate_zone_id` | 90 | PASS |
| `agri_business_mapping.crop_id` | `crops.crop_id` | 30 | PASS |
| `agri_business_mapping.processing_opportunity_id` | `agri_processing_opportunities.opportunity_id` | 30 | PASS |

V8 also verifies the **denormalised name columns** (`crop_name`, `soil_name`, `climate_zone_name`, `processing_opportunity_name`) agree with the row their ID points at. This is what caught the `crop_id` renumbering when `crops.csv` expanded from 35 to 45 rows and shifted every ID past `crop-004`; the three mapping datasets were regenerated rather than patched.

## Issues found and resolved during validation

Two real defects were caught by the checks before release:

**1. Sentinel-discipline breach (V5).** A `crops.csv` note read *"district attribution left PENDING_VERIFICATION"* — prose containing the literal sentinel token. This would have made any naive sentinel count wrong, and blurs the line between "this cell has no data" and "this cell describes missing data". The note was rewritten to *"district attribution not asserted in this release"*.

**2. Foreign key drift (V8).** Expanding `crops.csv` from 35 to 45 rows renumbered every `crop_id` above `crop-004`, silently invalidating all three mapping datasets — chickpea moved from `crop-008` to `crop-009`, turmeric from `crop-029` to `crop-035`, and so on. V8's denormalised-name check surfaced it immediately. The mappings were regenerated from the new IDs, not hand-corrected.

## Confidence distribution

Package range **50–78**, ceiling **85** (never reached).

The ceiling exists because WebFetch to `.gov.in` / `.nic.in` / `.ac.in` is blocked by this environment's egress policy, so no row in this package rests on a primary-source page read. Ranked lowest-confidence first, since that is where a reviewer should look:

| Dataset | Avg | Range | Why |
|---|---|---|---|
| `ai_precision_agriculture.csv` | 58.2 | 50–66 | Forward-looking technology assessment; rows for robotics, autonomous tractors and digital twins describe research stages, not products |
| `agri_processing_opportunities.csv` | 66.9 | 62–70 | Investment and capacity unsourceable; scored on licence and scheme attribution only |
| `farm_machinery.csv` | 67.9 | 62–72 | Equipment prices are manufacturer-set with no official public figure |
| `agri_business_mapping.csv` | 69.0 | 62–74 | 13 of 30 Package004 links have no counterpart to resolve against |
| `market_linkages.csv` | 70.0 | 66–76 | Channel-type description; institution counts move over time |
| `agriculture_training.csv` | 71.1 | 64–77 | Provider categories rather than named institutions |
| `farmer_producer_organizations.csv` | 71.6 | 68–75 | Organisation types rather than a named registry |
| `crop_categories.csv` | 72.1 | 57–78 | Hydroponics and aquaponics categories have sparse Indian documentation |
| `crop_disease_management.csv` | 72.4 | 65–76 | Named actives are label-dependent and change with CIB&RC approval |
| `agriculture_schemes.csv` | 73.2 | 69–78 | Benefit amounts change by budget cycle and state top-up |
| `crop_climate_mapping.csv` | 73.4 | 65–78 | Ordinal agro-climatic ratings from ICAR guidance |
| `crop_soil_mapping.csv` | 73.5 | 65–78 | Ordinal suitability ratings from ICAR guidance |
| `export_opportunities.csv` | 74.1 | 71–77 | APEDA and board attribution; prices and volumes are indicative only |
| `crops.csv` | 74.4 | 66–78 | Stable published agronomy from ICAR crop institutes |
| `climate_zones.csv` | 74.9 | 72–77 | ICAR-CRIDA framing, collapsed to an eight-zone screening model |
| `soil_types.csv` | 75.5 | 72–78 | ICAR-NBSS&LUP national soil classification |

The floor of 50 is confined to `ai_precision_agriculture`. That is deliberate: those rows describe research-stage technology, and the low score is the finding. Padding them upward to make the package look uniform would misrepresent the state of Indian precision agriculture.

## Sentinel distribution

**132 of 6062 cells (2.18%)** carry the bare sentinel. The concentration is the point — it is not spread thinly across the package but clustered in exactly the fields that could not be sourced without a primary page read:

| Dataset | Column | Rows |
|---|---|---|
| `agri_processing_opportunities.csv` | `investment_band` | 17 / 17 |
| `agri_processing_opportunities.csv` | `capacity_indicative` | 17 / 17 |
| `farm_machinery.csv` | `investment_inr` | 16 / 16 |
| `farm_machinery.csv` | `annual_maintenance_inr` | 16 / 16 |
| `crops.csv` | `major_districts` | 14 / 45 |
| `agri_business_mapping.csv` | `package004_opportunity_name` | 13 / 30 |
| `farm_machinery.csv` | `power_hp` | 10 / 16 |
| `ai_precision_agriculture.csv` | `approximate_cost_inr` | 10 / 10 |
| `crops.csv` | `duration_days` | 9 / 45 |
| `farm_machinery.csv` | `capacity` | 7 / 16 |
| `crops.csv` | `avg_yield_tons_per_ha` | 2 / 45 |
| `farm_machinery.csv` | `subsidy_scheme` | 1 / 16 |

Eleven of the sixteen datasets contain **zero** sentinels. The 132 that exist are almost entirely costs (84 cells across machinery, processing and precision agriculture), not-applicable concepts (`duration_days` on perennials), absent geographic footprint (`major_districts` for non-TG/AP crops), and unresolvable cross-package links.

## Verification status

**All 388 records are `VST-NEEDS_REVIEW`.** Nothing in this package has had human data-steward sign-off. Machine validation confirms structural and referential integrity and provenance completeness; it does not confirm factual accuracy. Consumers should treat every row as reviewed-by-machine only.

## Reproducing this report

```bash
cd packages/Package005_Agriculture
python3 validate.py       # writes validation_summary.json, exit 0 = clean
python3 build_docs.py     # regenerates this report from that summary
```

Every figure above is derived from the released CSVs rather than hand-maintained, so this report cannot drift out of agreement with the data it describes.
