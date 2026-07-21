# Package 004 — Industries & Livelihoods Foundation
### ValueWeave.in Data Factory · Release v1.0.0-RC1 (NOT YET MERGED TO MAIN)

**This is Release Candidate 1**, submitted for review before any decision to promote this package to
canonical/merge to `main`, per explicit instruction. See `CHANGELOG.md` for the full itemized history.

## Purpose of This Package

This package is ValueWeave's Industries & Livelihoods knowledge foundation, built to help students,
job seekers, entrepreneurs, self-employed professionals, MSMEs, investors, local businesses, women
entrepreneurs, rural youth, and skilled workers discover opportunities in their local ecosystem.

**Unlike Package001_Geography, Package002_Education, and Package003_Healthcare**, this package
catalogues **livelihood/industry categories** (e.g. "Spice Processing", "Plumbing") rather than
discrete, individually-verifiable institutions. Each row characterizes an opportunity type, not a
specific named business — see `docs/METHODOLOGY.md` for what this means for how the data was
collected and should be interpreted.

## Scope of This Release

The full package brief named roughly 150 sub-categories across 13 category groups (Manufacturing,
Agriculture & Allied, Construction & Skilled Trades, Technology, Repair & Maintenance, Tourism &
Hospitality, Retail & Local Commerce, Recycling & Circular Economy, Service Businesses, Education &
Training, Health & Wellness, Local Entrepreneurship, and China-Inspired Opportunities), with ~25
fields to collect per entity. **This release covers 5 datasets** spanning a curated slice of that
scope — see `docs/METHODOLOGY.md` "Scope Decision" and "Field-Depth Scope Reduction." Everything not
shipped is tracked, not silently dropped: see `acquisition_backlog.json` and
`registry/dataset_registry.csv`.

## A Note on How This Data Was Collected

Every fact in this release was collected via the WebSearch tool. **Direct WebFetch to `.gov.in`,
`.ac.in`, and `.nic.in` domains was blocked for the entire collection session** by this environment's
organizational egress policy (confirmed HTTP 403 policy denial, re-tested live immediately before
collection began) — the same constraint documented in Package001-003. Numeric investment-range
figures were only accepted where traced to a specific government DIC/MSME/PMFME/KVIC project-profile
document; where no such source existed, the field is `PENDING_VERIFICATION` rather than a plausible
guess. Full detail in `docs/METHODOLOGY.md`.

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
├── reports/                   — collection reports, data dictionaries, quality/coverage/validation/etc. reports
├── evidence/                  — source-citation audit trail (incl. the WebFetch-block disclosure)
├── registry/                  — dataset_registry.csv, the cross-package control center
├── schemas/                   — schema_catalog.json, the canonical column/PK/FK reference
├── raw_sources/                — human-readable per-dataset source inventories
├── imports/                    — import_sequence.json and per-dataset import manifests
└── docs/                        — methodology and usage guides
```

## Dataset List

| Dataset | Records | Covers |
|---|---|---|
| MSME & Entrepreneurship Support Schemes | 18 | National + Telangana + Andhra Pradesh schemes/bodies |
| Food & Agro-Processing Micro-Enterprises | 13 | Spice/pickle/masala/oil/millet/seed processing opportunities |
| Construction & Skilled Trade Services | 11 | Plumbing, electrical, welding, carpentry, etc. |
| Digital & Technology Livelihoods | 12 | IT/software, web/app dev, digital marketing |
| China-Inspired Adapted Opportunities | 9 | Real Indian/Telugu-state adaptations of China-inspired business models |

**Total: 63 records across 5 datasets.**

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
   build time).
2. Every `verification_status` starts at `VST-NEEDS_REVIEW` on import — promotion to `VST-VERIFIED`
   is a governance action, never automatic.
3. Where sources conflicted (e.g. Telangana's MSME Policy 2024 vs. the older T-IDEA/T-PRIDE
   framework, Facebook Marketplace's actual India-launch status), the conflict is documented in the
   relevant `reports/*.collection_report.md` rather than silently resolved.

## Relationship to Future Packages and Domains

This release is intentionally narrow. `acquisition_backlog.json` lists all ~145 remaining
sub-categories (most of Manufacturing and Agriculture & Allied beyond processing, Tourism &
Hospitality, Repair & Maintenance, Retail & Local Commerce general, Recycling, other Service
Businesses, Education & Training businesses, Health & Wellness businesses, Local Entrepreneurship
food/craft businesses) and all Indian states/UTs beyond Telangana & Andhra Pradesh, each with a
specific reason it wasn't shipped and what would unblock it.

## Release Status

**RC1 — awaiting review.** Per instruction, this package will NOT be merged to `main` automatically.
See `reports/coverage_report.md`, `reports/known_gaps.md`, and this README's stats above for what to
review before a promotion decision.
