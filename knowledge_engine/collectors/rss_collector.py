"""RSSCollector — fetches a local or remote RSS/Atom feed as raw text.

RSS/Atom is XML under the hood, but gets its own Collector (rather than reusing XMLCollector
directly) so that feeds are discoverable and auto-detected by their own convention (URLs containing
"rss"/"feed", or a `.rss`/`.atom` extension) independent of generic `.xml` files.
"""

from __future__ import annotations

from typing import Any

from knowledge_engine.collectors._io import FetchError, read_source
from knowledge_engine.collectors.base import BaseCollector, FetchResult


class RSSCollector(BaseCollector):
    name = "rss_collector"
    version = "0.1.0"

    def fetch(self, source: str, encoding: str = "utf-8", **kwargs: Any) -> FetchResult:
        try:
            content, metadata = read_source(source, timeout=kwargs.get("timeout", 15.0),
                                        headers=kwargs.get("headers"))
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
        lowered = source.lower()
        return lowered.endswith((".rss", ".atom")) or "rss" in lowered or "feed" in lowered
