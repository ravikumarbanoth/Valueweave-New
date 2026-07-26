"""
ValueWeave Knowledge Synchronization Framework (Platform v3.0, Step 1).

A permanent, one-way synchronisation layer from the Git knowledge repository into
Supabase. Not an importer: it detects change, validates, transforms, applies,
logs, measures, and can roll back.

    Git (packages/ + knowledge_graph/)   ← single source of truth
                 │  one-way, idempotent
                 ▼
    Supabase schema `knowledge`          ← read-optimised cache for the app

Nothing here writes to a user table, and nothing here reads application state to
decide what to write.
"""

__version__ = "1.0.0"

from knowledge_sync.config import TABLE_SPECS, TableSpec, TARGET_SCHEMA
from knowledge_sync.engine import SyncEngine, SyncMode

__all__ = ["TABLE_SPECS", "TableSpec", "TARGET_SCHEMA", "SyncEngine", "SyncMode",
           "__version__"]
