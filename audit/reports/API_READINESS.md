# API Readiness — ValueWeave v2.1 Phase 7

**Read-only assessment.**

## Readiness by API

| API | Data ready | Score | Notes |
|---|---|---|---|
| Entity API | READY | 95/100 | 647 entities, stable ids, provenance complete |
| Relationship API | READY | 95/100 | 865 edges, all endpoints resolve |
| Graph API | READY | 90/100 | traverse/neighbours/shortest_path implemented |
| Search API | READY | 85/100 | Resolver provides alias/prefix/fuzzy; no full-text index |
| Package API | READY | 80/100 | manifests and registries exist per package |
| Version API | PARTIAL | 55/100 | package VERSION files exist; graph has no version endpoint contract |
| Governance API | READY | 75/100 | ownership registry + ADRs are machine-readable CSV/MD |
| Recommendation API | False | 25/100 | blocked on Phase 6 gaps |

## Recommended implementation order

| # | API | Readiness |
|---|---|---|
| 1 | Entity API | 95/100 |
| 2 | Relationship API | 95/100 |
| 3 | Graph API | 90/100 |
| 4 | Search API | 85/100 |
| 5 | Package API | 80/100 |
| 6 | Governance API | 75/100 |
| 7 | Version API | 55/100 |
| 8 | Recommendation API | 25/100 |

The order follows dependency and risk, not perceived value:

1. **Entity API** first — everything else references entities. Stable ids (ADR-002),
   complete provenance, 647 entities validated by 10 checks.
2. **Relationship API** — 865 edges, all endpoints resolve, typed and provenance-carrying.
3. **Graph API** — traversal already implemented (`neighbours`, `traverse`,
   `shortest_path`); this is exposure, not construction.
4. **Search API** — `Resolver` provides alias, prefix and conservative fuzzy resolution.
   No full-text index exists; for 647 entities, linear scan is adequate.
5. **Package API** — manifests and dataset registries exist per package; needs a uniform
   contract across the Package001-004 / Package005-008 documentation split.
6. **Governance API** — ownership registry and ADRs are already machine-readable.
7. **Version API** — weakest of the ready set. Package `VERSION` files exist, but the
   graph has no versioning contract and no compatibility policy is defined.
8. **Recommendation API** — blocked; see `RECOMMENDATION_READINESS.md`.

## Blocking for every API

- Zero human-verified rows: an API industrialises whatever errors the data holds
- No auth, rate limiting or API versioning policy designed

The first is the serious one. **An API over unverified data industrialises whatever
errors it contains** — it converts a static repository nobody queries into a service that
returns wrong answers at scale, with an authoritative-looking response envelope.

## Minimum bar before any API ships

| # | Requirement | Status |
|---|---|---|
| 1 | Graph validation passes | **Done** — 0 violations, 10 checks |
| 2 | Stable identifiers | **Done** — ADR-002 |
| 3 | Provenance on every result | **Done** |
| 4 | Tier 1 + Tier 2 human review | **Not started** |
| 5 | ADR-003 resolved | **Open** |
| 6 | Auth, rate limiting, versioning policy | **Not designed** |

Items 1-3 are the platform's own responsibility and are complete. Items 4-5 gate whether
the data *should* be exposed. Item 6 is ordinary API engineering.

## Response contract requirement

Every response must carry, non-optionally:

```json
"meta": {
  "graph_version": "2.0.0",
  "verification_status": "VST-NEEDS_REVIEW",
  "warning": "No row in this knowledge base has had human data-steward review."
}
```

That warning is the most important field in the payload until stewardship exists, and it
should be removed only when `verified_pct` is meaningfully above zero — currently
**0.0%**.

## Recommendation

**Build Entity, Relationship and Graph APIs in v2.1** — they are ready, additive and
low-risk, and they make the platform consumable.

**Gate Search, Package, Governance and Version APIs behind Tier 2 review.**

**Do not build the Recommendation API.**
