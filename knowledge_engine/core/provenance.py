"""The ProvenanceRecord model — the Provenance Engine's core data structure.

Every record that survives the Validation Engine carries one of these, matching the 8-field evidence
trail used by hand in Package001_Geography through Package004_Industries: Source, Source URL,
Collection Date, Last Verified, Collector, Confidence, Verification Status, Package Version.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from knowledge_engine.core.types import VerificationStatus


@dataclass
class ProvenanceRecord:
    """The canonical 8-field provenance model.

    Attributes:
        source: Human-readable description of the source (e.g. "data.gov.in Open Government Data
            Platform" or "WebSearch aggregation of government portals").
        source_url: The specific URL(s) the fact was drawn from. Multiple URLs are represented as a
            list; downstream CSV serialization joins them with "; " to match the existing package
            convention of semicolon-separated multi-source cells.
        collection_date: The date this fact was first collected.
        last_verified: The date this fact was last re-checked against its source. Equals
            `collection_date` until a re-verification pass updates it.
        collector: The name (and, where relevant, version) of the Collector/Parser pipeline that
            produced this record, e.g. "csv_collector.CSVCollector/0.1.0" or
            "manual/websearch-agent".
        confidence: An integer 0-100 confidence score, calibrated per `core.types.ConfidenceTier`.
        verification_status: One of `core.types.VerificationStatus`. Defaults to NEEDS_REVIEW; a
            Knowledge Engine module must never construct a record with VERIFIED status directly.
        package_version: The semantic version of the package this record was collected for/into,
            e.g. "1.0.0" or "1.0.0-RC1". None while a record is still in staging, pre-package-build.
        notes: Free-text context — required whenever a field value is the PENDING_VERIFICATION
            sentinel, per the `[field_name]: explanation` convention used across all packages.
    """

    source: str
    source_url: list[str]
    collection_date: date
    collector: str
    confidence: int
    last_verified: Optional[date] = None
    verification_status: VerificationStatus = field(default_factory=VerificationStatus.default)
    package_version: Optional[str] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("ProvenanceRecord.source must not be empty")
        if not self.source_url:
            raise ValueError("ProvenanceRecord.source_url must contain at least one URL")
        if not (0 <= self.confidence <= 100):
            raise ValueError(f"confidence must be 0-100, got {self.confidence}")
        if self.last_verified is None:
            self.last_verified = self.collection_date

    def to_csv_fields(self) -> dict[str, str]:
        """Render this provenance record as the 6 flat CSV columns every package's datasets carry.

        Returns a dict with keys `data_source`, `source_url`, `collection_date`, `confidence_score`,
        `verification_status`, `notes` — matching `schemas/schema_catalog.json`'s column names across
        Package001-004 exactly, so records can be written straight into a package CSV.
        """
        return {
            "data_source": self.source,
            "source_url": "; ".join(self.source_url),
            "collection_date": self.collection_date.isoformat(),
            "confidence_score": str(self.confidence),
            "verification_status": self.verification_status.value,
            "notes": self.notes,
        }

    def to_dict(self) -> dict[str, Any]:
        """Full-fidelity serialization (for the Knowledge Database), including `last_verified` and
        `package_version`, which `to_csv_fields()` intentionally omits because no existing package's
        CSV schema carries them as separate columns."""
        d = asdict(self)
        d["collection_date"] = self.collection_date.isoformat()
        d["last_verified"] = self.last_verified.isoformat() if self.last_verified else None
        d["verification_status"] = self.verification_status.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProvenanceRecord":
        parsed = dict(data)
        parsed["collection_date"] = _parse_date(parsed["collection_date"])
        if parsed.get("last_verified"):
            parsed["last_verified"] = _parse_date(parsed["last_verified"])
        else:
            parsed["last_verified"] = None
        if "verification_status" in parsed:
            parsed["verification_status"] = VerificationStatus(parsed["verification_status"])
        return cls(**parsed)

    def re_verify(self, as_of: Optional[date] = None, new_confidence: Optional[int] = None) -> None:
        """Record a re-verification pass. Never silently raises confidence beyond +8 over the
        previous value, matching the discipline applied by hand during Package004's enrichment pass.
        """
        if new_confidence is not None:
            if new_confidence < self.confidence:
                raise ValueError(
                    "re_verify must not lower confidence; construct a new record if a fact was "
                    "found to be less reliable than previously recorded"
                )
            if new_confidence - self.confidence > 8:
                raise ValueError(
                    f"confidence increase of {new_confidence - self.confidence} exceeds the "
                    "+8-per-re-verification-pass discipline"
                )
            self.confidence = new_confidence
        self.last_verified = as_of or datetime.utcnow().date()


def _parse_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))
