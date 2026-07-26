# ADR-003: Government Scheme Data Ownership Across Six Packages

**Status:** ACCEPTED — Option 1 adopted
**Date raised:** 2026-07-25
**Date decided:** 2026-07-26 (Platform v2.2, Work Package 2)
**Supersedes:** the OPEN state recorded in the v2.1 audit (`audit/reports/OWNERSHIP_AUDIT.md`)

## Context

Six packages hold government scheme rows:

| Package | Scheme rows | Framing |
|---|---|---|
| Package002_Education | 25 | Scholarships |
| Package003_Healthcare | 9 | Health insurance schemes |
| Package004_Industries | 18 | MSME support schemes |
| Package005_Agriculture | 12 | Agriculture schemes |
| Package006_Skills_and_Training | 15 | Skill development schemes |
| **Package007_Government_Schemes** | **40** | **Cross-domain canonical registry** |

That is 79 domain rows plus 40 canonical rows. PM-KISAN appears in Package005 and
Package007. PMKVY appears in Package006 and Package007. AB PM-JAY appears in Package003
and Package007.

Package007 declared every overlap in `government_schemes.also_in_package`, and
`knowledge_graph/ownership/known_overlaps.csv` recorded it. **Declaring is not resolving.**
The graph made the cost concrete: `entities.csv` held one `GovernmentScheme` node per
distinct scheme, but the domain packages' scheme rows were not linked to it, so a benefit
updated in Package007 left Package005's copy stale with nothing detecting the divergence.

## Decision

**Option 1 is adopted. Package007_Government_Schemes is the authoritative owner of the
`GovernmentScheme` entity type and of every attribute the ownership registry assigns to
it.**

Implementation, all of it additive:

1. Each of the five domain scheme datasets gains two columns:

   | Column | Meaning |
   |---|---|
   | `package007_scheme_id` | the canonical Package007 `scheme_id`, or the bare sentinel `PENDING_VERIFICATION` |
   | `scheme_ownership` | `DEPRECATED_REFERENCE` or `DOMAIN_CANONICAL` |

2. `DEPRECATED_REFERENCE` means Package007 owns this scheme's attributes. The domain row
   is retained for backward compatibility and remains readable, but Package007 is where a
   change is made.

3. `DOMAIN_CANONICAL` means no Package007 counterpart exists. The domain package remains
   the owner of that scheme until a steward promotes it into Package007. This is a
   determinate statement, not an unknown.

4. New schemes land in Package007. A domain package adds a scheme only when it is
   genuinely outside Package007's cross-domain scope, and then it is `DOMAIN_CANONICAL`.

## What the crosswalk actually resolved

`governance/ownership/build_scheme_crosswalk.py` matched all 79 domain rows against the
40 canonical schemes. Every match records the matcher that produced it:

| Match method | Rows | Evidence |
|---|---:|---|
| `EXACT_NAME` | 16 | normalised canonical names identical |
| `ACRONYM` | 3 | parenthetical acronym equals a Package007 `short_name` |
| `PORTAL` | 2 | both rows cite the same official portal host |
| `FUZZY` | 0 | nothing cleared the 0.88 threshold unambiguously |
| **matched** | **21** | → `DEPRECATED_REFERENCE`, referencing 21 distinct canonical schemes |
| `NO_MATCH` | 58 | → `DOMAIN_CANONICAL` |

The 58 unmatched rows are not a failure of the crosswalk. They are schemes Package007's
40-row national registry does not cover: state schemes (Telangana ePASS, AP Post-Matric,
Rajiv Aarogyasri), minority and community scholarships, CGHS, ECHS, RKVY, NATS, RSETI, JSS
and the Startup India umbrella programme — which is distinct from Startup India Seed Fund
Scheme (`sch-020`), the scheme Package007 actually holds. Conflating those two would have
been exactly the error the conservative matcher exists to prevent.

## Why matching refuses rather than guesses

A wrong crosswalk row is worse than a missing one: it silently redirects a consumer from
one scheme to an unrelated one, and nothing downstream can detect it. So the matcher
accepts a fuzzy match only when **exactly one** candidate clears the threshold. Two
candidates is ambiguity, not a hint. This is the same position ADR-004 takes on entity
merges, applied to a narrower problem.

## Enforcement

The decision is mechanical, not documentary. `validate_graph.py` check **G11** fails the
build when:

- any entity type has more than one owner in the ownership registry;
- any of the five domain scheme datasets is missing either governance column;
- a `DEPRECATED_REFERENCE` row's `package007_scheme_id` does not resolve to a real
  Package007 scheme;
- a `DOMAIN_CANONICAL` row carries an id where the bare sentinel is expected.

G7 continues to enforce that no non-owner publishes a Package007-owned attribute.

## Backward compatibility

Verified mechanically before commit: for all five datasets, row count is unchanged, column
order is unchanged, and **zero** existing cell values changed. The two governance columns
are appended. A consumer that ignores them reads exactly what it read before v2.2.

## Consequences

**Accepted cost.** Domain packages are no longer fully self-contained for scheme
attributes: a consumer that wants the current benefit figure for PM-KISAN should read
Package007 `sch-005`, not Package005 `as-001`.

**Benefit.** One place to update when a scheme changes, and a mechanical check that
catches divergence. Scheme parameters change with every budget cycle; six copies of an
annually-changing figure will diverge, and the only question was when.

**Not resolved by this ADR.** `ExportCountry` remains `UNRESOLVED` under ADR-005 — no
package holds a country dataset, so the graph still derives those entities from free text.
That is a separate decision and is not in v2.2's scope.
