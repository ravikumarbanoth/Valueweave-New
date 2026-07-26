import json
import tempfile
import unittest
from pathlib import Path

from knowledge_engine.package_builder.builder import (
    DatasetSpec,
    PackageBuildError,
    PackageBuilder,
    PackageSpec,
)

SCHEMA = [
    {"name": "id", "type": "string"},
    {"name": "name", "type": "string"},
    {"name": "data_source", "type": "string"},
    {"name": "source_url", "type": "string"},
    {"name": "collection_date", "type": "date"},
    {"name": "confidence_score", "type": "integer"},
    {"name": "verification_status", "type": "enum", "values": ["VST-NEEDS_REVIEW", "VST-VERIFIED"]},
    {"name": "notes", "type": "string"},
]


def _valid_record(record_id: str) -> dict:
    return {
        "id": record_id,
        "name": f"Item {record_id}",
        "data_source": "Test Source",
        "source_url": "https://example.gov.in/x",
        "collection_date": "2026-07-24",
        "confidence_score": "75",
        "verification_status": "VST-NEEDS_REVIEW",
        "notes": "",
    }


class DatasetSpecTest(unittest.TestCase):
    def test_missing_schema_column_raises_at_construction(self):
        with self.assertRaises(ValueError):
            DatasetSpec(name="ds", records=[{"id": "1"}], schema_columns=SCHEMA)

    def test_valid_records_construct_cleanly(self):
        ds = DatasetSpec(name="ds", records=[_valid_record("1")], schema_columns=SCHEMA)
        self.assertEqual(ds.title, "Ds")


class PackageBuilderTest(unittest.TestCase):
    def _spec(self, records) -> PackageSpec:
        ds = DatasetSpec(name="test_dataset", records=records, schema_columns=SCHEMA, description="desc")
        return PackageSpec(package_number=999, domain_name="Test Domain", version="0.1.0-RC1", datasets=[ds])

    def test_build_creates_full_folder_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self._spec([_valid_record("1"), _valid_record("2")])
            package_dir = PackageBuilder(Path(tmp)).build(spec)

            expected_files = [
                "README.md", "VERSION", "CHANGELOG.md", "package_manifest.json",
                "validation_report.md", "acquisition_backlog.json", "package_health_report.md",
                "codex_handoff.md", "integration_checklist.md",
                "datasets/test_dataset.csv", "schemas/schema_catalog.json",
                "registry/dataset_registry.csv", "metadata/test_dataset.metadata.json",
                "evidence/test_dataset.evidence_manifest.json",
                "imports/test_dataset.import_manifest.json", "imports/import_sequence.json",
                "raw_sources/test_dataset.source_inventory.md",
                "reports/validation_report.md", "reports/test_dataset.data_dictionary.md",
                "docs/METHODOLOGY.md", "docs/USAGE.md",
            ]
            for relative_path in expected_files:
                self.assertTrue((package_dir / relative_path).exists(), f"missing {relative_path}")

    def test_csv_has_correct_row_and_column_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self._spec([_valid_record("1"), _valid_record("2")])
            package_dir = PackageBuilder(Path(tmp)).build(spec)
            csv_text = (package_dir / "datasets" / "test_dataset.csv").read_text()
            lines = csv_text.strip().split("\n")
            self.assertEqual(len(lines), 3)  # header + 2 rows
            self.assertEqual(len(lines[0].split(",")), len(SCHEMA))

    def test_manifest_is_valid_json_with_expected_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self._spec([_valid_record("1")])
            package_dir = PackageBuilder(Path(tmp)).build(spec)
            manifest = json.loads((package_dir / "package_manifest.json").read_text())
            self.assertEqual(manifest["total_records"], 1)
            self.assertIn("health_score", manifest)

    def test_refuses_to_overwrite_existing_package_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self._spec([_valid_record("1")])
            builder = PackageBuilder(Path(tmp))
            builder.build(spec)
            with self.assertRaises(PackageBuildError):
                builder.build(spec)

    def test_overwrite_true_allows_rebuild(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self._spec([_valid_record("1")])
            builder = PackageBuilder(Path(tmp))
            builder.build(spec)
            builder.build(spec, overwrite=True)  # should not raise

    def test_duplicate_ids_fail_final_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self._spec([_valid_record("1"), _valid_record("1")])
            with self.assertRaises(PackageBuildError):
                PackageBuilder(Path(tmp)).build(spec)

    def test_force_true_builds_despite_validation_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self._spec([_valid_record("1"), _valid_record("1")])
            package_dir = PackageBuilder(Path(tmp)).build(spec, force=True)
            registry_csv = (package_dir / "registry" / "dataset_registry.csv").read_text()
            self.assertIn("RELEASED_WITH_WARNINGS", registry_csv)

    def test_health_score_matches_hand_built_package_pattern(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self._spec([_valid_record("1"), _valid_record("2")])
            package_dir = PackageBuilder(Path(tmp)).build(spec)
            manifest = json.loads((package_dir / "package_manifest.json").read_text())
            # Matches the 59/100 pattern documented across Package001-004's health reports for a
            # dataset with full provenance but no geo/cross-government-ID columns.
            self.assertEqual(manifest["health_score"], 59)


if __name__ == "__main__":
    unittest.main()
