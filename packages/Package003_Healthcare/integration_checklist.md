# Integration Checklist — Package003_Healthcare v1.0.0-RC1

Step-by-step checklist for an integrating agent, mirroring Package001_Geography and Package002_Education's checklists.

1. [ ] Read `README.md` and `docs/METHODOLOGY.md` in full before touching the data — in particular, understand that **no row in this release is `VST-VERIFIED`** and confidence scores are capped at 88 due to a WebFetch environment constraint.
2. [ ] Follow `imports/import_sequence.json` for load order (datasets are independent in RC1, so order does not affect referential integrity).
3. [ ] Validate each dataset against `schemas/schema_catalog.json` before loading — check column names/types/enums match.
4. [ ] Check primary key (`id`) uniqueness per dataset and across the package before accepting a batch (already verified at build time — see `reports/validation_report.md` and top-level `validation_report.md` — but re-verify after any transform).
5. [ ] Do NOT treat `PENDING_VERIFICATION` as an empty string or null in downstream logic — treat it as an explicit "known unknown" sentinel distinct from missing data.
6. [ ] Do NOT auto-promote any row's `verification_status` to `VST-VERIFIED` — that is a governance action requiring Data Steward + Reviewer sign-off against a directly-fetched primary source.
7. [ ] Do NOT treat `medical_colleges_telangana_andhra_pradesh.attached_teaching_hospital` and `government_hospitals_telangana_andhra_pradesh.medical_college_affiliation` as an enforced relational join — these are free-text cross-references collected independently and may not match exactly.
8. [ ] If wiring this package's `state`/`district` fields to Package001_Geography, note there are no FK columns yet in RC1 — any join must be done by name-matching with manual review.
9. [ ] Consult `acquisition_backlog.json` before assuming any of the 36 un-shipped healthcare domains simply "don't exist" in ValueWeave's plan — they are queued/blocked, not out of scope permanently. PHC/CHC/Urban Health Centres are BLOCKED specifically because their scale requires a bulk data source, not more per-institution research.
10. [ ] Re-run `reports/validation_report.md`'s checks (PK uniqueness, column consistency, verification_status default, schema-column-order match) after any downstream transform, before loading to a knowledge graph or application database.
11. [ ] Preserve `source_url` and `confidence_score` per row through any downstream pipeline — this package's evidence trail is the core deliverable, not just the facts themselves.
12. [ ] Do NOT promote this package to Stable/merge to `main` without explicit review approval — RC1 is a review candidate, not a final release.
