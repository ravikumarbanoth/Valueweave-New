# Version Engine Specification

Module 6, `versioning/`. Semantic versioning parse/compare/bump (`semver.py`) plus a JSON-backed,
append-only version history with rollback support (`history.py`).

## 1. SemVer

```python
SemVer.parse("1.0.0-RC1")   # -> SemVer(major=1, minor=0, patch=0, prerelease="RC1")
str(SemVer(1, 0, 0, "RC1")) # -> "1.0.0-RC1"
```

Supports the exact `MAJOR.MINOR.PATCH[-PRERELEASE]` format already used in every package's `VERSION`
file. Comparison (`<`, `==`, sorting) treats a prerelease as *earlier* than its corresponding release
(`1.0.0-RC1 < 1.0.0`), matching the RC → Stable lifecycle every package has followed.

Bump methods: `bump_major()`, `bump_minor()`, `bump_patch()`, `drop_prerelease()` (the exact
transition an RC undergoes when promoted, e.g. `1.0.0-RC1` → `1.0.0`), and `with_prerelease(name)`.

### When to bump which component

Per `packages/README.md`'s existing convention:

- **Patch** (`1.0.0` → `1.0.1`): corrections that don't change structure or meaning.
- **Minor** (`1.0.0` → `1.1.0`): additive, backward-compatible content updates (e.g. Package004's v2
  enrichment pass, which added 24 columns without removing or renaming existing data, would have
  qualified as a minor bump had it not coincided with the RC → Stable transition already implying a
  version reset).
- **Major** (`1.0.0` → `2.0.0`): structural changes, breaking schema changes, or significant content
  model revisions.

## 2. VersionHistory

```python
history = VersionHistory()
history.record("1.0.0-RC1", "Initial release candidate", manifest_snapshot)
history.record("1.0.0", "Promoted to Stable after enrichment", manifest_snapshot_v2)
history.save(Path("packages/PackageNNN_Domain/registry/version_history.json"))

history.latest()                    # -> VersionEntry for "1.0.0"
history.rollback_to("1.0.0-RC1")    # -> the manifest snapshot recorded at that version
history.all_versions()              # -> ["1.0.0-RC1", "1.0.0"], sorted by SemVer
```

### Append-Only by Design

`record()` raises if the version already exists — history entries are never edited in place, matching
the same immutability principle `packages/README.md` applies to released package contents. Correcting
a mistake means recording a new, later version with an explanatory `change_summary`, not silently
rewriting what an earlier version's manifest said.

### Rollback Is Non-Destructive

`rollback_to(version)` returns the manifest snapshot recorded for that version — it does not itself
touch any file on disk. Actually rolling a package back to a prior version is a deliberate, separate
action a caller takes with the returned snapshot (e.g. re-running `PackageBuilder.build()` with that
snapshot's `PackageSpec`, then a human decides whether to commit the result). This engine never
silently reverts released content.

## 3. Persistence Format

`VersionHistory.save()`/`.load()` read/write a simple JSON document:

```json
{
  "entries": [
    {
      "version": "1.0.0-RC1",
      "released_at": "2026-07-22T00:00:00+00:00",
      "change_summary": "Initial release candidate",
      "manifest_snapshot": { "...": "the full package_manifest.json content at this version" }
    }
  ]
}
```

This is intentionally a plain file (not a database) in this foundation release — see `ROADMAP.md`
Phase 1 for the plan to back this with the real Knowledge Database once that's built, without
changing `VersionHistory`'s public interface.
