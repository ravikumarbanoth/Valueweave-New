# Knowledge Engine — ValueWeave Platform v2.2

**VKE v0.1.0** · recovered from commit `71ac7e1` · **COMPATIBLE** with Platform v2

---

## What happened

Platform v2 was specified on the premise that the Knowledge Engine was already
implemented. It was not present on `main`, and ADR-006 recorded that as a high-severity
gap: `git ls-files knowledge_engine` returned 0.

The premise of ADR-006 was right and its conclusion was reached without a key fact. The
engine had never been lost. It was committed on `claude/knowledge-engine-foundation` and
simply never merged — 62 files, 5,322 insertions, 13 modules, **zero merge-conflict
markers** against the merge base. The v2.1 audit located it; v2.2 Work Package 1
recovered it.

**Recovered by merge, not by copying.** `git log -- knowledge_engine/core/types.py`
still shows `71ac7e1`, so the original authorship and history of every file survived.
Re-adding the files as new work would have produced an identical working tree and
destroyed the provenance of the code — which would be a strange thing for a platform
built on provenance to do. `tests/test_knowledge_engine.py::test_history_was_preserved_not_recopied`
asserts it.

ADR-006 is now **RESOLVED**.

---

## The eight modules

| Module | What it does |
|---|---|
| `collectors/` | Plugin-based fetchers: CSV, JSON, XML, RSS, API. A registry with autodetection. |
| `parsers/` | Normalise a raw payload into flat dict records: CSV, JSON, XML, RSS, HTML tables, PDF. |
| `validation/` | Seven reusable rules — required fields, foreign keys, duplicates, source validity, confidence scoring, schema, freshness — and the engine that runs them. |
| `provenance/` | The eight-field provenance model and its tracker. Emits the six mandatory CSV columns. |
| `package_builder/` | Assembles a package directory: datasets, manifests, evidence, import manifests. |
| `versioning/` | Semantic versioning, ordering, and version history with rollback. |
| `update_engine/` | The check → detect → validate → update → draft → approve → release workflow. |
| `rule_engine/` | Structured, non-AI querying over record lists. Ten operators, AND/OR composition. |

Plus `core/types.py`, which holds the enums every module shares:
`VerificationStatus`, `SourceTier`, `ConfidenceTier` and the `PENDING_VERIFICATION`
sentinel.

**No third-party runtime dependency.** The engine runs on the standard library alone,
by design, so it can be reviewed and executed without provisioning anything. `pytest`
appears in `requirements.txt` for the test suite only — and the suite also runs under
`unittest`, which is how `tests/run_all.py` executes it.

---

## Compatibility report

Generated, not asserted. `python3 knowledge_engine/check_compatibility.py` runs nine
checks against the eight real packages and the built graph, writes
`knowledge_engine/compatibility_report.json`, and exits non-zero on any failure.

**Result: COMPATIBLE — 9/9 checks passed.**

| Check | Title | Status | Detail |
|---|---|---|---|
| `C1` | Import surface | **PASS** | 10 modules, 49 exported symbols, 0 failures |
| `C2` | Sentinel agreement | **PASS** | 2456 cells hold the bare sentinel 'PENDING_VERIFICATION'; 0 non-bare occurrences in the six provenance columns |
| `C3` | Verification enum | **PASS** | packages use ['VST-NEEDS_REVIEW']; engine defines ['VST-NEEDS_REVIEW', 'VST-REJECTED', 'VST-VERIFIED']; 0 unrepresented |
| `C4` | Provenance columns | **PASS** | engine emits ['collection_date', 'confidence_score', 'data_source', 'notes', 'source_url', 'verification_status']; 77/77 package datasets carry all six |
| `C5` | Confidence bands | **PASS** | 2299 scored cells, range 50-92, 38 distinct values, 0 unclassifiable |
| `C6` | Validation rules | **PASS** | 2 rules over 40 rows of government_schemes.csv: 0 violations |
| `C7` | Lifecycle vocabulary | **PASS** | 11 workflow states map onto 6 of 7 record lifecycle states; APPROVED is reached only by a steward, never by the engine |
| `C8` | Rule engine | **PASS** | RuleQuery over 40 Package008 businesses returned 3 rows with risk_level == 'Low' |
| `C9` | Collector/parser availability | **PASS** | 5 collectors, 6 parsers are now nameable by the source registry (ADR-006 resolved) |

