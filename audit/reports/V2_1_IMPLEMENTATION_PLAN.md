# Version 2.1 Implementation Plan — ValueWeave

Derived from the nine-phase audit. Every item traces to a specific finding.

## Priority 1 — do these first

| # | Item | Effort | Why first | Finding |
|---|---|---|---|---|
| **1.1** | **Merge `claude/knowledge-engine-foundation` into `main`** | **15 min** | 62 files, 5,322 lines, **0 conflicts**. The engine was never lost — only unmerged. Highest value-to-effort ratio in the entire plan. | Phase 5 |
| **1.2** | **Tier 1 human review: top 40 entities by graph degree** | **~6 h** | Covers **37.2% of all graph edge endpoints**. Currently 0.0% of 2299 rows are verified. Gates the API and the recommender. | Phase 4 |
| **1.3** | **Assign one Package Steward per package** | Decision | Zero stewards assigned. Without this, 1.2 has nobody to perform it and the lifecycle model stays unstaffed. | Phase 4 |
| **1.4** | **Decide ADR-003 (scheme ownership)** | Decision | 119 scheme rows across 6 packages. Recommended: Option 1, Package007 canonical. Every release that passes without deciding enlarges the eventual reconciliation. | Phase 3 |

**1.1 is a fifteen-minute merge that closes an open ADR.** Do it today.

## Priority 2 — high impact, medium effort

| # | Item | Effort | Impact | Finding |
|---|---|---|---|---|
| **2.1** | **Fix Package006 certification vocabulary** | Low-Med | Un-orphans **30 entities** and populates `CERTIFIED_BY` (currently 0 edges). `related_skill_names` uses "Two-Wheeler Servicing" where `skills.csv` says "Two-Wheeler Mechanic". Single-package fix. | Phase 2 |
| **2.2** | **Extract Package007's 565 unmodelled rows into the graph** | Medium | 11 datasets — eligibility, benefits, application process, documents — contribute nothing today. Largest extraction gap. | Phase 1 |
| **2.3** | **Tier 2 review: all 128 entities with degree ≥ 5** | ~19 h | Precondition for any API beyond read-only Entity/Relationship. | Phase 4 |
| **2.4** | **Split `RELATED_TO` into `SUITABLE_FOR_SOIL` / `SUITABLE_FOR_CLIMATE`** | Low | `RELATED_TO` is the most-used type at 190 edges — a modelling smell. 180 are agro-suitability, and the qualifier is already in `notes`. | Phase 2 |
| **2.5** | **Add skill→provider mappings (Package006)** | Medium | `TRAINED_BY` has 3 edges; 22 of 25 providers are orphans. Unblocks the "Training" recommender output. | Phase 6 |
| **2.6** | **Ship Entity, Relationship and Graph APIs** | Medium | Data is ready (95/95/90). Additive, low-risk, makes the platform consumable. | Phase 7 |

## Priority 3 — worthwhile, not urgent

| # | Item | Effort | Finding |
|---|---|---|---|
| 3.1 | Consolidate `Industry` taxonomy into Package004 | Medium | Phase 3 — 4 packages maintain overlapping sector labels; would reduce 17 orphan Industry nodes |
| 3.2 | Country reference dataset in Package001 | Low | Phase 3 — turns 29 parsed `ExportCountry` entities into real foreign keys |
| 3.3 | Business→channel mappings (Package008) | Medium | Phase 6 — `SELLS_TO` has 12 edges |
| 3.4 | Structured scheme predecessor fields | Medium | Phase 2 — would populate `SUCCESSOR_OF`/`PREDECESSOR_OF`, currently 0 |
| 3.5 | Extend entity model for Hospital / Mandal, or declare the boundary | Decision | Phase 1 — Package003 and Package001 datasets that the model cannot represent |
| 3.6 | Goal taxonomy for the recommender | Medium | Phase 6 — "Goals" input has no representation anywhere |

## Quick wins — under an hour each

| # | Item | Effort |
|---|---|---|
| Q1 | Merge the knowledge engine branch (= 1.1) | 15 min |
| Q2 | Delete 12 orphan `__pycache__` directories | 2 min |
| Q3 | Qualify `ai_readiness` / `automation_level` by entity type in the ownership registry | 10 min |
| Q4 | Document the id-convention split (`id` vs `<entity>_id`) rather than retrofitting | 20 min |
| Q5 | Supersede ADR-006 with the Phase 5 finding | 30 min |
| Q6 | Add `verified_pct` as a tracked metric in the audit | 15 min |

## Technical debt register

| Debt | Severity | Interest accruing |
|---|---|---|
| **2299 unverified rows** | **Critical** | Blocks API, recommender, and any external use |
| 119 scheme rows across 6 packages (ADR-003 open) | High | Copies diverge silently; nothing compares them |
| 37 datasets not reaching the graph | Medium | Graph looks sparser than the data warrants |
| `RELATED_TO` overloaded at 190 edges | Medium | Type system loses information |
| Documentation standard drift (P001-004 vs P005-008) | Low | Uneven consumer experience |
| Id convention split | Low | Cosmetic; joins unaffected |

## Architecture improvements

1. **`GraphStore` → DuckDB or Postgres.** The three-layer separation already isolates
   this; only that class changes. Do it when entity count or query volume justifies it —
   not yet at 647 entities.
2. **Incremental graph rebuild.** Currently full extraction each time. Fine at this scale.
3. **Make `verified_pct` a release gate.** The graph validator has 10 checks and none
   looks at verification status. A G11 check reporting it would make the gap visible on
   every build.
4. **Extraction coverage metric.** The 37-dataset gap was invisible until this audit. It
   should be a standing number.

## Future package candidates

Not recommended for v2.1 — **the platform's gap is depth, not breadth.** Recorded for
completeness:

| Candidate | Rationale | Verdict |
|---|---|---|
| Package009_Employment | Job roles, employers, wage data | Defer — would add orphans |
| Package010_Finance | Credit products beyond scheme-linked | Defer |
| Country reference | Would fix `ExportCountry` | **Fold into Package001 instead** (3.2) |
| Industrial machinery reference | 54 Package008 machinery refs cannot resolve | **Consider** — smallest useful new package |

## Sequenced plan

```
Week 1   1.1 merge engine  ·  Q2 Q3 Q4 Q5 quick wins  ·  1.3 assign stewards
Week 2   1.2 Tier 1 review (6h)  ·  1.4 decide ADR-003
Week 3-4 2.1 certification fix  ·  2.2 Package007 extraction  ·  2.4 split RELATED_TO
Week 5-6 2.3 Tier 2 review  ·  2.5 skill→provider mappings
Week 7-8 2.6 Entity/Relationship/Graph APIs
Then     Priority 3, re-audit, reassess recommender readiness
```

## Success criteria for v2.1

| Metric | Now | Target |
|---|---|---|
| Knowledge engine files on `main` | 0 | 62 |
| Rows verified | 0 (0.0%) | ≥ 128 entities' source rows |
| Graph connectivity | 78.05% | ≥ 85% |
| Connected components | 150 | ≤ 40 |
| Datasets reaching the graph | 40/77 | ≥ 60/77 |
| Unused relationship types | 4 | ≤ 2 |
| Open ADRs | 2 | 0 |
| Repository maturity | 68.5/100 | ≥ 80 |
