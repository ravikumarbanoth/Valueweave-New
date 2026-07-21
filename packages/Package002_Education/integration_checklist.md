# Integration Checklist — Package002_Education v1.0.0

Step-by-step checklist for an integrating agent (Codex or otherwise), mirroring Package001_Geography's checklist.

1. [ ] Read `README.md` and `docs/METHODOLOGY.md` in full before touching the data — in particular, understand that **no row in this release is `VST-VERIFIED`** and confidence scores are capped due to a WebFetch environment constraint (see below).
2. [ ] Follow `imports/import_sequence.json` for load order (datasets are independent in v1.0.0, so order does not affect referential integrity, but the file documents the intended sequence).
3. [ ] Validate each dataset against `schemas/schema_catalog.json` before loading — check column names/types/enums match.
4. [ ] Check primary key (`id`) uniqueness per dataset before accepting a batch (already verified at build time — see `reports/validation_report.md` — but re-verify after any transform).
5. [ ] Do NOT treat `PENDING_VERIFICATION` as an empty string or null in downstream logic — treat it as an explicit "known unknown" sentinel distinct from missing data.
6. [ ] Do NOT auto-promote any row's `verification_status` to `VST-VERIFIED` — that is a governance action requiring Data Steward + Reviewer sign-off against a directly-fetched primary source, per package policy.
7. [ ] If wiring this package's `state`/`jurisdiction` fields to Package001_Geography, note there are no FK columns yet in v1.0.0 — this is deliberate (see `schemas/schema_catalog.json` relationship note) and any join must be done by name-matching with manual review, not treated as a verified FK relationship.
8. [ ] Consult `acquisition_backlog.json` before assuming any of the 36 un-shipped education domains simply "don't exist" in ValueWeave's plan — they are queued/blocked, not out of scope permanently.
9. [ ] Re-run `reports/validation_report.md`'s checks (PK uniqueness, column consistency, verification_status default) after any downstream transform, before loading to a knowledge graph or application database.
10. [ ] Preserve `source_url` and `confidence_score` per row through any downstream pipeline — this package's evidence trail is the core deliverable, not just the facts themselves.
