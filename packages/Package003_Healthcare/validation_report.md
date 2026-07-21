# Package003_Healthcare v1.0.0-RC1 — Top-Level Validation Summary

This is the package-level validation summary required by the package brief's structure list. The
detailed per-dataset breakdown (identical checks, full per-dataset results) lives at
`reports/validation_report.md`; this file is the at-a-glance record of what was checked and the
overall result.

## Checks Performed

| Check | Result |
|---|---|
| All package files present per documented folder structure | PASS |
| All JSON files parse as valid JSON | PASS |
| All 4 CSV datasets have consistent column counts per row | PASS |
| All 4 CSV datasets have unique primary keys (`id`) within themselves | PASS |
| No `id` collisions across datasets (134 total rows checked) | PASS |
| CSV column order matches `schemas/schema_catalog.json` for every dataset | PASS |
| Every row's `verification_status` defaults to `VST-NEEDS_REVIEW` | PASS |
| Every row has `data_source`, `source_url`, `collection_date`, `confidence_score` populated | PASS |
| No confidence score exceeds 88 (the session's direct-fetch-unavailable ceiling) | PASS |
| No literal fabricated value found — unverifiable fields carry `PENDING_VERIFICATION` | PASS (spot-checked; full sentinel counts in `reports/missing_data`-equivalent sections of each quality report) |

## Overall Result: ALL CHECKS PASS

## What This Validation Does NOT Claim

- It does not claim any row's underlying facts are independently re-confirmed against a live primary
  source — that requires WebFetch access this session did not have (see `docs/METHODOLOGY.md`).
- It does not claim completeness against the full 40-domain brief — see `acquisition_backlog.json`
  for the 36 domains not yet researched.
- It does not claim `VST-VERIFIED` status for any row — promotion to verified is a separate
  governance action, not a validation outcome.

See `reports/validation_report.md` for the full per-dataset detail behind each PASS above.
