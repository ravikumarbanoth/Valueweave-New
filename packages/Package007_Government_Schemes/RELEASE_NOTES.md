# Release Notes — Package007_Government_Schemes v1.0.0

**Released 2026-07-25 · Stable · validation PASS (0 violations across 12 checks)**

## What this is

The Policy Intelligence Graph of the ValueWeave knowledge base: a canonical registry of
40 government schemes, surrounded by the structures that make schemes
actionable rather than merely listed — decomposed eligibility logic, itemised benefits, ordered
application workflows, document requirements, implementing agencies and financial institutions —
then bound outward to five released domain packages and upward into a profile-based recommendation
layer.

15 datasets · 655 records · 10401 cells.

## The questions it answers

The package was built around the citizen questions in the specification. Each maps to a concrete
query — see `docs/USAGE.md` for the SQL:

| Question | Where it is answered |
|---|---|
| Which schemes am I eligible for? | `eligibility_criteria` joined to `government_schemes` |
| Which schemes are available for students / farmers / MSMEs? | `scheme_categories.category_group` = Sector or Beneficiary Group |
| Which subsidies and loans exist? | `scheme_benefits.benefit_type` |
| Which departments implement them? | `government_schemes.ministry` + `implementing_agencies` |
| Which documents are required? | `eligibility_criteria.verification_document_hint` → `required_documents` |
| How do I apply? | `application_process`, ordered by `step_number` |
| Which schemes are district-specific? | `district_scheme_mapping` (5 schemes × 61 districts) |
| Which agriculture / education / skill schemes are relevant? | the three domain mapping datasets |

## Cross-package integration

Nine distinct foreign key sets into five released packages — the widest cross-package surface in
the knowledge base. All resolved against the upstream CSVs at generation time and re-checked on
every validation run:

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

**Zero unresolved.** Sentinels are honest absences where the upstream package has no counterpart
record — documented row by row in `validation_report.md`.

## Read this before using the data

**No monetary amount is asserted anywhere in this package.** Every benefit quantum, premium rate,
loan ceiling and subsidy percentage is the bare `PENDING_VERIFICATION` sentinel. Scheme amounts
are revised by notification and budget cycle, and a figure stated here would date badly in
precisely the field applicants rely on most. Every row carries `official_portal` — fetch the
current figure there.

**No processing timeline is asserted.** `application_process.typical_timeline` is the sentinel on
all 43 rows; no published service standard was confirmable except MGNREGA's statutory period.

**`priority_score` in `scheme_ai_recommendations` is a designed heuristic, not evidence.** It is a
deterministic function of eligibility overlap and sequencing logic, intended as a rule-engine
seed. There is no uptake or approval-rate data behind it. Confidence is 60 on every row — the
lowest in the package, deliberately.

**Nothing has had human review.** All 655 rows are `VST-NEEDS_REVIEW`.
Machine validation confirms structure, references and provenance; it does not confirm currency,
and currency is the binding risk for scheme data.

## Scope boundaries

- **All 40 schemes are Central.** State schemes for Telangana and Andhra Pradesh already live in
  Package002, Package003 and Package004; a reconciled state registry is a v1.1.0 target.
- **8 of 40 schemes have modelled application workflows**; the rest are single-step or lack
  documented multi-stage processes.
- **5 of 40 schemes have a district-mediated application step.** The other 35 are nationally
  administered, and padding them across 61 districts would assert a district dimension that does
  not exist.
- **No hard foreign key into Package003_Healthcare.** AB PM-JAY declares the overlap in
  `also_in_package`, but `health_scheme_mapping.csv` is deferred to v1.1.0.

## Defects caught before release

Five classes, all by the validation checks. Two were cross-package foreign keys pointing at
upstream records that do not exist — including one case where a Package006 collection report
describes a skill the released dataset does not contain. Full detail in `validation_report.md`.

## Governance question this release surfaces

Five packages now hold scheme data: Package002 (25 scholarships), Package003 (9 health insurance),
Package004 (18 MSME support), Package005 (12 agriculture), Package006 (15 skill), and now
Package007 (40 cross-domain). `government_schemes.also_in_package`
declares every overlap so it is explicit and reconcilable — but declaring is not resolving. Either
Package007 becomes the single source of truth and the domain packages reference it, or the two
drift apart. See `quality_report.md` and `codex_handoff.md`.

## Files

```
Package007_Government_Schemes/
├── datasets/              15 released CSVs
├── metadata/              15 per-dataset metadata JSON files
├── reports/               15 per-dataset collection reports
├── schemas/               schema_catalog.json
├── registry/              dataset_registry.csv
├── docs/                  METHODOLOGY, USAGE, DATA_DICTIONARY, IMPORT_GUIDE
├── package_manifest.json
├── validation_report.md   validation_summary.json
├── quality_report.md
├── VERSION_HISTORY.md     RELEASE_NOTES.md  CHANGELOG.md  VERSION
├── codex_handoff.md
├── validate.py            12-check validation engine
└── gen_core.py  gen_mappings.py  build_artifacts.py  build_docs.py
```

Generator scripts ship with the package: the datasets are reproducible from source, and a reviewer
can see exactly what was asserted and what was left sentinelled.
