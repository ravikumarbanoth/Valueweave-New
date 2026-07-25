# Package007_Government_Schemes v1.0.0

**ValueWeave.in Government Scheme Intelligence Knowledge Base**

| | |
|---|---|
| **Version** | 1.0.0 (Stable) |
| **Release date** | 2026-07-25 |
| **Datasets** | 15 |
| **Records** | 655 |
| **Schemes registered** | 40 |
| **Validation** | PASS — 0 violations across 12 checks |
| **Cross-package FK sets** | 9, into 5 released packages, 0 unresolved |
| **Confidence range** | 60–78 (policy ceiling 85) |
| **Sentinel rate** | 5.13% of cells (`PENDING_VERIFICATION`) |
| **Verification status** | `VST-NEEDS_REVIEW` — no human data-steward sign-off |

## Purpose

This is not a list of schemes. It is a Policy Intelligence Graph: a canonical scheme registry
surrounded by the structures that make a scheme actionable — decomposed eligibility logic,
itemised benefits, ordered application workflows, document requirements, implementing agencies and
lending institutions — then bound outward to five released domain packages and upward into a
profile-based recommendation layer.

```
Citizen → Profile → Eligibility → Government Scheme → Benefits
   → {Education, Healthcare, Agriculture, Skills, Industry, MSME}
   → Finance → Employment → Future Growth
```

## The questions it answers

| Question | Query surface |
|---|---|
| Which schemes am I eligible for? | `eligibility_criteria` ⨝ `government_schemes` |
| Which schemes exist for students / farmers / MSMEs / women? | `scheme_categories.category_group` |
| Which subsidies and loans are available? | `scheme_benefits.benefit_type` |
| Which department implements this? | `government_schemes.ministry` + `implementing_agencies` |
| What documents do I need? | `eligibility_criteria.verification_document_hint` → `required_documents` |
| How do I apply, and what happens next? | `application_process` ordered by `step_number` |
| Which schemes are district-specific? | `district_scheme_mapping` — 5 schemes × 61 districts |
| Which agriculture / education / skill schemes fit me? | the three domain mapping datasets |
| Which bank delivers this scheme? | `financial_institutions.scheme_roles` |
| What should I apply for next? | `scheme_ai_recommendations.suggested_next_scheme_id` |

See `docs/USAGE.md` for the SQL.

## Datasets

Load in this order — it is the dependency order and `import_order` in `package_manifest.json`.

### Layer 1 — Reference taxonomies

| Dataset | Rows | PK |
|---|---|---|
| `scheme_categories.csv` | 24 | `category_id` |
| `required_documents.csv` | 15 | `document_id` |
| `implementing_agencies.csv` | 20 | `agency_id` |
| `financial_institutions.csv` | 12 | `institution_id` |
| `scheme_application_status.csv` | 8 | `status_id` |

### Layer 2 — Canonical registry

| Dataset | Rows | PK |
|---|---|---|
| `government_schemes.csv` | 40 | `scheme_id` |

### Layers 3–4 — Scheme detail

| Dataset | Rows | PK |
|---|---|---|
| `eligibility_criteria.csv` | 55 | `criterion_id` |
| `scheme_benefits.csv` | 51 | `benefit_id` |
| `application_process.csv` | 43 | `step_id` |

### Layer 7 — Cross-package mappings

| Dataset | Rows | Links to |
|---|---|---|
| `education_scheme_mapping.csv` | 7 | Package002_Education |
| `agriculture_scheme_mapping.csv` | 14 | Package005_Agriculture |
| `skill_scheme_mapping.csv` | 12 | Package006_Skills_and_Training |
| `industry_scheme_mapping.csv` | 12 | Package004_Industries |
| `district_scheme_mapping.csv` | 305 | Package001_Geography |

### Layer 8 — Recommendation layer

| Dataset | Rows | PK |
|---|---|---|
| `scheme_ai_recommendations.csv` | 37 | `recommendation_id` |

## Cross-package integration

Nine foreign key sets into five released packages — the widest cross-package surface in the
knowledge base. Every id was resolved by reading the upstream CSVs at generation time, and all are
re-checked on every validation run, so an upstream rename fails the build rather than silently
breaking.

| Upstream | Foreign key | Resolved | Sentinel |
|---|---|---|---|
| Package001_Geography | `district_scheme_mapping.package001_dist_id` | 305 | 0 |
| Package002_Education | `education_scheme_mapping.package002_record_id` | 4 | 3 |
| Package004_Industries | `industry_scheme_mapping.package004_opportunity_name` | 12 | 0 |
| Package005_Agriculture | `agriculture_scheme_mapping.package005_scheme_id` | 12 | 2 |
| Package005_Agriculture | `agriculture_scheme_mapping.package005_crop_id` | 12 | 2 |
| Package006_Skills | `skill_scheme_mapping.package006_scheme_id` | 9 | 3 |
| Package006_Skills | `skill_scheme_mapping.package006_skill_id` | 11 | 1 |
| Package006_Skills | `skill_scheme_mapping.package006_certification_id` | 4 | 8 |
| Package006_Skills | `skill_scheme_mapping.package006_provider_id` | 3 | 9 |

**Zero unresolved.** Sentinels are honest absences where the upstream package has no counterpart
record — every case is documented in `validation_report.md`.

**Package003_Healthcare** has no hard foreign key. AB PM-JAY declares the overlap in
`also_in_package`, but `health_scheme_mapping.csv` is deferred to v1.1.0.
**Package008_MSME** is unreleased; `industry_scheme_mapping` is the intended join surface.

## This package is the canonical registry

