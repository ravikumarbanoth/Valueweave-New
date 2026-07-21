# CHANGELOG — Package001_Geography

## [1.0.0] — 2026-07-20

### Finalized
- Promoted 1.0.0-RC1 to the final production release. No dataset, schema, or content changes — this is a packaging finalization only, per the frozen-architecture instruction governing this release.
- Excluded two artifacts from the shipped SDK payload as working notes / process documents rather than package content: `PACKAGE_001_INVENTORY.md` (the Release Audit's own duplicate-finding working paper) and `engineering_recommendation.md` (forward-looking roadmap content about work outside this package's scope). Both remain available in the project's release history; neither is required by, or referenced from, any shipped SDK file.
- `VERSION` updated from `1.0.0-RC1` to `1.0.0`; `package_manifest.json`'s `version` and `release_date` fields updated to match.
- `README.md` title and folder-tree listing updated to remove the now-excluded `PACKAGE_001_INVENTORY.md` reference.
- Confirmed all 35 shipped files conform to the SDK v1.0 naming convention (`{dataset}.{artifact_type}.{ext}` per-dataset; `{dataset1}_{dataset2}.{artifact_type}.{ext}` for artifacts covering a joint collection batch; unprefixed for package-level artifacts) — zero renames were required, since this convention was already established and applied consistently during the prior Release Audit.
- Confirmed exactly one canonical copy of every metadata, manifest, and registry file — no new duplicates introduced since the RC1 audit.

## [1.0.0-RC1] — 2026-07-19

### Added
- `state.csv` — 2 states (Telangana, Andhra Pradesh)
- `district.csv` — 61 districts (33 TG + 28 AP)
- `revenue_division_telangana.csv` — 75 revenue divisions
- `revenue_division_andhra_pradesh.csv` — schema only (0 rows, see Blocked)
- `mandal.csv` — schema only (0 rows, see Blocked)
- `schemas/schema_catalog.json` — new centralized PK/FK/relationship reference for all datasets in the package
- `imports/import_sequence.json` — Codex-facing import ordering with per-step validation and rollback
- `codex_handoff.md`, `integration_checklist.md`, `acquisition_backlog.json`, `package_health_report.md` — new release-management artifacts
- `PACKAGE_001_INVENTORY.md` — full artifact inventory and duplicate-resolution log (this audit)

### Updated
- `registry/dataset_registry.csv` schema evolved to include `mode_used` and `package` columns (now version 0.3.0 of the registry format)
- Directory structure standardized from four separate per-dataset folder trees (`state/`, `district/`, `revenue_division/`, `mandal/`, each with their own `csv/metadata/reports/manifest/raw_sources`) into the single flat, type-organized structure now in effect (`datasets/`, `metadata/`, `reports/`, `evidence/`, `registry/`, `schemas/`, `raw_sources/`, `imports/`)

### Corrected
- **Telangana Suryapet district revenue division count:** source table stated 2, but listed 3 division names and two independent dedicated pages confirmed 3 — corrected to 3, revising Telangana's total from the source's stated 74 to **75**.
- **Andhra Pradesh district count re-confirmed at 28** (not 29): a 25 Nov 2025 Group-of-Ministers proposal described a third new district (Madanapalle); the AP Cabinet's final 29 Dec 2025 decision did not adopt that part of the proposal. This is a confirmation of the existing `district.csv` figure, not a change to it.

### Deduplicated
- Merged two byte-identical copies of the State/District `metadata.json` into `metadata/state_district.metadata.json`
- Merged two byte-identical copies of the State/District `import_manifest.json` into `imports/state_district.import_manifest.json`
- Merged two byte-identical copies of the State/District collection report into `reports/state_district.collection_report.md`
- Merged the separate `revenue_division` and `mandal` `integration_map.json` files into the single package-wide `schemas/schema_catalog.json`
- Retired the pre-Package-structure `dataset_registry.csv` generation in favor of the current Package-aware version
- (Full detail: `PACKAGE_001_INVENTORY.md`, Task 2 Duplicate Findings #1–#5)

### Blocked
- **Andhra Pradesh Revenue Divisions** — 0 rows. The only available structured source is self-flagged stale by its own editors, its row-level division counts sum to 82 against its own stated total of 79, and this run independently confirmed at least one specific division (Nakkapalli, Anakapalli district) is missing from it. No data shipped rather than risk it (MODE C).
- **Mandal (Telangana & Andhra Pradesh)** — 0 rows. Every primary government source attempted this run returned either a `robots.txt` block or a fetch failure; the only available secondary compilation lost its table structure on extraction, making automated district-attribution unsafe.

### Known Issues
- No dataset in this release fully clears the ≥85 Tier-1 confidence threshold for **both** states simultaneously (Telangana District and most Telangana Revenue Division rows individually clear it; Andhra Pradesh does not, on either dataset).
- LGD codes are 0% populated across every dataset in this release.
- Latitude/longitude geocoding is 0% populated across every dataset in this release.
- `mandal_count` on `revenue_division_telangana.csv` is independently verified for only 6 of 75 rows; the remaining 69 carry the district-level count as a less-precise placeholder pending direct sub-page verification.

### Future Work
- Obtain the AP gazette notification to unblock Andhra Pradesh Revenue Division and upgrade District from provisional to confirmed.
- Obtain (via manual download/upload) the LGD export or Census/Statistical Abstract PDF to unblock Mandal.
- Batch-geocode all district and revenue-division headquarters.
- Populate LGD codes package-wide in a single dedicated pass rather than per-dataset.
- Proceed to Village, Municipal Corporations/ULBs, Industrial Parks/SEZ, Infrastructure, Water Resources, and Natural Resources per the dependency-ordered queue in `registry/dataset_registry.csv`.
