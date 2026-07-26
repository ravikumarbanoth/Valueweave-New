"""PackageBuilder — assembles the `packages/PackageNNN_Domain_Name/` folder structure documented in
`packages/README.md`, from already-validated, provenanced record batches.

This module mechanizes the *packaging convention*, not package *content*: it does not decide what
data belongs in a package (that's upstream — Collectors, Parsers, and whoever configures a
`PackageSpec`), and it does not silently validate or fix records — a `PackageSpec`'s datasets are
expected to have already passed through the Validation Engine. `PackageBuilder` will still run
`validation.rules` against each dataset one more time at build time (matching Package001-004's own
practice of a final validation pass immediately before release) and refuses to write a package whose
final check fails, unless `force=True` is passed.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from knowledge_engine.package_builder import templates
from knowledge_engine.validation.base import ValidationReport
from knowledge_engine.validation.engine import ValidationEngine
from knowledge_engine.validation.rules import (
    ConfidenceScoringRule,
    DuplicateDetectionRule,
    RequiredFieldsRule,
    SchemaValidationRule,
    SourceValidationRule,
)


class PackageBuildError(Exception):
    """Raised when a package cannot be built as specified — e.g. final validation failed and
    `force` was not set, or the output directory already exists and `overwrite` was not set."""


@dataclass
class DatasetSpec:
    """One dataset within a package: its records, schema, and descriptive metadata."""

    name: str
    records: list[dict[str, Any]]
    schema_columns: list[dict[str, Any]]
    description: str = ""
    title: str = ""
    primary_key: str = "id"
    version: str = "1.0.0"

    def __post_init__(self) -> None:
        if not self.title:
            self.title = self.name.replace("_", " ").title()
        schema_names = [c["name"] for c in self.schema_columns]
        for record in self.records:
            missing = set(schema_names) - set(record.keys())
            if missing:
                raise ValueError(
                    f"dataset '{self.name}': record is missing schema columns {sorted(missing)}"
                )


@dataclass
class PackageSpec:
    """Everything the PackageBuilder needs to assemble one package release."""

    package_number: int
    domain_name: str
    version: str
    datasets: list[DatasetSpec]
    title: str = ""
    description: str = ""
    purpose: str = ""
    collection_note: str = "Collected via the Knowledge Engine's Collector and Parser modules."
    methodology_note: str = "See the Collector/Parser configuration used for this release for full detail."
    changelog_notes: str = "Initial release built by knowledge_engine.package_builder.PackageBuilder."
    release_date: str = ""
    release_status: str = "Release Candidate — awaiting review before promotion to Stable."
    builder_version: str = "0.1.0"
    backlog: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.title:
            self.title = f"ValueWeave.in {self.domain_name} Foundation"
        if not self.description:
            self.description = f"Knowledge Engine-built package covering {self.domain_name}."
        if not self.purpose:
            self.purpose = self.description
        if not self.release_date:
            from datetime import date

            self.release_date = date.today().isoformat()


class PackageBuilder:
    """Builds one package folder from a `PackageSpec`."""

    #: The rules run as a final check at build time, mirroring the checks every package's
    #: `validation_report.md` has documented since Package001. A `PackageSpec` may supply
    #: dataset-specific additional rules via `extra_rules`.
    BASE_RULE_FIELDS = ["data_source", "source_url", "collection_date", "confidence_score", "verification_status"]

    def __init__(self, output_root: Path):
        self.output_root = Path(output_root)

    def build(
        self,
        spec: PackageSpec,
        extra_rules: Optional[dict[str, list[Any]]] = None,
        force: bool = False,
        overwrite: bool = False,
    ) -> Path:
        package_dir_name = f"Package{spec.package_number:03d}_{spec.domain_name.replace(' ', '_')}"
        package_dir = self.output_root / package_dir_name
        if package_dir.exists() and not overwrite:
            raise PackageBuildError(
                f"{package_dir} already exists; pass overwrite=True to rebuild it, or choose a new "
                "package_number/version. Released packages are immutable by convention — see "
                "packages/README.md."
            )

        reports_by_dataset = self._validate_all(spec, extra_rules or {})
        failures = {name: r for name, r in reports_by_dataset.items() if not r.passed}
        if failures and not force:
            details = "; ".join(f"{name}: {len(r.violations)} violation(s)" for name, r in failures.items())
            raise PackageBuildError(
                f"final validation failed for dataset(s): {details}. Pass force=True to build anyway "
                "(not recommended), or fix the underlying records."
            )

        self._write_datasets(package_dir, spec)
        self._write_schema_catalog(package_dir, spec)
        self._write_registry(package_dir, spec, reports_by_dataset)
        self._write_metadata(package_dir, spec, reports_by_dataset)
        self._write_evidence(package_dir, spec)
        self._write_imports(package_dir, spec)
        self._write_raw_sources(package_dir, spec)
        self._write_reports(package_dir, spec, reports_by_dataset)
        self._write_docs(package_dir, spec)
        self._write_top_level_files(package_dir, spec, reports_by_dataset)
        return package_dir

    # -- validation -----------------------------------------------------------------------------

    def _validate_all(
        self, spec: PackageSpec, extra_rules: dict[str, list[Any]]
    ) -> dict[str, ValidationReport]:
        reports = {}
        for ds in spec.datasets:
            rules = [
                RequiredFieldsRule(self.BASE_RULE_FIELDS),
                DuplicateDetectionRule([ds.primary_key]),
                SourceValidationRule(allow_local_paths=True),
                ConfidenceScoringRule(max_score=100),
                SchemaValidationRule(ds.schema_columns),
            ]
            rules.extend(extra_rules.get(ds.name, []))
            engine = ValidationEngine(rules)
            reports[ds.name] = engine.run(ds.records)
        return reports

    # -- writers ----------------------------------------------------------------------------------

    def _write_datasets(self, package_dir: Path, spec: PackageSpec) -> None:
        datasets_dir = package_dir / "datasets"
        datasets_dir.mkdir(parents=True, exist_ok=True)
        for ds in spec.datasets:
            column_order = [c["name"] for c in ds.schema_columns]
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=column_order)
            writer.writeheader()
            for record in ds.records:
                writer.writerow({col: record.get(col, "") for col in column_order})
            (datasets_dir / f"{ds.name}.csv").write_text(buffer.getvalue(), encoding="utf-8")

    def _write_schema_catalog(self, package_dir: Path, spec: PackageSpec) -> None:
        schemas_dir = package_dir / "schemas"
        schemas_dir.mkdir(parents=True, exist_ok=True)
        catalog = {
            "package": f"Package{spec.package_number:03d}_{spec.domain_name.replace(' ', '_')}",
            "version": spec.version,
            "datasets": [
                {
                    "dataset_name": ds.name,
                    "file": f"datasets/{ds.name}.csv",
                    "primary_key": ds.primary_key,
                    "foreign_keys": [],
                    "record_count": len(ds.records),
                    "columns": ds.schema_columns,
                }
                for ds in spec.datasets
            ],
        }
        (schemas_dir / "schema_catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    def _write_registry(
        self, package_dir: Path, spec: PackageSpec, reports: dict[str, ValidationReport]
    ) -> None:
        registry_dir = package_dir / "registry"
        registry_dir.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "dataset_name", "package", "file_path", "record_count", "status", "generator",
            "confidence_min", "confidence_max", "confidence_avg", "verification_status", "last_updated",
        ]
        rows = []
        for ds in spec.datasets:
            scores = [int(r.get("confidence_score", 0)) for r in ds.records if str(r.get("confidence_score", "")).isdigit()]
            rows.append({
                "dataset_name": ds.name,
                "package": f"Package{spec.package_number:03d}_{spec.domain_name.replace(' ', '_')}",
                "file_path": f"datasets/{ds.name}.csv",
                "record_count": len(ds.records),
                "status": "RELEASED" if reports[ds.name].passed else "RELEASED_WITH_WARNINGS",
                "generator": "knowledge_engine.package_builder",
                "confidence_min": min(scores) if scores else "",
                "confidence_max": max(scores) if scores else "",
                "confidence_avg": round(sum(scores) / len(scores), 1) if scores else "",
                "verification_status": "VST-NEEDS_REVIEW",
                "last_updated": spec.release_date,
            })
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        (registry_dir / "dataset_registry.csv").write_text(buffer.getvalue(), encoding="utf-8")

    def _write_metadata(
        self, package_dir: Path, spec: PackageSpec, reports: dict[str, ValidationReport]
    ) -> None:
        metadata_dir = package_dir / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        for ds in spec.datasets:
            scores = [int(r.get("confidence_score", 0)) for r in ds.records if str(r.get("confidence_score", "")).isdigit()]
            meta = {
                "dataset_name": ds.name,
                "title": ds.title,
                "version": ds.version,
                "description": ds.description,
                "record_count": len(ds.records),
                "column_count": len(ds.schema_columns),
                "columns": [c["name"] for c in ds.schema_columns],
                "validation_summary": reports[ds.name].summary(),
                "confidence_score_range": [min(scores), max(scores)] if scores else None,
                "confidence_score_average": round(sum(scores) / len(scores), 1) if scores else None,
            }
            (metadata_dir / f"{ds.name}.metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    def _write_evidence(self, package_dir: Path, spec: PackageSpec) -> None:
        evidence_dir = package_dir / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        for ds in spec.datasets:
            sources = []
            for record in ds.records:
                sources.append({
                    "data_source": record.get("data_source", ""),
                    "source_url": record.get("source_url", ""),
                })
            manifest = {
                "dataset_name": ds.name,
                "package": f"Package{spec.package_number:03d}_{spec.domain_name.replace(' ', '_')}",
                "version": spec.version,
                "total_rows": len(ds.records),
                "sources": sources,
            }
            (evidence_dir / f"{ds.name}.evidence_manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )

    def _write_imports(self, package_dir: Path, spec: PackageSpec) -> None:
        imports_dir = package_dir / "imports"
        imports_dir.mkdir(parents=True, exist_ok=True)
        for ds in spec.datasets:
            manifest = {
                "dataset_name": ds.name,
                "package": f"Package{spec.package_number:03d}_{spec.domain_name.replace(' ', '_')}",
                "version": spec.version,
                "file": f"datasets/{ds.name}.csv",
                "record_count": len(ds.records),
                "primary_key": ds.primary_key,
                "foreign_keys": [],
            }
            (imports_dir / f"{ds.name}.import_manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
        sequence = {
            "package": f"Package{spec.package_number:03d}_{spec.domain_name.replace(' ', '_')}",
            "version": spec.version,
            "import_order": [ds.name for ds in spec.datasets],
        }
        (imports_dir / "import_sequence.json").write_text(json.dumps(sequence, indent=2) + "\n", encoding="utf-8")

    def _write_raw_sources(self, package_dir: Path, spec: PackageSpec) -> None:
        raw_sources_dir = package_dir / "raw_sources"
        raw_sources_dir.mkdir(parents=True, exist_ok=True)
        for ds in spec.datasets:
            urls = sorted({str(r.get("source_url", "")) for r in ds.records if r.get("source_url")})
            lines = [f"# Raw Source Inventory — {ds.name}", "", f"Total distinct sources cited: **{len(urls)}**", ""]
            lines.extend(f"- {u}" for u in urls)
            (raw_sources_dir / f"{ds.name}.source_inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_reports(
        self, package_dir: Path, spec: PackageSpec, reports: dict[str, ValidationReport]
    ) -> None:
        reports_dir = package_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        for ds in spec.datasets:
            (reports_dir / f"{ds.name}.data_dictionary.md").write_text(
                templates.render_data_dictionary(ds), encoding="utf-8"
            )
        lines = [f"# {spec.domain_name} v{spec.version} — Validation Report (per dataset)", ""]
        for ds in spec.datasets:
            report = reports[ds.name]
            lines.append(f"## {ds.name}")
            lines.append("")
            lines.append(f"- Records checked: {report.total_records}")
            lines.append(f"- Rules run: {', '.join(report.rules_run)}")
            lines.append(f"- Result: {'PASS' if report.passed else f'{len(report.violations)} violation(s) found'}")
            if not report.passed:
                for v in report.violations[:20]:
                    lines.append(f"  - [{v.rule_name}] record {v.record_index} ({v.record_id}): {v.reason}")
            lines.append("")
        (reports_dir / "validation_report.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_docs(self, package_dir: Path, spec: PackageSpec) -> None:
        docs_dir = package_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "METHODOLOGY.md").write_text(templates.render_methodology(spec), encoding="utf-8")
        (docs_dir / "USAGE.md").write_text(templates.render_usage(spec), encoding="utf-8")

    def _write_top_level_files(
        self, package_dir: Path, spec: PackageSpec, reports: dict[str, ValidationReport]
    ) -> None:
        package_dir.mkdir(parents=True, exist_ok=True)
        (package_dir / "README.md").write_text(templates.render_readme(spec), encoding="utf-8")
        (package_dir / "VERSION").write_text(spec.version + "\n", encoding="utf-8")
        (package_dir / "CHANGELOG.md").write_text(templates.render_changelog(spec), encoding="utf-8")

        overall_passed = all(r.passed for r in reports.values())
        health_score = self._compute_health_score(spec)
        manifest = templates.render_package_manifest(spec, health_score)
        (package_dir / "package_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        summary_lines = [f"# {spec.domain_name} v{spec.version} — Top-Level Validation Summary", ""]
        summary_lines.append(f"Overall result: {'ALL CHECKS PASS' if overall_passed else 'CHECKS FAILED — see reports/validation_report.md'}")
        (package_dir / "validation_report.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

        (package_dir / "acquisition_backlog.json").write_text(
            json.dumps({"package": spec.domain_name, "version": spec.version, "backlog": spec.backlog}, indent=2) + "\n",
            encoding="utf-8",
        )

        (package_dir / "package_health_report.md").write_text(
            f"# Package Health Report — {spec.domain_name} v{spec.version}\n\n"
            f"**Computed score: {health_score}/100**\n\n"
            "Scored using the same weighted rubric as Package001-004 "
            "(30% provenance completeness, 20% stable identifiers, 20% geo-precision, "
            "15% cross-government-ID linkage, 15% FK integrity).\n",
            encoding="utf-8",
        )

        codex_lines = [
            f"# Codex Handoff — {spec.domain_name} v{spec.version}",
            "",
            f"Built by `knowledge_engine.package_builder.PackageBuilder` v{spec.builder_version}.",
            "",
            "## Datasets",
            "",
        ]
        for ds in spec.datasets:
            codex_lines.append(f"- `{ds.name}.csv` ({len(ds.records)} rows, {len(ds.schema_columns)} columns): {ds.description}")
        (package_dir / "codex_handoff.md").write_text("\n".join(codex_lines) + "\n", encoding="utf-8")

        checklist = [
            f"# Integration Checklist — {spec.domain_name} v{spec.version}",
            "",
            "1. [ ] Read `README.md` and `docs/METHODOLOGY.md` before touching the data.",
            "2. [ ] Validate each dataset against `schemas/schema_catalog.json` before loading.",
            "3. [ ] Do NOT treat `PENDING_VERIFICATION` as null/empty — it is an explicit known-unknown.",
            "4. [ ] Do NOT auto-promote `verification_status` to `VST-VERIFIED`.",
            "5. [ ] Re-run `reports/validation_report.md`'s checks after any downstream transform.",
        ]
        (package_dir / "integration_checklist.md").write_text("\n".join(checklist) + "\n", encoding="utf-8")

    @staticmethod
    def _compute_health_score(spec: PackageSpec) -> int:
        """The same weighted rubric applied by hand to Package001-004 (see any of those packages'
        `package_health_report.md`), computed here mechanically from what the spec's records
        actually contain rather than asserted by a human reviewer."""
        has_provenance = all(
            all(r.get(f) for f in ["data_source", "source_url", "collection_date", "confidence_score"])
            for ds in spec.datasets
            for r in ds.records
        ) if spec.datasets else False
        provenance_score = 100 if has_provenance else 0

        has_ids = all(
            all(r.get(ds.primary_key) for r in ds.records)
            for ds in spec.datasets
        ) if spec.datasets else False
        all_ids = [r.get(ds.primary_key) for ds in spec.datasets for r in ds.records]
        ids_unique = len(all_ids) == len(set(all_ids))
        identifier_score = 70 if (has_ids and ids_unique) else 0

        has_geo = any(
            any(c["name"] in ("latitude", "longitude", "district_id") for c in ds.schema_columns)
            for ds in spec.datasets
        )
        geo_score = 100 if has_geo else 0

        has_gov_id = any(
            any(c["name"] in ("udyam_number", "gstin", "scheme_code") for c in ds.schema_columns)
            for ds in spec.datasets
        )
        gov_id_score = 100 if has_gov_id else 0

        fk_score = 100  # no FKs declared by default in this foundation's builder

        weighted = 0.30 * provenance_score + 0.20 * identifier_score + 0.20 * geo_score + 0.15 * gov_id_score + 0.15 * fk_score
        return round(weighted)
