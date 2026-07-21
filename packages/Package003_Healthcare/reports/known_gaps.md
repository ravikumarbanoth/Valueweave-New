# Package003_Healthcare v1.0.0 — Known Gaps

See `acquisition_backlog.json` for the full structured list. Summary:

## Domain-level (36 of 40 briefed domains not researched — unchanged from RC1)
RC2 was an enrichment pass on the existing 4 domains, not an expansion. PHCs, CHCs, and Urban Health Centres remain BLOCKED; the remaining 26 domains remain QUEUED.

## Dataset-specific gaps (as of RC2)
- **Government hospitals**: TVVP/APVVP's master hospital-list pages still never surfaced in WebSearch snippets — the biggest structural gap, unresolved after 2 collection passes. 6 new gap-district hospitals were added, but several districts remain unrepresented. 6 bed-count/address conflicts remain disclosed rather than resolved (one, Kakinada, got MORE conflicting with additional sources rather than resolving).
- **Medical colleges**: 4 new colleges added (GMC Sangareddy, GMC Kamareddy, GMC Ramagundam, AIIMS Mangalagiri); ~13-15 more newer Telangana government colleges remain unrepresented. 11 rows still lack a confirmed official website; 46 lack a verifiable college-specific email; 32 lack a named department list; 24 lack scheme-coverage confirmation.
- **Regulatory bodies & schemes**: CDSCO's precise founding year and both states' NHM-unit establishment years remain genuinely unverifiable after 2 passes. CGHS beneficiary count (42-50 lakh range) still not fully resolved despite a narrower 47.44 lakh figure found in RC2.

## Field-level gaps
- New RC2 columns are unevenly filled: government_scheme_coverage_summary is deliberately conservative (only ~10-34 of ~55-58 rows per dataset) since empanelment claims require a specific confirming source, not a generic assumption.
- No row across any dataset has latitude/longitude, Google Maps links, ICU availability flag, dialysis availability flag, or working hours — still descoped as of RC2.

## Environment constraint
WebFetch to .gov.in/.ac.in/Wikipedia domains was re-confirmed blocked immediately before RC2 enrichment began, same as RC1. All data remains WebSearch-snippet-sourced with confidence capped at 88.
