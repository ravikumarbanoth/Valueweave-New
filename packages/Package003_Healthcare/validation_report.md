# Package003_Healthcare v1.0.0-RC2 — Top-Level Validation Summary

This is the package-level validation summary; the detailed per-dataset breakdown lives at
`reports/validation_report.md`.

## Checks Performed

| Check | Result |
|---|---|
| All package files present per documented folder structure | PASS |
| All JSON files parse as valid JSON | PASS |
| All 4 CSV datasets have consistent column counts per row | PASS |
| All 4 CSV datasets have unique primary keys (`id`) within themselves | PASS |
| No `id` collisions across datasets (146 total rows checked) | PASS |
| CSV column order matches `schemas/schema_catalog.json` for every dataset (including the 4 new hospital columns and 3 new college columns) | PASS |
| Every row's `verification_status` defaults to `VST-NEEDS_REVIEW` | PASS |
| Every row has `data_source`, `source_url`, `collection_date`, `confidence_score` populated | PASS |
| No confidence score exceeds 88 | PASS |
| No literal fabricated value found — unverifiable fields carry `PENDING_VERIFICATION` | PASS |

## Overall Result: ALL CHECKS PASS

## RC1 → RC2 Record Growth

| Dataset | RC1 | RC2 | Delta |
|---|---|---|---|
| medical_regulatory_bodies_and_health_missions | 23 | 24 | +1 |
| medical_colleges_telangana_andhra_pradesh | 54 | 58 | +4 |
| government_hospitals_telangana_andhra_pradesh | 49 | 55 | +6 |
| government_health_insurance_schemes | 8 | 9 | +1 |
| **Total** | **134** | **146** | **+12** |

## What This Validation Does NOT Claim

- It does not claim any row's underlying facts are independently re-confirmed against a live primary
  source — WebFetch access was re-confirmed blocked immediately before RC2 enrichment began.
- It does not claim completeness against the full 40-domain brief.
- It does not claim `VST-VERIFIED` status for any row.

See `reports/validation_report.md` for the full per-dataset detail and
`reports/rc1_vs_rc2_comparison.md` for the complete enrichment diff.
