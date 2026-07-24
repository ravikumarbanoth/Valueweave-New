# Package 004 — Industries & Livelihoods: Business Opportunity Knowledge Base
### ValueWeave.in Data Factory · Release v1.0.0 (Stable — merged to main)

See `CHANGELOG.md` for the full itemized history, including the RC1 → v1.0.0 evolution.

## Purpose of This Package

This package is ValueWeave's Business Opportunity Knowledge Base, built to help students, job
seekers, entrepreneurs, self-employed professionals, MSMEs, investors, local businesses, women
entrepreneurs, rural youth, and skilled workers not just discover an opportunity, but act on it —
answering questions like: *What business can I start in my district? How much investment is needed?
Where can I get training? Which government schemes support it? Who are the suppliers? Who buys the
products? What machinery is required? Which AI tools can help? Which successful businesses already
exist nearby?*

**Unlike Package001_Geography, Package002_Education, and Package003_Healthcare**, this package
catalogues **livelihood/industry opportunities** (e.g. "Spice Processing", "Plumbing") rather than
discrete, individually-verifiable institutions. Each row characterizes an opportunity type, not a
specific named business — see `docs/METHODOLOGY.md` for what this means for how the data was
collected and should be interpreted.

## From Industry Classification to Business Opportunity Knowledge Base

This package shipped in two stages:

1. **RC1 (2026-07-22)** — an Industry Classification Package: 5 datasets, 63 rows, an 18/15-column
   core schema (identity, category, description, target customers, investment range where sourced,
   skill level, training, licenses, government schemes, rural/urban suitability).
2. **v1.0.0 (2026-07-24, this release)** — a deep-enrichment pass expanded 4 of the 5 datasets to a
   36-column Business Opportunity schema, adding ideal target audience, minimum investment, working
   capital, machinery/equipment, raw materials, supplier ecosystem, customer segments, training
   providers, marketing channels, online selling options, estimated setup time, typical risks,
   seasonal factors, AI tools, automation opportunities, sustainability, future demand, related
   businesses, district suitability, and success stories — wherever reliable public information
   exists. See `reports/business_opportunity_enrichment_summary.md` for exactly what filled and what
   didn't.

`msme_entrepreneurship_support_schemes` — the scheme/support-body reference dataset — was
intentionally left at its original schema; it characterizes support infrastructure, not individual
opportunities. See `docs/METHODOLOGY.md`.

## Scope of This Release

The full package brief named roughly 150 sub-categories across 13 category groups (Manufacturing,
Agriculture & Allied, Construction & Skilled Trades, Technology, Repair & Maintenance, Tourism &
Hospitality, Retail & Local Commerce, Recycling & Circular Economy, Service Businesses, Education &
Training, Health & Wellness, Local Entrepreneurship, and China-Inspired Opportunities). **This
release covers 5 datasets** spanning a curated slice of that scope, now enriched to Business
Opportunity depth for 4 of the 5 — see `docs/METHODOLOGY.md` "Scope Decision" and "The v2
Deep-Enrichment Pass." Everything not shipped is tracked, not silently dropped: see
`acquisition_backlog.json` and `registry/dataset_registry.csv`.

## A Note on How This Data Was Collected

Every fact in this release was collected via the WebSearch tool. **Direct WebFetch to `.gov.in`,
`.ac.in`, and `.nic.in` domains was blocked for the entire collection session** by this environment's
organizational egress policy (confirmed HTTP 403 policy denial, re-tested live immediately before
both the RC1 pass and the v2 enrichment pass) — the same constraint documented in Package001-003.
Numeric investment figures were only accepted where traced to a specific government DIC/MSME/PMFME/
KVIC project-profile document; where no such source existed, the field is `PENDING_VERIFICATION`
rather than a plausible guess. `china_inspired_adapted_opportunities.csv` additionally draws on
explicitly-flagged Tier-5 qualitative sources (founder interviews, forums, YouTube creators) for
color, per the enrichment brief. Full detail in `docs/METHODOLOGY.md`.

## Folder Structure

