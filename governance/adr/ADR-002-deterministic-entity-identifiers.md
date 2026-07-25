# ADR-002: Deterministic, Human-Readable Global Entity Identifiers

**Status:** Accepted
**Date:** 2026-07-25

## Context

Every entity in the Global Entity Registry needs a `global_entity_id` that is stable
across rebuilds, unique across 19 entity types and 8 packages, and usable as a foreign
key by future API consumers.

Candidate schemes:

1. **UUIDv4** — what several packages use internally.
2. **Sequential** — `vw-000001`, assigned in build order.
3. **Deterministic slug** — `vw:<entity_type>:<canonical_name_slug>`.

## Decision

**`vw:<entity_type_slug>:<canonical_name_slug>`**, for example
`vw:crop:turmeric`, `vw:governmentscheme:pradhan-mantri-kisan-samman-nidhi`.

Slug generation normalises to ASCII, lowercases, converts `&` to `and`, and collapses
non-alphanumerics to hyphens.

## Consequences

**Positive**

- **Stable across rebuilds.** The same input produces the same id, so a git diff of
  `entities.csv` shows real change rather than churn. A UUID scheme would rewrite every
  id on every rebuild, making the registry undiffable.
- **Readable in logs, queries and provenance chains.** `vw:skill:python-programming`
  is self-documenting where `vw-000417` is not.
- **Type is visible in the id**, which validation check G1 exploits: an id whose prefix
  does not match its `entity_type` is a violation.

**Negative**

- **A canonical name change changes the id.** This is a real cost. Mitigation: renames
  go through the steward workflow in `DATA_GOVERNANCE.md`, and the old id is recorded
  as an alias so external references keep resolving.
- **Slug collisions are possible.** Two entities of the same type whose names normalise
  identically collapse into one node. This is detected — `cross_package_sightings.csv`
  records every case — and it caught a real one: `Agriculture & Allied` (Package005) and
  `Agriculture and Allied` (Package008) are the same industry, and collapsing them fixed
  a query that was silently returning nothing.
- **Length cap at 80 characters** truncates very long scheme names.

## Note on the `&` decision

Normalising `&` to `and` is **orthographic**, not semantic — they are the same word.
This is deliberately different from merging `Healthcare` with `Healthcare Services`,
which is a semantic judgement and stays with a human steward. See ADR-004.
