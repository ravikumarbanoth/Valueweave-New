# Integration Checklist — Package001_Geography v1.0.0-RC1
*For use by Codex (or any automated integration agent). Check items off in order — several depend on the prior step's success.*

- [ ] **Read `package_manifest.json`** — confirm package version (1.0.0-RC1), datasets included/blocked/queued, and import order before touching any data file.
- [ ] **Validate schema** — cross-check every CSV's actual header row against `schemas/schema_catalog.json`'s per-dataset field list; halt and flag if they've drifted out of sync.
- [ ] **Validate CSV** — confirm row counts match `package_manifest.json`'s stated counts exactly (state: 2, district: 61, revenue_division_telangana: 75, revenue_division_andhra_pradesh: 0, mandal: 0); confirm encoding is UTF-8; confirm no unescaped delimiters broke row structure.
- [ ] **Validate foreign keys** — for each child table, confirm every FK value resolves to an existing parent row per the table in `codex_handoff.md` §6, BEFORE inserting (not as a post-hoc cleanup pass).
- [ ] **Create tables** — in the exact order state → district → revenue_division → mandal, per `imports/import_sequence.json`, applying the recommended indexes from `schemas/schema_catalog.json`.
- [ ] **Import data** — load each CSV into its table, mapping `PENDING_VERIFICATION`/`PENDING_GEOCODING` sentinel strings to NULL (or your system's equivalent "known-unknown" marker) rather than literal text.
- [ ] **Build indexes** — confirm all `UNIQUE`/`INDEX` constraints from `schemas/schema_catalog.json` are actually active post-import, not just declared.
- [ ] **Generate APIs** — per `codex_handoff.md` §8; confirm `verification_status` and `confidence_score` are exposed on every endpoint response, not just internal columns.
- [ ] **Update search** — index `district_name`, `revenue_division_name`, and `*_ref` codes; explicitly exclude sentinel-value fields from the search index.
- [ ] **Register Knowledge Graph nodes** — `:State` (2), `:District` (61), `:RevenueDivision` (75) — only after the corresponding import step has succeeded; do NOT register `:Mandal` nodes (0 exist).
- [ ] **Register Knowledge Graph edges** — only the non-"planned" edges in `schemas/schema_catalog.json`; explicitly skip any edge marked `"status": "planned"`.
- [ ] **Update dataset registry** — write the actual post-import row counts, confidence scores, and any verification_status changes back to `registry/dataset_registry.csv` (or its target-environment equivalent table).
- [ ] **Generate import log** — a timestamped record of every step above, its result, and any validation failures encountered — store alongside `evidence/` per the archive convention already established in this package, so this import itself becomes auditable evidence for the next release.
- [ ] **Final check before declaring the package "integrated":** confirm zero rows were fabricated to fill `mandal.csv` or `revenue_division_andhra_pradesh.csv` — both should remain exactly as empty in the target system as they are in this release's CSVs, with `acquisition_backlog.json` as the tracked path to filling them later.
