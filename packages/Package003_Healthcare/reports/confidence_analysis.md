# Package003_Healthcare v1.0.0-RC1 — Confidence Analysis

All confidence scores in this release were capped at 88 (no row claims a 90+ 'direct official fetch' score), because WebFetch to .gov.in/.ac.in/Wikipedia domains was blocked throughout the collection session (confirmed via live re-test immediately before collection began) — see docs/METHODOLOGY.md.

| Dataset | Min | Max | Average |
|---|---|---|---|
| medical_regulatory_bodies_and_health_missions | 80 | 85 | 82.3 |
| medical_colleges_telangana_andhra_pradesh | 73 | 88 | 84.0 |
| government_hospitals_telangana_andhra_pradesh | 78 | 85 | 82.0 |
| government_health_insurance_schemes | 80 | 85 | 83.1 |

## Interpretation

No row in this package carries a confidence score above 88, and no row should be treated as `VST-VERIFIED` — every row starts at `VST-NEEDS_REVIEW` per package policy, and promotion to verified is a governance action, not an automatic result of collection.
