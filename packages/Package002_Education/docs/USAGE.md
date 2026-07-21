# Package002_Education v1.0.0 — Usage Guide

## What's in this package

Four CSV datasets under `datasets/`, each independently loadable (no inter-dataset foreign keys in
this release):

| File | Rows | Covers |
|---|---|---|
| `education_boards_regulatory_bodies.csv` | 21 | National + Telangana + Andhra Pradesh education boards/regulators |
| `universities_telangana_andhra_pradesh.csv` | 66 | State/central/deemed/private/INI universities in Telangana & AP (as of RC2: +5 rows, +3 columns vs RC1) |
| `entrance_exams.csv` | 29 | National + Telangana/AP entrance exams (as of RC2: +1 row vs RC1) |
| `scholarships.csv` | 25 | Central + Telangana/AP scholarship schemes |

RC2 added `ownership`, `contact_details`, and `student_services_summary` columns to the universities
dataset. Only `ownership` is fully populated (66/66); the other two are populated for 5 flagship
universities only — see `reports/rc1_vs_rc2_comparison.md`.

## Before treating any row as fact-checked

Every row's `verification_status` is `VST-NEEDS_REVIEW`. Nothing in this release has been promoted to
`VST-VERIFIED`. See `docs/METHODOLOGY.md` for why (this session could not directly fetch primary
source pages), and treat `confidence_score` as a relative signal, not an absolute guarantee.

## Fields you should expect to be incomplete

- `universities_telangana_andhra_pradesh.csv`: `vice_chancellor` is `PENDING_VERIFICATION` for all
  61 rows by design (VC appointments change frequently; not systematically searched). `naac_grade`
  and `nirf_rank` are populated only where a clearly-dated source was found.
- Any field showing the literal string `PENDING_VERIFICATION` means: searched for, not found with
  sufficient confidence — never a blank left by omission.

## Where to look for provenance

- `metadata/*.metadata.json` — per-dataset stats, confidence calibration notes, collection method.
- `evidence/*.evidence_manifest.json` — full list of cited sources + the WebFetch-block explanation.
- `raw_sources/*.source_inventory.md` — human-readable source list per dataset.
- `reports/*.collection_report.md` — full research methodology, conflicts found/resolved, and
  exclusions, per dataset.

## What's NOT in this package yet

See `acquisition_backlog.json` and `registry/dataset_registry.csv` for the full list of the other 36
education domains (Schools, Colleges, ITIs, MOOCs, etc.) and all non-TG/AP states — each is marked
`BLOCKED` or `QUEUED` with a specific reason and unblock path, not silently missing.
