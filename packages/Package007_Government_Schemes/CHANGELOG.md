# Changelog — Package007_Government_Schemes

All notable changes to this package. Released versions are immutable; corrections ship as new
versions. Format follows [Keep a Changelog](https://keepachangelog.com/); this package uses
semantic versioning.

## [1.0.0] — 2026-07-25

First release. Promotes Package007 from an empty placeholder to a Stable 15-dataset Policy
Intelligence Graph.

### Added

**Reference taxonomies (Layer 1)**

- `scheme_categories.csv` — 24 categories across three axes, separated by `category_group`:
  Sector (12), Beneficiary Group (8) and Instrument (2), plus Production-independent groupings.
  The separation matters: a flat list would imply a single classification the domain does not have.
- `required_documents.csv` — 15 documents with issuing authority, typical use and DigiLocker
  availability.
- `implementing_agencies.csv` — 20 agencies across central ministry, central authority,
  development financial institution, statutory body, state department, district office, local body
  and assisted-service network.
- `financial_institutions.csv` — 12 banks and DFIs with the schemes each actually delivers.
- `scheme_application_status.csv` — 8 statuses. Includes `QUERY_RAISED`, which the specification
  omitted but which is the most common cause of silent application failure.

**Canonical registry (Layer 2)**

- `government_schemes.csv` — 40 Central schemes with ministry, objective, benefit summary,
  coverage, application mode and official portal. Each row is attributed to the scheme's own
  portal rather than an aggregator. The `also_in_package` column declares overlap with the five
  domain packages that already hold scheme data.

**Scheme detail (Layers 3–4)**

- `eligibility_criteria.csv` — 55 rows, one per condition, typed against a closed 12-value
  vocabulary. `is_mandatory` distinguishes hard gates from quantum-affecting factors.
- `scheme_benefits.csv` — 51 rows, itemised by benefit type. Multi-component schemes carry
  multiple rows.
- `application_process.csv` — 43 ordered steps across 8 schemes, with channel, responsible actor
  and the artifact each step produces.

**Cross-package mappings (Layer 7)**

- `education_scheme_mapping.csv` — 7 rows → Package002_Education
- `agriculture_scheme_mapping.csv` — 14 rows → Package005_Agriculture (scheme and crop)
- `skill_scheme_mapping.csv` — 12 rows → Package006 (scheme, skill, certification, provider)
- `industry_scheme_mapping.csv` — 12 rows → Package004_Industries
- `district_scheme_mapping.csv` — 305 rows → Package001_Geography (5 schemes × 61 districts)

**Recommendation layer (Layer 8)**

- `scheme_ai_recommendations.csv` — 37 rows across 10 citizen profile archetypes, each with a
  ranked recommendation set, an auditable basis sentence, next-scheme sequencing and related
  schemes.

**Release artifacts**

- `schemas/schema_catalog.json`, 15 `metadata/*.metadata.json`, 15
  `reports/*.collection_report.md`, `registry/dataset_registry.csv`, `package_manifest.json`,
  `VERSION`, `validation_report.md`, `validation_summary.json`, `quality_report.md`,
  `VERSION_HISTORY.md`, `RELEASE_NOTES.md`, `codex_handoff.md`.
- `docs/METHODOLOGY.md`, `docs/USAGE.md`, `docs/DATA_DICTIONARY.md`, `docs/IMPORT_GUIDE.md`.
- `validate.py` — 12-check validation engine.
- `gen_core.py`, `gen_mappings.py`, `build_artifacts.py`, `build_docs.py` — generators, retained so
  the package is reproducible from source.

### Cross-package integration

Nine foreign key sets into five released packages — the widest cross-package surface in the
knowledge base. All resolved against upstream CSVs at generation time, all re-checked on every
validation run, **zero unresolved**:

| Upstream | Resolved | Sentinel |
|---|---|---|
| Package001 `district.dist_id` | 305 | 0 |
| Package002 `scholarships.id` | 4 | 3 |
| Package004 opportunity names | 12 | 0 |
| Package005 `agriculture_schemes.scheme_id` | 12 | 2 |
| Package005 `crops.crop_id` | 12 | 2 |
| Package006 `government_skill_schemes.scheme_id` | 9 | 3 |
| Package006 `skills.skill_id` | 11 | 1 |
| Package006 `certifications.certification_id` | 4 | 8 |
| Package006 `training_providers.provider_id` | 3 | 9 |

Package003_Healthcare has no hard foreign key; the overlap is declared in `also_in_package` and
`health_scheme_mapping.csv` is deferred to v1.1.0.

### Validation

655 records, 10,401 cells, **0 violations** across 12 checks. Three checks are new relative to
Package005's ten: V11 (scheme coverage), V12 (enum integrity), and an extended V8 that validates
semicolon-delimited multi-value members and document-hint resolution.

Five defect classes were caught before release:

1. **Cross-package FK to a non-existent record** — the skill mapping assumed Package006 held an
   entrepreneurship skill, which a Package006 *collection report* describes but the released
   `skills.csv` does not contain. The generator aborted rather than writing an unresolvable UUID.
   **A collection report described data the dataset does not have**; only reading the CSV found it.
2. **A second non-existent record** — the industry mapping assumed Package004 held an AI
   opportunity. Repointed at the real software startup record.
3. **Denormalised name drift** — `government_schemes` recorded Stand-Up India's `short_name` as
   `SUI` while five child datasets used `Stand-Up India`. Joins worked; any `GROUP BY` on the
   denormalised column would have split one scheme into two.
4. **Document hint pointing at no document** — two eligibility rows cited `Bonafide Certificate`
   against an actual name of `Bonafide / Study Certificate`.
5. **Scheme coverage gaps** — four universal or institutional schemes had no eligibility rows at
   all. Absence could not be distinguished from omission; explicit rows stating universality were
   added.

### Provenance

- Confidence **60–78** against an **85** ceiling (never reached). The ceiling records that WebFetch
  to `.gov.in` / `.nic.in` / `.ac.in` is blocked by this environment's egress policy — the same
  constraint as Package004, Package005 and Package006.
- Sentinel rate **5.13%** (534 of 10,401 cells), more than double Package005's, concentrated in
  district variation (305), monetary quantum (~85), timelines (43) and cross-package absences.
- All 655 rows are `VST-NEEDS_REVIEW`. **No human data-steward sign-off.**

### Deliberately not asserted

- **No monetary amount anywhere.** Benefit quantum, premium rates, loan ceilings and subsidy
  percentages are sentinelled throughout. Scheme amounts are revised by notification and budget
  cycle; a figure dated 2026-07-25 with no primary source would look authoritative, be
  unverifiable, and go wrong unpredictably — in the field applicants rely on most. Every row
  carries `official_portal`.
- **No processing timelines.** `typical_timeline` is sentinelled on all 43 process rows; only
  MGNREGA has a statutory period, and that is stated in `notes` rather than asserted as data.
- **No numeric eligibility thresholds.** Stated qualitatively, making this a candidate-set
  narrower rather than an eligibility decider.
- **No district-level variation.** Sentinelled on all 305 district rows.

### Known limitations

- All 40 schemes are Central. State schemes for Telangana and Andhra Pradesh already live in
  Package002, Package003 and Package004.
- Only 8 of 40 schemes have modelled application workflows.
- Only 5 of 40 have a district-mediated application step; the other 35 are nationally administered
  and padding them across 61 districts would assert a dimension that does not exist.
- `priority_score` in `scheme_ai_recommendations` is a designed heuristic with no empirical
  calibration — a rule-engine seed, not evidence. Confidence 60 on every row.
- Scheme categories are not mutually exclusive, but each scheme carries one dominant category, so
  per-category counts understate cross-cutting reach.

### Open governance question

Six packages now hold scheme data: Package002 (25), Package003 (9), Package004 (18), Package005
(12), Package006 (15) and Package007 (40). `also_in_package` declares every overlap so it is
explicit and reconcilable — but declaring is not resolving. Either Package007 becomes the single
source of truth and the domain packages reference it, or the two drift apart. Flagged in
`quality_report.md` and `codex_handoff.md` as the highest-priority open item.

---

## [Unreleased] — planned for 1.1.0

- `health_scheme_mapping.csv` giving Package003 a hard foreign key — the one released package with
  no structural link.
- State scheme registry for Telangana and Andhra Pradesh, reconciled against the state slices
  already in Package002, Package003 and Package004.
- Package008_MSME foreign keys via `industry_scheme_mapping`.
- Monetary quantum and processing timelines, contingent on primary-source access — this would
  clear the two dominant sentinel clusters and is the main thing standing between this package and
  citizen-facing use.
- Application workflows for the remaining 32 schemes.
- District-level variation in `district_scheme_mapping` (305 sentinelled cells).
- Human data-steward review to move rows from `VST-NEEDS_REVIEW` to `VST-VERIFIED`.

---

## [0.0.0] — 2026-07-20

- Placeholder `README.md` reserving Package007 for government scheme knowledge assets. No data.
