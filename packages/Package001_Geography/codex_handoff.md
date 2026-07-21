# Codex Handoff — Package001_Geography v1.0.0-RC1
*Written specifically for an AI coding agent integrating this package into ValueWeave. Read this before touching any file.*

## 1. What This Package Is
Four CSVs (`datasets/state.csv`, `district.csv`, `revenue_division_telangana.csv` + `revenue_division_andhra_pradesh.csv`, `mandal.csv`) representing India's administrative geography for two states, plus everything needed to import, validate, and graph-load them without asking a human for clarification on anything covered below. Two of these CSVs currently contain zero data rows by design (`revenue_division_andhra_pradesh.csv`, `mandal.csv`) — this is documented, expected, and not an error in your pipeline if the row count comes back as 0 for those two files specifically.

## 2. Package Structure (recap — see README.md for the full tree)
Read files in this order: `package_manifest.json` → `schemas/schema_catalog.json` → `imports/import_sequence.json` → the individual CSVs in `datasets/`. Everything else (`reports/`, `evidence/`, `raw_sources/`) is human-facing audit trail — useful for provenance queries later, not required to complete the import itself.

## 3. Datasets & Schemas
Full column-level definitions live in `reports/*.data_dictionary.md` (human-readable) and are summarized machine-readably in `schemas/schema_catalog.json` (PK/FK/relationships/indexes/validation rules per dataset). Do not infer a schema from the CSV headers alone — several columns carry sentinel string values (`PENDING_VERIFICATION`, `PENDING_GEOCODING`) that must be handled as NULL-equivalent in your target schema, not as literal text data.

## 4. Import Order
Exactly as specified in `imports/import_sequence.json`: **state → district → revenue_division → mandal**. This is a hard dependency chain — every table's primary key is referenced by the next table's foreign key. Do not parallelize these four imports; run them sequentially and validate each step's success before proceeding to the next.

## 5. Database Creation Order
1. Create `state` table per `schemas/schema_catalog.json`'s `state` entry — no FKs to worry about, this is the root.
2. Create `district` table with `st_id` as a FK constraint against `state.st_id`.
3. Create `revenue_division` table with `dist_ref`/`dist_id` as a FK constraint against `district`.
4. Create `mandal` table with `dist_id` as a FK constraint against `district`, plus a `revenue_division_name` free-text column (not yet a formal FK — see schema_catalog.json's note on this planned upgrade).
5. Apply the recommended indexes listed per-dataset in `schema_catalog.json` (mostly `UNIQUE` on each dataset's `_ref` code column, plus `INDEX` on FK columns) — these are not optional performance tuning, they are how the coding-standard's uniqueness guarantee (Part 0.3 of the original Entity & Relationship Model) gets enforced at the database level.

## 6. Foreign Keys
| Child | FK Column | Parent | Parent Column |
|---|---|---|---|
| district | st_id | state | st_id |
| revenue_division | dist_ref | district | dist_ref |
| mandal | dist_id | district | dist_id |

No other FK relationships exist within this package. Do not create a `revenue_division_id` FK on `mandal` yet — that column doesn't exist in the current `mandal.csv` schema (it's a planned future addition, tracked in `acquisition_backlog.json` and `schemas/schema_catalog.json`'s relationships section, not something to invent now).

## 7. Search Indexing
Recommend indexing on: `district_name`, `revenue_division_name` (once populated for AP), and each dataset's `*_ref` code — these are the fields a human user is most likely to type into a search box (e.g., "Medak," "Sangareddy revenue division"). Do not index `PENDING_VERIFICATION`/`PENDING_GEOCODING` sentinel values as searchable content — filter them out of the search index build, or a user searching for an actual place name will get noise matches against every unpopulated field.

## 8. API Generation
Recommended REST/GraphQL surface for this package, mirroring the table structure exactly:
- `GET /states`, `GET /states/{st_ref}`
- `GET /districts`, `GET /districts/{dist_ref}`, `GET /states/{st_ref}/districts`
- `GET /revenue-divisions`, `GET /districts/{dist_ref}/revenue-divisions`
- `GET /mandals` (will return an empty array in this release — do not treat this as an API bug; surface it with a clear "data pending" indicator rather than a generic empty-state)
Every response should include the record's `verification_status` and `confidence_score` fields prominently, not just bury them in a metadata blob — downstream consumers (including the AI Intelligence Layer) need to make trust-weighted decisions per record, per the framework already established for this project.

## 9. Admin UI Generation
Recommend a simple table-per-dataset admin view with: (a) a `verification_status` filter defaulting to showing `VST-NEEDS_REVIEW` records first (since that's this whole release's actual state — nothing here is `VST-VERIFIED` yet), (b) an inline "promote to verified" action restricted to whatever role your auth system maps to "Reviewer"/"Approver" per the Data Governance Framework's role definitions, and (c) a visible badge on any row containing a `PENDING_VERIFICATION`/`PENDING_GEOCODING` sentinel, so a human reviewer can immediately see which fields still need sourcing without reading every column.

## 10. Knowledge Graph Integration
Node types: `:State`, `:District`, `:RevenueDivision`, `:Mandal` (the last with 0 instances in this release). Edge types and exact Cypher-equivalent shapes are fully specified in `schemas/schema_catalog.json`'s `relationships` array per dataset — use that file as the single source, do not re-derive edges from the CSV column names, since a couple of the intended edges (e.g., `Mandal -[:PART_OF_REVENUE_DIVISION]-> RevenueDivision`) are marked `"status": "planned"` and should NOT be created yet (the underlying data doesn't support them — `mandal.csv` has 0 rows). Only create edges for relationships marked without a "planned" status flag.

## 11. What NOT To Do
- Do not populate `mandal.csv` or `revenue_division_andhra_pradesh.csv` with placeholder/estimated rows to "complete" the import — their emptiness is intentional and documented; see `acquisition_backlog.json` for the correct unblock path.
- Do not auto-promote any row's `verification_status` from `VST-NEEDS_REVIEW` to `VST-VERIFIED` as part of the import process — that is a human governance action.
- Do not treat `PENDING_VERIFICATION`/`PENDING_GEOCODING` as data quality bugs to silently fix with a default value — they are the correct, honest representation of "not yet known."

## 12. Minimal-Instruction Success Criteria
You should be able to complete this package's integration using only: `package_manifest.json`, `schemas/schema_catalog.json`, `imports/import_sequence.json`, and the four CSVs in `datasets/`. If you find yourself needing to open a `reports/*.md` file to figure out a schema or FK relationship, that's a signal the machine-readable files above are incomplete — flag it, don't guess from the prose.
