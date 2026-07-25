# Recommendation Engine — Design Only (Module 6)

**Status: DESIGN. Not implemented, and deliberately so.**

The brief asks for design only. This document is the design, plus an honest account of
why building it now would be premature.

## Intended shape

```
INPUT                          ENGINE                        OUTPUT
─────                          ──────                        ──────
Education      ┐                                          ┌ Business
Skills         │      ┌──────────────────────┐            │ Skills to acquire
District       │      │ 1. Profile → entities│            │ Schemes
Budget         ├─────►│ 2. Candidate gen     ├───────────►│ Training
Interests      │      │ 3. Constraint filter │            │ MSME path
Experience     │      │ 4. Rank              │            │ Markets
Goals          ┘      │ 5. Explain           │            └ AI tools
                      └──────────────────────┘
```

## Stage design

### 1. Profile resolution
Map free-text profile inputs to `global_entity_id`s using `Resolver`. "I know Python and
live in Nizamabad" → `vw:skill:python-programming`, `vw:district:nizamabad`. Unresolved
inputs are reported, never guessed.

### 2. Candidate generation
Graph traversal, not a model:

| Input | Traversal | Yields |
|---|---|---|
| Skills held | `Skill ←REQUIRES_SKILL← MSME` | Businesses the user can already staff |
| District | `District ←GENERATES_EMPLOYMENT← MSME` | Locally-evidenced businesses |
| Interests | `Industry ←PART_OF← MSME` | Sector-aligned businesses |
| Education | `Institution →RELATED_TO→ Industry` | Sectors the user's institution feeds |

Union the candidate sets; the intersection is usually empty and over-filters.

### 3. Constraint filtering
Budget maps to `udyam_classification` (Micro/Small/Medium) — **not to a rupee figure**,
because Package008 asserts none (its `investment_range` is sentinelled on all 40 rows).
Experience maps to `difficulty`. Both are ordinal filters over closed domains.

### 4. Ranking
A weighted sum over signals the graph actually has:

| Signal | Source | Weight (proposed) |
|---|---|---|
| Skill overlap | count of `REQUIRES_SKILL` already satisfied | 0.30 |
| District evidence | `GENERATES_EMPLOYMENT` edge exists for the user's district | 0.25 |
| Scheme support | count of `SUPPORTED_BY_SCHEME` edges | 0.20 |
| Path confidence | `Result.min_confidence()` | 0.15 |
| Interest alignment | `PART_OF` industry match | 0.10 |

**These weights are a starting hypothesis, not a calibrated model.** No outcome data
exists — nobody has started a business on this platform's advice, so there is nothing to
fit against.

### 5. Explanation
Every recommendation returns its `Result.provenance()` chain. "Spice Grinding recommended
because Package008 `skill_mapping.csv` row kmap-004 says it requires Food Processing &
Preservation, which you have." Recommendations without traceable reasons should not be
shown to someone making a livelihood decision.

## Why this is not implemented

**1. No outcome data exists.** Ranking weights would be invented and then look
authoritative. Package008 already faced this and refused: its `investment_intelligence`
carries ordinal judgements and explicitly no computed return.

**2. The graph is 78.05% connected.** 142 entities have no edges — 30
certifications, 22 training providers, 21 schemes. A recommender over a sparse graph
systematically under-recommends whatever is under-linked, and the user cannot tell.

**3. Nothing is human-reviewed.** Every row is `VST-NEEDS_REVIEW`. A recommendation
engine over unreviewed data industrialises whatever errors it contains.

**4. Scheme ownership is unresolved (ADR-003).** Six packages hold scheme data. A
recommender might surface a stale copy.

## Preconditions for building it

| # | Precondition | Status |
|---|---|---|
| 1 | Human review of the ~170 highest-connectivity rows | Not started |
| 2 | Connectivity above ~85% (certification vocabulary fix alone adds 30 entities) | 78.05% |
| 3 | ADR-003 decided | Open |
| 4 | Some outcome signal, even coarse, to calibrate weights | None |

Preconditions 1 and 2 are tractable now. 3 is a decision. 4 requires the platform to be
in use, which is the genuine bootstrapping problem — and the honest answer is to ship
**explained traversal** first (which the query engine already does) and add ranking once
there is something to rank against.

## What exists today instead

`Queries.full_business_context(name)` returns everything the graph knows about a business
across six packages, with provenance. That is a recommender's candidate-generation stage,
working, without the ranking layer that would require data nobody has.
