# Package 003 — Healthcare Foundation
### ValueWeave.in Data Factory · Release v1.0.0-RC1 (NOT YET MERGED TO MAIN)

**This is Release Candidate 1**, submitted for review before any decision to promote this package to
canonical/merge to `main`, per explicit instruction. See `CHANGELOG.md` for the full itemized history.

## Purpose of This Package

This package is ValueWeave's Healthcare knowledge foundation. It anchors healthcare-domain entities
(regulatory bodies, medical colleges, government hospitals, health insurance schemes) that future
packages and application features will reference. Like Package002_Education, this package does not
yet declare enforced foreign keys into other packages — its `state`/`district` fields are free-text
values, not verified relational links (see `schemas/schema_catalog.json`).

## Scope of This Release

The full package brief named 40 healthcare data domains across all of India, with ~30 fields to
collect per entity. **This release covers 4 of those 40 domains**, scoped to Telangana, Andhra
Pradesh, and genuinely national-level entities, with a reduced per-entity field set. This was a
deliberate scoping decision directly following the brief's own instruction to "prioritize depth,
accuracy and verification over maximum coverage" — see `docs/METHODOLOGY.md` "Scope Decision" and
"Field-Depth Scope Reduction." Everything not shipped is tracked, not silently dropped: see
`acquisition_backlog.json` and `registry/dataset_registry.csv`.

## A Note on How This Data Was Collected

Every fact in this release was collected via the WebSearch tool. **Direct WebFetch to `.gov.in`,
`.ac.in`, `.edu.in`, and Wikipedia domains was blocked for the entire collection session** by this
environment's organizational egress policy (confirmed HTTP 403 policy denial, re-tested live
immediately before collection began) — the same constraint documented in Package001_Geography and
Package002_Education. No page cited in this package was directly fetched and re-read; all facts are
search-snippet-sourced and cited by URL, with confidence scores capped at 88. Full detail in
`docs/METHODOLOGY.md`.

## Folder Structure

```
Package003_Healthcare/
├── README.md                 — this file
├── package_manifest.json     — machine-readable package descriptor
├── CHANGELOG.md               — version history
├── VERSION                    — current version string
├── codex_handoff.md           — integration guide for an AI coding agent
├── integration_checklist.md   — step-by-step integration checklist
├── package_health_report.md   — coverage/completion/readiness scoring
├── validation_report.md       — top-level validation summary
├── acquisition_backlog.json   — every un-shipped domain and what unblocks it
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

| Dataset | Records | Jurisdictions | Verification Status |
|---|---|---|---|
| Medical Regulatory Bodies & Health Missions | 23 | National (11), Telangana (6), Andhra Pradesh (6) | Needs Review |
| Medical Colleges (Telangana & AP) | 54 | Telangana (29), Andhra Pradesh (25) | Needs Review |
| Government Hospitals (Telangana & AP) | 49 | Telangana (28), Andhra Pradesh (21) | Needs Review |
| Government Health Insurance Schemes | 8 | National (4), Telangana (2), Andhra Pradesh (2) | Needs Review |

**Total: 134 records across 4 datasets.**

## Import Instructions

Follow `imports/import_sequence.json`. All 4 datasets are independent in this release (no enforced
inter-dataset foreign keys) — see `schemas/schema_catalog.json` for the two documented, non-enforced
free-text cross-references between the medical_colleges and government_hospitals datasets.

## Evidence Policy

Every dataset carries per-row provenance (`data_source`, `source_url`, `collection_date`,
`confidence_score`, `verification_status`, `notes`) and a corresponding entry in `evidence/`
documenting exactly what was searched and the environment constraint that shaped this release's
sourcing method. No row in this package was fabricated, estimated, or inferred — unverifiable fields
carry the literal sentinel `PENDING_VERIFICATION` rather than a guessed value.

## Validation Process

1. Primary key uniqueness (within and across datasets), column-count consistency, schema-column-order
   match, and default `verification_status` are checked programmatically for every dataset — see
   `reports/validation_report.md` and the top-level `validation_report.md` (all checks passed at
   build time).
2. Every `verification_status` starts at `VST-NEEDS_REVIEW` on import — promotion to `VST-VERIFIED`
   is a governance action (Data Steward + Reviewer sign-off against a directly-fetched primary
   source), never an automatic result of collection.
3. Where sources conflicted (e.g. hospital bed-count discrepancies, the Dental Council of India →
   National Dental Commission transition, Andhra Pradesh's repeated scheme renames), the conflict is
   documented and resolved in the relevant `reports/*.collection_report.md`.

## Relationship to Future Packages and Domains

This release is intentionally narrow. `acquisition_backlog.json` lists all 36 remaining healthcare
domains (PHCs, CHCs, specialty hospitals, blood banks, ambulance services, health programmes, etc.)
and all Indian states/UTs beyond Telangana & Andhra Pradesh, each with a specific reason it wasn't
shipped and what would unblock it — most commonly, either a bulk structured data source (e.g.
HMIS/NHM facility registry) rather than per-institution web research, or restored WebFetch access to
directly re-verify sources at higher confidence.

## Release Status

**RC1 — awaiting review.** Per instruction, this package will NOT be merged to `main` automatically.
See `reports/coverage_report.md`, `reports/known_gaps.md`, and this README's stats above for what to
review before a promotion decision.
