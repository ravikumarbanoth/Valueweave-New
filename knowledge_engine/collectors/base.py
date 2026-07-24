"""Collector Engine — base interface and plugin registry.

A Collector's only job is to fetch a raw payload from a named source and return it, unparsed,
alongside fetch metadata. Interpreting the payload into records is the Parser Engine's job
(see `parsers/base.py`). This separation is what lets one Parser (e.g. `JSONParser`) serve payloads
fetched by multiple different Collectors (a local file, an HTTP API, an S3 bucket in the future) with
no changes to either side.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class FetchResult:
    """The raw output of a Collector run.

    Attributes:
        payload: The unparsed payload — bytes, str, or an already-decoded structure, depending on
            the collector. Parsers declare which payload shapes they accept.
        source_url: Where this payload came from (a URL, a file path, or another locator string).
        fetched_at: UTC timestamp of the fetch.
        collector_name: The registered name of the collector that produced this result, e.g.
            "csv_collector". Combined with `collector_version` this becomes the ProvenanceRecord's
            `collector` field.
        collector_version: The collector implementation's version string.
        status: "ok" or "error".
        error: Populated when status == "error"; None otherwise.
        metadata: Collector-specific extra context (HTTP status code, response headers, file size,
            etc.) that a Parser or the caller may find useful but that isn't part of the core
            contract.
    """

    payload: Any
    source_url: str
    collector_name: str
    collector_version: str
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "ok"
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def collector_label(self) -> str:
        """The `collector` string to record on a ProvenanceRecord, e.g. "csv_collector/0.1.0"."""
        return f"{self.collector_name}/{self.collector_version}"

    @property
    def ok(self) -> bool:
        return self.status == "ok"


class BaseCollector(ABC):
    """The interface every Collector plugin must implement.

    A Collector implementation must NOT perform any AI inference. If a source genuinely requires
    AI to extract structured data (a PDF, a news article, an unstructured webpage), it belongs in
    the future AI-assisted collector family described in `docs/ai_integration_plan.md`, not here.
    """

    #: Registered name used to look this collector up in `CollectorRegistry`. Subclasses must set
    #: this to a short, stable, snake_case identifier.
    name: str = "base_collector"

    #: Semantic version of this collector implementation.
    version: str = "0.1.0"

    @abstractmethod
    def fetch(self, source: str, **kwargs: Any) -> FetchResult:
        """Fetch the raw payload located at `source` (a URL, file path, or other locator).

        Implementations must catch their own I/O exceptions and return a `FetchResult` with
        `status="error"` and `error` populated rather than raising, so a batch of collector runs
        can complete and report partial failures instead of aborting entirely.
        """
        raise NotImplementedError

    def supports(self, source: str) -> bool:
        """Optional hint used by `CollectorRegistry.autodetect` to pick a collector for a source
        string when the caller hasn't named one explicitly. Default: never auto-selected: a caller
        must name this collector explicitly. Override to enable auto-detection (e.g. by file
        extension or URL scheme)."""
        return False


class CollectorRegistry:
    """A simple name -> BaseCollector plugin registry.

    New source types are added by implementing `BaseCollector` and calling `register()` — nothing
    else in the Collector Engine needs to change, satisfying the brief's requirement for an
    adapter/plugin architecture.
    """

    def __init__(self) -> None:
        self._collectors: dict[str, BaseCollector] = {}

    def register(self, collector: BaseCollector) -> None:
        if collector.name in self._collectors:
            raise ValueError(f"a collector named '{collector.name}' is already registered")
        self._collectors[collector.name] = collector

    def get(self, name: str) -> BaseCollector:
        try:
            return self._collectors[name]
        except KeyError as exc:
            available = ", ".join(sorted(self._collectors)) or "(none registered)"
            raise KeyError(
                f"no collector registered under '{name}'. Available: {available}"
            ) from exc

    def autodetect(self, source: str) -> BaseCollector:
        """Find the first registered collector whose `supports(source)` returns True.

        Raises ValueError if none or more than one collector claims support, since an ambiguous
        auto-detection is worse than an explicit error asking the caller to name a collector.
        """
        matches = [c for c in self._collectors.values() if c.supports(source)]
        if not matches:
            raise ValueError(f"no registered collector supports source: {source!r}")
        if len(matches) > 1:
            names = ", ".join(c.name for c in matches)
            raise ValueError(
                f"source {source!r} is ambiguous between collectors: {names}. "
                "Call get(name) explicitly instead."
            )
        return matches[0]

    def names(self) -> list[str]:
        return sorted(self._collectors)


#: A process-wide default registry, pre-populated by `collectors/__init__.py` with the built-in
#: collectors. Callers may also construct their own `CollectorRegistry()` for isolated tests.
default_registry = CollectorRegistry()
