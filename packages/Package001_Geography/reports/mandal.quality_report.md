# Quality Report — `mandal` Dataset

## Data Quality Tier Assignment (per the Data Collection & Governance Framework, Part 3.3)
**Tier assignment: N/A — no data rows exist to score.** The dataset would be Tier 1 (Profile P1, Government Registry & Statistical Source) once populated, carrying the framework's ≥85 acceptance threshold.

## Component Scores
| Score | Value | Basis |
|---|---|---|
| Confidence | N/A | No rows collected |
| Completeness | 0% (data), 100% (schema) | Schema fully specified; zero data rows populated |
| Freshness | N/A | No rows to date-check |
| Accuracy | N/A | No rows to cross-validate |
| **Overall** | **N/A (schema-only deliverable)** | See Collection Report §8 for the schema-design confidence score (95/100) |

## Validation Rules Applied to the Schema Itself
- Every column has a defined data type and mandatory/optional flag (Section: Data Dictionary).
- `mandal_id` (PK), `dist_id` (FK → `district.dist_id`) — referential integrity rule pre-defined and ready to enforce the moment real rows are supplied.
- `mandal_ref` follows the ValueWeave Coding Standard (`{STATE}-{DISTRICT}-{MANDAL_MNEMONIC}`, e.g. `TG-MDK-NKD` for a Narayankhed-pattern mandal in Medak district) — format rule defined, not yet applied to real values.
- Lookup validation: none required — Mandal does not consume any of the 61 lookup tables directly.

## Duplicate Detection Method (pre-defined, ready for use)
Composite uniqueness on (`district_id`, `mandal_name`) — mandal names can repeat across different districts (e.g., multiple "Kothagudem"-pattern names exist across Telangana), so district-scoped uniqueness, not global name uniqueness, is the correct rule. Fuzzy-matching (Jaro-Winkler similarity) recommended as a secondary check once real rows exist, given the same mandal is sometimes rendered with different transliteration/spacing across sources (e.g., "Shankarampet_A" vs. "Shankarampet (A)").

## Missing Data Report
100% of intended rows (~1,290–1,300 across both states) are missing, for the reasons documented in the Collection Report. No field-level "missing data" analysis applies since no rows exist yet.

## Recommended Acceptance Threshold (once populated)
≥85 (Tier 1), consistent with State and District — Mandal sits in the same Profile P1/Tier-1 classification since it is sourced from the same class of official registries (LGD, Census, State Statistical Abstract).
