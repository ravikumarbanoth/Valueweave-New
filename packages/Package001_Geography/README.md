# Package 001 — Geography Foundation
### ValueWeave.in Data Factory · Release v1.0.0

## Purpose of This Package
This package is the geographic root of ValueWeave's entire Knowledge Graph. Every other package that will ever be built (Education Foundation, Industrial Infrastructure, Industries & Products, Skills & Training, Companies & MSMEs, Government Schemes, Manufacturing Knowledge, Supply Chain, and the cross-cutting Knowledge Graph Relationships package) anchors its records back to a `district_id` (and eventually a `mandal_id`) defined here. Get this package right, and every downstream package inherits reliable geography for free; get it wrong, and every downstream package inherits the error.

## Architecture
Geography Foundation follows a strict dependency chain — each tier's foreign key points to the tier above it:
```
State → District → Revenue Division → Mandal → Village → Municipality → ...
```
This release covers the first three tiers for Telangana & Andhra Pradesh (State, District, and Telangana's Revenue Divisions); Mandal and everything below it remains schema-defined but data-empty pending source access (see Known Issues in `CHANGELOG.md`).

## Folder Structure
```
Package001_Geography/
├── README.md                 — this file
├── package_manifest.json     — machine-readable package descriptor
├── CHANGELOG.md               — version history
├── VERSION                    — current version string
├── codex_handoff.md           — integration guide for an AI coding agent
├── integration_checklist.md   — step-by-step Codex checklist
├── package_health_report.md   — coverage/completion/readiness scoring
├── acquisition_backlog.json   — every blocked dataset and what unblocks it
├── datasets/                  — the production CSVs
├── metadata/                  — source catalogues, reliability scores, conflict logs
├── reports/                   — collection reports, data dictionaries, quality reports
├── evidence/                  — source-access audit trail
├── registry/                  — dataset_registry.csv, the cross-package control center
├── schemas/                   — schema_catalog.json, the canonical PK/FK/relationship reference
├── raw_sources/                — source inventories and manual-download links for blocked items
└── imports/                    — import_sequence.json and per-dataset import manifests
```

## Dataset List
| Dataset | Records (TG / AP) | Status |
|---|---|---|
| State | 1 / 1 | Needs Review |
| District | 33 / 28 | Needs Review (AP below confidence threshold) |
| Revenue Division | 75 / 0 | TG Needs Review; AP Blocked |
| Mandal | 0 / 0 | Blocked (schema only) |

## Import Instructions
Follow `imports/import_sequence.json` exactly — it encodes the dependency order (`state → district → revenue_division → mandal`), the validation check for each step, and a rollback strategy. Do not import any table out of this order; every table in this package has a foreign key chain back to `state`.

## Evidence Policy
Every dataset in this package carries per-row provenance (`data_source`, `source_url`, `collection_date`, `last_verified_date`, `confidence_score`, `verification_status`, `reviewer`, `version`, `license`, `attribution`) and a corresponding entry in `evidence/` documenting exactly what was fetched, what was blocked, and why. No row in this package was fabricated, estimated, or inferred — unverifiable fields carry the literal sentinel `PENDING_VERIFICATION` or `PENDING_GEOCODING` rather than a guessed value.

## Validation Process
1. Every foreign key is checked against its parent table before a batch is accepted (Section: `imports/import_sequence.json`).
2. Every `verification_status` starts at `VST-NEEDS_REVIEW` on import — promotion to `VST-VERIFIED` is a governance action (Data Steward + Reviewer sign-off), never an automatic result of a successful import.
3. Where multiple sources disagreed, the conflict is documented, a resolution is recommended, and the reasoning is preserved (see `reports/*.collection_report.md` for every conflict found and resolved or explicitly left open in this release).

## Relationship to Future Packages
Package 001 is intentionally the *only* package with no upstream dependency. Package 002 (Education Foundation) and every package after it will declare Package 001 as a dependency and reference its `dist_id` (and, once populated, `mandal_id`) rather than re-deriving geography themselves. Package 001 should be re-opened only when (a) a blocked dataset here becomes unblockable, or (b) a downstream package discovers a genuine gap in the geography model — not to redesign anything already frozen.
