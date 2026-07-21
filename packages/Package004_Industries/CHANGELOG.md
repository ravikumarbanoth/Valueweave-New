# CHANGELOG — Package004_Industries_and_Livelihoods

## [1.0.0-RC1] — 2026-07-22 — NOT MERGED TO MAIN

### Added
- `msme_entrepreneurship_support_schemes.csv` — 18 rows: 8 national (PMEGP, Stand-Up India, PMMY, Startup India, NSDC, CGTMSE, PM Vishwakarma) + 7 Telangana (T-IDEA, T-PRIDE, TG-iPASS, WE-HUB, TASK, TGIIC, MSME Policy 2024) + 3 Andhra Pradesh (APIIC, AP Innovation Society/Startup AP, AP MSME Policy 4.0)
- `food_agro_processing_micro_enterprises.csv` — 13 rows across all 7 requested categories (food processing, spice/pickle/masala, cold-pressed oils, millets, seed processing), split by TG/AP where genuinely different
- `construction_skilled_trade_services.csv` — 11 rows (plumbing, electrical, welding, carpentry, painting, aluminium fabrication, borewell services, tiles fixing, POP works)
- `digital_technology_livelihoods.csv` — 12 rows (software/IT, web/app dev, digital marketing, cloud, cybersecurity, plus a Telangana GRID/LEAP rural-BPO row)
- `china_inspired_adapted_opportunities.csv` — 9 rows: all 6 brief-mandated examples (Douyin Store, Livestream Commerce, Hanfu Rental, Mini Programs, Agricultural Social Commerce, Courtyard Guesthouse) + 3 additional verified adaptations
- `schemas/schema_catalog.json` — column-level schema reference for all 5 datasets
- `imports/import_sequence.json` and 5 per-dataset import manifests
- `evidence/*.evidence_manifest.json` — per-dataset source citation lists, including the WebFetch environment-block disclosure
- `raw_sources/*.source_inventory.md` — human-readable per-dataset source listings
- `reports/` — per-dataset collection reports, data dictionaries, and quality reports; package-level coverage, confidence-analysis, source-analysis, duplicate-analysis, category-and-subcategory-statistics, rural-urban-suitability-distribution, known-gaps, future-expansion-roadmap, and validation reports
- `docs/METHODOLOGY.md`, `docs/USAGE.md` — collection methodology (including the investment-range fabrication-risk discipline and the WebFetch environment constraint) and consumption guide
- `acquisition_backlog.json` — every one of the remaining ~145 briefed sub-categories and every non-TG/AP state, each marked BLOCKED or QUEUED with a specific unblock path
- `codex_handoff.md`, `integration_checklist.md`, `package_health_report.md`, top-level `validation_report.md` — release-management artifacts

### Scope Decisions
- RC1 covers 5 of the ~150 named industry/livelihood sub-categories, scoped to Telangana, Andhra Pradesh, and genuinely national-level entities — a deliberate narrow-and-deep decision consistent with Package001-003's precedent, stated explicitly before collection began.
- Estimated Monthly Revenue Range was dropped from the schema entirely rather than shipped as a mostly-empty column — no reliable public source exists for typical small-business revenue in these categories.
- Analytical/predictive fields from the brief (Business Risks, Opportunities, AI Opportunities, Sustainability, Market Trends, Future Potential, Related Industries, District Suitability) are not populated in RC1 — these require a distinct, source-grounded methodology to avoid presenting unsourced commentary as verified knowledge; see docs/METHODOLOGY.md.

### Environment Constraint Disclosed
- This session's organizational egress proxy blocked direct WebFetch to `.gov.in`, `.ac.in`, and `.nic.in` domains (confirmed HTTP 403 policy denial, re-tested live immediately before collection began) — the same constraint documented in Package001-003. All 63 rows in this release were sourced via WebSearch result snippets rather than direct page fetch. Several DIC/PMFME project-profile PDFs were located by URL but their content was only seen via search snippet, never directly read. Confidence scores capped at 82 (no row exceeds this); every row starts at `verification_status: VST-NEEDS_REVIEW`.

### Notable Findings
- **Facebook Marketplace** (named in the brief's own China-inspired-adaptation examples) confirmed NOT officially launched in India — documented explicitly rather than silently substituted.
- **PM Vishwakarma Yojana** confirmed to cover only 2 of the 9 construction/skilled-trade categories researched (Carpenter, Mason) — checked rather than assumed.
- **Telangana state-abbreviation shift**: TS-iPASS → TG-iPASS, TSIIC → TGIIC.
- **Telangana MSME Policy 2024** layers atop the older T-IDEA/T-PRIDE framework with some conflicting subsidy figures — disclosed as unresolved rather than guessed.

### Known Issues
- 20 of 1,053 total fields (1.9%) across the package are marked `PENDING_VERIFICATION` — concentrated in `typical_investment_range_summary` (all 12 digital/technology rows, 8 of 13 food/agro rows).
- No dataset in this release has any row promoted to `VST-VERIFIED`.
- ~145 of ~150 briefed sub-categories not researched (BLOCKED/QUEUED, not guessed).

### Future Work
- See `reports/future_expansion_roadmap.md` for the full 10-item roadmap: re-verification with restored WebFetch, resolving the Telangana MSME-policy overlap, expanding Manufacturing/Agriculture & Allied beyond processing, adding Tourism/Repair/Retail/Recycling/Service/Education/Health/Local-Entrepreneurship categories, extending geographic coverage, designing a source-grounded methodology for the descoped analytical fields, and evaluating cross-package FK wiring.
