# API Vision — ValueWeave Platform v2

**Status: VISION. Nothing here is built.** This document states the intended shape so
that the layers below it are built against a known target.

## Principles

**1. Provenance is not optional.** Every response carries the package, dataset and row
that produced it. An API that returns facts without sources is not this platform.

**2. Confidence travels with data.** Every entity and path carries a confidence score and
`verification_status`. A consumer must be able to tell that nothing has human sign-off.

**3. Read-only against the graph.** Writes go to packages (ADR-001). There is no API path
that mutates the graph.

**4. Entity ids are the contract.** `vw:crop:turmeric` is stable across rebuilds
(ADR-002), so it is safe as an external reference.

## Proposed surface

```
GET  /v2/entities/{global_entity_id}
GET  /v2/entities?type=Skill&q=python
GET  /v2/entities/{id}/neighbours?rel=REQUIRES_SKILL&direction=in
GET  /v2/paths?from={id}&to={id}&max_hops=4

GET  /v2/query/businesses-requiring-skill?skill=Python
GET  /v2/query/schemes-supporting?subject=Millet+Processing
GET  /v2/query/skills-for-business?business=Solar+Rooftop+EPC+Contractor
GET  /v2/query/districts-for?industry=Food+Processing
GET  /v2/query/ai-tools-for?industry=Manufacturing
GET  /v2/context/business/{name}          # full cross-package context

GET  /v2/meta/entity-types
GET  /v2/meta/relationship-types
GET  /v2/meta/ownership
GET  /v2/meta/graph-summary
```

## Response shape

```json
{
  "data": [
    {
      "global_entity_id": "vw:msme:custom-software-development-firm",
      "canonical_name": "Custom Software Development Firm",
      "entity_type": "MSME",
      "source_package": "Package008_MSME",
      "path_confidence": 72,
      "hops": 1,
      "provenance": [
        {"package": "Package008_MSME", "dataset": "skill_mapping.csv",
          "row_id": "kmap-016", "relationship": "REQUIRES_SKILL", "confidence": "72"}
      ]
    }
  ],
  "meta": {
    "graph_version": "2.0.0",
    "verification_status": "VST-NEEDS_REVIEW",
    "warning": "No row in this knowledge base has had human data-steward review."
  }
}
```

That `meta.warning` is not decoration. It is the most important field in the response
until stewardship exists.

## AI integration

The graph is a **grounding source for retrieval, not a training corpus.**

| Use | Fit | Why |
|---|---|---|
| RAG grounding | Good | Every fact carries a citation; hallucination becomes checkable |
| Structured tool-calling for an agent | Good | The five named queries map cleanly to tool definitions |
| Entity linking in free text | Good | `Resolver` already does this conservatively |
| Fine-tuning on the CSVs | **Poor** | Unreviewed data, sparse graph — a model would learn the gaps as facts |
| Answering without citation | **Refuse** | Contradicts principle 1 |

An MCP-style tool surface over `queries.py` is the natural first AI integration: the
functions already return provenance-carrying results.

## What must exist before an API ships

| # | Requirement | Status |
|---|---|---|
| 1 | Graph validation passes | Done (0 violations) |
| 2 | Stable identifiers | Done (ADR-002) |
| 3 | Provenance on every result | Done |
| 4 | Human review of core entities | **Not started** |
| 5 | ADR-003 decided | **Open** |
| 6 | Knowledge Engine recovered | **Open (ADR-006)** |
| 7 | Auth, rate limiting, versioning policy | Not designed |

Items 1-3 are the platform's responsibility and are done. 4-6 gate whether the data
should be exposed at all. 7 is ordinary API engineering.

**Shipping an API over unreviewed data would industrialise its errors.** The technical
work is the easy part; item 4 is the real blocker.
