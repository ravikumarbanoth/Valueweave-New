# Migration Guide — Platform v2.1 → v2.2

**Every data change in v2.2 is additive.** No column was renamed, reordered or removed;
no row was deleted; no existing cell value changed. A consumer written against v2.1
keeps working without modification.

That claim is tested, not asserted:
`tests/test_regression.py::BackwardCompatibilityRegressionTest` diffs all seven touched
datasets against `main` cell by cell and fails on any difference.

---

## 1. What changed at a glance

| Change | Kind | Action needed |
|---|---|---|
| `knowledge_engine/` recovered, 62 files | new code | none — it did not exist before |
| `package007_scheme_id`, `scheme_ownership` on 5 scheme datasets | new columns | none; adopt when convenient |
| `notes` on 5 Package001 datasets | new column | none |
| `pipeline_rationale` in `source_registry/sources.csv` | new column | none |
| `collector` / `parser` no longer `PENDING_IMPLEMENTATION` | value change in a derived artifact | re-read if you cached it |
| Graph check **G11** added | new validation | a build that violated it already had a problem |
| `api/`, `search/`, `stewardship/` | new modules | opt in |
| ADR-003 `OPEN` → `ACCEPTED`; ADR-006 → `RESOLVED` | governance | none |

---

## 2. Scheme ownership (ADR-003)

Five datasets gained two columns:

```
packages/Package002_Education/datasets/scholarships.csv
packages/Package003_Healthcare/datasets/government_health_insurance_schemes.csv
packages/Package004_Industries/datasets/msme_entrepreneurship_support_schemes.csv
packages/Package005_Agriculture/datasets/agriculture_schemes.csv
packages/Package006_Skills_and_Training/datasets/government_skill_schemes.csv
```

| Column | Values |
|---|---|
| `package007_scheme_id` | a Package007 `scheme_id`, or `PENDING_VERIFICATION` |
| `scheme_ownership` | `DEPRECATED_REFERENCE` \| `DOMAIN_CANONICAL` |

### If you read scheme data

Nothing breaks. But **prefer Package007 for scheme attributes** where a row says
`DEPRECATED_REFERENCE` — that is the point of the decision. The domain copy is retained
for compatibility and will drift as budgets change.

```python
import csv

canonical = {r["scheme_id"]: r for r in csv.DictReader(
    open("packages/Package007_Government_Schemes/datasets/government_schemes.csv"))}

for row in csv.DictReader(open("packages/Package005_Agriculture/datasets/agriculture_schemes.csv")):
    if row["scheme_ownership"] == "DEPRECATED_REFERENCE":
        row = {**row, **canonical[row["package007_scheme_id"]]}   # canonical wins
    ...
```

### If you write scheme data

New schemes go in Package007. A domain package adds one only when it is genuinely
outside Package007's cross-domain scope, and then it is `DOMAIN_CANONICAL` with the bare
sentinel in `package007_scheme_id`. **G11 fails the build otherwise.**

Regenerate the crosswalk after any scheme change:

```bash
python3 governance/ownership/build_scheme_crosswalk.py            # dry run
python3 governance/ownership/build_scheme_crosswalk.py --apply
python3 knowledge_graph/build_graph.py
python3 knowledge_graph/validate_graph.py
```

See [OWNERSHIP_FINAL.md](OWNERSHIP_FINAL.md).

---

## 3. The `notes` column on Package001

Package001_Geography was built before `notes` became the sixth mandatory provenance
column. Nothing noticed, because no consumer required all six — until the Knowledge
Engine was recovered. Its `ProvenanceRecord.to_csv_fields()` emits exactly six columns
and cannot write a record into a dataset with nowhere to put one of them
(compatibility check C4).

```bash
python3 migrations/v2_2_add_notes_column.py --check     # report only, exit 1 if pending
python3 migrations/v2_2_add_notes_column.py --apply     # idempotent
```

**The value is empty, and that is the honest value.** There is no note for these rows,
and inventing explanatory text to fill a column would be fabrication. A blank `notes`
cell is already accepted elsewhere — Package002 has 12, Package006 has 12.

---

## 4. Source registry: `collector` and `parser`

Before v2.2 all 605 source rows read `PENDING_IMPLEMENTATION`, because
`knowledge_engine/` held no tracked files and there was no module to name. Now each URL
routes to a real class by the payload it serves:

