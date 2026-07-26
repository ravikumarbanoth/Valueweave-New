# ValueWeave Platform v2.1 — Executive Summary

**Audit date:** 2026-07-26
**Scope:** repository stabilization and roadmap audit — architecture and governance only.
**Nothing was implemented, refactored, or modified.** `audit/run_audit.py` is read-only; it
writes exactly one file, `audit/audit_findings.json`. Every figure below is computed from that
file, not typed by hand.

---

## 1. The one-paragraph answer

The knowledge base is structurally sound and epistemically unfinished. Eight packages,
77 datasets and 2,299 rows carry complete provenance, and of
730 cross-package reference cells checked, **zero are
broken**. What is missing is not integrity but *confirmation*: **0 of
2,299 rows have been verified by a human** — every row in the repository sits at
`VST-NEEDS_REVIEW`. Separately, the Knowledge Engine that was believed lost is not lost; it is
sitting on an unmerged branch, complete, at commit `71ac7e1`. The repository
scores **68.5/100** on maturity, and the two dimensions dragging it
down — human verification (0/100) and collection reproducibility
(30/100) — are the same problem seen twice: nobody has
independently confirmed what the repository asserts, and nothing re-collects it automatically.

---

## 2. Repository maturity — 68.5/100

| Dimension | Score | Reading |
|---|---:|---|
| Structure and validation | 95 | 4 validators, 14 generators, all packages pass |
| Provenance completeness | 95 | 3,164 provenance records; six mandatory columns everywhere |
| Cross-package integrity | 90 | 0.0% broken, 17.4% weak references |
| Documentation | 90 | 252 markdown documents |
| Graph connectivity | 78 | 78.05% of entities connected |
| Ownership governance | 70 | 2 unresolved overlaps, 87 enforceable attributes |
| Collection reproducibility | 30 | collectors and parsers are `PENDING_IMPLEMENTATION` |
| Human verification | 0 | **0.0% of rows verified** |

---

## 3. The five findings that matter

### Finding 1 — The Knowledge Engine is recoverable in minutes, not weeks

`main` contains **0 knowledge-engine source files**. The engine
exists at `71ac7e1` on `claude/knowledge-engine-foundation` — present both
locally and on origin — carrying **62 files, 5322 insertions(+)** across
13 modules, with **0 merge-conflict
markers** against merge base `3161186`. It is
1 commit ahead of that base while `main` has moved
18 commits on.

This supersedes ADR-006, which weighed "recover or rebuild" without knowing that recovery is a
merge. **Action: merge it.** See `KNOWLEDGE_ENGINE_RECOVERY.md`.

### Finding 2 — Zero rows are human-verified

2,299 rows across 8 packages,
40,503 cells, **0 verified**. Confidence scores are honest —
capped at 85 because authoritative `.gov.in` fetches are blocked by egress policy — but a
confidence score is a *claim about a claim*, not verification. This one fact blocks the
Recommendation Engine, blocks every public API, and is the single largest component of the
maturity gap.

The mitigation is cheap because verification value is concentrated:
**128 high-leverage entities** exist, and the **top 40 alone touch
643 of 1730 edge endpoints (37.2%)**.
Forty verifications buy disproportionate trust. See `DATA_STEWARDSHIP.md`.

### Finding 3 — Half the collected data never reaches the graph

**37 of 77 datasets
(1,142 rows) contribute no entity and no edge**, and
**142 entities** carry no edge at all. The graph reaches
78.05% connectivity with a largest component of
75.58% across 150 components, of which
142 are singletons.

This is not corruption. It is value already collected and already paid for that no query can
currently reach. See `GRAPH_HEALTH.md`.

### Finding 4 — Ownership is declared but only partly enforceable

87 attributes have exactly one owning package and are enforced
mechanically by the graph validator. But **119 scheme rows live across
6 packages** — Package007 owns 40, the other
79 are domain-package copies — and
**2 entity types (GovernmentScheme, ExportCountry) have no
resolved owner**. ADR-003 is still open, which means a recommendation could surface a stale
scheme copy instead of the canonical row.

