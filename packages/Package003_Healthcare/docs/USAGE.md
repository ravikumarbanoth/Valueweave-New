# Package003_Healthcare v1.0.0-RC1 — Usage Guide

## What's in this package

Four CSV datasets under `datasets/`, each independently loadable (no inter-dataset foreign keys in
this release, though two datasets carry free-text cross-references to each other — see below):

| File | Rows | Covers |
|---|---|---|
| `medical_regulatory_bodies_and_health_missions.csv` | 23 | National + Telangana + Andhra Pradesh medical regulators, standards bodies, and health missions |
| `medical_colleges_telangana_andhra_pradesh.csv` | 54 | Government + private MBBS colleges in Telangana & AP |
| `government_hospitals_telangana_andhra_pradesh.csv` | 49 | District/Area/Teaching Hospitals run by the Telangana & AP state governments |
| `government_health_insurance_schemes.csv` | 8 | Central + Telangana/AP health insurance schemes |

## Before treating any row as fact-checked

Every row's `verification_status` is `VST-NEEDS_REVIEW`. Nothing in this release has been promoted to
`VST-VERIFIED`. See `docs/METHODOLOGY.md` for why, and treat `confidence_score` (capped at 88) as a
relative signal, not an absolute guarantee.

## Cross-references between datasets (not enforced FKs)

`medical_colleges_telangana_andhra_pradesh.attached_teaching_hospital` and
`government_hospitals_telangana_andhra_pradesh.medical_college_affiliation` refer to each other by
name, but these were collected independently and are **not** guaranteed to match exactly (e.g. minor
naming variants). Do not treat them as a verified relational join — do a name-match with manual
review if you need to link them.

## Fields you should expect to be incomplete

- `bed_capacity` and `contact_number` (government hospitals): PENDING_VERIFICATION for many rows;
  where sources disagreed on bed counts, the conflict is recorded in `notes` rather than silently
  resolved.
- `mbbs_seats` (medical colleges): PENDING_VERIFICATION for most rows — current-year intake figures
  weren't independently confirmable this session.
- `emergency_services` (government hospitals): only "Yes" where a specific confirming source was
  found; otherwise PENDING_VERIFICATION — do not assume all hospitals in this dataset have confirmed
  emergency services.

## Where to look for provenance

- `metadata/*.metadata.json` — per-dataset stats, confidence calibration, collection method.
- `evidence/*.evidence_manifest.json` — full cited-source list + the WebFetch-block explanation.
- `raw_sources/*.source_inventory.md` — human-readable source list per dataset.
- `reports/*.collection_report.md` — full research methodology, conflicts found/resolved, exclusions.

## What's NOT in this package yet

See `acquisition_backlog.json` and `registry/dataset_registry.csv` for the other 36 healthcare
domains (PHCs, CHCs, specialty hospitals, blood banks, ambulance services, health programmes, etc.)
and all non-TG/AP states — each is marked `BLOCKED` or `QUEUED` with a specific reason and unblock
path.
