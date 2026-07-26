"""Runnable example: Collector -> Parser -> Provenance -> Validation, end to end, on local fixture
data. No network access is required.

Run with: python examples/example_collect_and_validate.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from knowledge_engine.collectors import CSVCollector
from knowledge_engine.parsers import CSVParser
from knowledge_engine.provenance import ProvenanceTracker
from knowledge_engine.validation import (
    ConfidenceScoringRule,
    DuplicateDetectionRule,
    RequiredFieldsRule,
    SourceValidationRule,
    ValidationEngine,
)

FIXTURE_CSV = """id,name,district,minimum_investment,skill_level
1,Mushroom Cultivation,Medak,120000,Beginner
2,Cybersecurity Consulting,Hyderabad,800000,Advanced
3,Mushroom Cultivation,Medak,120000,Beginner
"""


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fixture_path = Path(tmp) / "opportunities.csv"
        fixture_path.write_text(FIXTURE_CSV, encoding="utf-8")

        # 1. Collect
        fetch_result = CSVCollector().fetch(str(fixture_path))
        print(f"Collected via {fetch_result.collector_label}: status={fetch_result.status}")

        # 2. Parse
        records = CSVParser().parse(fetch_result.payload)
        print(f"Parsed {len(records)} records")

        # 3. Attach provenance
        provenance = ProvenanceTracker.default_provenance(
            source="Example Fixture Data",
            source_url=f"file://{fixture_path}",
            confidence=72,
            collector=fetch_result.collector_label,
        )
        records = ProvenanceTracker.attach_uniform(records, provenance)

        # 4. Validate
        engine = ValidationEngine(
            [
                RequiredFieldsRule(["id", "name", "data_source", "source_url"]),
                DuplicateDetectionRule(["id"]),
                SourceValidationRule(allow_local_paths=True),
                ConfidenceScoringRule(max_score=85),
            ]
        )
        report = engine.run(records)
        print("Validation summary:", report.summary())

        # Note: this fixture intentionally has no duplicate `id` values, so this should show 0
        # violations. To see a duplicate_detection violation, change one row's id to collide with
        # another.


if __name__ == "__main__":
    main()
