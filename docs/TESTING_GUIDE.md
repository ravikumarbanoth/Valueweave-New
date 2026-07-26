# Testing Guide — ValueWeave Platform v2.2

```bash
python3 tests/run_all.py                        # everything: 248 tests
python3 tests/run_all.py --suite api search     # selected suites
python3 tests/run_all.py --quiet                # summary table only
python3 -m unittest tests.test_ownership -v     # one suite, verbose
```

Exit code 0 = everything passed.

---

## Why `unittest` and not `pytest`

The Knowledge Engine was written to depend on the standard library alone so it can be
run and reviewed on a bare Python install. A test runner that needs a `pip install`
would quietly undo that. `pytest` is listed in `knowledge_engine/requirements.txt` as a
convenience; the suites are plain `unittest.TestCase` and run either way.

---

## The eight suites

| Suite | Tests | What it protects |
|---|---:|---|
| `knowledge_engine_unit` | 117 | The engine's own behaviour. Recovered with the engine at `71ac7e1`. |
| `knowledge_engine` | 9 | That the *recovery* worked: files tracked, history preserved, nine compatibility checks green. |
| `ownership` | 11 | ADR-003 cannot decay: one owner per type, crosswalk sound, governance columns present. |
| `api` | 29 | Envelope, routing, filters, pagination, error codes, and one class over real HTTP. |
| `search` | 27 | Each match mode does what it claims, and stays in its lane. |
| `stewardship` | 31 | Transition refusals, ledger integrity, review queue ordering. |
| `graph` | 15 | The 11 G-checks pass, and the graph is genuinely derived. |
| `regression` | 9 | One test per bug that has actually been found and fixed here. |
| **Total** | **248** | |

---

## What each suite is really for

### `knowledge_engine` — the recovery, not the engine

The engine already ships 117 tests of its own; repeating them would be duplication. What
those cannot cover is whether the recovered engine works *against this repository*.

The sharpest test here is `test_history_was_preserved_not_recopied`. It asserts that
`git log -- knowledge_engine/core/types.py` still contains `71ac7e1`. A copy-paste
recovery would produce an identical working tree and pass every other test in the
repository — and silently destroy the provenance of 62 files.

### `ownership` — making a governance decision non-optional

A decision recorded only in Markdown drifts the moment someone adds a scheme row and
forgets. These tests assert the decision from both ends: that the crosswalk is
internally consistent, and that the five domain datasets actually carry what it
requires.

`test_remaining_unresolved_overlaps_are_declared_and_attributed` is the honesty check:
anything still `UNRESOLVED` must name the ADR that owns it, and that ADR must not be
ADR-003.

### `api` — in-process and over the wire

`Application.handle()` is transport-agnostic, so 26 tests run without binding a socket.
`HttpTransportTest` binds a real ephemeral port, because "it works in-process" and "it
works over HTTP" are different claims and clients depend on the second.

`test_warning_is_computed_not_hardcoded` mutates a copy of the repository in memory to
mark everything `VST-VERIFIED` and asserts the warning **disappears**. A hard-coded
warning would still be sitting there in a year, long after it stopped being true.

### `search` — modes staying in their lane

Most of these check separation rather than matching. `test_exact_only_returns_no_approximation`
holds that `modes=["EXACT"]` never returns a fuzzy hit. `test_threshold_override_does_not_leak`
holds that a one-off loose search cannot leave the engine permanently loose.

### `stewardship` — refusals are the product

Most tests assert that something is **refused**: backward transitions, skipped states,
reviews without a named actor, machine approval. A workflow that permits an illegal
transition has recorded a decision nobody made, which is worse than one that does
nothing.

`SpecificationAgreementTest` checks that the code and `governance/DATA_STEWARDSHIP.md`
still agree, so the document cannot quietly become fiction.

`RealLedgerTest` fails if anyone commits invented review decisions. Every writing test
uses a temporary ledger.

### `graph` — derived means derived

