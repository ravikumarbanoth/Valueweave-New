# Codex Handoff — Package005_Agriculture v1.0.0

Written for whoever picks this package up next, human or agent. It records what exists, what was
deliberately left undone, and where the traps are.

## State

**Released, Stable v1.0.0.** 16 datasets, 388 records, validation clean (0 violations across 10
checks). Branch `claude/package005-agriculture-import`, merged to `main`.

## What to read first, in order

1. `README.md` — what the package is, layer structure, what it does not assert
2. `docs/METHODOLOGY.md` §2 — the no-fabrication rule and how it produced the sentinel pattern
3. `validation_report.md` — the two real defects the checks caught, and the confidence table
4. `schemas/schema_catalog.json` — canonical PK/FK reference, per-dataset limitations

## Rebuild

```bash
cd packages/Package005_Agriculture
python3 enrich_datasets.py     # crop_categories, crops, farm_machinery,
                               # agri_processing_opportunities, ai_precision_agriculture
python3 regen_mappings.py      # crop_soil_mapping, crop_climate_mapping, agri_business_mapping
python3 validate.py            # 10 checks; writes validation_summary.json; exit 0 = clean
python3 build_artifacts.py     # schema catalog, 16 metadata, registry, manifest, 16 reports
python3 build_docs.py          # DATA_DICTIONARY, IMPORT_GUIDE, validation_report
```

**Order matters.** `build_artifacts.py` and `build_docs.py` both read
`validation_summary.json`, so `validate.py` must run before them. Every count in the manifest,
registry, schema catalog, collection reports and docs is derived from the CSVs — nothing is
hand-maintained, which is why they cannot drift.

Datasets not covered by a generator (`soil_types`, `climate_zones`,
`farmer_producer_organizations`, `agriculture_training`, `agriculture_schemes`,
`crop_disease_management`, `market_linkages`, `export_opportunities`) are hand-authored and live
only as CSVs. Edit them directly, then re-run `validate.py`.

## Traps

**Renumbering `crops.csv` breaks three datasets.** `crop_id` values are positional
(`crop-001`…`crop-045`). Inserting a crop mid-list shifts every ID after it and silently
invalidates `crop_soil_mapping`, `crop_climate_mapping` and `agri_business_mapping`. This
already happened once during this release. **Append new crops at the end** (`crop-046`
onward), or regenerate all three mappings via `regen_mappings.py`. V8's denormalised-name check
will catch you either way, but appending avoids the work.

**The sentinel is load-bearing.** `PENDING_VERIFICATION` must be the *entire* cell value, never
embedded in prose. V5 enforces this. If you write a note explaining that a field is
unverified, do not use the literal token in that note — it broke once already.

**Do not fill the cost fields with estimates.** 84 of the 132 sentinel cells are equipment and
plant costs. They are empty because no official public figure exists, not because nobody got
round to it. Filling them with plausible numbers would be the single worst thing you could do
to this package. If you have DIC or MSME project profiles, cite them per row and raise
confidence accordingly.

**`avg_yield_tons_per_ha` is not cross-comparable.** Cotton is lint, turmeric dry, ginger fresh,
coconut sentinelled. Any dashboard that averages this column across crops is producing a
meaningless number.

## Where the gaps are, ranked

| # | Gap | Effort | Unblocks |
|---|---|---|---|
| 1 | **8 allied categories have no entity datasets** — livestock, poultry, dairy, fisheries, sericulture, apiculture, mushroom, forest produce exist in `crop_categories.csv` but nowhere else | High | The largest scope gap in v1.0.0 |
| 2 | **84 sentinelled cost cells** | Medium | Requires DIC / MSME project profile access |
| 3 | **13 sentinelled Package004 links** | Low | Blocked on Package004 adding rice milling, dal milling, jaggery, cold storage, essential oil, animal feed, vermicompost, cashew shelling |
| 4 | **No Package001 `dist_id` FK** | Medium | Requires district-level crop statistics; `crops.major_districts` is free text and sentinelled for 13 of 45 crops |
| 5 | **Package007 / Package008 FKs** | Low | Blocked on those packages releasing |
| 6 | **Zero rows are `VST-VERIFIED`** | High | Requires human data-steward review; machine validation confirms integrity, not factual accuracy |

## Environment constraint you will also hit

WebFetch to `.gov.in`, `.nic.in` and `.ac.in` is blocked by organizational egress policy. Every
row is attributed to the governing body but no primary page was read, which is why
`confidence_score` is capped at 85 package-wide (observed max 78). Same constraint applied to
Package004 and Package006 — this is environmental, not a data-collection failure.

If that policy changes, the highest-value re-collection targets are: scheme benefit amounts
(`agriculture_schemes`), export prices and volumes (`export_opportunities`), and institution
counts (`agriculture_training`, `market_linkages`). Those are the fields whose confidence is
currently limited by volatility rather than by absence of a source.

## Reconciliation owed to other packages

- **Package007_Government_Schemes** will overlap `agriculture_schemes.csv` (12 rows). Decide
  whether Package005 keeps its agriculture slice or defers entirely to Package007. Deferring is
  probably right; duplicating scheme data in two packages guarantees they diverge.
- **Package008_MSME** should join on `agri_processing_opportunities.csv` — that is the intended
  surface, and its `licenses_required` / `linked_scheme` columns were populated with that join
  in mind.
- **Package004_Industries** overlap is already handled correctly: Package005 points at
  Package004 for investment detail rather than duplicating it. Preserve that.

## Verification checklist before any future release

```bash
python3 validate.py                              # must exit 0
python3 -c "import json; s=json.load(open('validation_summary.json')); \
            assert s['violations']==0 and s['result']=='PASS'; print('clean')"
git status --short                               # nothing unexpected
```

Then confirm `package_manifest.json`, `registry/dataset_registry.csv` and
`validation_report.md` were regenerated (they carry record counts; a stale one is a silent lie
about the release).
