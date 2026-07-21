# Package003_Healthcare v1.0.0-RC1 — Methodology

## Collection Approach

Each of the 4 datasets in this release was researched independently via the WebSearch tool, following
the source-priority order defined in the package brief:

1. **Tier 1 — Highest confidence**: official hospital websites, state health department portals,
   Ministry of Health & Family Welfare, National Health Mission, Telangana/AP Health Departments, NMC,
   government notifications, official PDFs/annual reports.
2. **Tier 2 — Official digital channels**: verified social media accounts, used only where they
   provided genuinely newer information than official websites; not the primary source for any row.
3. **Tier 3 — Trusted healthcare directories** (Practo, Medindia, National Health Portal, etc.): used
   as cross-checks, or as primary source only where official sources were unavailable.
4. **Tier 4 — Trusted news & media**: used for time-sensitive facts — scheme renames, new facility
   launches, regulatory transitions (e.g. the Dental Council of India → National Dental Commission
   transition, dated 19 March 2026).
5. **Tier 5 — Community sources**: not used for any factual institutional data in this release, per
   the package brief's explicit restriction to qualitative-only use.

## A Material Environment Constraint

This session's outbound network access goes through an organization-managed egress proxy. **Every
direct WebFetch request to `.gov.in`, `.ac.in`, `.edu.in`, and Wikipedia domains was rejected with an
HTTP 403 policy denial** — confirmed via a live test fetch immediately before collection began, and
via the proxy's own status endpoint as a fixed organizational policy rather than a transient failure.
This is the same constraint documented in Package001_Geography and Package002_Education.

**Practical consequence:** no source page cited in this package was directly fetched and re-read.
All facts were instead sourced from WebSearch tool result snippets — real government and institutional
content, surfaced as indexed summaries rather than live-fetched pages.

**How this was handled without fabricating anything:**
- Every fact carries a real, specific `source_url` — nothing was invented.
- Confidence scores were capped at 88 (no row claims a 90+ "direct official fetch" score).
- Every field the researching agents could not corroborate through search was left as the literal
  sentinel `PENDING_VERIFICATION` rather than guessed.
- Every row's `verification_status` starts at `VST-NEEDS_REVIEW`.

## Field-Depth Scope Reduction

The package brief specified ~30 fields to collect per healthcare entity, including Latitude/Longitude,
Contact Numbers, Emergency Numbers, Email, Departments, Specialties, Available Services, ICU
Availability, Dialysis, Ambulance Availability, Insurance Accepted, Working Hours, and Google Maps
Link. **This release does not carry most of these fields.** The 4 shipped schemas (see
`schemas/schema_catalog.json`) cover a smaller, more verifiable core per entity type: identity,
category/ownership, managing organization or affiliation, location (district/city), official website,
and category-specific fields (bed capacity/teaching status for hospitals; MBBS seats/affiliation for
colleges; coverage/beneficiaries for schemes).

This reduction was a deliberate quality tradeoff: search-snippet-only research could not reliably
surface facility-level details (ICU beds, working hours, exact contact numbers) for dozens of
institutions without either extensive per-institution deep dives or a real risk of guessing. Rather
than fabricate or leave 15+ additional columns mostly `PENDING_VERIFICATION` across 134 rows, the
schema itself was narrowed to what could be populated with genuine confidence. Latitude/longitude and
Google Maps links are 0% populated in this release — the same known gap documented in
Package001_Geography and Package002_Education for the same underlying reason.

## Multi-Source Validation in Practice

Per the brief's instruction to prefer newer verified information over outdated official sources when
multiple independent sources agree: this played out concretely in the government_health_insurance_schemes
dataset, where Andhra Pradesh's flagship scheme has been renamed across recent government transitions
(most recently Dr. YSR Aarogyasri → Dr. NTR Vaidya Seva, July 2024) and Telangana's employee scheme was
relaunched as NEHS just 4 days before this collection date (17 July 2026) under a new administering
trust. Both are recorded under their current names with prior names cross-referenced in `notes`, and
the NEHS row's confidence was deliberately kept lower given how recent the change is.

## Scope Decision

Given the scale of the full 40-domain brief, this release deliberately narrows to 4 domains (Medical
Regulatory Bodies & Health Missions, Medical Colleges, Government Hospitals, Government Health
Insurance Schemes) scoped to Telangana, Andhra Pradesh, and genuinely national-level entities — mirroring
Package001_Geography and Package002_Education's precedent of shipping a narrow, real, well-documented
slice rather than a broad but unverifiable one, and directly following this package's own brief
("prioritize depth, accuracy and verification over maximum coverage"). The remaining 36 domains and
all other states/UTs are catalogued in `acquisition_backlog.json` and `registry/dataset_registry.csv`
as `BLOCKED` or `QUEUED`, not silently omitted. PHCs, CHCs, and Urban Health Centres are specifically
`BLOCKED` (not merely queued) because their sheer volume — hundreds per state — exceeds what
per-institution search-snippet research can verify; unlocking them requires a bulk structured data
source (e.g. HMIS/NHM facility registry) rather than more research time.
