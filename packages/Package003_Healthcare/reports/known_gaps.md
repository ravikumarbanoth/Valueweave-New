# Package003_Healthcare v1.0.0-RC1 — Known Gaps

See `acquisition_backlog.json` for the full structured list (29 domain-level gaps + 3 dataset-specific gaps). Summary:

## Domain-level (36 of 40 briefed domains not researched)
PHCs, CHCs, and Urban Health Centres are BLOCKED (scale exceeds per-institution search-snippet verification). The remaining 26 domains (private hospitals in general, specialty hospitals of every kind, diagnostic centres, blood banks, dialysis/organ-donation/ambulance/trauma/mental-health/rehab centres, telemedicine, public health labs, helplines, vaccination, disease surveillance, public health campaigns, broader national health programmes, pharma support services, health NGOs, and all non-TG/AP states) are QUEUED.

## Dataset-specific gaps
- **Government hospitals**: TVVP/APVVP's own master hospital lists exist but their tabular content did not surface in WebSearch snippets — only aggregate counts (~175 TVVP, ~228 APVVP) were found. This dataset's 49 rows are a verified subset, not the full state rosters. Several 2022-reorganization districts in both states have no verified row.
- **Medical colleges**: ~17-19 of Telangana's newer (2022-2023) government colleges and several more Andhra Pradesh colleges were excluded rather than guessed.
- **Health insurance schemes**: AP EHS's exact coverage ceiling, ECHS contribution amounts, current hospital-network counts, and CGHS beneficiary count (sources disagreed 42-50 lakh) are PENDING_VERIFICATION.

## Field-level gaps
- `bed_capacity` and `contact_number` are PENDING_VERIFICATION for many government hospital rows (130 of 1,029 total fields in that dataset).
- `mbbs_seats` is PENDING_VERIFICATION for most medical college rows (current-year intake figures were not independently confirmable this session).
- No row across any dataset has latitude/longitude, Google Maps links, ICU availability, dialysis availability, working hours, or email — these fields from the original brief's ~30-field list were descoped for RC1; see docs/METHODOLOGY.md 'Field-Depth Scope Reduction'.

## Environment constraint
WebFetch to .gov.in/.ac.in/Wikipedia domains was blocked all session; all data is WebSearch-snippet-sourced with confidence capped at 88. See docs/METHODOLOGY.md.