Five packages already carry domain scheme slices: Package002 (25 scholarships), Package003
(9 health insurance), Package004 (18 MSME support), Package005 (12 agriculture), Package006
(15 skill). Package007 does not silently duplicate them —
`government_schemes.also_in_package` names every package that already holds each scheme, so the
overlap is explicit, and the corresponding mapping dataset carries a hard foreign key to that
package's record.

**This is an unresolved governance question, not a solved one.** Declaring the overlap is not the
same as resolving it. Either Package007 becomes the single source of truth and the domain packages
reference it, or the two drift. See `quality_report.md` and `codex_handoff.md`.

## What this package does not assert

Being explicit about the gaps is part of the deliverable.

- **No monetary amount, anywhere.** Every benefit quantum, premium rate, loan ceiling and subsidy
  percentage is the bare sentinel. Scheme amounts are revised by notification and budget cycle; a
  figure here would date badly in exactly the field applicants rely on most. Every row carries
  `official_portal` — fetch the live figure there.
- **No processing timelines.** `application_process.typical_timeline` is the sentinel on all 43
  rows. No published service standard was confirmable except MGNREGA's statutory period.
- **No numeric eligibility thresholds.** Income ceilings, age bands and land limits are stated as
  "below the prescribed ceiling" because the figures move. This package narrows a candidate set;
  it cannot decide a case.
- **`priority_score` is a heuristic, not evidence.** It is a deterministic function of eligibility
  overlap and sequencing logic — a rule-engine seed. No uptake or approval-rate data backs it.
  Confidence is 60 on every row, the lowest in the package, deliberately.
- **No state schemes.** All 40 registry rows are Central. Telangana and Andhra Pradesh state
  schemes live in Package002, Package003 and Package004.
- **No district-level variation.** `district_specific_variation` is the sentinel on all 305 rows.

## Provenance model

Six mandatory provenance columns on every row of every dataset:

| Column | Meaning |
|---|---|
| `data_source` | The scheme portal, ministry or authority the row is attributed to |
| `source_url` | Public URL for that body |
| `collection_date` | `2026-07-25`, uniform package-wide |
| `confidence_score` | Integer 0–100, capped at 85 |
| `verification_status` | `VST-NEEDS_REVIEW` |
| `notes` | Caveats and sourcing remarks |

### Confidence bands

| Band | Tier |
|---|---|
| 70–85 | Tier 1 — the scheme's own portal and administering ministry |
| 62–69 | Tier 2 — government notifications and gazette references |
| 56–61 | Tier 3 — official scheme guidelines and operational manuals |
| 45–55 | Tier 4 — ministry annual reports and derived aggregates |

The 85 ceiling records that WebFetch to `.gov.in` / `.nic.in` / `.ac.in` is blocked in this
environment, so no row rests on a primary-source page read — the same constraint that applied to
Package004, Package005 and Package006. Observed range is 60–78.

### Sentinel discipline

`PENDING_VERIFICATION` appears only as a complete, bare cell value — never appended to other text,
never embedded in prose, never substituting for a numeric `confidence_score`. Check V5 enforces
this.

## Validation

```bash
cd packages/Package007_Government_Schemes
python3 validate.py
```

Twelve checks:

| Check | Enforces |
|---|---|
| V1 | Structural — row length matches header |
| V2 | Primary key unique and non-empty |
| V3 | All six provenance columns present |
| V4 | `confidence_score` integer, 0–100, ≤ 85 |
| V5 | Bare-sentinel discipline |
| V6 | `verification_status` enum |
| V7 | Uniform `collection_date` |
| V8 | In-package FKs resolve; denormalised names agree; multi-value column members resolve |
| V9 | Cross-package FKs resolve upstream, and upstream names agree |
| V10 | No silently blank cells |
| V11 | Every scheme has ≥1 eligibility criterion and ≥1 benefit row |
| V12 | Closed enum domains |

Exit 0 = release-clean. Machine-readable output in `validation_summary.json`; narrative in
`validation_report.md`. Five defect classes were caught by these checks before release, including
two cross-package foreign keys pointing at upstream records that do not exist.

## Repository layout

```
Package007_Government_Schemes/
├── datasets/                    15 released CSVs
├── metadata/                    15 per-dataset metadata JSON files
├── reports/                     15 per-dataset collection reports
├── schemas/schema_catalog.json  canonical PK/FK/column reference
├── registry/dataset_registry.csv
├── docs/
│   ├── METHODOLOGY.md           how the data was collected and scored
│   ├── USAGE.md                 query recipes and traps
│   ├── DATA_DICTIONARY.md       every column, with observed domains
│   └── IMPORT_GUIDE.md          load order and DDL
├── package_manifest.json
├── validation_report.md         validation_summary.json
├── quality_report.md            what this is and is not fit for
├── VERSION_HISTORY.md           RELEASE_NOTES.md  CHANGELOG.md  VERSION
├── codex_handoff.md
├── validate.py                  12-check validation engine
└── gen_core.py  gen_mappings.py  build_artifacts.py  build_docs.py
```

Full rebuild — order matters, because the artifact and doc builders read the validation summary:

```bash
python3 gen_core.py && python3 gen_mappings.py \
  && python3 validate.py && python3 build_artifacts.py && python3 build_docs.py
```

Every count in the manifest, registry, schema catalog, collection reports and docs is derived from
the CSVs rather than hand-maintained, so they cannot drift.

## Versioning

Released versions are immutable. Changes ship as new versions under
`Package007_Government_Schemes_vMAJOR.MINOR.PATCH`. See `VERSION_HISTORY.md` for lineage and
policy, `CHANGELOG.md` for detail, and `package_manifest.json` → `planned_next_release` for the
v1.1.0 target.
