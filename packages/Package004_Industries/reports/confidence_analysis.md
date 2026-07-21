# Package004_Industries_and_Livelihoods v1.0.0-RC1 — Confidence Analysis

Confidence scores in this release reflect two source tiers: rows traced to a specific government DIC/MSME/PMFME/KVIC project-profile document or an equivalent authoritative source score 70-85; rows where only portal/blog estimates were found (with no government backing) are capped at 58-65 even where the qualitative description is informative. No row exceeds 85 since no direct page fetch was possible this session (WebFetch to .gov.in/.ac.in was blocked, re-confirmed live before collection began).

| Dataset | Min | Max | Average |
|---|---|---|---|
| msme_entrepreneurship_support_schemes | 70 | 82 | 77.5 |
| food_agro_processing_micro_enterprises | 48 | 78 | 60.2 |
| construction_skilled_trade_services | 58 | 82 | 69.7 |
| digital_technology_livelihoods | 65 | 78 | 72.3 |
| china_inspired_adapted_opportunities | 60 | 80 | 70.0 |

## Interpretation

No row in this package should be treated as `VST-VERIFIED` — every row starts at `VST-NEEDS_REVIEW`. The food/agro-processing dataset has the lowest average confidence (60.2) because most of its investment-range claims could only be portal-sourced rather than traced to a government project profile — this is disclosed, not hidden.
