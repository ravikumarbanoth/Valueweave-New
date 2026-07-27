# Compiler Architecture

**Workstream 3** · Target design for `knowledge_graph/build_graph.py`

**Design document. The refactor is specified here and has not been executed** — §7
explains the acceptance test any implementation must pass first.

---

## 0. What the refactor must and must not change

| Must not change | Why |
|---|---|
| **Graph output** | A rebuild must produce byte-identical `entities.csv` and `relationships.csv` modulo `BUILD_DATE`. This is the acceptance test |
| `vw:<type_slug>:<name_slug>` | Ids are referenced by the crosswalks, the sync manifest and the frontend |
| Entity dedup on `(type, slug)` | Why there are 0 duplicate entities |
| Edge dedup on `(from, type, to)` | Why there are 0 duplicate edges |
| Closed type sets aborting the build | Why every edge type is meaningful |
| `PENDING_VERIFICATION` treated as absent | The platform's core discipline |

| Must change | Why |
|---|---|
| **Hardcoded `read()` calls** | Adding a dataset means editing 839 procedural lines |
| **Import-time execution** | No builder can be unit-tested |
| **No coverage metric** | 38 skipped datasets, no signal anywhere |
| **No attribute channel** | 19 datasets structurally unreachable |
| **Four bypassed guards** | ~44 join failures recorded nowhere |

**The current design is not bad code.** Its invariants are strong and they hold by
construction. It is a *script* being asked to behave like a *compiler*, and the gap is
structural rather than qualitative.

---

## 1. Target structure

```
knowledge_graph/
  build_graph.py            entry point — orchestration only, ~80 lines
  compiler/
    __init__.py
    registry.py             DATASETS: the single source of truth
    model.py                Registry, edge(), slug(), conf(), vst()
    entities.py             entity builders
    relationships.py        relationship builders
    attributes.py           NEW — the third channel
    validation.py           pre- and post-conditions
    diagnostics.py          coverage, unused FKs, unresolved endpoints
    metrics.py              structured output
```

Six modules. **No new dependency, no new concept** — every one of these already exists
inside the 839 lines, unnamed.

---

## 2. Dataset Registry — the central change

Today a dataset is a `read()` call somewhere in the body. It becomes a table row:

```python
# compiler/registry.py

@dataclass(frozen=True)
class Dataset:
    package: str
    filename: str
    channel: Channel                 # ENTITY | RELATIONSHIP | ATTRIBUTE | NONE
    builder: str                     # function name in entities/relationships/attributes
    required: bool = True            # False => maybe(), tolerate absence
    foreign_keys: tuple = ()         # (column, target_type) — checked, reported
    note: str = ""                   # why NONE, when NONE

DATASETS = (
    Dataset("Package007_Government_Schemes", "district_scheme_mapping.csv",
            Channel.RELATIONSHIP, "scheme_available_in_district",
            foreign_keys=(("scheme_id", "GovernmentScheme"),
                          ("package001_dist_id", "District"))),

    Dataset("Package007_Government_Schemes", "eligibility_criteria.csv",
            Channel.ATTRIBUTE, "scheme_eligibility",
            foreign_keys=(("scheme_id", "GovernmentScheme"),)),

    Dataset("Package001_Geography", "mandal.csv",
            Channel.NONE, "", required=False,
            note="header-only; nothing to consume until collected"),
    ...
)
```

**Three properties this buys.**

**Coverage becomes computable.** `len(DATASETS)` against the files on disk *is* the
coverage metric. No grep, no parsing, no drift.

**`Channel.NONE` is explicit.** A dataset that contributes nothing must say so **and say
why**. Today, skipping a dataset and forgetting one are indistinguishable — that is how
38 went unnoticed.

**Foreign keys become declared.** The registry knows `district_scheme_mapping.scheme_id`
should resolve to a `GovernmentScheme`, so the compiler can report the join rate per
dataset instead of leaving it to be discovered by audit.

---

## 3. Entity and relationship builders

A builder is a pure function over rows. It receives the registry and returns
contributions; it does not touch global state.

