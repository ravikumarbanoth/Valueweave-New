"""VersionHistory — a JSON-backed record of every version transition for a package.

Mirrors what Package001-004 have tracked by hand in each package's `CHANGELOG.md`: for every version,
when it was released, a change summary, and (here, additionally) a full manifest snapshot so a prior
version can be inspected or rolled back to without needing git history.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from knowledge_engine.versioning.semver import SemVer


@dataclass
class VersionEntry:
    version: str
    released_at: str
    change_summary: str
    manifest_snapshot: dict[str, Any] = field(default_factory=dict)


class VersionHistory:
    """In-memory version history, optionally backed by a JSON file on disk.

    Usage:
        history = VersionHistory.load(path) if path.exists() else VersionHistory()
        history.record("1.0.0-RC1", "Initial release candidate", manifest)
        ...
        history.record("1.0.0", "Promoted to Stable", manifest)
        history.save(path)
    """

    def __init__(self, entries: Optional[list[VersionEntry]] = None):
        self.entries: list[VersionEntry] = entries or []

    def record(
        self,
        version: str,
        change_summary: str,
        manifest_snapshot: dict[str, Any],
        released_at: Optional[datetime] = None,
    ) -> VersionEntry:
        """Append a new version entry. Raises if `version` already exists, since history entries
        are append-only — correcting a mistaken entry means adding a new, later version, not
        editing history in place (the same immutability principle `packages/README.md` applies to
        released package contents)."""
        SemVer.parse(version)  # validates format; raises ValueError if malformed
        if any(e.version == version for e in self.entries):
            raise ValueError(f"version '{version}' is already recorded in this history")
        entry = VersionEntry(
            version=version,
            released_at=(released_at or datetime.now(timezone.utc)).isoformat(),
            change_summary=change_summary,
            manifest_snapshot=manifest_snapshot,
        )
        self.entries.append(entry)
        return entry

    def latest(self) -> Optional[VersionEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: SemVer.parse(e.version))

    def get(self, version: str) -> VersionEntry:
        for entry in self.entries:
            if entry.version == version:
                return entry
        raise KeyError(f"no version '{version}' recorded in this history")

    def rollback_to(self, version: str) -> dict[str, Any]:
        """Return the manifest snapshot recorded for `version`, for a caller to re-apply.

        This does not itself mutate any package files — actually rolling a package back is a
        deliberate, separate action the caller takes with the returned snapshot (matching the
        general principle that this engine never takes destructive action silently).
        """
        return self.get(version).manifest_snapshot

    def all_versions(self) -> list[str]:
        return sorted((e.version for e in self.entries), key=SemVer.parse)

    def to_dict(self) -> dict[str, Any]:
        return {"entries": [asdict(e) for e in self.entries]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VersionHistory":
        return cls(entries=[VersionEntry(**e) for e in data.get("entries", [])])

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "VersionHistory":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)
