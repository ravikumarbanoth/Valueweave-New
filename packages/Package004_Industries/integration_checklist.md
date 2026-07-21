# Integration Checklist — Package004_Industries_and_Livelihoods v1.0.0-RC1

Step-by-step checklist for an integrating agent, mirroring Package001-003's checklists.

1. [ ] Read `README.md` and `docs/METHODOLOGY.md` in full before touching the data — in particular, understand that **no row in this release is `VST-VERIFIED`** and confidence scores are capped at 82 due to a WebFetch environment constraint.
2. [ ] Understand this package catalogues **livelihood/industry categories**, not individually-verified institutions — the relational model differs from Package001-003 (see `schemas/schema_catalog.json`).
3. [ ] Follow `imports/import_sequence.json` for load order (datasets are independent in RC1, so order does not affect referential integrity).
4. [ ] Validate each dataset against `schemas/schema_catalog.json` before loading — check column names/types/enums match.
5. [ ] Check primary key (`id`) uniqueness per dataset and across the package before accepting a batch (already verified at build time — see `reports/validation_report.md` and top-level `validation_report.md` — but re-verify after any transform).
6. [ ] Do NOT treat `PENDING_VERIFICATION` as an empty string or null in downstream logic — treat it as an explicit "known unknown" sentinel distinct from missing data.
7. [ ] Do NOT treat `typical_investment_range_summary` as a structured numeric range — in some datasets it is the bare `PENDING_VERIFICATION` sentinel, in others it is a descriptive qualitative summary with no hard number. Parse as free text; check `confidence_score` before surfacing.
8. [ ] Do NOT auto-promote any row's `verification_status` to `VST-VERIFIED` — that is a governance action requiring Data Steward + Reviewer sign-off against a directly-fetched primary source.
9. [ ] Consult `acquisition_backlog.json` before assuming any of the ~145 un-shipped sub-categories simply "don't exist" in ValueWeave's plan — they are queued/blocked, not out of scope permanently.
10. [ ] Re-run `reports/validation_report.md`'s checks (PK uniqueness, column consistency, verification_status default, schema-column-order match) after any downstream transform, before loading to a knowledge graph or application database.
11. [ ] Preserve `source_url` and `confidence_score` per row through any downstream pipeline — this package's evidence trail is the core deliverable, not just the facts themselves.
12. [ ] Do NOT promote this package to Stable/merge to `main` without explicit review approval — RC1 is a review candidate, not a final release.
