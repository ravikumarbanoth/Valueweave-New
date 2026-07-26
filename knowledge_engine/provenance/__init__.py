"""Provenance Engine — the 8-field evidence model and helpers to attach/update it on records.

`ProvenanceRecord` itself lives in `knowledge_engine.core.provenance` (it's a shared type other
modules, like `package_builder`, also depend on). This package holds the JSON Schema
(`schema.json`) and the operational helper (`tracker.ProvenanceTracker`).
"""

from knowledge_engine.core.provenance import ProvenanceRecord
from knowledge_engine.provenance.tracker import ProvenanceTracker

__all__ = ["ProvenanceRecord", "ProvenanceTracker"]