```python
# compiler/entities.py
def crops(rows, ctx) -> list[EntityDecl]:
    return [EntityDecl(type="Crop", name=r["crop_name"],
                       package="Package005_Agriculture", local_id=r["crop_id"],
                       confidence=conf(r), verification=vst(r),
                       aliases=split(r.get("also_known_as")))
            for r in rows]

# compiler/relationships.py
def scheme_available_in_district(rows, ctx) -> list[EdgeDecl]:
    out = []
    for r in rows:
        out.append(EdgeDecl(
            type="AVAILABLE_IN",
            frm=ctx.lookup("GovernmentScheme", ctx.scheme_name(r["scheme_id"])),
            to=ctx.lookup("District", r["district_name"]),
            confidence=conf(r), row_id=r["mapping_id"],
            note=r.get("district_specific_variation", "")))
    return out
```

**`EdgeDecl` is emitted even when an endpoint is `None`.** The pipeline — not the builder
— decides whether that becomes an edge or an `UNRESOLVED` row.

> **This is the fix for the four bypassed guards, made structural.**
>
> Today a builder can pre-check with `if ... and E(...)` and the failure disappears. In
> the target design a builder **cannot** suppress a failure, because it does not perform
> the resolution — it declares an intent, and the pipeline resolves it. The bug becomes
> unexpressible rather than merely fixed.

Builders are pure, so each is unit-testable against a handful of rows without building
the graph.

---

## 4. The attribute channel — new

Nineteen datasets carry per-entity detail and no relationship: eligibility, benefits,
application steps, required documents, investment, licence and compliance, automation
risk, skill categories. **The compiler has no way to attach any of it**, which is the
architectural reason 77/77 is currently unreachable.

```python
@dataclass(frozen=True)
class AttributeDecl:
    entity_type: str
    entity_name: str
    key: str
    value: str
    package: str
    dataset: str
    row_id: str
```

Output: `knowledge_graph/entities/entity_attributes.csv`

```
global_entity_id, key, value, provenance_package, provenance_dataset, provenance_row_id
```

**A side table, not new entity columns.** Three reasons:

| | |
|---|---|
| **Cardinality** | A scheme has many eligibility criteria. They do not fit one row |
| **Provenance** | Each attribute keeps its own source row, matching how edges work |
| **Stability** | `entities.csv` keeps its 11 columns, so the sync `TableSpec` and every consumer are untouched |

**Attributes are not facts the graph invents.** Each carries package, dataset and row, so
`scheme.eligibility.income_ceiling` traces to
`Package007/eligibility_criteria.csv:ec-0042` exactly as an edge does.

**Value: ~393 rows of the most actionable content in the repository.** A scheme
recommendation that names the eligibility rule, benefit amount, application channel and
required documents is a different product from one that names a scheme.

---

## 5. Validation, diagnostics, metrics

### Validation — pre and post

```python
# pre-flight, before any building
check_registry_matches_disk()      # every file registered, every entry exists
check_required_columns()           # declared FKs are present in the header
check_no_duplicate_builders()

# post-build
check_types_closed()               # every emitted type is registered
check_no_duplicate_edges()         # G12
check_no_self_loops()              # G13
check_orphan_census()              # G15 — fail on regression
```

**Pre-flight matters most.** Today a renamed dataset fails mid-build with `sys.exit`
after some output has been written. A pre-flight pass fails in a second, before anything
is touched.

### Diagnostics — `knowledge_graph/diagnostics/`

| File | Contents |
|---|---|
| `dataset_coverage.json` | Per-dataset: channel, rows read, entities, edges, attributes |
| `unused_foreign_keys.csv` | FK-shaped columns never read — **with population counts** |
| `unresolved_endpoints.csv` | *(exists)* — now complete, once the guards go |
| `join_rates.csv` | Per declared FK: attempted, resolved, rate |

**Population counts are what makes the FK diagnostic usable.** Of 22 unused FK columns,
**21 are populated and 1 is empty** — `district.primary_industry_sector_id`, 0 of 61.
Without the count, that empty column looks exactly like the 40-of-40
`business_model_id`, and someone spends two days chasing an `Industry → District` edge
that has no data behind it.

### Metrics — structured, not printed

`graph_summary.json` gains:

```json
"coverage": {
  "datasets_total": 77, "datasets_registered": 77, "datasets_read": 39,
  "by_channel": {"ENTITY": 30, "RELATIONSHIP": 28, "ATTRIBUTE": 17, "NONE": 2},
  "rows_read": 1112, "rows_available": 2299
}
```

