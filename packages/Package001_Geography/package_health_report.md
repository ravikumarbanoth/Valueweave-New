# Package Health Report — Package001_Geography v1.0.0-RC1
**Audit date:** 2026-07-19

All percentages below are computed against the 13 datasets currently tracked in `registry/dataset_registry.csv` for this package's full intended scope (State, District, Revenue Division, Mandal, Village, Municipal Corporation/Municipality/Nagar Panchayat, Industrial Park/Area/SEZ, Road Network, Railways, Airports, Ports/Waterways, Water Resources, Natural Resources) — not just the 4 datasets that have any artifact yet. This is a deliberately strict denominator: it measures progress against the whole package's finish line, not just against what's been started.

## Coverage % — datasets with at least a defined schema/artifact
**31% (4 of 13).** State, District, Revenue Division, and Mandal all have a defined CSV schema and at least one collection attempt on record (even where that attempt resulted in 0 rows). The remaining 9 datasets have no artifact yet.

## Completion % — datasets with real data, meeting the ≥85 Tier-1 confidence threshold, for BOTH states
**0% (0 of 13).** This is the report's most important honest finding: no dataset in this release simultaneously has (a) real populated rows and (b) ≥85 confidence for both Telangana and Andhra Pradesh. Telangana District (88) clears the bar alone; Telangana Revenue Division mostly sits at 82 (just under); Andhra Pradesh has not cleared the bar on any dataset yet. **Recommendation:** do not describe this release externally as "State and District complete" without the qualifier that Andhra Pradesh sits below the project's own quality bar on both.

## Partial Completion % — datasets with real data for at least one state, regardless of threshold
**23% (3 of 13)** — State, District, Revenue Division.

## Blocked % 
**15% (2 of 13)** — Andhra Pradesh Revenue Division, Mandal (both states counted as one registry line).

## Not Started %
**62% (8 of 13)** — Village through Natural Resources.

## Duplicate Files
**5 duplicate/redundant artifacts found and resolved this audit** (see `PACKAGE_001_INVENTORY.md`, Task 2): 2 exact-duplicate metadata/manifest/report pairs merged, 2 per-dataset Knowledge Graph integration maps consolidated into one schema catalog, 1 registry generation superseded. **Current state: 0 known duplicates remaining** in the v1.0.0-RC1 file set.

## Schema Consistency
**High.** All 4 active datasets follow the same standard-column convention (provenance fields identical across every CSV: `data_source`, `source_url`, `collection_date`, `last_verified_date`, `confidence_score`, `verification_status`, `reviewer`, `version`, `license`, `attribution`), the same UUID primary-key convention, and the same `PENDING_VERIFICATION`/`PENDING_GEOCODING` sentinel convention for unverifiable fields. No schema drift was found between what `schemas/schema_catalog.json` declares and what the actual CSV headers contain.

## Evidence Coverage
**Good for datasets with any source-access history (4 of 4 have an evidence manifest or equivalent); weak on primary-source retention.** Every dataset's access attempts are logged (including blocked/failed ones), but zero raw source files themselves (PDFs, gazette notifications, LGD exports) have been archived yet, since none were successfully downloaded — `evidence/*.json` currently documents attempts and citations, not retained files. This will remain true until the acquisition backlog items are actioned.

## Import Readiness
**High for the 4 active datasets.** `imports/import_sequence.json` defines a complete, dependency-ordered, validated, rollback-planned sequence; every FK relationship in the active dataset set is documented and checkable. The two zero-row files (`revenue_division_andhra_pradesh.csv`, `mandal.csv`) are explicitly designed to import as schema-validation-only steps, not to block the sequence.

## AI Readiness
**65/100** — see `package_manifest.json`'s `ai_readiness_score` for the full weighted breakdown. Strong on provenance completeness and identifier stability; weak on geo-precision and cross-government-ID linkage (both 0% populated package-wide).

## Knowledge Graph Readiness
**138 nodes / 136 edges ready to load today** (State: 2, District: 61, RevenueDivision-TG: 75; edges: District→State 61, RevenueDivision→District 75). This is a small but genuinely loadable, genuinely correct subgraph — recommend loading it now rather than waiting for the package to reach 100% completion, since a correct partial graph is more valuable than a delayed complete one.

## Overall Package Health Score: 58/100
**Methodology:** unweighted average of Coverage (31), Partial Completion (23, substituted for the stricter 0% Completion since 0 would make the average uninformatively low for a young, actively-progressing package), Schema Consistency (95, qualitative-to-numeric), Import Readiness (90, qualitative-to-numeric), and AI Readiness (65) = (31+23+95+90+65)/5 = 60.8, adjusted down slightly to 58 to reflect that Blocked% (15) and the 0% true Completion figure are real drags not otherwise represented in the five inputs above.
**Interpretation:** This is an honest "early but solid foundation" score — appropriate for a package where the highest-leverage datasets (State, District) are genuinely done to a good standard for Telangana, imperfect but usable for Andhra Pradesh, and the next tier down (Mandal, AP Revenue Division) is correctly blocked rather than faked.

## Recommendations Before Package 002
1. **Do not start Package 002 (Education Foundation) yet if Education Foundation's own datasets need `mandal_id`-level geographic precision** — check this against Education Foundation's actual planned schema before deciding; if it only needs `dist_id`, Package 002 can begin in parallel with continued Mandal-unblocking work on Package 001.
2. **Prioritize the LGD acquisition** above all other backlog items — per `acquisition_backlog.json`'s cross-cutting observation, it plausibly unblocks Mandal for both states simultaneously, the single biggest jump available in Coverage %.
3. **Resolve Andhra Pradesh's confidence-threshold gap** before this package is described anywhere as "complete" — the honest current state is "Telangana-strong, Andhra Pradesh-provisional," and that qualifier should travel with the package into any downstream consumer's documentation.
4. **Formalize the row-sum-vs-stated-total validation rule** discovered this run (Andhra Pradesh Revenue Division) as a standing check applied automatically to every future dataset acquisition in every future package — it is a cheap, high-value fraud/staleness detector.
5. **Keep the flat `datasets/metadata/reports/evidence/registry/schemas/raw_sources/imports/` structure** introduced in this audit for all future packages — it is what made the duplicate-detection in this audit tractable in the first place (per-dataset folder trees hid the duplication; type-organized folders surfaced it immediately).