```
knowledge_engine.collectors.api_collector.APICollector
knowledge_engine.parsers.html_table_parser.HTMLTableParser
```

**Two things this does not mean.** Routing is a decision about which module *would* run;
no source has been collected by the engine, and `last_collection` remains the date a
human collected the data by hand. And a URL whose payload cannot be determined keeps
`PENDING_IMPLEMENTATION` — guessing a parser is worse than admitting we do not know.

Every assigned name is checked importable before it is written, and
`tests/test_knowledge_engine.py::SourceRegistryTest` imports each one.

If you cached `sources.csv`, re-read it. A new column, `pipeline_rationale`, explains
each routing decision.

---

## 5. Graph validation: check G11

The validator now runs 11 checks. G11 enforces ADR-003 mechanically and fails the build
when an entity type has more than one owner, a governance column is missing, a
`DEPRECATED_REFERENCE` points at a non-existent scheme, or a `DOMAIN_CANONICAL` row
carries an id where the sentinel belongs.

If your pipeline parses `validation_summary.json`, note two new keys:
`domain_scheme_rows_governed` and `domain_scheme_rows_deprecated_reference`.

---

## 6. New modules, all opt-in

```bash
python3 -m api                       # REST API — docs/API_REFERENCE.md
python3 -m search.cli "turmeric"     # search    — docs/SEARCH_GUIDE.md
python3 -m stewardship.cli status    # review    — docs/... (below)
```

None is imported by any existing module. Ignoring them changes nothing.

---

## 7. Stewardship: two vocabularies

`stewardship/` implements the seven-state record lifecycle from
`governance/DATA_STEWARDSHIP.md`. If you are integrating with it, the distinction that
matters most is that it is **not** the Knowledge Engine's `WorkflowState`:

| | `WorkflowState` (engine) | `lifecycle_state` (record) |
|---|---|---|
| Describes | one update *cycle* | one *row* |
| States | 11 | 7 |
| Lives in | `knowledge_engine/update_engine/states.py` | `stewardship/lifecycle.py`, graph check G8 |

The mapping is in `knowledge_engine/compatibility_report.json` and check C7 verifies it.

### The retroactive-review path

All 647 entities are `PUBLISHED` and none passed through `REVIEWED`, because no steward
existed when they were released. Under a strict forward-only rule that is a dead end —
a steward who reads a published record has nowhere to record it, and the platform can
never leave 0% verified.

v2.2 adds `PUBLISHED → REVIEWED`, gated: **refused the moment a record is
`VST-VERIFIED`**. It fills in a state that was skipped rather than undoing one that was
completed, which is why it is not a relaxation of the forward-only rule.

```bash
python3 -m stewardship.cli queue --limit 40
python3 -m stewardship.cli review vw:crop:turmeric --actor "name" \
    --evidence "checked against https://indianspices.com/ on 2026-07-26"
python3 -m stewardship.cli approve vw:crop:turmeric --actor "name"
python3 -m stewardship.cli apply            # dry run
python3 -m stewardship.cli apply --write    # writes verification_status
```

`review` and `approve` only append to `stewardship/review_ledger.csv`. `apply` is the
only command that touches a package, and it requires `--write`.

**The committed ledger is empty and must stay that way until real reviews happen.**
`tests/test_stewardship.py::RealLedgerTest` fails if anyone commits invented decisions.

---

## 8. Rollback

Nothing in v2.2 requires a rollback path for data, because nothing was overwritten. If
you need the pre-v2.2 view of a dataset:

```bash
git show <pre-v2.2-commit>:packages/Package005_Agriculture/datasets/agriculture_schemes.csv
```

To disable pipeline routing in the source registry without reverting code, set
`ASSIGN_PIPELINE = False` in `source_registry/build_source_registry.py` and rebuild;
both columns return to `PENDING_IMPLEMENTATION`.

---

## 9. Verifying the migration on your checkout

```bash
python3 migrations/v2_2_add_notes_column.py --check
python3 governance/ownership/build_scheme_crosswalk.py
python3 knowledge_engine/check_compatibility.py
python3 knowledge_graph/build_graph.py
python3 knowledge_graph/validate_graph.py
python3 tests/run_all.py
```

Expected: compatibility `COMPATIBLE 9/9`, graph `PASS` with 0 violations and one
pre-existing orphan warning, tests `248 PASS`.
