# Package002_Education v1.0.0 — Confidence Analysis

RC2 raised confidence scores modestly across most previously-collected rows via stronger multi-source corroboration (max +10/row for universities, +8/row for boards/exams/scholarships), capped at 82 (universities) / 88 (others) — still below the 85-95 'direct official source' band, since WebFetch remained unavailable.

| Dataset | Min | Max | Average | RC1 Average |
|---|---|---|---|---|
| education_boards_regulatory_bodies | 63 | 88 | 79.1 | 74.6 |
| universities_telangana_andhra_pradesh | 58 | 82 | 74.8 | 68.9 |
| entrance_exams | 78 | 92 | 85.0 | 84.6 |
| scholarships | 60 | 88 | 76.8 | 72.0 |

## Interpretation

No row in this package carries a confidence score above 92 (entrance_exams' pre-existing ceiling), and no row should be treated as `VST-VERIFIED` — every row remains `VST-NEEDS_REVIEW`.
