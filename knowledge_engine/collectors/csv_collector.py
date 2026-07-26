"""CSVCollector — fetches a local or remote CSV file as raw text."""

from __future__ import annotations

from typing import Any

from knowledge_engine.collectors._io import FetchError, read_source
from knowledge_engine.collectors.base import BaseCollector, FetchResult


class CSVCollector(BaseCollector):
    name = "csv_collector"
    version = "0.1.0"

    def fetch(self, source: str, encoding: str = "utf-8", **kwargs: Any) -> FetchResult:
        try:
            content, metadata = read_source(source)
        except FetchError as exc:
            return FetchResult(
                payload=None,
                source_url=source,
                collector_name=self.name,
                collector_version=self.version,
                status="error",
                error=str(exc),
            )
        return FetchResult(
            payload=content.decode(encoding),
            source_url=source,
            collector_name=self.name,
            collector_version=self.version,
            metadata=metadata,
        )

    def supports(self, source: str) -> bool:
        return source.lower().endswith(".csv")
