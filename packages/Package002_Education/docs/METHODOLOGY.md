# Package002_Education v1.0.0 — Methodology

## Collection Approach

Each of the 4 datasets in this release was researched independently via the WebSearch tool, following
the source-priority order defined in the package brief:

1. **Priority 1 — Government sources**: Ministry of Education, UGC, AICTE, NCERT, NTA, AISHE, NIRF,
   NAAC, NBA, NCVET, state education departments, SCERT, official university/institution sites,
   official notifications, gazettes.
2. **Priority 2 — Official social media**: used only where it provided genuinely newer information
   than the official website; not the primary source for any row in this release.
3. **Priority 3 — Trusted education portals** (Shiksha, Careers360, CollegeDunia, GetMyUni, Jagran
   Josh, major newspaper education sections): used as cross-checks, or as the primary source only
   where official sources could not be reached.
4. **Priority 4 — Community sources** (Reddit, Quora, forums, reviews): not used for any factual
   institutional data in this release, per the package brief's explicit restriction.
5. **Priority 5 — News**: used for scheme-rename verification (see Andhra Pradesh scholarship renames
   in `reports/scholarships.collection_report.md`) and similar time-sensitive facts.

## A Material Environment Constraint

This session's outbound network access goes through an organization-managed egress proxy. During
collection, **every direct WebFetch request to `.gov.in`, `.ac.in`, `.edu.in`, and Wikipedia domains
was rejected with an HTTP 403 policy denial**, confirmed via the proxy's own status endpoint as a
fixed organizational policy rather than a transient or client-side failure. Per the proxy's own
operating instructions, policy denials are to be reported, not retried or routed around — so they
were not.

**Practical consequence:** no source page cited in this package was directly fetched and re-read by
the researching agent. All facts were instead sourced from WebSearch tool result snippets — which do
surface real government and institutional page content, but as indexed/cached summaries rather than
a live, directly-verified fetch.

**How this was handled without fabricating anything:**
- Every fact still carries a real, specific `source_url` — nothing was invented.
- Confidence scores were deliberately capped lower than Package001_Geography's methodology (which had
  working WebFetch access): this package's scores top out at 92 and mostly sit in the 58–85 range,
  versus Package001's 85–95 band for directly-confirmed official sources.
- Every field the researching agents could not corroborate through search was left as the literal
  sentinel `PENDING_VERIFICATION` rather than guessed.
- Every row's `verification_status` starts at `VST-NEEDS_REVIEW`. Promotion to `VST-VERIFIED` requires
  a governance step — ideally one where a human (or a future session with working WebFetch) directly
  re-opens each `source_url` and confirms the cited fact.

## Confidence Scoring

| Band | Meaning |
|---|---|
| 85–95 | Would indicate a directly-fetched, re-read official source (not achieved in this release — reserved for future re-verification) |
| 70–92 | Strong, specific search-result corroboration from an official domain's indexed content |
| 58–69 | Single-source or conflicting-source corroboration; flagged in the relevant collection report |

## Field-Depth Scope Reduction

The package brief specified ~33 fields to collect per institution, including Fee Structure, Admission
Process, Eligibility, Contact Details, Latitude/Longitude, Hostel, Library, Laboratories, Placement,
Facilities, Research, Incubation, Student Intake, Ownership, Approval, Departments, and NBA/AISHE
status. **This release does not carry most of these fields.** The 4 shipped schemas (see
`schemas/schema_catalog.json`) cover a smaller, more verifiable core: identity, type/category,
jurisdiction, affiliation, establishment year, official website, and (for universities specifically)
NAAC grade and NIRF rank where confidently sourced.

This reduction was a deliberate quality tradeoff, not an oversight: search-snippet-only research (see
above) could not reliably surface facts like fee structures, precise lat/long coordinates, or
facility-level details (hostel/library/lab presence) for dozens of institutions without either
extensive per-institution deep dives (out of scope for this release's row-count target) or a real risk
of guessing. Rather than fabricate or leave 15+ additional columns mostly `PENDING_VERIFICATION`
across 135 rows, the schema itself was narrowed to what could be populated with genuine confidence.
Latitude/longitude in particular is 0% populated in this release — same as Package001_Geography's
known gap for the same reason.

Expanding field depth on the 4 already-shipped domains is tracked in `acquisition_backlog.json`
alongside the 36 un-shipped domains.

## Scope Decision

Given the scale of the full 40-domain / all-India brief, this release deliberately narrows to 4
domains (Educational Boards & Regulatory Bodies, Universities, Entrance Exams, Scholarships) scoped
to Telangana, Andhra Pradesh, and genuinely national-level entities — a decision made explicitly with
the requester before collection began, mirroring Package001_Geography's precedent of shipping a
narrow, real, well-documented slice rather than a broad but unverifiable one. The remaining 36 domains
and all other states/UTs are catalogued in `acquisition_backlog.json` and `registry/dataset_registry.csv`
as `BLOCKED` or `QUEUED`, not silently omitted.