Normalization nonetheless scores **96.6/100**: the Package008
non-duplication rule held under mechanical test. See `OWNERSHIP_AUDIT.md`.

### Finding 5 — APIs are data-ready; the platform is not policy-ready

7 of 8 planned APIs
already have the data they need. Both remaining blockers are non-technical:

- Zero human-verified rows: an API industrialises whatever errors the data holds
- No auth, rate limiting or API versioning policy designed

Exposing an API over unverified rows industrialises whatever errors the data holds. See
`API_READINESS.md`.

---

## 4. Recommendation Engine readiness — 56.9/100

The engine should not be built yet, and the reason is instructive: the traversals it needs
already work; the *signals* it needs in order to rank do not exist.

- No outcome data exists to calibrate ranking weights
- No goal taxonomy: 'Goals' input has no representation in any package
- TRAINED_BY has only 3 edges; 'Training' output would be near-empty
- SELLS_TO has only 12 edges; 'Market' output would be near-empty
- Zero rows human-verified
- ADR-003 open: a recommendation could surface a stale scheme copy

Ranking without outcome data is ranking by assertion. See `RECOMMENDATION_READINESS.md`.

---

## 5. What is genuinely healthy

These are audit results, not reassurance:

- **730 cross-package reference cells checked, 0 broken.** Foreign keys resolve at generation time; generators abort rather than write an unresolvable reference.
- **0 duplicate entity ids, 0 duplicate edges, 0 self-loops, 0 directed cycles, 0 alias conflicts.**
- **100.0% entity-type coverage** — every registered entity type is populated by real rows.
- **3,164 provenance records.** No row anywhere is missing the six mandatory provenance columns.
- **Sentinel discipline held.** 23 fully-sentinel columns are declared unknowns, not silent gaps — the repository says what it does not know.

---

## 6. Immediate actions (first two weeks)

| # | Action | Effort | Unblocks |
|---|---|---|---|
| 1 | Merge `claude/knowledge-engine-foundation` into `main` | ~15 min | Collection reproducibility; `collector`/`parser` in the source registry |
| 2 | Verify the top 40 high-leverage entities | ~2 days | 37.2% of edge endpoints; API and recommendation credibility |
| 3 | Close ADR-003 (scheme canonicalisation) | ~1 day | Removes the stale-copy risk across 119 scheme rows |
| 4 | Resolve ownership for GovernmentScheme and ExportCountry | ~half day | Ownership governance 70 → ~85 |
| 5 | Remove 12 orphan `__pycache__` directories and 7 empty directories | ~10 min | Repository hygiene |

Full sequencing, the technical-debt register and success criteria are in
`V2_1_IMPLEMENTATION_PLAN.md`.

---

## 7. Verdict

**Stabilize before extending.** The instinct to add Package009 should be resisted. The repository
already holds 1,142 rows that no query can reach and 2,299 rows no human has
confirmed; a ninth domain multiplies both numbers without improving either. The highest-return
work for the next eight weeks is merging what already exists, verifying what already matters, and
connecting what was already collected.

---

### Report index

| Report | Question it answers |
|---|---|
| `REPOSITORY_AUDIT.md` | What is actually in the repository, and what is duplicated, dead or undocumented? |
| `GRAPH_HEALTH.md` | Is the knowledge graph internally consistent, and how much of it is connected? |
| `OWNERSHIP_AUDIT.md` | Who owns which entity types and attributes, and where is that violated? |
| `DATA_STEWARDSHIP.md` | What is the verification state, and which rows should be verified first? |
| `KNOWLEDGE_ENGINE_RECOVERY.md` | Where did the Knowledge Engine go, and how is it recovered? |
| `RECOMMENDATION_READINESS.md` | Can the Recommendation Engine be built now? |
| `API_READINESS.md` | Which APIs can be exposed, and in what order? |
| `V2_1_IMPLEMENTATION_PLAN.md` | What should be done, in what sequence, over eight weeks? |
| `EXECUTIVE_SUMMARY.md` | This document. |

*Generated from `audit/audit_findings.json`. No package data, graph artifact or source file was
modified by this audit.*