`test_rebuild_is_idempotent` builds the graph twice and compares the artifacts **to
themselves**, not to `main`. Comparing to `main` would only prove nothing has changed
since the last commit, and something always has — `derived_at` carries the build date.
What matters is that two builds from the same packages produce the same bytes. If they
do not, state is hiding somewhere and ADR-001's "derived" claim is false.

### `regression` — one test, one real bug

Nothing speculative. Each test is a short account of a failure that actually happened:

| Test | The bug |
|---|---|
| `SentinelDisciplineRegressionTest` | A note read `district attribution left PENDING_VERIFICATION`. A consumer filtering on the sentinel silently misses embedded ones. |
| `AmpersandRegressionTest` | `Agriculture & Allied` and `Agriculture and Allied` became two nodes; a named query silently returned nothing. |
| `ResolverShadowingRegressionTest` | `Manufacturing (General)` shadowed `Manufacturing`; parent and child scored a false 1.000 similarity. |
| `ForeignKeyRegressionTest` | `AP-GNT` shipped for `AP-GUN`. Guessing an id format is not reading it. |
| `StaleFigureRegressionTest` | Docs said 650 entities and 77.85% when the truth was 647 and 78.05%. Generated artifacts were right; hand-typed prose had drifted. |
| `BackwardCompatibilityRegressionTest` | v2.2 appended columns to seven datasets. A rewritten value would be invisible — row count and column order still look right. |
| `PackageValidatorRegressionTest` | Every package validator must still exit 0 after those additions. |

---

## Tests that are deliberately not here

| Not tested | Why |
|---|---|
| Data *accuracy* | No test can tell you PM-KISAN's benefit is correct. That is what stewardship is for, and 0 of 2,299 rows have been reviewed. |
| Live collection from sources | `.gov.in` egress is blocked in this environment. A test that cannot reach its source tests nothing. |
| Load and concurrency | The API is a scaffold with no auth; performance testing an interface that must not be exposed is premature. |
| The recommendation engine | Not built. v2.1 scored it 56.9/100 ready and v2.2 left it out of scope. |

---

## Adding a test

Put it in the suite that owns the behaviour, register nothing — `run_all.py` discovers
by module name from the `SUITES` table, so a new *file* needs one line there.

Two conventions worth keeping:

**Assert on artifacts, not by importing scripts.** `knowledge_graph/build_graph.py`
rebuilds the entire graph at import time. `AmpersandRegressionTest` therefore checks
`entities.csv` for &/and collisions rather than importing `slug()` — and the artifact is
also what was actually wrong.

**A regression test should name its bug.** The value of the file is that a future
failure says what the original mistake was, not just that an assertion failed.

---

## Other checks that are not `unittest`

These run standalone and are quoted in the release report:

```bash
python3 knowledge_engine/check_compatibility.py    # 9 checks → COMPATIBLE
python3 knowledge_graph/validate_graph.py          # 11 G-checks → PASS
python3 packages/Package005_Agriculture/validate.py   # 10 package checks
python3 packages/Package007_Government_Schemes/validate.py   # 12
python3 packages/Package008_MSME/validate.py       # 13
```

`tests/test_graph_integrity.py` and `tests/test_regression.py` invoke the graph
validator and the package validators as subprocesses, so a failure in any of them also
fails `run_all.py`.

---

## Expected output

```
suite                     tests  fail  err  skip   secs  status
------------------------------------------------------------------------
api                          29     0    0     0   1.51  PASS
graph                        15     0    0     0   0.46  PASS
knowledge_engine              9     0    0     0   0.45  PASS
knowledge_engine_unit       117     0    0     0   0.07  PASS
ownership                    11     0    0     0   0.03  PASS
regression                    9     0    0     0   0.35  PASS
search                       27     0    0     0   0.82  PASS
stewardship                  31     0    0     0   0.18  PASS
------------------------------------------------------------------------
TOTAL                       248     0    0     0   3.98  PASS
```

Two lines of noise are expected and harmless: the API transport tests log three
loopback requests, and `test_graph_integrity` prints the graph build it runs.
