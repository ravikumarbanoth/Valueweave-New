# Knowledge Engine Recovery — ValueWeave v2.1 Phase 5

**Read-only investigation.** No branch was merged, no file restored.

## Conclusion, stated first

**The Knowledge Engine is not lost. It is intact in git, on an unmerged branch, and
merges into `main` with zero conflicts.**

ADR-006 recorded that `knowledge_engine/` had no tracked files and recommended
"recover or rebuild". This investigation resolves that: **recovery is a merge, not a
rebuild.**

## Evidence

| Question | Answer |
|---|---|
| Files tracked on `main` | **0** |
| Source files in the working tree | 0 (only `__pycache__` residue) |
| Origin commit | `71ac7e1f3127` |
| Commit subject | feat(knowledge_engine): add ValueWeave Knowledge Engine (VKE) v0.1.0 foundation |
| Commit date | 2026-07-24 09:16:31 +0000 |
| **Files in that commit** | **62** |
| Insertions | 62 files changed, 5322 insertions(+) |
| Branches containing it | `claude/knowledge-engine-foundation`, `remotes/origin/claude/knowledge-engine-foundation` |
| **Reachable from `main`** | **False** |
| Commits ahead of `main` | 1 |
| Commits `main` is ahead | 18 |
| Merge base | `3161186 Merge branch 'claude/package004-industries-import' into main` |
| **Merge conflict markers** | **0** |

The branch exists **both locally and on `origin`**. Nothing was deleted; the branch was
simply never merged.

## What the commit contains

62 files implementing all eight specified modules:

| Module |
|---|
| `collectors/` |
| `config/` |
| `core/` |
| `docs/` |
| `examples/` |
| `package_builder/` |
| `parsers/` |
| `provenance/` |
| `rule_engine/` |
| `tests/` |
| `update_engine/` |
| `validation/` |
| `versioning/` |

Module breakdown from the commit message: Collector Engine (BaseCollector +
CollectorRegistry, stdlib-only CSV/JSON/XML/RSS/API collectors), Parser Engine
(CSV/JSON/XML/RSS/HTML-table; PDF an explicit `NotImplementedError` rather than a brittle
heuristic), Validation Engine (7 reusable rule types), Provenance Engine (the 8-field
evidence model every package has used since Package001), Package Builder, Version Engine,
Update Engine, Rule Engine — plus 8 module specs, examples and tests.

## Why it was missed

The v2.0.0 audit checked `git ls-files knowledge_engine` on `main`, which correctly
returned 0. It did not check `git log --all`. **The engine was one command away from
being found.** ADR-006's conclusion was right about the symptom and wrong about the
cause.

## Dependency impact

| Consumer | Impact of merging |
|---|---|
| Platform v2 graph builder | **None** — reads package CSVs directly, no engine import |
| Query engine | **None** |
| Validators (package + graph) | **None** |
| Source registry | **Positive** — 605 rows currently `PENDING_IMPLEMENTATION` in `collector` and `parser` become populatable |
| Released packages | **None** — each ships its own generator scripts |

Files referencing the engine today:

- `source_registry/build_source_registry.py`
- `governance/adr/ADR-006-knowledge-engine-absent-from-repository.md`
- `audit/run_audit.py`
- `PLATFORM_V2.md`
- `docs/architecture/SYSTEM_ARCHITECTURE.md`
- `docs/architecture/ROADMAP_V2.md`

All are documentation. **No code depends on it**, so merging is additive and cannot break
anything.

## Recommendation: RESTORE

| Option | Verdict |
|---|---|
| **Restore** (merge `claude/knowledge-engine-foundation`) | **RECOMMENDED** |
| Rebuild | Rejected — would discard 62 working files and 5,322 lines |
| Archive | Rejected — the source registry needs it, and reproducibility claims depend on it |

### Restoration procedure

```bash
git checkout main
git merge claude/knowledge-engine-foundation --no-ff
python3 knowledge_graph/validate_graph.py     # confirm nothing regressed
python3 audit/run_audit.py                    # confirm tracked file count moves 0 → 62
```

Zero conflicts predicted by `git merge-tree`. The branch is 18 commits behind `main`
but touches only paths `main` does not have.

### Follow-up once merged

1. Delete the 12 orphan `__pycache__` directories under `knowledge_engine/`
2. Verify the engine runs against current Python
3. **Amend ADR-006** — it currently records "no tracked source files… recover or rebuild".
   Supersede it with an ADR recording that the engine was found and restored, and the
   process lesson: *a v2.0.0 audit checked one branch and concluded a component was
   lost.* Check `--all` before declaring anything missing.
4. Populate `collector` and `parser` in `source_registry/sources.csv` for the 77 datasets
   the engine actually produced

## Risk

**Low.** Additive merge, no conflicts, no runtime dependents. The only risk is that the
engine's code has bitrotted against the current Python version — testable in minutes
after merging.
