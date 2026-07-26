# Recommendation Engine Readiness — ValueWeave v2.1 Phase 6

**Read-only assessment.** Figures computed by `audit/run_audit.py`.

## Readiness score: 56.9 / 100

**Verdict: NOT READY.** Candidate generation and explanation are fully solved; ranking
and two of seven outputs are not.

| Factor | Score |
|---|---|
| candidate generation possible | 100/100 |
| constraint filtering possible | 60/100 |
| explanation possible | 100/100 |
| ranking calibratable | 0/100 |
| graph density sufficient | 78/100 |
| data human verified | 0/100 |
| ownership stable | 60/100 |

Two factors score zero, and both are data problems rather than engineering problems.

## Input availability

| Input | Available | Via | Entities |
|---|---|---|---|
| Education | YES | Institution entities + RELATED_TO talent pipeline | 66 |
| Skills | YES | Skill entities + REQUIRES_SKILL | 45 |
| District | YES | District entities + GENERATES_EMPLOYMENT | 61 |
| Budget | PARTIAL | udyam_classification ordinal band only; no rupee figure exists | 40 |
| Interests | YES | Industry entities + PART_OF | 78 |
| Experience | PARTIAL | msme_businesses.difficulty ordinal; not an entity attribute | 40 |
| Goals | False | no goal taxonomy exists in any package | 0 |

**Five of seven inputs are usable today.** Two are not:

- **Budget** is partial by design. Package008 asserts no rupee figure anywhere;
  `investment_range` is sentinel on all 40 businesses. Only the statutory
  `udyam_classification` band (Micro/Small/Medium) exists. A recommender can filter by
  band, not by "I have ₹5 lakh".
- **Goals** has **no representation in any package**. There is no goal taxonomy, no
  outcome vocabulary, nothing to map a user's stated objective onto. This is a genuine
  modelling gap, not a data-collection gap.

## Output availability

| Output | Available | Detail |
|---|---|---|
| Business | YES | 40 entities |
| Skills | YES | 45 entities |
| Schemes | YES | 40 entities |
| Training | WEAK | 25 providers but only 3 TRAINED_BY edges |
| MSME | YES | 40 entities |
| Market | WEAK | 11 channels, 12 SELLS_TO edges |
| AI Tools | YES | 16 USES_AI edges |

**Two outputs would be near-empty:**

- **Training** — 3 `TRAINED_BY` edges across 25 training providers. A user
  asking "where do I learn this" gets almost nothing.
- **Market** — 12 `SELLS_TO` edges. Channel applicability is stated at channel
  level in Package008, not per business, so the graph has almost no business-to-channel
  edges to traverse.

## Blocking gaps

1. No outcome data exists to calibrate ranking weights
2. No goal taxonomy: 'Goals' input has no representation in any package
3. TRAINED_BY has only 3 edges; 'Training' output would be near-empty
4. SELLS_TO has only 12 edges; 'Market' output would be near-empty
5. Zero rows human-verified
6. ADR-003 open: a recommendation could surface a stale scheme copy

## What is already solved

Worth stating, because it is most of the hard architectural work:

- **Candidate generation** — every traversal the design calls for exists and runs
  (`Skill ←REQUIRES_SKILL← MSME`, `District ←GENERATES_EMPLOYMENT← MSME`,
  `Industry ←PART_OF← MSME`)
- **Explanation** — `Result.provenance()` returns the exact package, dataset and row
  behind every result. A recommendation can always say why.
- **Cross-package context** — `full_business_context()` spans six packages in one call

## Path to ready

| # | Gap | Action | Effort | Lifts score to ~ |
|---|---|---|---|---|
| 1 | Data unverified | Tier 1 + Tier 2 review (128 entities) | ~19 h | 66 |
| 2 | Training output empty | Add skill→provider mappings in Package006 | Medium | 72 |
| 3 | Market output empty | Add business→channel mappings in Package008 | Medium | 76 |
| 4 | Graph density | Extract the 37 unmodelled datasets | Medium | 82 |
| 5 | Ownership unstable | Resolve ADR-003 | Decision | 86 |
| 6 | No goal taxonomy | Design one; likely a new small reference dataset | Medium | 90 |
| 7 | No outcome data | **Requires the platform to be in use** | — | Blocked |

Item 7 is the genuine bootstrap problem and it cannot be engineered away.

## Recommendation

**Do not build a ranking recommender in v2.1.**

Ship **explained traversal** instead — which already works. `full_business_context()`
returns everything the graph knows about a business, with provenance, and makes no claim
about which option is *better*. That is honest, useful, and available today.

Add ranking when there is something to calibrate it against. A weighted sum with invented
weights would look authoritative and be unfounded — the same trap Package008 refused when
it declined to compute an ROI figure from investment data it did not have.
