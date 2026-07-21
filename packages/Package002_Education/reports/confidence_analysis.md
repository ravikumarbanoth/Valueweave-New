# Package002_Education v1.0.0 — Confidence Analysis

All confidence scores in this release were capped below the 85-95 'direct official source' band used in Package001_Geography, because WebFetch (direct page retrieval) was unavailable this session — see `source_analysis.md`. Scores instead reflect WebSearch-snippet corroboration strength.

| Dataset | Min | Max | Average |
|---|---|---|---|
| education_boards_regulatory_bodies | 58 | 85 | 74.6 |
| universities_telangana_andhra_pradesh | 58 | 75 | 68.9 |
| entrance_exams | 72 | 92 | 84.6 |
| scholarships | 60 | 80 | 72.0 |

## Interpretation

No row in this package carries a confidence score above 92, and no row should be treated as `VST-VERIFIED` — every row starts at `VST-NEEDS_REVIEW` per package policy, and promotion to verified is a governance action (Data Steward + Reviewer sign-off against a directly-fetched primary source), not an automatic result of collection.
