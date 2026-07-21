# Codex Handoff — Package004_Industries_and_Livelihoods v1.0.0-RC1

Integration guide for an AI coding agent picking up this package, mirroring Package001-003's
`codex_handoff.md`.

## What this package is

5 CSV datasets (63 rows total) covering MSME & Entrepreneurship Support Schemes, Food & Agro-
Processing Micro-Enterprises, Construction & Skilled Trade Services, Digital & Technology
Livelihoods, and China-Inspired Adapted Opportunities, scoped to Telangana, Andhra Pradesh, and
national-level entities. This is a *narrow, real, cited* slice of a much larger ~150-sub-category
brief — see `acquisition_backlog.json` for everything not yet shipped. **This is RC1 — not yet
merged to main.**

## Unlike Package001-003: this package catalogues categories, not institutions

Package001_Geography, Package002_Education, and Package003_Healthcare each catalogue discrete,
individually-verifiable entities (a district, a university, a hospital). This package catalogues
**livelihood/industry categories** — "Spice Processing" or "Plumbing" as an opportunity type, not a
specific named business. Do not expect this package's rows to map onto individual companies you
could look up and confirm exist; each row is a characterization of an opportunity, sourced wherever
possible to government project-profile documents or authoritative scheme/policy sources.

## Before you write any integration code

1. Read `README.md`, `docs/METHODOLOGY.md`, and `docs/USAGE.md` in full.
2. Understand that **no row is `VST-VERIFIED`** — every row is `VST-NEEDS_REVIEW`.
3. Understand that `typical_investment_range_summary` is NOT a uniformly-structured numeric field —
   in some datasets it's the bare `PENDING_VERIFICATION` sentinel, in others a descriptive
   qualitative summary. See `docs/USAGE.md` for the exact breakdown per dataset.
4. This package's confidence scores (48-82) are lower on average than Package001-003 — this
   reflects a genuine difference in how sourceable this content is, not a quality regression. See
   `package_health_report.md`.
5. Estimated Monthly Revenue Range does not exist in this package's schema at all — it was dropped,
   not merely left unpopulated. Don't build a UI field expecting it.

## Data model

- 5 independent CSVs, each with a UUIDv4 `id` primary key, no enforced foreign keys between them or
  into other packages (see `schemas/schema_catalog.json`).
- No `district`/geo field in this package (unlike Package001-003) — the unit of analysis is a
  category, not a sited institution.

## Validation before load

Run the same checks documented in `reports/validation_report.md` and the top-level
`validation_report.md` (PK uniqueness within and across datasets, column-count consistency, schema
column order, verification_status default) — they passed at build time but should be re-verified
after any transform in your pipeline.

## What NOT to do

- Do not silently drop rows with `PENDING_VERIFICATION` fields.
- Do not infer/backfill missing fields (revenue range, machinery, raw materials, business risks, AI
  opportunities, market trends, etc.) — they were deliberately left out of scope for RC1 rather than
  guessed; see `docs/METHODOLOGY.md` "Field-Depth Scope Reduction."
- Do not auto-promote `verification_status` to `VST-VERIFIED` anywhere in application code.
- Do not merge this package to `main` or otherwise treat it as canonical — it is RC1, explicitly
  awaiting review before promotion to Stable.
- Do not present `typical_investment_range_summary`'s qualitative descriptions as if they were
  verified numeric ranges in any UI.

## Extending this package

If you are asked to add one of the ~145 queued/blocked sub-categories, start from
`acquisition_backlog.json` for the specific unblock requirement, and follow the same collection
methodology in `docs/METHODOLOGY.md` (source-priority tiers, the investment-range fabrication-risk
discipline, PENDING_VERIFICATION sentinel discipline) rather than inventing a new approach per
domain. Pay special attention to the analytical fields (Business Risks, AI Opportunities, Market
Trends, Future Potential) that were explicitly descoped in RC1 — populating them well requires a
distinct, source-grounded methodology, not just more of the same research pattern.
