# ADR-006: The Knowledge Engine Is Absent From This Repository

**Status:** RESOLVED — superseded by Platform v2.2, Work Package 1
**Date:** 2026-07-25
**Date resolved:** 2026-07-26
**Severity:** High (at the time of writing)

> **Resolution.** The premise of this ADR was correct — the engine was absent from `main` —
> but its conclusion was reached without knowing where the engine had gone. The v2.1 audit
> located it at commit `71ac7e1` on `claude/knowledge-engine-foundation`, complete, with
> zero merge-conflict markers against the merge base. Platform v2.2 recovered it by
> **merging that branch**, which preserves the original commit history of all 62 files
> rather than re-adding them as new work.
>
> Everything below is retained as the record of what was believed on 2026-07-25. Two
> things it says are no longer true: `git ls-files knowledge_engine` now returns 62, and
> the source registry's `collector` / `parser` columns no longer have to say
> `PENDING_IMPLEMENTATION` for want of a module to name. See `docs/KNOWLEDGE_ENGINE.md`
> and `docs/MIGRATION_GUIDE.md`.

## Context

Platform v2 was specified on the premise that "Knowledge Engine is already implemented."
The Source Registry (Module 7) requires a `collector` and `parser` per source, which
implies named modules in that engine.

**`knowledge_engine/` contains no tracked source files.**

```
$ git ls-files knowledge_engine | wc -l
0
$ find knowledge_engine -type f -not -path "*__pycache__*" | wc -l
0
```

The directory holds only `__pycache__` subdirectories — the residue of code that once
ran in a working tree. `.gitignore` line 51 (`*pyc*`) means even those are untracked.
The subdirectory names (`collectors/`, `parsers/`, `validation/`, `provenance/`,
`package_builder/`, `versioning/`, `update_engine/`, `rule_engine/`) match the eight
modules the engine was specified to contain, so the work was done — it was never
committed, or was committed and lost.

## Decision

**Record the absence rather than paper over it.** Specifically:

1. `source_registry/sources.csv` carries `PENDING_IMPLEMENTATION` in the `collector` and
   `parser` columns on all 605 rows. No module path is invented.
2. Platform v2 documentation treats the Knowledge Engine as a **contract**, not a live
   dependency. `SYSTEM_ARCHITECTURE.md` describes where it fits and what it must provide;
   no v2 component imports from it.
3. Nothing in Platform v2 depends on it at runtime. The graph builder, resolver, query
   engine and validators read package CSVs directly and have no engine dependency.

## Consequences

**Positive**

- Platform v2 is fully functional without the engine. Everything delivered runs.
- The gap is visible in three places (this ADR, the source registry, and the
  architecture doc) rather than discovered later by someone trying to import it.

**Negative**

- The source registry cannot describe how any source is actually collected, which is a
  material limitation for a registry whose purpose includes scheduling re-collection.
- `frequency` and `next_collection` are computed and stored, but nothing acts on them.
  They are a schedule with no scheduler.

## Required action

Recover or rebuild `knowledge_engine/` and commit it. Until then, every package's data
was collected by a process this repository does not contain, which weakens the
reproducibility claim each package's METHODOLOGY makes.

The packages themselves are unaffected — each ships its own generator scripts and is
reproducible from source.
