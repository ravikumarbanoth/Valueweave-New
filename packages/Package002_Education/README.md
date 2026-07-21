# Package 002 — Education Foundation
### ValueWeave.in Data Factory · Release v1.0.0-RC2 (NOT YET MERGED TO MAIN)

**This is Release Candidate 2.** RC1 (2026-07-21) was the initial collection; RC2 (2026-07-22) is a
data-quality enrichment pass on the same 4 datasets, done at explicit request before any decision to
promote this package to canonical/merge to `main`. See `reports/rc1_vs_rc2_comparison.md` for the full
diff and `CHANGELOG.md` for the itemized changes.

## Purpose of This Package

This package is ValueWeave's Education knowledge foundation. It anchors education-domain entities
(boards, universities, exams, scholarships) that future packages and application features will
reference. Unlike Package001_Geography, this package does not yet declare foreign keys into other
packages — its `state`/`jurisdiction` fields are free-text values, not verified relational links (see
`schemas/schema_catalog.json`).

## Scope of This Release

The full package brief named 40 education data domains across all of India, with ~33 fields to
collect per institution. **This release covers 4 of those 40 domains**, scoped to Telangana, Andhra
Pradesh, and genuinely national-level entities, with a reduced per-institution field set. This was a
deliberate, explicitly-agreed scoping decision — see `docs/METHODOLOGY.md` "Scope Decision" and
"Field-Depth Scope Reduction" — made to avoid shipping fabricated or unverifiably-thin data across the
full brief. Everything not shipped is tracked, not silently dropped: see `acquisition_backlog.json`
and `registry/dataset_registry.csv`.

## A Note on How This Data Was Collected

Every fact in this release was collected via the WebSearch tool. **Direct WebFetch to `.gov.in`,
`.ac.in`, `.edu.in`, and Wikipedia domains was blocked for the entire collection session** by this
environment's organizational egress policy (a confirmed HTTP 403 policy denial, not a transient
error). No page cited in this package was directly fetched and re-read; all facts are
search-snippet-sourced and cited by URL, with confidence scores capped accordingly. Full detail in
`docs/METHODOLOGY.md`.

## Folder Structure

```
Package002_Education/
├── README.md                 — this file
├── package_manifest.json     — machine-readable package descriptor
├── CHANGELOG.md               — version history
├── VERSION                    — current version string
├── codex_handoff.md           — integration guide for an AI coding agent
├── integration_checklist.md   — step-by-step integration checklist
├── package_health_report.md   — coverage/completion/readiness scoring
├── acquisition_backlog.json   — every un-shipped domain and what unblocks it
├── datasets/                  — the production CSVs
├── metadata/                  — source catalogues, confidence calibration, provenance stats
├── reports/                   — collection reports, data dictionaries, quality/coverage/validation reports
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
| Educational Boards & Regulatory Bodies | 21 | National (13), Telangana (4), Andhra Pradesh (4) | Needs Review |
| Universities (Telangana & AP) | 66 | Telangana (29), Andhra Pradesh (37) | Needs Review |
| Entrance Exams | 29 | National (15), Telangana (7), Andhra Pradesh (7) | Needs Review |
| Scholarships | 25 | National (15), Telangana (5), Andhra Pradesh (5) | Needs Review |

**Total: 141 records across 4 datasets** (RC1 was 135; +6 in RC2 — see `reports/rc1_vs_rc2_comparison.md`).

As of RC2, the universities dataset also carries three new columns: `ownership` (100% filled),
`contact_details` (5/66 filled), and `student_services_summary` (5/66 filled).

## Import Instructions

Follow `imports/import_sequence.json`. All 4 datasets are independent in this release (no
inter-dataset foreign keys), so import order does not affect referential integrity — see
`schemas/schema_catalog.json`.

## Evidence Policy

Every dataset carries per-row provenance (`data_source`, `source_url`, `collection_date`,
`confidence_score`, `verification_status`, `notes`) and a corresponding entry in `evidence/`
documenting exactly what was searched and the environment constraint that shaped this release's
sourcing method. No row in this package was fabricated, estimated, or inferred — unverifiable fields
carry the literal sentinel `PENDING_VERIFICATION` rather than a guessed value.

## Validation Process

1. Primary key uniqueness, column-count consistency, and default `verification_status` are checked
   programmatically for every dataset — see `reports/validation_report.md` (all checks passed at
   build time).
2. Every `verification_status` starts at `VST-NEEDS_REVIEW` on import — promotion to `VST-VERIFIED`
   is a governance action (Data Steward + Reviewer sign-off against a directly-fetched primary
   source), never an automatic result of collection.
3. Where sources conflicted (e.g. Andhra Pradesh scholarship scheme renames, GPAT's conducting-body
   transfer, university establishment-year discrepancies), the conflict is documented and resolved in
   the relevant `reports/*.collection_report.md`.

## Relationship to Future Packages and Domains

This release is intentionally narrow. `acquisition_backlog.json` lists all 36 remaining education
domains (Schools, Colleges, ITIs, MOOCs, Fellowships, Research Institutions, etc.) and all Indian
states/UTs beyond Telangana & Andhra Pradesh, each with a specific reason it wasn't shipped and what
would unblock it — most commonly, either a bulk structured data source (e.g. UDISE+) rather than
per-institution web research, or restored WebFetch access to directly re-verify sources at higher
confidence.
