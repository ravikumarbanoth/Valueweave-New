"""Collector Engine — plugin-based raw-data fetchers.

Importing this package populates `default_registry` with every built-in collector. A new collector
plugin is added by implementing `BaseCollector` and calling `default_registry.register(...)` (or by
constructing a private `CollectorRegistry()` for isolated use, e.g. in tests).
"""

from knowledge_engine.collectors.api_collector import APICollector
from knowledge_engine.collectors.base import BaseCollector, CollectorRegistry, FetchResult, default_registry
from knowledge_engine.collectors.csv_collector import CSVCollector
from knowledge_engine.collectors.json_collector import JSONCollector
from knowledge_engine.collectors.rss_collector import RSSCollector
from knowledge_engine.collectors.xml_collector import XMLCollector

default_registry.register(CSVCollector())
default_registry.register(JSONCollector())
default_registry.register(XMLCollector())
default_registry.register(RSSCollector())
default_registry.register(APICollector())

__all__ = [
    "BaseCollector",
    "CollectorRegistry",
    "FetchResult",
    "default_registry",
    "CSVCollector",
    "JSONCollector",
    "XMLCollector",
    "RSSCollector",
    "APICollector",
]
