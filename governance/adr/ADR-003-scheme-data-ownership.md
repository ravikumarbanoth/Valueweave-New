# ADR-003: Government Scheme Data Ownership Across Six Packages

**Status:** OPEN — decision required
**Date raised:** 2026-07-25
**Priority:** Highest open governance item in the platform

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

That is roughly 119 rows describing perhaps 90 distinct schemes. PM-KISAN appears in
Package005 and Package007. PMKVY appears in Package006 and Package007. AB PM-JAY appears
in Package003 and Package007.

Package007 declares every overlap in `government_schemes.also_in_package`, and
`knowledge_graph/ownership/known_overlaps.csv` records it. **Declaring is not resolving.**

The graph makes the cost concrete: `entities.csv` contains one `GovernmentScheme` node
per distinct scheme, but the domain packages' scheme rows are not linked to it, so a
scheme benefit updated in Package007 leaves Package005's copy stale with nothing
detecting the divergence.

## Options

### Option 1 — Package007 becomes canonical (recommended)

Domain packages keep their scheme datasets but mark them `DEPRECATED_REFERENCE` and add
a `package007_scheme_id` foreign key. New schemes land only in Package007.

- **Cost:** one coordinated release across five packages.
- **Benefit:** one place to update when a scheme changes. The graph's `GovernmentScheme`
  nodes gain a single authoritative source.
- **Risk:** the domain packages lose self-containment.

### Option 2 — Domain packages stay canonical for their slice

Package007 holds only schemes with no domain home (~19 of its 40).

- **Cost:** Package007 loses more than half its registry.
- **Benefit:** no coordinated release; packages stay self-contained.
- **Risk:** cross-domain schemes (PM Vishwakarma spans skills, MSME and artisan trades)
  have no natural owner.

### Option 3 — Do nothing

- **Cost:** copies drift silently. Nothing compares them today.

## Decision

**Not yet made.** Recorded here so that it is a visible open decision rather than an
implicit one.

## Recommendation

**Option 1.** Scheme parameters change with every budget cycle. Six copies of a figure
that changes annually will diverge; the only question is when. The coordinated release
is a one-time cost against a recurring correctness risk.

## Interim mitigation now in place

`validate_graph.py` check G7 fails the build on **undeclared** cross-package attribute
duplication. Declared overlaps — the ones in `known_overlaps.csv` pointing at this ADR —
downgrade to a warning. This means new undeclared duplication cannot be introduced
silently while this decision is open.
