"""Runnable example: build a complete package folder (matching packages/README.md's convention)
from a small in-memory dataset, using the PackageBuilder. Writes to a temporary directory so running
this example never touches the real packages/ tree.

Run with: python examples/example_build_package.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from knowledge_engine.package_builder import DatasetSpec, PackageBuilder, PackageSpec

SCHEMA_COLUMNS = [
    {"name": "id", "type": "uuid", "description": "Unique row identifier"},
    {"name": "name", "type": "string", "description": "Opportunity name"},
    {"name": "district", "type": "string", "description": "Telangana/AP district"},
    {"name": "data_source", "type": "string"},
    {"name": "source_url", "type": "string"},
    {"name": "collection_date", "type": "date"},
    {"name": "confidence_score", "type": "integer", "range": [0, 100]},
    {"name": "verification_status", "type": "enum", "values": ["VST-NEEDS_REVIEW", "VST-VERIFIED"]},
    {"name": "notes", "type": "string"},
]

RECORDS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Example Opportunity A",
        "district": "Medak",
        "data_source": "Example Government Source",
        "source_url": "https://example.gov.in/a",
        "collection_date": "2026-07-24",
        "confidence_score": "75",
        "verification_status": "VST-NEEDS_REVIEW",
        "notes": "",
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "name": "Example Opportunity B",
        "district": "Warangal",
        "data_source": "Example Government Source",
        "source_url": "https://example.gov.in/b",
        "collection_date": "2026-07-24",
        "confidence_score": "68",
        "verification_status": "VST-NEEDS_REVIEW",
        "notes": "",
    },
]


def main() -> None:
    dataset = DatasetSpec(
        name="example_opportunities",
        records=RECORDS,
        schema_columns=SCHEMA_COLUMNS,
        description="Two example business opportunities, for demonstration only.",
    )
    spec = PackageSpec(
        package_number=900,
        domain_name="Example Domain",
        version="0.1.0-RC1",
        datasets=[dataset],
        purpose="Demonstrates PackageBuilder's output shape; not a real ValueWeave package.",
    )

    with tempfile.TemporaryDirectory() as tmp:
        builder = PackageBuilder(Path(tmp))
        package_dir = builder.build(spec)
        print(f"Built package at: {package_dir}")

        manifest = json.loads((package_dir / "package_manifest.json").read_text())
        print(f"Health score: {manifest['health_score']}/100")
        print(f"Total records: {manifest['total_records']}")

        print("\nFiles created:")
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                print(f"  {path.relative_to(package_dir)}")


if __name__ == "__main__":
    main()
