# Collection Report: license_compliance.csv

**Package**: Package008_MSME v1.0.0
**Dataset**: `datasets/license_compliance.csv`
**Layer**: 4 - Compliance
**Collection date**: 2026-07-25
**Source tier**: Tier 1 (issuing authorities: Ministry of MSME, GSTN, FSSAI, CPCB, BIS, CDSCO, DGFT)

## Purpose

Licences, registrations and clearances with issuing authority, jurisdiction, applicability and renewal cycle.

## Methodology

Fourteen items covering the registration, tax, sector-licence, establishment, environmental, safety, product-certification and trade classes. The brief's twelve were extended by two that materially gate MSME operation: Shops and Establishments registration (which applies to most service and trading businesses) and EPR Authorisation (which is what creates the recycler market). applicability states who actually needs each one, which matters more than the licence name.

Collection mode for this package was knowledge synthesis from documented public sources.
Direct WebFetch to `.gov.in` / `.nic.in` / `.ac.in` domains is blocked by this session's
organizational egress policy, so no row rests on a primary-source page read. Every row names
the ministry, authority or association that governs the fact in `data_source`, and
`confidence_score` is capped at 85 to record that limitation.

## Fill rates

| Metric | Value |
|---|---|
| Records | 14 |
| Columns | 16 |
| Primary key | `license_id` |
| Primary key uniqueness | PASS (14/14 distinct) |
| Total cells | 224 |
| Bare `PENDING_VERIFICATION` cells | 6 (2.68%) |
| Blank cells | 0 |
| Confidence range | 66-78 (ceiling 85) |
| Confidence average | 71.4 |
| Verification status | `VST-NEEDS_REVIEW` (all rows) |
| Collection date | `2026-07-25` (all rows) |

## Columns

- `license_id`
- `license_name`
- `license_type`
- `issuing_authority`
- `jurisdiction`
- `applicability`
- `is_mandatory_when_applicable`
- `renewal_cycle`
- `online_application`
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
| `official_portal` | 6 of 14 |

Each sentinel above means no public source was found for that specific fact, or that the upstream package holds no counterpart record. No estimate was substituted.

## Known limitations

State-administered licences (Factory Licence, Trade Licence, Fire NOC, Electrical Inspectorate, Shops and Establishments) sentinel official_portal because there is no single national portal; the route differs by state and often by local body. Thresholds are described qualitatively because they are revised by notification. ISO certification is included but is not a government licence -- the ISO row records that distinction explicitly.

## Validation

This dataset passes all thirteen package checks, including V13 which mechanically enforces
the non-duplication rule from the package brief. Re-run with `python3 validate.py` from the
package root.

## Files

- Dataset: `packages/Package008_MSME/datasets/license_compliance.csv`
- Metadata: `packages/Package008_MSME/metadata/license_compliance.metadata.json`
- This report: `packages/Package008_MSME/reports/license_compliance.collection_report.md`
