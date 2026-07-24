"""String templates the PackageBuilder fills in from a PackageSpec/DatasetSpec.

Kept separate from `builder.py` so the *content* of each generated file (what a README, a
CHANGELOG entry, a data dictionary row looks like) can be reviewed and adjusted without touching the
file-assembly logic that decides *where* each piece goes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - avoids a circular import at module load time
    from knowledge_engine.package_builder.builder import DatasetSpec, PackageSpec


def render_readme(spec: "PackageSpec") -> str:
    dataset_rows = "\n".join(
        f"| {ds.title or ds.name} | {len(ds.records)} | {ds.description} |" for ds in spec.datasets
    )
    total_records = sum(len(ds.records) for ds in spec.datasets)
    return f"""# Package {spec.package_number:03d} — {spec.domain_name}
### ValueWeave.in Data Factory · Release v{spec.version}

{spec.description}

## Purpose of This Package

{spec.purpose}

## Dataset List

| Dataset | Records | Covers |
|---|---|---|
{dataset_rows}

**Total: {total_records} records across {len(spec.datasets)} dataset(s).**

## A Note on How This Data Was Collected

{spec.collection_note}

## Folder Structure

```
Package{spec.package_number:03d}_{spec.domain_name.replace(' ', '_')}/
├── README.md                 — this file
├── package_manifest.json     — machine-readable package descriptor
├── CHANGELOG.md               — version history
├── VERSION                    — current version string
├── codex_handoff.md           — integration guide for an AI coding agent
├── integration_checklist.md   — step-by-step integration checklist
├── package_health_report.md   — coverage/completion/readiness scoring
├── validation_report.md       — top-level validation summary
├── acquisition_backlog.json   — every un-shipped scope item and what unblocks it
├── datasets/                  — the production CSVs
├── metadata/                  — source catalogues, confidence calibration, provenance stats
├── reports/                   — validation and quality reports
├── evidence/                  — source-citation audit trail
├── registry/                  — dataset_registry.csv, the cross-package control center
├── schemas/                   — schema_catalog.json, the canonical column/PK/FK reference
├── raw_sources/                — human-readable per-dataset source inventories
├── imports/                    — import_sequence.json and per-dataset import manifests
└── docs/                        — methodology and usage guides
```

## Validation Process

Every dataset in this package was validated by the Knowledge Engine's Validation Engine before
release — see `reports/validation_report.md` for the per-dataset results and `validation_report.md`
for the package-level summary.

## Release Status

**{spec.release_status}**
"""


def render_changelog(spec: "PackageSpec") -> str:
    dataset_bullets = "\n".join(
        f"- `{ds.name}.csv` — {len(ds.records)} rows: {ds.description}" for ds in spec.datasets
    )
    return f"""# CHANGELOG — {spec.domain_name}

## [{spec.version}] — {spec.release_date}

### Added
{dataset_bullets}
- `schemas/schema_catalog.json` — column-level schema reference for all datasets in this release
- `package_manifest.json`, `registry/dataset_registry.csv`, `metadata/*.metadata.json`,
  `evidence/*.evidence_manifest.json`, `imports/*.import_manifest.json`,
  `raw_sources/*.source_inventory.md` — provenance and integration scaffolding
- `reports/validation_report.md`, top-level `validation_report.md` — Knowledge Engine validation
  results for this release
- `docs/METHODOLOGY.md`, `docs/USAGE.md`, `codex_handoff.md`, `integration_checklist.md`,
  `package_health_report.md`, `acquisition_backlog.json`

### Notes
{spec.changelog_notes}
"""


def render_package_manifest(spec: "PackageSpec", health_score: int) -> dict:
    return {
        "package_name": f"Package{spec.package_number:03d}_{spec.domain_name.replace(' ', '_')}",
        "package_id": f"PKG-{spec.package_number:03d}",
        "package_title": spec.title,
        "version": spec.version,
        "release_date": spec.release_date,
        "release_status": spec.release_status,
        "description": spec.description,
        "datasets_included": [
            {
                "name": ds.name,
                "records": len(ds.records),
                "columns": len(ds.schema_columns),
            }
            for ds in spec.datasets
        ],
        "total_records": sum(len(ds.records) for ds in spec.datasets),
        "generated_by": "knowledge_engine.package_builder.PackageBuilder",
        "generator_version": spec.builder_version,
        "health_score": health_score,
    }


def render_data_dictionary(ds: "DatasetSpec") -> str:
    lines = [f"# Data Dictionary — {ds.name} (v{ds.version})", "", f"Records: {len(ds.records)}", "",
              "| Column | Type | Description |", "|---|---|---|"]
    for col in ds.schema_columns:
        desc = col.get("description", "")
        if "values" in col:
            desc = (desc + f" Allowed values: {', '.join(col['values'])}.").strip()
        lines.append(f"| {col['name']} | {col.get('type', 'string')} | {desc} |")
    return "\n".join(lines) + "\n"


def render_methodology(spec: "PackageSpec") -> str:
    return f"""# {spec.domain_name} v{spec.version} — Methodology

## Collection Approach

{spec.methodology_note}

## Validation

Every record in this package passed through the Knowledge Engine's Validation Engine
(`knowledge_engine/validation/`) before release — see `reports/validation_report.md` for the exact
rules run and their results per dataset.

## Provenance

Every record carries the 8-field provenance model defined in
`knowledge_engine/core/provenance.py` and documented in `knowledge_engine/provenance/schema.json`:
source, source URL(s), collection date, last verified date, collector, confidence score,
verification status, and package version.
"""


def render_usage(spec: "PackageSpec") -> str:
    dataset_rows = "\n".join(
        f"| `{ds.name}.csv` | {len(ds.records)} | {ds.description} |" for ds in spec.datasets
    )
    return f"""# {spec.domain_name} v{spec.version} — Usage Guide

## What's in this package

| File | Rows | Covers |
|---|---|---|
{dataset_rows}

## Before treating any row as fact-checked

Every row's `verification_status` starts at `VST-NEEDS_REVIEW`. Promotion to `VST-VERIFIED` is a
governance action performed outside this package's build process, never automatically.
"""
