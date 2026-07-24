"""Version Engine — semantic versioning and JSON-backed version history with rollback support."""

from knowledge_engine.versioning.history import VersionEntry, VersionHistory
from knowledge_engine.versioning.semver import SemVer

__all__ = ["SemVer", "VersionHistory", "VersionEntry"]
