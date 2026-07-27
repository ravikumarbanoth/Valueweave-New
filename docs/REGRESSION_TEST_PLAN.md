# Regression Test Plan — Graph Compiler

**Workstream 6** · `tests/test_graph_compiler.py` · **11 tests · implemented and passing**

---

## 0. Status

**This workstream is built, not planned.** The brief said *create automated tests that
fail whenever a new dataset is added to a package but not registered in the builder* —
so the file exists, is registered in `run_all.py`, and the suite is **458 tests, 0
failures**.

Sections 1–4 document what was built. Sections 5–7 plan the checks that only become
possible after the refactor in `COMPILER_ARCHITECTURE.md`.

---

## 1. The regression being protected against

The repository reached **39 of 77 datasets consumed** without anyone deciding to skip 38.
Datasets were added to packages and the builder was not updated, and **nothing anywhere
said so** — not the build output, not `graph_summary.json`, not the 447-test suite.

A dataset the compiler does not read contributes nothing, however well researched. That
failure is silent, cumulative, and invisible until someone audits by hand — which is
exactly how the 305-row `district_scheme_mapping.csv` sat unread while `RS2-VIA_DISTRICT`
was diagnosed as a dead rule.

**One test makes the next occurrence impossible.**

---

## 2. What was built

| Group | Tests | Protects |
|---|---:|---|
| `DatasetRegistrationTest` | 3 | Every dataset on disk is classified |
| `ManifestFidelityTest` | 3 | The manifest matches the builder |
| `CoverageTest` | 2 | Coverage floor; silent packages pinned |
| `CompilerInvariantTest` | 3 | Properties the refactor must preserve |

### 2.1 The primary guard

```python
def test_every_dataset_is_registered(self):
    unregistered = sorted(on_disk() - CONSUMED - IGNORED - EMPTY)
    self.assertEqual(unregistered, [], ...)
```

Every CSV under `packages/*/datasets/` must be in exactly one of three sets. A new file
is in none, so the test fails with the path and instructions.

**`IGNORED` is a census, not an aspiration.** It records 36 datasets that exist and are
not consumed — each with an entry in `BUILDER_REGISTRY.md` naming its entity types,
foreign keys and expected contribution. **Moving an entry from `IGNORED` to `CONSUMED` is
the unit of progress the compiler work measures.**

A test that failed on all 36 today would be turned off within a week. A test that fails
only on the *37th* is one people keep.

### 2.2 The guard that keeps the guard honest

```python
def test_consumed_manifest_matches_the_builder_source(self):
    reads = builder_reads()
    self.assertEqual(sorted(CONSUMED - reads), [], "CONSUMED claims datasets the builder never opens")
    self.assertEqual(sorted(reads - CONSUMED), [], "builder reads datasets missing from CONSUMED")
```

`builder_reads()` parses `build_graph.py` for **both** loading styles:

```python
read("Package005_Agriculture/datasets/crops.csv")      # literal
read(f"Package004_Industries/datasets/{fname}.csv")    # from P4_FILES
```

**This is the test that would have caught my own error.** The Phase 2 report claimed 35
consumed datasets because it only matched string literals and missed Package004's four
dynamically-loaded files. The brief for this mission said 42. **The real figure is 39**,
and it is now verified on every run rather than re-derived by hand each time somebody
asks.

A manifest that drifts from the compiler is worse than no manifest: it reports coverage
that does not exist, and every downstream figure inherits the error.

### 2.3 Coverage floor and silent packages

```python
MIN_CONSUMED = 39
```

Registering a dataset is progress; un-registering one is a regression. The floor rises
with each stage in `BUILDER_REGISTRY.md`.

`test_every_package_contributes_something` pins the silent set to exactly
`["Package003_Healthcare"]` — 4 datasets, 146 rows, 0 entities, 0 edges. Recorded as a
known state rather than asserted away, so the day healthcare is wired in, the suite says
so instead of quietly passing.

### 2.4 Invariants the refactor must preserve

```python
def test_unresolved_endpoints_are_logged_by_the_edge_helper(self):
    body = self.src.split("def edge(")[1].split("\ndef ")[0]
    self.assertIn("UNRESOLVED.append", body)
```

`edge()` logging unresolvable endpoints is the compiler's only diagnostic for a mapping
that fails to join. Four call sites currently bypass it by pre-checking, and the fix is
to delete those guards — **so the helper itself must not lose the behaviour in the
process.**

