# Version History — Package007_Government_Schemes

Released versions are immutable. Corrections and additions ship as new versions under
`Package007_Government_Schemes_vMAJOR.MINOR.PATCH`.

| Version | Date | Status | Datasets | Records | Schemes | Validation | Summary |
|---|---|---|---|---|---|---|---|
| **1.0.0** | 2026-07-25 | Stable | 15 | 655 | 40 | PASS (0 violations, 12 checks) | First release. Canonical scheme registry plus eligibility, benefits, process, institutions, five cross-package mappings and a recommendation layer. |
| 0.0.0 | 2026-07-20 | Placeholder | 0 | 0 | 0 | n/a | `README.md` reserving Package007 for government scheme assets. No data. |

## Semantic versioning policy

| Change class | Version bump | Examples |
|---|---|---|
| Correction with no structural or semantic change | **Patch** (1.0.x) | Fixing a typo in `objective`; correcting a `source_url` |
| Additive, backward-compatible | **Minor** (1.x.0) | New schemes; new datasets such as `health_scheme_mapping`; populating existing sentinels |
| Structural or breaking | **Major** (x.0.0) | Renaming or removing a column; changing a primary-key scheme; splitting the registry |

## v1.0.0 lineage notes

The package was built in four stages, each gated by validation:

1. **Core generation** (`gen_core.py`) — 7 scheme-intrinsic datasets
2. **Mapping generation** (`gen_mappings.py`) — 8 relational and workflow datasets, resolving
   cross-package foreign keys against the released upstream CSVs at generation time
3. **Validation** (`validate.py`) — 12 checks; 5 defect classes found and fixed before release
4. **Artifacts and documentation** (`build_artifacts.py`, `build_docs.py`) — generated from the
   CSVs plus the validation summary, so no count is hand-maintained

Two of the five defects were cross-package foreign keys pointing at upstream records that do not
exist. Both were caught because the generator resolves ids against the actual upstream CSVs and
aborts rather than writing an unresolvable reference. One of those cases is instructive: a
Package006 collection report describes an entrepreneurship skill that the released `skills.csv`
does not contain. Only reading the dataset — not its documentation — surfaced it.

## Upstream package versions this release was built against

| Package | Version | What Package007 references |
|---|---|---|
| Package001_Geography | 1.0.0 | `district.dist_id` (61 districts) |
| Package002_Education | 1.0.0 | `scholarships.id` |
| Package003_Healthcare | 1.0.0 | Declared in `also_in_package`; no hard FK yet |
| Package004_Industries | 1.0.0 | Opportunity names across 4 datasets |
| Package005_Agriculture | 1.0.0 | `agriculture_schemes.scheme_id`, `crops.crop_id` |
| Package006_Skills_and_Training | 1.0.0 | `government_skill_schemes.scheme_id`, `skills.skill_id`, `certifications.certification_id`, `training_providers.provider_id` |

If any upstream package issues a version that renames these ids, `validate.py` check V9 fails and
this package needs a corresponding release.