Coverage becomes a **build output**, not an audit finding. The 38 skipped datasets would
have been visible on day one.

---

## 6. Orchestration

```python
def build(root=ROOT, write=True):
    ctx = Context(root)
    validation.preflight(DATASETS, root)

    for ds in DATASETS:                      # phase 1
        if ds.channel is Channel.ENTITY:
            ctx.registry.absorb(call(ds), ds)

    for ds in DATASETS:                      # phase 2
        if ds.channel is Channel.RELATIONSHIP:
            ctx.edges.absorb(call(ds), ds)   # resolves; logs failures

    for ds in DATASETS:                      # phase 3
        if ds.channel is Channel.ATTRIBUTE:
            ctx.attributes.absorb(call(ds), ds)

    validation.postflight(ctx)
    diagnostics.write(ctx)
    if write:
        outputs.write_all(ctx)
    return ctx

if __name__ == "__main__":
    build()
```

**`build()` returns the context and takes `write=False`.** That single signature makes
the whole compiler testable: a test can build the graph in memory and assert on it
without writing files or shelling out — which no current test can do.

**Phase order is unchanged**, so entity availability during relationship building behaves
exactly as today.

---

## 7. Acceptance test — non-negotiable

```bash
python3 knowledge_graph/build_graph.py                 # before
cp -r knowledge_graph/entities /tmp/before-e
cp -r knowledge_graph/relationships /tmp/before-r

# ... refactor ...

python3 knowledge_graph/build_graph.py                 # after
diff <(sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/<DATE>/g' /tmp/before-e/entities.csv) \
     <(sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/<DATE>/g' knowledge_graph/entities/entities.csv)
# must be empty
```

**A refactor that changes graph output is not a refactor.** The date-normalised diff must
be empty for `entities.csv`, `relationships.csv`, `aliases.csv` and
`cross_package_sightings.csv` before any new dataset is registered.

`relationship_id` is positional (`vwr:000123`), so **builder execution order must be
preserved exactly**. Reordering `DATASETS` renumbers every edge and produces a diff that
looks catastrophic and is cosmetic. Keep the current order in the initial registry; sort
it later, in a commit that does nothing else.

---

## 8. Sequencing

| # | Step | Effort | Risk | Output change |
|---|---|---:|---|---|
| **1** | **Delete the four bypass guards** | 1 h | **None** | `unresolved_endpoints.csv` 132 → ~176 |
| 2 | Extract `compiler/model.py` — move helpers verbatim | 2 h | Low | **None** |
| 3 | Build `DATASETS` describing the current 39 | 3 h | Low | **None** |
| 4 | Move builders into `entities.py` / `relationships.py` | 6 h | **Medium** | **None** — §7 gate |
| 5 | Wrap in `build()`, guard `__main__` | 2 h | Medium | **None** |
| 6 | Add validation, diagnostics, metrics | 4 h | Low | New files only |
| 7 | Add the attribute channel | 6 h | Low | New file only |
| 8 | Register the 36 ignored datasets | 3 d | Medium | **Intended** |
| | | **~5.5 d** | | |

**Step 1 first, and it is subtractive.** Deleting four guards makes ~44 hidden failures
visible before anything is added. Doing it after step 8 means 36 new datasets land in a
compiler that hides a quarter of its join failures.

**Step 4 is the risky one.** Six hundred lines move between files with no behaviour
change, and the only defence is the §7 diff. Do it in one commit that moves code and
changes nothing else, so the diff is reviewable as a move.

**Steps 1–7 change no graph output. Step 8 is the only one that should.**

---

## 9. What this design refuses

**No plugin discovery.** Builders are named in the registry, not found by scanning. A
compiler whose behaviour depends on which files happen to be importable is not
deterministic, and determinism is the property the whole platform rests on.

**No inference.** The compiler emits what a package asserts. Deriving
`Industry → District` from MSME addresses is defensible and it is inference, and an
inferred edge carrying a package's provenance is a claim the package never made.

**No new dependency.** Standard library only, as today.

**No config file.** The registry is Python because foreign keys reference builder
functions and closed type sets. A YAML registry would need a schema, a loader and a
validator to be as safe as a `@dataclass` is for free.

**Attributes stay a side table.** Widening `entities.csv` would break the sync
`TableSpec`, the Supabase projection and every consumer — to solve a cardinality problem
that a side table solves properly.