Also pinned: type sets abort the build when violated (`FATAL: unregistered …`), and edges
de-duplicate on `(from, type, to)` — the reason the graph has 0 duplicate edges, about to
be tested by six new sources.

---

## 3. Verified to fail for the right reason

A guard that has never been seen to fail is a guard nobody should trust.

```
$ printf 'a,b\n1,2\n' > packages/Package008_MSME/datasets/__probe_new_dataset.csv
$ python3 -m unittest tests.test_graph_compiler

FAIL: test_every_dataset_is_registered
AssertionError: dataset(s) present in packages/ but absent from the compiler registry.
Add each to CONSUMED (and wire it into build_graph.py) or to IGNORED
(with an entry in docs/BUILDER_REGISTRY.md saying why):
  Package008_MSME/datasets/__probe_new_dataset.csv

$ rm packages/Package008_MSME/datasets/__probe_new_dataset.csv
$ python3 -m unittest tests.test_graph_compiler
OK
```

The failure message names the file and both remedies. Someone hitting this at 5pm should
not need to read this document.

---

## 4. Suite impact

| | Before | After |
|---|---:|---:|
| Suites | 12 | **13** |
| Tests | 447 | **458** |
| Runtime | ~4 s | ~9 s |
| Failures | 0 | **0** |

Registered in `tests/run_all.py` as `graph_compiler`.

---

## 5. Planned — after the registry refactor

These become possible once `DATASETS` exists (`COMPILER_ARCHITECTURE.md` §2). They cannot
be written against the current procedural builder.

| # | Test | Replaces |
|---|---|---|
| R1 | Every `Dataset` entry resolves to a file on disk | Source parsing |
| R2 | Every `Dataset` names a builder that exists and is callable | — |
| R3 | Every declared foreign key column exists in the CSV header | — |
| R4 | Every `Channel.NONE` entry carries a `note` explaining why | — |
| R5 | No two entries share `(package, filename)` | — |
| R6 | Builders are pure — same rows in, same declarations out | — |

**R1 replaces `builder_reads()` source parsing with a data lookup.** Parsing Python to
discover what it reads is a workaround for the absence of a registry; once the registry
exists, the manifest *is* the registry and the fidelity test collapses to a set
comparison.

**R4 is the one that keeps `Channel.NONE` honest.** Without it, marking a dataset `NONE`
becomes a way to silence the primary guard. Requiring a written reason makes skipping a
dataset a decision someone signed rather than a default.

## 6. Planned — after the attribute channel

| # | Test |
|---|---|
| A1 | Every `AttributeDecl` resolves to an existing entity |
| A2 | Every attribute row carries package, dataset and row id |
| A3 | Attribute keys are namespaced (`scheme.eligibility.income_ceiling`) |
| A4 | `entities.csv` keeps its 11 columns — attributes stay a side table |

**A4 protects the sync `TableSpec`.** Widening `entities.csv` would break the Supabase
projection and every consumer downstream of it.

## 7. Planned — the refactor gate

| # | Test |
|---|---|
| B1 | **Date-normalised graph output is byte-identical before and after** |
| B2 | `build(write=False)` returns a context and writes nothing |
| B3 | Relationship ids stay positional and stable for unchanged input |

**B1 is the acceptance test for the whole refactor** and is worth writing *before* step 4
of the sequencing, not after. `relationship_id` is positional (`vwr:000123`), so
reordering `DATASETS` renumbers every edge — a diff that looks catastrophic and is
cosmetic. B3 catches that specifically.

---

## 8. What this plan does not test

**That a dataset's content is correct.** `validate_graph.py` (G1–G11) and each package's
own validator own that. This file tests only that the compiler *sees* the dataset.

**That a registered dataset produces the expected number of edges.** Coupling a test to
edge counts makes every legitimate data update a test failure. Coverage is the invariant;
edge counts are an output.

**That `IGNORED` shrinks.** Deliberately. A test demanding progress fails for months and
gets disabled, and then the primary guard goes with it. `MIN_CONSUMED` rises when work
lands — a ratchet, not a deadline.

**Nothing about `unresolved_endpoints.csv` row counts.** After the four guards are
deleted the count rises from 132 to ~176, and that rise is the compiler working. A test
pinning the number would fail on the fix.
