# Package002_Education v1.0.0 — Source Analysis

## Collection Method

Every fact in this release was collected via the WebSearch tool. Direct WebFetch to primary .gov.in / .ac.in / .edu.in / Wikipedia pages was blocked throughout the collection session by this environment's organizational egress policy (confirmed HTTP 403 policy denial via the proxy status endpoint, not a retriable error). No page was directly fetched and re-read for any dataset in this release; all facts are search-snippet-sourced and cited by URL.

## Distinct Sources Cited Per Dataset

| Dataset | Distinct Source URLs | Total Rows |
|---|---|---|
| education_boards_regulatory_bodies | 21 | 21 |
| universities_telangana_andhra_pradesh | 61 | 61 |
| entrance_exams | 28 | 28 |
| scholarships | 24 | 25 |

**Total distinct source URLs across the package: 134**

Full per-source listings are in `raw_sources/*.source_inventory.md`; full evidence manifests (including the WebFetch-block note) are in `evidence/*.evidence_manifest.json`.
