"""ProvenanceTracker — attaches/updates ProvenanceRecords on parsed records without touching their
substantive fields.

Sits between the Parser Engine and the Validation Engine in the data flow described in
`architecture.md`: a Parser produces bare `dict` records with only domain fields; the tracker attaches
one `ProvenanceRecord` per record (flattened into the 6 provenance CSV columns) so the Validation
Engine's `SourceValidationRule`/`ConfidenceScoringRule`/etc. have something to check.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Callable, Optional

from knowledge_engine.core.provenance import ProvenanceRecord
from knowledge_engine.core.types import PENDING_VERIFICATION, VerificationStatus


class ProvenanceTracker:
    """Attaches a shared or per-record `ProvenanceRecord` to a batch of parsed records.

    Two usage modes:
    - `attach_uniform`: every record in the batch shares one provenance record (typical for a single
      API/CSV fetch where all rows came from the same source at the same time).
    - `attach_per_record`: a caller-supplied function derives a distinct `ProvenanceRecord` for each
      record (needed when, e.g., different rows cite different source URLs).
    """

    @staticmethod
    def attach_uniform(
        records: list[dict[str, Any]],
        provenance: ProvenanceRecord,
    ) -> list[dict[str, Any]]:
        fields = provenance.to_csv_fields()
        return [{**record, **fields} for record in records]

    @staticmethod
    def attach_per_record(
        records: list[dict[str, Any]],
        derive: Callable[[dict[str, Any]], ProvenanceRecord],
    ) -> list[dict[str, Any]]:
        result = []
        for record in records:
            fields = derive(record).to_csv_fields()
            result.append({**record, **fields})
        return result

    @staticmethod
    def mark_pending_verification(
        record: dict[str, Any],
        field: str,
        explanation: str,
    ) -> dict[str, Any]:
        """Set `record[field]` to the bare PENDING_VERIFICATION sentinel and append `explanation` to
        `notes` using the `[field_name]: explanation` convention — the exact normalization applied by
        hand across Package001-004 whenever a research pass wrote an inline explanation instead of
        the bare sentinel.
        """
        updated = dict(record)
        updated[field] = PENDING_VERIFICATION
        prefix = f"[{field}]: {explanation}"
        existing_notes = str(updated.get("notes", "")).strip()
        updated["notes"] = f"{existing_notes} | {prefix}" if existing_notes else prefix
        return updated

    @staticmethod
    def find_sentinel_violations(records: list[dict[str, Any]]) -> list[tuple[int, str, str]]:
        """Return (record_index, field_name, value) for every cell that starts with the
        PENDING_VERIFICATION sentinel but has extra text appended — the recurring bug found and
        fixed by hand three times across Package002-004. Running this before every commit is how
        that class of bug gets caught mechanically instead of by manual review.
        """
        violations = []
        for i, record in enumerate(records):
            for field_name, value in record.items():
                if not isinstance(value, str):
                    continue
                stripped = value.strip()
                if stripped.startswith(PENDING_VERIFICATION) and stripped != PENDING_VERIFICATION:
                    violations.append((i, field_name, value))
        return violations

    @staticmethod
    def default_provenance(
        source: str,
        source_url: list[str] | str,
        confidence: int,
        collector: str,
        collection_date: Optional[date] = None,
        package_version: Optional[str] = None,
        notes: str = "",
    ) -> ProvenanceRecord:
        """Convenience constructor for the common case of one uniform provenance record per batch."""
        urls = [source_url] if isinstance(source_url, str) else list(source_url)
        return ProvenanceRecord(
            source=source,
            source_url=urls,
            collection_date=collection_date or date.today(),
            collector=collector,
            confidence=confidence,
            verification_status=VerificationStatus.default(),
            package_version=package_version,
            notes=notes,
        )
