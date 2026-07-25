# ADR-005: Declared Overlaps Are Governed; Undeclared Overlaps Are Violations

**Status:** Accepted
**Date:** 2026-07-25

## Context

Package008 introduced validation check V13, which fails the build if a column name
restates an attribute owned by an upstream package. Platform v2 generalises this to all
eight packages as graph check **G7**.

A naive generalisation fails immediately. The first G7 run produced 22 violations, and
almost all were false positives:

- `jurisdiction` appears in Package002, Package003, Package004 and Package006. It is a
  generic column, not a Package006 attribute.
- `ownership` on a university, a hospital and a bank means three different things.
- `official_portal` on a **licence** (FOSCOS, GST) is not a **scheme** portal — the exact
  false positive Package008's own V13 had already found and fixed.

But some hits were genuine: Package005's `agriculture_schemes.objective` really does
restate a Package007-owned attribute.

## Decision

Two mechanisms, applied in order:

**1. Only distinctive attributes are enforceable.** Generic and context-dependent column
names are excluded from `attribute_ownership.csv`: `jurisdiction`, `ownership`,
`established_year`, `affiliation`, `capacity`, `risk_level`, `provider_type`,
`institution_type`, `official_portal`, `objective`, and similar. Enforcement covers
attributes like `nsqf_level`, `avg_yield_tons_per_ha`, `water_requirement_mm`,
`udyam_classification` — names that mean one thing in one domain.

**2. Declared overlaps downgrade to warnings.** `known_overlaps.csv` records duplication
that is known and accepted, each row naming the ADR that tracks it. G7 consults it:
declared duplication produces a warning citing the ADR; **undeclared** duplication is a
hard failure.

## Consequences

**Positive**

- `known_overlaps.csv` becomes load-bearing rather than documentation. A governance
  registry that no check reads is a wish; one that gates the build is a control.
- New duplication cannot be introduced silently. To add it, you must declare it and
  point at an ADR — which forces the conversation at the right moment.
- The distinction is meaningful: five packages duplicating scheme data **knowingly**,
  tracked under ADR-003, is a different situation from a ninth package quietly adding a
  sixth copy.

**Negative**

- A lazy contributor can silence G7 by adding a row to `known_overlaps.csv`. This is
  mitigated only by review, not by tooling.
- The generic-attribute exclusion list is a judgement call and will need revisiting as
  packages add columns.

## Lesson recorded

This is the second time in the programme that an over-broad correctness rule produced
false positives, and the second time the right fix was **narrowing the rule rather than
suppressing the check**. A suppressed check stops finding anything.
