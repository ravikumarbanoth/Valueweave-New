# Package004_Industries_and_Livelihoods v1.0.0 — Validation Report

Re-run after the v2 deep-enrichment pass that expanded 4 of 5 datasets to the 36-column Business
Opportunity schema (2026-07-24).

## msme_entrepreneurship_support_schemes (unchanged, 15 columns)

- Primary key uniqueness: PASS
- Column count consistency across all rows: PASS
- verification_status defaults to VST-NEEDS_REVIEW: PASS
- CSV column order matches schema_catalog.json: PASS

## food_agro_processing_micro_enterprises (enriched, 36 columns)

- Primary key uniqueness: PASS
- Column count consistency across all rows: PASS (13/13 rows, 36 columns each)
- verification_status defaults to VST-NEEDS_REVIEW: PASS
- CSV column order matches schema_catalog.json: PASS
- PENDING_VERIFICATION sentinel purity (no cell starts with the sentinel plus appended text): PASS (0 violations; 26 violations found and fixed during the enrichment draft, before this validation run)

## construction_skilled_trade_services (enriched, 36 columns)

- Primary key uniqueness: PASS
- Column count consistency across all rows: PASS (11/11 rows, 36 columns each)
- verification_status defaults to VST-NEEDS_REVIEW: PASS
- CSV column order matches schema_catalog.json: PASS
- PENDING_VERIFICATION sentinel purity: PASS (0 violations; 89 violations found and fixed during the enrichment draft, before this validation run)

## digital_technology_livelihoods (enriched, 36 columns)

- Primary key uniqueness: PASS
- Column count consistency across all rows: PASS (12/12 rows, 36 columns each)
- verification_status defaults to VST-NEEDS_REVIEW: PASS
- CSV column order matches schema_catalog.json: PASS
- PENDING_VERIFICATION sentinel purity: PASS (0 violations; 83 violations found and fixed during the enrichment draft, before this validation run)

## china_inspired_adapted_opportunities (enriched, 36 columns)

- Primary key uniqueness: PASS
- Column count consistency across all rows: PASS (9/9 rows, 36 columns each)
- verification_status defaults to VST-NEEDS_REVIEW: PASS
- CSV column order matches schema_catalog.json: PASS
- PENDING_VERIFICATION sentinel purity: PASS (0 violations)

## Cross-dataset checks

- Cross-dataset ID collisions: PASS (0 found across all 63 rows)
- Every row has non-empty data_source, source_url, collection_date, confidence_score: PASS
- No confidence_score outside [0, 85]: PASS (observed range 55-85)

## Overall: ALL CHECKS PASS

Verified programmatically against `schemas/schema_catalog.json` immediately before promotion to
Stable v1.0.0 — see `reports/business_opportunity_enrichment_summary.md` for the content-depth
(field-fill-rate) analysis this structural validation does not cover.
