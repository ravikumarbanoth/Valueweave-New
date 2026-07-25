# Collection Report: market_channels.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/market_channels.csv`
**Layer**: 7 - Market Access
**Collection date**: 2026-07-25
**Source tier**: Tier 1-2 (Ministry of MSME; GeM; DPIIT/ONDC; Ministry of Commerce)

## Purpose

Sales channels with buyer type, entry barrier, digital intensity and payment cycle.

## Methodology

Eleven channels covering the physical, digital and hybrid routes named in the brief, classified by buyer_type (B2C, B2B, B2G) and entry_barrier. The brief listed platforms; this dataset adds the structural attributes that determine whether a given MSME can actually use them.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 11 |
| Columns | 15 |
| Primary key | `channel_id` |
| Primary key uniqueness | PASS (11/11 distinct) |
| Total cells | 165 |
| Bare `PENDING_VERIFICATION` cells | 19 (11.52%) |
| Blank cells | 0 |
| Confidence range | 62-74 (ceiling 85) |
| Confidence average | 68.5 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `channel_id`
- `channel_name`
- `channel_type`
- `buyer_type`
- `description`
- `typical_payment_cycle`
- `entry_barrier`
- `digital_intensity`
- `official_portal`
- `data_source` — Authoritative body the row is attributed to
- `source_url` — Public URL for that body
- `collection_date` — Collection date; uniform 2026-07-25 across the package
- `confidence_score` — Integer 0-100, capped at the 85 package policy ceiling
- `verification_status` — VST-NEEDS_REVIEW pending human data-steward sign-off
- `notes` — Caveats, qualifications and sourcing remarks

## Foreign keys

- None (reference dataset; no outbound foreign keys)

## Sentinel usage

| Column | Sentinel rows |
|---|---|
| `typical_payment_cycle` | 11 of 11 |
| `official_portal` | 8 of 11 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

typical_payment_cycle is the bare sentinel on every row: payment terms are negotiated per buyer and vary by orders of magnitude between B2C marketplace settlement and government tender payment. Marketplace rows sentinel official_portal because platform seller-onboarding URLs change; the platform name is the durable identifier. Commission structures are described qualitatively in notes, never as percentages.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/market_channels.csv`
- Metadata: `packages/Package008_MSME/metadata/market_channels.metadata.json`
- This report: `packages/Package008_MSME/reports/market_channels.collection_report.md`