```
Package004_Industries/
├── README.md                 — this file
├── package_manifest.json     — machine-readable package descriptor
├── CHANGELOG.md               — version history
├── VERSION                    — current version string
├── codex_handoff.md           — integration guide for an AI coding agent
├── integration_checklist.md   — step-by-step integration checklist
├── package_health_report.md   — coverage/completion/readiness scoring
├── validation_report.md       — top-level validation summary
├── acquisition_backlog.json   — every un-shipped sub-category and what unblocks it
├── datasets/                  — the production CSVs
├── metadata/                  — source catalogues, confidence calibration, provenance stats
├── reports/                   — collection/enrichment reports, data dictionaries, quality/coverage/validation/etc. reports
├── evidence/                  — source-citation audit trail (incl. the WebFetch-block disclosure)
├── registry/                  — dataset_registry.csv, the cross-package control center
├── schemas/                   — schema_catalog.json, the canonical column/PK/FK reference
├── raw_sources/                — human-readable per-dataset source inventories
├── imports/                    — import_sequence.json and per-dataset import manifests
└── docs/                        — methodology and usage guides
```

## Dataset List

| Dataset | Records | Columns | Covers |
|---|---|---|---|
| MSME & Entrepreneurship Support Schemes | 18 | 15 | National + Telangana + Andhra Pradesh schemes/bodies |
| Food & Agro-Processing Micro-Enterprises | 13 | 36 | Spice/pickle/masala/oil/millet/seed processing opportunities |
| Construction & Skilled Trade Services | 11 | 36 | Plumbing, electrical, welding, carpentry, etc. |
| Digital & Technology Livelihoods | 12 | 36 | IT/software, web/app dev, digital marketing |
| China-Inspired Adapted Opportunities | 9 | 36 | Real Indian/Telugu-state adaptations of China-inspired business models |

**Total: 63 records across 5 datasets, 159 total columns.**

## Import Instructions

Follow `imports/import_sequence.json`. All 5 datasets are independent in this release (no
inter-dataset foreign keys) — see `schemas/schema_catalog.json`.

## Evidence Policy

Every dataset carries per-row provenance (`data_source`, `source_url`, `collection_date`,
`confidence_score`, `verification_status`, `notes`) and a corresponding entry in `evidence/`
documenting exactly what was searched and the environment constraint that shaped this release's
sourcing method. No row in this package was fabricated, estimated, or inferred — unverifiable
numeric claims carry the literal sentinel `PENDING_VERIFICATION` rather than a plausible guess.

## Validation Process

1. Primary key uniqueness (within and across datasets), column-count consistency, schema-column-order
   match, and default `verification_status` are checked programmatically for every dataset — see
   `reports/validation_report.md` and the top-level `validation_report.md` (all checks passed at
   both RC1 build time and again after the v1.0.0 enrichment pass, before promotion to Stable).
2. Every `verification_status` starts at `VST-NEEDS_REVIEW` on import — promotion to `VST-VERIFIED`
   is a governance action, never automatic.
3. Where sources conflicted (e.g. Telangana's MSME Policy 2024 vs. the older T-IDEA/T-PRIDE
   framework, Facebook Marketplace's actual India-launch status), the conflict is documented in the
   relevant `reports/*.collection_report.md` or `reports/*.enrichment_v2_report.md` rather than
   silently resolved.

## Relationship to Future Packages and Domains

This release remains intentionally narrow on *domain* coverage even though it deepened
*content* per opportunity. `acquisition_backlog.json` lists all ~145 remaining sub-categories (most
of Manufacturing and Agriculture & Allied beyond processing, Tourism & Hospitality, Repair &
Maintenance, Retail & Local Commerce general, Recycling, other Service Businesses, Education &
Training businesses, Health & Wellness businesses, Local Entrepreneurship food/craft businesses) and
all Indian states/UTs beyond Telangana & Andhra Pradesh, each with a specific reason it wasn't shipped
and what would unblock it.

## Release Status

**Stable v1.0.0 — merged to main.** See `reports/coverage_report.md`,
`reports/business_opportunity_enrichment_summary.md`, `reports/known_gaps.md`, and this README's
stats above for the full picture of what's included and what remains a disclosed gap.
