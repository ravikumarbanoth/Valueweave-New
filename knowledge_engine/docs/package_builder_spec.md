# Package Builder Specification

Module 5, `package_builder/`. Mechanizes the packaging convention documented in `packages/README.md`
and followed by hand for Package001_Geography through Package004_Industries, so a future package can
be assembled from already-collected, validated, provenanced records without manual folder assembly.

## 1. Inputs: DatasetSpec and PackageSpec

```python
@dataclass
class DatasetSpec:
    name: str
    records: list[dict]
    schema_columns: list[dict]     # schema_catalog.json-shaped column definitions
    description: str = ""
    title: str = ""                 # defaults to a title-cased version of `name`
    primary_key: str = "id"
    version: str = "1.0.0"

@dataclass
class PackageSpec:
    package_number: int
    domain_name: str
    version: str
    datasets: list[DatasetSpec]
    title: str = ""                  # defaults to "ValueWeave.in {domain_name} Foundation"
    description: str = ""
    purpose: str = ""
    collection_note: str = "..."
    methodology_note: str = "..."
    changelog_notes: str = "..."
    release_date: str = ""           # defaults to today
    release_status: str = "Release Candidate — awaiting review before promotion to Stable."
    backlog: list[dict] = []
```

`DatasetSpec.__post_init__` raises immediately if any record is missing a column declared in
`schema_columns` — a spec-construction-time check, before any file is written, so a malformed spec
fails fast rather than producing a package with ragged CSV rows.

## 2. What Gets Built

`PackageBuilder(output_root).build(spec)` creates `output_root/PackageNNN_Domain_Name/` containing
every file documented in `packages/README.md`'s folder structure:

| File/Folder | Generated from |
|---|---|
| `README.md` | `templates.render_readme(spec)` |
| `VERSION` | `spec.version` |
| `CHANGELOG.md` | `templates.render_changelog(spec)` |
| `package_manifest.json` | `templates.render_package_manifest(spec, health_score)` |
| `datasets/*.csv` | each `DatasetSpec.records`, columns ordered per `schema_columns` |
| `schemas/schema_catalog.json` | every dataset's `schema_columns` |
| `registry/dataset_registry.csv` | one row per dataset with confidence min/max/avg computed from records |
| `metadata/*.metadata.json` | per-dataset stats + that dataset's `ValidationReport.summary()` |
| `evidence/*.evidence_manifest.json` | every record's `data_source`/`source_url` |
| `imports/*.import_manifest.json`, `imports/import_sequence.json` | dataset order and record counts |
| `raw_sources/*.source_inventory.md` | distinct `source_url` values per dataset |
| `reports/validation_report.md`, `reports/*.data_dictionary.md` | the final validation pass + schema |
| `docs/METHODOLOGY.md`, `docs/USAGE.md` | `spec.methodology_note`, dataset descriptions |
| `codex_handoff.md`, `integration_checklist.md` | dataset list + standard integration warnings |
| `package_health_report.md` | the computed health score (see below) |
| `validation_report.md` (top-level) | pass/fail summary across all datasets |
| `acquisition_backlog.json` | `spec.backlog` |

## 3. The Final Validation Pass

Before writing anything, `PackageBuilder.build()` runs a `ValidationEngine` over every dataset with a
baseline rule set (`RequiredFieldsRule` on the 5 core provenance columns, `DuplicateDetectionRule` on
the primary key, `SourceValidationRule`, `ConfidenceScoringRule`, `SchemaValidationRule`) plus any
`extra_rules` the caller supplies per dataset. If any dataset fails, `build()` raises
`PackageBuildError` **and writes nothing** — unless the caller passes `force=True`, which writes the
package anyway but records `"RELEASED_WITH_WARNINGS"` in `dataset_registry.csv` instead of
`"RELEASED"`. This mirrors Package001-004's practice of a final validation pass immediately before
release, made mandatory rather than optional.

## 4. Health Score Computation

`PackageBuilder._compute_health_score()` reimplements the exact weighted rubric applied by hand in
every `package_health_report.md` so far:

```
0.30 × provenance_completeness + 0.20 × stable_identifiers +
0.20 × geo_precision + 0.15 × cross_government_id_linkage + 0.15 × fk_integrity
```

- **Provenance completeness** (100 or 0): do all records across all datasets have
  `data_source`/`source_url`/`collection_date`/`confidence_score`?
- **Stable identifiers** (70 or 0): are primary keys present and unique across every dataset? (Capped
  at 70, not 100, because this foundation's builder doesn't yet support a secondary immutable
  reference-code system — matching why every hand-built package has scored 70 here too.)
- **Geo-precision** (100 or 0): does any dataset declare a `latitude`/`longitude`/`district_id`
  column?
- **Cross-government-ID linkage** (100 or 0): does any dataset declare a
  `udyam_number`/`gstin`/`scheme_code` column?
- **FK integrity** (100, always, in this release): no foreign keys are declared by the builder's
  baseline rule set, so none can be broken — matching every hand-built package's "100% of what
  exists" scoring.

Running this against a real `PackageSpec` reproduces the same 58-59/100 range documented in
Package001-004's health reports whenever the same structural gaps (no geo layer, no cross-government
IDs) are present — a useful cross-check that the mechanized score means the same thing as the
hand-computed one.

## 5. Immutability

`build()` refuses to overwrite an existing `PackageNNN_Domain_Name/` directory unless
`overwrite=True` is passed — released packages are immutable by convention (`packages/README.md`);
producing a new version means calling `build()` with an updated `PackageSpec.version`, not overwriting
the old one in place.

## 6. What the Package Builder Does NOT Do

- It does not decide package *content* — what records exist, what they say — that's entirely upstream
  (Collectors, Parsers, whoever assembles a `PackageSpec`).
- It does not merge into `packages/` or `main` — `output_root` is any directory the caller chooses; a
  human (or a future CI step) reviews the built package before it's copied into `packages/` and
  committed.
- It does not run AI-based content generation for any doc field — every generated file's content
  comes directly from the `PackageSpec`/`DatasetSpec` fields a caller provides.
