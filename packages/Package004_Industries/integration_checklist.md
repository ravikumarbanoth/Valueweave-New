# Integration Checklist — Package004_Industries_and_Livelihoods v1.0.0

Step-by-step checklist for an integrating agent, mirroring Package001-003's checklists.

1. [ ] Read `README.md`, `docs/METHODOLOGY.md`, and `docs/USAGE.md` in full before touching the data — in particular, understand that **no row in this release is `VST-VERIFIED`** and confidence scores are capped at 85 due to a WebFetch environment constraint present across both the RC1 and v1.0.0 enrichment passes.
2. [ ] Understand this package catalogues **livelihood/industry opportunities**, not individually-verified institutions — the relational model differs from Package001-003 (see `schemas/schema_catalog.json`).
3. [ ] Understand that 4 of the 5 datasets carry a 36-column Business Opportunity schema (investment, machinery, suppliers, training, licenses, schemes, marketing, AI tools, district suitability, success stories, etc.); `msme_entrepreneurship_support_schemes` deliberately retains its original 15-column schema. Do not treat the schema mismatch as an error.
4. [ ] Follow `imports/import_sequence.json` for load order (datasets are independent, so order does not affect referential integrity).
5. [ ] Validate each dataset against `schemas/schema_catalog.json` before loading — check column names/types/enums match, including the full 36-column list for the 4 enriched datasets.
6. [ ] Check primary key (`id`) uniqueness per dataset and across the package before accepting a batch (already verified — see `reports/validation_report.md` and top-level `validation_report.md` — but re-verify after any transform).
7. [ ] Do NOT treat `PENDING_VERIFICATION` as an empty string or null in downstream logic — treat it as an explicit "known unknown" sentinel distinct from missing data. It appears in 16.93% of fields across the 4 enriched datasets — see `reports/business_opportunity_enrichment_summary.md` for the per-field breakdown before assuming any field is reliably populated.
8. [ ] Do NOT treat `minimum_investment` or `investment_range_summary` as structured numeric fields you can parse and trust uniformly — both may be the bare `PENDING_VERIFICATION` sentinel or a descriptive summary with no hard number. Parse as free text; check `confidence_score` before surfacing.
9. [ ] Do NOT auto-promote any row's `verification_status` to `VST-VERIFIED` — that is a governance action requiring Data Steward + Reviewer sign-off against a directly-fetched primary source.
10. [ ] Check `notes` for Tier-5/anecdotal sourcing flags in `china_inspired_adapted_opportunities.csv` before surfacing `success_stories_summary` or similar fields with the same confidence as government/news-sourced rows.
11. [ ] Consult `acquisition_backlog.json` before assuming any of the ~145 un-shipped sub-categories simply "don't exist" in ValueWeave's plan — they are queued/blocked, not out of scope permanently.
12. [ ] Re-run `reports/validation_report.md`'s checks (PK uniqueness, column consistency, verification_status default, schema-column-order match, PENDING_VERIFICATION sentinel purity) after any downstream transform, before loading to a knowledge graph or application database.
13. [ ] Preserve `source_url` and `confidence_score` per row through any downstream pipeline — this package's evidence trail is the core deliverable, not just the facts themselves.
