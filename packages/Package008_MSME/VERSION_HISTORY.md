# Version History — Package008_MSME

Released versions are immutable. Corrections and additions ship as new versions under
`Package008_MSME_vMAJOR.MINOR.PATCH`.

| Version | Date | Status | Datasets | Records | Businesses | Validation | Summary |
|---|---|---|---|---|---|---|---|
| **1.0.0** | 2026-07-25 | Stable | 18 | 477 | 40 | PASS (0 violations, 13 checks) | First release. Business Intelligence Layer: 40 MSME opportunities with inputs, compliance, finance, market, export, AI and investment intelligence, referencing six upstream packages. |
| 0.0.0 | 2026-07-20 | Placeholder | 0 | 0 | 0 | n/a | `README.md` reserving Package008 for MSME assets. No data. |

## Semantic versioning policy

| Change class | Version bump | Examples |
|---|---|---|
| Correction with no structural or semantic change | **Patch** (1.0.x) | Fixing a `source_url`; correcting a description |
| Additive, backward-compatible | **Minor** (1.x.0) | New businesses; populating existing sentinels; new mapping datasets |
| Structural or breaking | **Major** (x.0.0) | Renaming or removing a column; changing the `business_id` scheme |

## v1.0.0 lineage

Built in four validation-gated stages:

1. **Core generation** (`gen_core.py`) — 9 datasets with no upstream dependency
2. **Mapping generation** (`gen_mappings.py`) — 9 datasets, resolving every upstream id against
   the released CSVs at generation time and aborting on any failure
3. **Validation** (`validate.py`) — 13 checks; 5 defect classes found and fixed before release
4. **Artifacts and documentation** — generated from the CSVs plus the validation summary

V13, which mechanically enforces the brief's non-duplication rule, is new in this package and has
no counterpart in Package001 through Package007.

## Upstream package versions this release was built against

| Package | Version | What Package008 references |
|---|---|---|
| Package001_Geography | 1.0.0 | `district.dist_id` |
| Package002_Education | 1.0.0 | `universities_telangana_andhra_pradesh.id` |
| Package003_Healthcare | 1.0.0 | Nothing — no counterpart record type exists |
| Package004_Industries | 1.0.0 | Opportunity `id` across 4 datasets |
| Package005_Agriculture | 1.0.0 | `crops.crop_id`, `farm_machinery.machinery_id`, `agri_processing_opportunities.opportunity_id` |
| Package006_Skills_and_Training | 1.0.0 | `skills.skill_id`, `training_providers.provider_id` |
| Package007_Government_Schemes | 1.0.0 | `government_schemes.scheme_id` |

If any upstream release renames these ids, V9 fails and Package008 needs a corresponding release.
This is the most upstream-dependent package in the programme — by design, since it is the
integration layer.
