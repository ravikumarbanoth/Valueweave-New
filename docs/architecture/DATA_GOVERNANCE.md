# Data Governance

The full governance policy lives at [`governance/DATA_GOVERNANCE.md`](../../governance/DATA_GOVERNANCE.md),
alongside the artifacts it governs:

- `governance/DATA_GOVERNANCE.md` — naming, ownership, validation, stewardship, versioning, deprecation, contribution and release rules
- `governance/DATA_STEWARDSHIP.md` — the seven-state entity lifecycle
- `governance/adr/` — six Architecture Decision Records

It is kept there rather than duplicated here, for the same reason the knowledge graph
does not duplicate package data: one authoritative copy beats two that drift.

## Quick reference

| Question | Answer | Enforced by |
|---|---|---|
| Who owns this entity type? | `knowledge_graph/ownership/ownership_registry.csv` | G7 |
| May my package hold this column? | Only if you own it, or it is a reference/denormalised name | G7 |
| How do I add a fact? | Add it to the owning package; the graph is derived | ADR-001 |
| Can duplicates be merged automatically? | No — proposed only, steward decides | ADR-004 |
| What if my package must duplicate something? | Declare it in `known_overlaps.csv` with an ADR | G7 |
| Has any of this been human-reviewed? | **No.** Every row is `VST-NEEDS_REVIEW` | — |
