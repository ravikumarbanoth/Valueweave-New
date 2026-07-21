# Package004_Industries_and_Livelihoods v1.0.0-RC1 — Methodology

## What Kind of Package This Is

Unlike Package001_Geography, Package002_Education, and Package003_Healthcare — which catalogue
discrete, individually-verifiable institutions (a specific district, a specific university, a
specific hospital) — this package catalogues **livelihood/industry categories**: types of business
or trade a person could pursue (e.g. "Spice Processing" or "Plumbing"), not individual named
businesses. This is a meaningfully different research task. There is no finite list of "all spice
processors in Telangana" to verify against; instead, each row characterizes the *opportunity itself*
— what it typically requires, what support exists, and where it's viable — grounded in real
government/industry documentation wherever such documentation exists.

## Collection Approach

Each of the 5 datasets was researched independently via the WebSearch tool, following the
source-priority order defined in the package brief:

1. **Tier 1 — Government**: MSME, NSDC, Skill India, Startup India, Telangana/AP industry
   departments, District Industries Centres, official reports/PDFs. This tier was prioritized above
   all others for any numeric claim (investment ranges, subsidy percentages).
2. **Tier 2 — Official business/association websites**: company/industry-association/chamber-of-
   commerce/industrial-park/incubator sites, used for context and cross-checks.
3. **Tier 3 — Verified social media**: not used as the primary source for any row in this release.
4. **Tier 4 — Trusted news**: used for policy updates and scheme renames (see below).
5. **Tier 5 — Community sources**: not used for any factual claim, per the package brief's
   restriction to qualitative-insight use only — and this release doesn't include qualitative
   sentiment data at all, so Tier 5 wasn't drawn on.

## The Investment-Range Fabrication Risk — How It Was Handled

"Typical Investment Range" is the single highest fabrication-risk field in this package: it's easy
to state a plausible-sounding number without any real source, and generic business-advice content
online is full of exactly that. **The rule enforced across every research pass**: a numeric
investment-range figure was only accepted if traced to a specific, citable government document —
principally District Industries Centre (DIC) or MSME-Development Institute "project profiles" /
"detailed project reports" (DPRs), KVIC project profiles, or PMFME model-DPRs, which are real
published documents with concrete machinery/working-capital/total-investment figures for specific
small-scale industries. Where no such document could be found, the field is `PENDING_VERIFICATION`
(or, for the two trade/livelihood datasets with more qualitative research, a descriptive summary of
cost drivers without a solid number) and confidence was capped at 58-65 rather than the 70-85 band
used for government-sourced figures.

**Estimated Monthly Revenue Range was dropped from the schema entirely** rather than shipped as a
mostly-`PENDING_VERIFICATION` column. There is no reliable public source for typical small-business
monthly revenue in these categories — attempting to populate it would have meant either 100%
`PENDING_VERIFICATION` (adding a column with no informational value) or fabrication risk. This
mirrors the same judgment call as dropping other genuinely-unsourceable fields in prior packages.

## A Material Environment Constraint

Direct WebFetch to `.gov.in`, `.ac.in`, and `.nic.in` domains was blocked by this session's
organizational egress policy — confirmed via a live test fetch immediately before collection began,
the same constraint documented in Package001-003. Several government DIC/PMFME project-profile PDFs
were located by URL during research but their content could only be seen through WebSearch snippets,
never a direct read. This is the clearest concrete example in this package of where restored
WebFetch access would likely unlock real improvement (see `acquisition_backlog.json`).

## Field-Depth Scope Reduction

The package brief specified ~25 fields per entity, including Estimated Monthly Revenue Range,
Machinery, Raw Materials, Suppliers, Business Risks, Opportunities, Government Support, Typical
Workforce, Technology Adoption, AI Opportunities, Sustainability, Market Trends, Future Potential,
Related Industries, and District Suitability. **This release does not carry most of these fields.**
The 5 shipped schemas (see `schemas/schema_catalog.json`) cover a smaller, verifiable core: identity,
category/sub-category, description, target customers, investment range (where sourced), skill level,
training availability, licenses required, government schemes, and rural/urban suitability.

Beyond the revenue-range field (dropped entirely, see above), the remaining descoped fields are
mostly **analytical or predictive commentary** (Business Risks, Opportunities, AI Opportunities,
Sustainability, Market Trends, Future Potential) rather than discrete verifiable facts in the same
sense as an institution's address or establishment year. Presenting AI-generated analysis of "future
potential" as if it were sourced, verified knowledge would blur the line this package's entire
evidence model depends on — so these fields are left for a future release with an explicitly
different, source-grounded methodology (e.g. citing specific NITI Aayog / industry-association
market reports per claim) rather than populated with plausible-sounding commentary now.

## Notable Findings During Research

- **Facebook Marketplace** — named in the package brief's own China-inspired-adaptation examples —
  was checked and confirmed **not officially launched in India**. This is documented explicitly in
  the relevant row's notes rather than silently substituted or ignored.
- **PM Vishwakarma Yojana** covers only 2 of the 9 construction/skilled-trade categories researched
  (Carpenter and Mason) — this was independently verified rather than assumed to apply broadly to
  "skilled trades" as a category.
- **Telangana's state-abbreviation convention shifted**: TS-iPASS → TG-iPASS, TSIIC → TGIIC.
- **Telangana's MSME Policy 2024** layers atop the older T-IDEA/T-PRIDE framework with some
  conflicting subsidy figures across sources — this overlap is disclosed as unresolved rather than
  guessed at.

## Scope Decision

Given the scale of the full ~150-sub-category brief, this release deliberately narrows to 5 datasets
(MSME & Entrepreneurship Support Schemes, Food & Agro-Processing Micro-Enterprises, Construction &
Skilled Trade Services, Digital & Technology Livelihoods, and the explicitly-requested China-Inspired
Adapted Opportunities) scoped to Telangana and Andhra Pradesh — mirroring Package001-003's precedent
of shipping a narrow, real, well-documented slice rather than a broad but unverifiable one. The
remaining ~145 sub-categories and all other states/UTs are catalogued in `acquisition_backlog.json`
and `registry/dataset_registry.csv` as `BLOCKED` or `QUEUED`, not silently omitted.
