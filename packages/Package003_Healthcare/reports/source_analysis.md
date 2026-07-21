# Package003_Healthcare v1.0.0-RC1 — Source Analysis

## Collection Method

Every fact in this release was collected via the WebSearch tool. Direct WebFetch to primary .gov.in / .ac.in / .edu.in / Wikipedia pages was blocked throughout the collection session (confirmed HTTP 403 policy denial, re-tested live before collection began). No page was directly fetched and re-read for any dataset in this release; all facts are search-snippet-sourced and cited by URL.

## Distinct Sources Cited Per Dataset

| Dataset | Distinct Source URLs | Total Rows |
|---|---|---|
| medical_regulatory_bodies_and_health_missions | 23 | 23 |
| medical_colleges_telangana_andhra_pradesh | 54 | 54 |
| government_hospitals_telangana_andhra_pradesh | 43 | 49 |
| government_health_insurance_schemes | 8 | 8 |

**Total distinct source URLs across the package: 128**

Full per-source listings are in `raw_sources/*.source_inventory.md`; full evidence manifests (including the WebFetch-block note) are in `evidence/*.evidence_manifest.json`.
