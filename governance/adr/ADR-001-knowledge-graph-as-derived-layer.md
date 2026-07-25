# ADR-001: The Knowledge Graph is a Derived Layer, Not a Source of Truth

**Status:** Accepted
**Date:** 2026-07-25
**Deciders:** Platform architecture
**Supersedes:** none

## Context

Eight packages are Stable. Each owns a domain and validates itself. The platform now
needs cross-package query capability: "which schemes support millet processing" spans
Package005, Package007 and Package008 and no single package can answer it.

Two ways to build that capability:

1. **Authored graph** — a new registry where entities and edges are written directly,
   independently of the packages.
2. **Derived graph** — an extraction that reads the packages and emits entities and
   edges, owning nothing itself.

Option 1 is faster to start and produces a richer graph immediately, because the author
is not limited to what packages already contain.

## Decision

**The knowledge graph is derived. It creates no domain knowledge.**

Every entity carries `source_package` and `package_local_id`. Every edge carries
`provenance_package`, `provenance_dataset` and `provenance_row_id`. Validation check
G4 confirms that a claimed `package_local_id` actually exists in the claimed package.

If a fact is not already in a package, it does not appear in the graph. To add a fact,
add it to the owning package and rebuild.

## Consequences

**Positive**

- The graph cannot drift from the packages, because it is regenerated from them.
- Every query answer traces to a specific CSV row in a specific package. An answer that
  cannot cite its source is not an answer the platform gives.
- Package release discipline (validation, versioning, provenance) automatically governs
  the graph. No second quality regime is needed.
- Rebuilding is safe. `python3 knowledge_graph/build_graph.py` is idempotent.

**Negative**

- The graph inherits every package gap. 142 of 650 entities have no relationships, not
  because the relationships do not exist in reality but because no package records them.
  This is visible and honest rather than papered over.
- Relationship types can be registered with zero edges. `CERTIFIED_BY`, `SUCCESSOR_OF`
  and `PREDECESSOR_OF` are registered and empty; the data to populate them does not
  exist upstream in structured form.
- Enriching the graph requires enriching a package first, which is slower.

**Accepted trade-off:** an honest sparse graph beats a rich graph that cannot say where
its facts came from.

## Alternatives considered

**Authored graph with package back-references.** Rejected: the moment an edge can be
authored in the graph, the graph becomes a ninth source of truth with no validation
regime of its own, and the ownership rules the packages spent eight releases
establishing lose their meaning.