### Warnings — real findings that are not incompatibilities

- **C2 Sentinel agreement** — 41 prose cells outside `notes` embed the sentinel in a sentence (Package002_Education 7, Package003_Healthcare 4, Package004_Industries 30). These predate the bare-sentinel discipline introduced in Package005 and are honest prose, not fabrication. The engine reads them correctly, so this is a data-remediation item, not an incompatibility.
- **C4 Provenance columns** — 2 dataset(s) are header-only and hold no rows: Package001_Geography/mandal.csv, Package001_Geography/revenue_division_andhra_pradesh.csv. The columns are declared, so the engine can write into them; there is simply nothing there yet.

Neither warning blocks the engine. Both are recorded rather than suppressed, because a
compatibility check that hides what it noticed is not worth running.

---

## Two vocabularies that must not be conflated

The engine has `WorkflowState` (11 states). The graph has `lifecycle_state` (7 states).
They describe different things:

- **`WorkflowState`** describes one *update cycle* — a run of the pipeline against a
  source.
- **`lifecycle_state`** describes one *record* — where a row sits between draft and
  archive.

The mapping between them is the contract, and check C7 verifies every target lands in a
registered lifecycle state:

| `WorkflowState` | `lifecycle_state` |
|---|---|
| `CHECKING_SOURCE` | `COLLECTED` |
| `DETECTING_CHANGES` | `COLLECTED` |
| `VALIDATING` | `VALIDATED` |
| `UPDATING_DATABASE` | `VALIDATED` |
| `GENERATING_DRAFT` | `DRAFT` |
| `PENDING_HUMAN_APPROVAL` | `REVIEWED` |
| `STABLE_RELEASE` | `PUBLISHED` |
| `REJECTED` | `ARCHIVED` |

`APPROVED` appears nowhere in that table. It is the one state the engine may never
reach: approval is a person accepting responsibility for a claim, and
`stewardship/lifecycle.py` refuses it to a machine. See
[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) and `governance/DATA_STEWARDSHIP.md`.

---

## What recovery unblocked

**The source registry can name real modules.** Before v2.2, all 605 source
rows carried `collector: PENDING_IMPLEMENTATION` because no module existed to name.
`source_registry/build_source_registry.py` now routes each URL to a real collector and
parser by the payload it serves, and **verifies the class is importable before writing
its name** — a registry naming a module that does not exist is worse than one that
admits ignorance.

Two honesties are preserved in that change:

- Routing is a decision about which module *would* run. **No source has yet been
  collected by the engine**; `last_collection` dates are when a human collected the data
  by hand.
- A URL whose payload type cannot be determined keeps `PENDING_IMPLEMENTATION`.
  Guessing a parser is worse than admitting we do not know which one applies.

Collectors available: api_collector, csv_collector, json_collector, rss_collector, xml_collector.
Parsers available: CSVParser, JSONParser, XMLParser, RSSParser, HTMLTableParser, PDFParser.

---

## Running it

```bash
python3 knowledge_engine/check_compatibility.py     # nine compatibility checks
python3 -m unittest discover -s knowledge_engine/tests -t .   # 117 unit tests
python3 knowledge_engine/examples/example_collect_and_validate.py
python3 knowledge_engine/examples/example_build_package.py
python3 knowledge_engine/examples/example_rule_query.py
```

The engine's own docs travel with it: `knowledge_engine/README.md`,
`architecture.md`, `ROADMAP.md`, and eight module specifications under
`knowledge_engine/docs/`.

---

## What the engine still does not do

Recovery restored the foundation. It did not make the platform self-collecting.

| Gap | Consequence |
|---|---|
| No source has been collected by the engine | Every row in the knowledge base was gathered by hand. Collection reproducibility scored 30/100 in the v2.1 audit and recovery alone does not move it. |
| No scheduler | Nothing invokes the update engine on the cadence the source registry prescribes. |
| No network access to `.gov.in` in this environment | Egress policy blocks the authoritative domains, which is why confidence is capped at 85. |
| Collectors are routed, not exercised | 604 of 605 sources fall to the generic HTML route. That is honest for portal pages and untested against them. |

The next real step is not more engine code. It is one source, collected end to end by
the engine, with the resulting rows compared against the hand-collected ones.
