# ADR-004: Entity Resolution Proposes Merges, Never Executes Them

**Status:** Accepted
**Date:** 2026-07-25

## Context

The Entity Resolution Engine detects probable duplicates across packages. Four
near-duplicate `Industry` pairs surfaced on the first run, three of which were
`&`/`and` spelling variants of the same industry.

The obvious next step is to merge them automatically above a similarity threshold.

## Decision

**The resolver proposes. A human decides. `propose_merges()` never mutates the graph.**

Proposals are written to `knowledge_graph/resolution/merge_proposals.csv` with a
similarity score, the shared and distinguishing tokens, both owning packages, and a
`decision` column set to `PENDING_STEWARD_REVIEW`.

One exception is applied automatically, and it is deliberately narrow: **orthographic**
normalisation in slug generation (`&` → `and`, ASCII folding, case). That is not a
semantic judgement — `&` and `and` are the same word.

## Consequences

**Positive**

- A wrong merge is silent and corrupting: every query traversing the merged node returns
  wrong results, with no error and no way to notice. A missed merge is merely incomplete
  and shows up as two similar nodes a user can see.
- The `&`/`and` collapse — safe because orthographic — reduced proposals from 4 to 1.
  The one remaining, `Healthcare` vs `Healthcare Services`, is exactly the judgement call
  a machine should not make: they may be the same industry or a parent and a child.

**Negative**

- Duplicates persist until a steward acts. No steward is currently assigned (see
  `DATA_GOVERNANCE.md`), so in practice they persist indefinitely in v2.0.0.

## Evidence from this build

The first similarity implementation scored `Manufacturing` against
`Manufacturing (Automotive)` at **1.000**, because the comparison normaliser stripped
parenthetical qualifiers. Those are a parent and a child, not duplicates. Under an
auto-merge policy above 0.95, the graph would have silently collapsed four distinct
manufacturing sub-sectors into one node.

The bug was fixed — comparison now keeps parentheticals — but the incident is the
argument for this ADR. The threshold was not the problem; automation of an irreversible
semantic judgement was.
