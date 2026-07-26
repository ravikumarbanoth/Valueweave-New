"""Semantic versioning parse/compare/bump, matching the `MAJOR.MINOR.PATCH[-PRERELEASE]` convention
already used across every package's VERSION file (e.g. `1.0.0`, `1.0.0-RC1`, `1.1.0`)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

_SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?$"
)


@total_ordering
@dataclass(frozen=True)
class SemVer:
    """An immutable semantic version. Prerelease versions (e.g. `1.0.0-RC1`) sort before their
    corresponding release (`1.0.0`), matching how Package001-004's RC1 -> Stable lifecycle works."""

    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None

    @classmethod
    def parse(cls, version_string: str) -> "SemVer":
        match = _SEMVER_RE.match(version_string.strip())
        if not match:
            raise ValueError(f"'{version_string}' is not a valid MAJOR.MINOR.PATCH[-PRERELEASE] version")
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            prerelease=match.group("prerelease"),
        )

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"{base}-{self.prerelease}" if self.prerelease else base

    def _sort_key(self) -> tuple[int, int, int, int, str]:
        # A version with a prerelease sorts before the same MAJOR.MINOR.PATCH without one.
        return (self.major, self.minor, self.patch, 0 if self.prerelease else 1, self.prerelease or "")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return self._sort_key() == other._sort_key()

    def __lt__(self, other: "SemVer") -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return self._sort_key() < other._sort_key()

    def bump_major(self) -> "SemVer":
        return SemVer(self.major + 1, 0, 0)

    def bump_minor(self) -> "SemVer":
        return SemVer(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "SemVer":
        return SemVer(self.major, self.minor, self.patch + 1)

    def drop_prerelease(self) -> "SemVer":
        """The transition an RC undergoes when promoted to Stable, e.g. `1.0.0-RC1` -> `1.0.0`."""
        return SemVer(self.major, self.minor, self.patch)

    def with_prerelease(self, prerelease: str) -> "SemVer":
        return SemVer(self.major, self.minor, self.patch, prerelease)
