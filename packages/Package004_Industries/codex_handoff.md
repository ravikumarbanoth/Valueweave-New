# Codex Handoff — Package004_Industries_and_Livelihoods v1.0.0

Integration guide for an AI coding agent picking up this package, mirroring Package001-003's
`codex_handoff.md`.

## What this package is

5 CSV datasets (63 rows total) covering MSME & Entrepreneurship Support Schemes, Food & Agro-
Processing Micro-Enterprises, Construction & Skilled Trade Services, Digital & Technology
Livelihoods, and China-Inspired Adapted Opportunities, scoped to Telangana, Andhra Pradesh, and
national-level entities. This is a *narrow, real, cited* slice of a much larger ~150-sub-category
brief — see `acquisition_backlog.json` for everything not yet shipped. **This is Stable v1.0.0,
merged to main.**

## This is a Business Opportunity Knowledge Base, not just a classification list

4 of the 5 datasets (all except `msme_entrepreneurship_support_schemes`) carry a 36-column schema
built to answer practical entrepreneurship questions per opportunity: investment, machinery, raw
materials, suppliers, customers, training, licenses, government schemes, marketing channels, online
selling options, setup time, risks, seasonality, AI tools, automation, sustainability, future demand,
related businesses, district suitability, and success stories. `msme_entrepreneurship_support_schemes`
retains its original 15-column scheme/support-body schema — it characterizes support infrastructure,
not something a person starts, so the richer schema doesn't apply to it. See `docs/METHODOLOGY.md`
and `reports/business_opportunity_enrichment_summary.md`.

## Unlike Package001-003: this package catalogues opportunities, not institutions

Package001_Geography, Package002_Education, and Package003_Healthcare each catalogue discrete,
individually-verifiable entities (a district, a university, a hospital). This package catalogues
**livelihood/industry opportunities** — "Spice Processing" or "Plumbing" as an opportunity type, not a
specific named business. Do not expect this package's rows to map onto individual companies you
could look up and confirm exist; each row is a characterization of an opportunity, sourced wherever
possible to government project-profile documents or authoritative scheme/policy sources (plus, in
`china_inspired_adapted_opportunities.csv` only, explicitly-flagged Tier-5 qualitative sources for
color).

## Before you write any integration code

1. Read `README.md`, `docs/METHODOLOGY.md`, and `docs/USAGE.md` in full.
2. Understand that **no row is `VST-VERIFIED`** — every row is `VST-NEEDS_REVIEW`.
3. Understand that `investment_range_summary` and `minimum_investment` are NOT uniformly-structured
   numeric fields — `minimum_investment` is a specific rupee figure only where a government
   project-profile source exists (13.3% fill rate across the 4 enriched datasets); otherwise both
   fields may be the bare `PENDING_VERIFICATION` sentinel. See `docs/USAGE.md`.
4. This package's confidence scores (55-85) are lower on average than Package001-003 — this
   reflects a genuine difference in how sourceable this content is, not a quality regression. See
   `package_health_report.md`.
5. Estimated Monthly Revenue Range does not exist in this package's schema at all — it was dropped,
   not merely left unpopulated. Don't build a UI field expecting it.
6. 320 of 1,890 fields (16.93%) across the 4 enriched datasets are `PENDING_VERIFICATION` — this is
   *higher* than RC1's 1.9% because the schema tripled in size (18→36 columns), not because quality
   dropped. See `reports/business_opportunity_enrichment_summary.md` for the exact per-field table
   before building any UI that assumes a field is always populated.

## Data model

- 5 independent CSVs, each with a UUIDv4 `id` primary key, no enforced foreign keys between them or
  into other packages (see `schemas/schema_catalog.json`).
- No structured `district_id`/lat-long geo field in this package (unlike Package001-003) —
  `district_suitability_summary` is free text, not a foreign key into Package001_Geography.

## Validation before load

Run the same checks documented in `reports/validation_report.md` and the top-level
`validation_report.md` (PK uniqueness within and across datasets, column-count consistency, schema
column order, verification_status default) — they passed at build time and again after the v1.0.0
enrichment pass, but should be re-verified after any transform in your pipeline.

## What NOT to do

- Do not silently drop rows with `PENDING_VERIFICATION` fields.
- Do not infer/backfill missing fields — every unsourced field is deliberately `PENDING_VERIFICATION`
  rather than guessed; see `docs/METHODOLOGY.md`.
- Do not auto-promote `verification_status` to `VST-VERIFIED` anywhere in application code.
- Do not present `investment_range_summary` or `minimum_investment` as verified numeric figures in
  any UI without checking `confidence_score` first.
- Do not treat the 4 Tier-5-flagged rows/fields in `china_inspired_adapted_opportunities.csv` as
  equivalent-confidence to government/news-corroborated rows — check `notes` for the flag.
- Do not migrate `msme_entrepreneurship_support_schemes` to the 36-column schema without a genuine
  reason — it was left alone deliberately, not as an oversight.

## Extending this package

If you are asked to add one of the ~145 queued/blocked sub-categories, start from
`acquisition_backlog.json` for the specific unblock requirement, and follow the same collection
methodology in `docs/METHODOLOGY.md` (source-priority tiers including the Tier-5 qualitative-color
allowance, the investment fabrication-risk discipline, `PENDING_VERIFICATION` sentinel discipline)
rather than inventing a new approach per domain. If asked to close existing `PENDING_VERIFICATION`
gaps rather than add new domains, work from `reports/business_opportunity_enrichment_summary.md`'s
per-field fill-rate table to prioritize the weakest fields (`minimum_investment`,
`estimated_setup_time_summary`, `seasonal_factors_summary`, `working_capital_summary`,
`sustainability_summary`, `ai_tools_summary`).
