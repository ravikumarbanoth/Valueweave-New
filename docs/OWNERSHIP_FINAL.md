# Ownership — Final Model (ValueWeave Platform v2.2)

**ADR-003 is decided.** `Package007_Government_Schemes` is the authoritative owner of
the `GovernmentScheme` entity type and every attribute the registry assigns to it.

---

## 1. The decision

Six packages held scheme rows: 40 canonical in Package007 and
79 across five domain packages that predate it. Package007 declared
every overlap in `government_schemes.also_in_package`, and `known_overlaps.csv` recorded
it — but **declaring is not resolving**. A benefit updated in Package007 left
Package005's copy stale with nothing detecting the divergence.

ADR-003 offered three options. **Option 1 is adopted:** Package007 becomes canonical;
domain packages keep their rows and declare their relationship to the canonical row.

The argument is simple. Scheme parameters change with every budget cycle. Six copies of
an annually-changing figure will diverge; the only question was when. A one-time
coordinated change is cheaper than a recurring correctness risk.

## 2. What every domain scheme row now carries

Two appended columns:

| Column | Values |
|---|---|
| `package007_scheme_id` | the canonical `scheme_id`, or the bare sentinel `PENDING_VERIFICATION` |
| `scheme_ownership` | `DEPRECATED_REFERENCE` or `DOMAIN_CANONICAL` |

**`DEPRECATED_REFERENCE`** — Package007 owns this scheme's attributes. The domain row
stays readable for backward compatibility, but Package007 is where a change is made.

**`DOMAIN_CANONICAL`** — no Package007 counterpart exists. The domain package remains the
owner until a steward promotes the scheme into Package007. This is a determinate
statement about the world, not an admission of ignorance.

## 3. What the crosswalk resolved

`governance/ownership/build_scheme_crosswalk.py` matched all 79 domain
rows against the 40 canonical schemes.

| Match method | Rows |
|---|---:|
| `NO_MATCH` | 58 |
| `EXACT_NAME` | 16 |
| `ACRONYM` | 3 |
| `PORTAL` | 2 |

**21 matched** → `DEPRECATED_REFERENCE`, referencing
21 distinct canonical schemes.
**58 unmatched** → `DOMAIN_CANONICAL`.

| Package | Scheme rows | Matched | Domain-canonical |
|---|---:|---:|---:|
| Package002_Education | 25 | 3 | 22 |
| Package003_Healthcare | 9 | 1 | 8 |
| Package004_Industries | 18 | 5 | 13 |
| Package005_Agriculture | 12 | 8 | 4 |
| Package006_Skills_and_Training | 15 | 4 | 11 |

### The 58 unmatched rows are not a failure

Package007's registry is 40 *national* schemes. The unmatched rows are things it does
not cover: state schemes (Telangana ePASS, AP Post-Matric, Rajiv Aarogyasri), minority
and community scholarships, CGHS, ECHS, RKVY, NATS, RSETI, JSS — and the **Startup
India** umbrella programme, which is a different thing from **Startup India Seed Fund
Scheme** (`sch-020`), the scheme Package007 actually holds.

Conflating those two would have been precisely the error the matcher exists to prevent.

## 4. Why matching refuses rather than guesses

Four matchers run in decreasing order of evidential strength, and each records how it
fired:

| Matcher | Evidence |
|---|---|
| `EXACT_NAME` | normalised canonical names are identical |
| `ACRONYM` | a parenthetical acronym equals a Package007 `short_name` — `"... (PM-KISAN)"` → `PM-KISAN` |
| `PORTAL` | both rows cite the same official portal host |
| `FUZZY` | blended token-and-sequence similarity ≥ 0.88, accepted **only when exactly one** candidate clears it |

Two candidates above the threshold is ambiguity, not a hint, and the matcher refuses.

A wrong crosswalk row is worse than a missing one: it silently redirects a consumer from
one scheme to an unrelated one, and nothing downstream can detect it. A missing row is
visible as `DOMAIN_CANONICAL`. This is the same position ADR-004 takes on entity merges,
applied to a narrower problem.

## 5. Backward compatibility

Verified mechanically before commit, for all five datasets:

- row count unchanged
- column order unchanged
- **zero existing cell values changed**

The two columns are appended. A consumer that ignores them reads exactly what it read
before v2.2. `tests/test_regression.py::BackwardCompatibilityRegressionTest` diffs every
touched dataset against `main` and fails on any changed value.

## 6. Enforcement

A governance decision recorded only in Markdown decays the moment someone adds a row and
forgets. This one is mechanical.

**`validate_graph.py` check G11** fails the build when:

- any entity type has more than one owner in the ownership registry;
- any of the five domain scheme datasets is missing either governance column;
- a `DEPRECATED_REFERENCE` row's `package007_scheme_id` does not resolve to a real
  Package007 scheme;
- a `DOMAIN_CANONICAL` row carries an id where the bare sentinel belongs.

**Check G7** continues to enforce that no non-owner publishes a Package007-owned
attribute — the generalisation of Package008's V13 to all eight packages.

**`tests/test_ownership.py`** (11 tests) asserts the registry has exactly one owner per
type, that ADR-003's overlap reads `RESOLVED`, that every crosswalk row has a named match
method, and that fuzzy matches clear the declared threshold.

## 7. The full ownership registry

19 entity types, 87 enforceable owned attributes, one owner each.

| Entity type | Owner |
|---|---|
| District, State, Country, ExportCountry | Package001_Geography |
| Institution | Package002_Education |
| Industry, BusinessOpportunity | Package004_Industries |
| Crop, Soil, ClimateZone, Machinery | Package005_Agriculture |
| Skill, Certification, TrainingProvider | Package006_Skills_and_Training |
| **GovernmentScheme**, FinancialInstitution | **Package007_Government_Schemes** |
| MSME, RawMaterial, Market | Package008_MSME |

## 8. What remains open

ADR-003 is closed. One declared overlap is not, and v2.2 did not touch it:

| Entity type | Status | ADR | Why |
|---|---|---|---|
| `ExportCountry` | `UNRESOLVED` | ADR-005 | No package holds a country dataset. The graph derives 29 ExportCountry entities by parsing free-text destination lists. A proper country reference in Package001 would make this a real foreign key. |

Three others are settled as governed, not violations: `Industry`
(`PARTIALLY_RESOLVED`, four sector taxonomies normalised into one type),
`FinancialInstitution` (`ACCEPTED`, two framings of the same bodies), and `Machinery`
(`ACCEPTED`, a scope boundary rather than duplication).

`tests/test_ownership.py::test_remaining_unresolved_overlaps_are_declared_and_attributed`
requires anything still open to name the ADR that owns it, and requires that ADR not to
be ADR-003.

## 9. Artifacts

| Path | Contents |
|---|---|
| `governance/adr/ADR-003-scheme-data-ownership.md` | the decision and its reasoning |
| `governance/ownership/build_scheme_crosswalk.py` | the matcher; `--apply` writes the columns |
| `governance/ownership/scheme_crosswalk.csv` | 79 rows with match method and score |
| `governance/ownership/crosswalk_summary.json` | the figures quoted above |
| `knowledge_graph/ownership/ownership_registry.csv` | 19 types, one owner each |
| `knowledge_graph/ownership/attribute_ownership.csv` | 87 enforceable attributes |
| `knowledge_graph/ownership/known_overlaps.csv` | 5 declared overlaps and their status |
