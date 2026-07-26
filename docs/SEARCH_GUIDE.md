# Search Guide — ValueWeave Platform v2.2

```bash
python3 -m search.cli "turmeric"
python3 -m search.cli "PM-KISAN" --scope alias
python3 -m search.cli "manufactring" --scope entity
python3 -m search.cli --stats
curl 'localhost:8000/search?q=turmeric&scope=entity'
```

---

## What is searchable

One index, five scopes, **1,747 documents**:

| Scope | Documents | The text that is matched |
|---|---:|---|
| `entity` | 647 | `canonical_name` |
| `relationship` | 865 | the sentence the edge asserts: `Turmeric EXPORTS_TO UAE` |
| `alias` | 150 | the alias, resolving to its entity |
| `dataset` | 77 | the dataset filename, humanised |
| `package` | 8 | the package name |

Relationships are searchable as sentences on purpose: `"turmeric exports"` should
find the edge, not just its two endpoints.

A directory with no datasets is not a package. `Package006_Skills` holds a README
and nothing else, and is not indexed.

## The four match modes

Modes run as a ladder, strongest first. The first mode to find a document claims
it, so nothing appears twice.

| Mode | Fires when | Rank weight |
|---|---|---:|
| `EXACT` | normalised query equals the title | 1000 |
| `ALIAS` | the query matches a registered alias | 800 |
| `PREFIX` | the title, or a word in it, starts with the query | 600 |
| `FUZZY` | similarity clears a threshold | 400 |

**An exact match can never be displaced by a high-scoring fuzzy one.** That is what
the weights are for; the within-mode score only orders results inside a band.

### Aliases belong to `ALIAS` alone

`EXACT` and `PREFIX` skip alias documents. Without that rule, searching `PM-KISAN`
would report `match_mode: EXACT` — technically true, since the alias text matched
exactly — and `mode=ALIAS` would be a mode that never fires on the queries people
actually type. **The mode names what was matched, not which function ran.**

```
$ python3 -m search.cli "PM-KISAN"
  [ALIAS  1.00] [78] alias   PM-KISAN
     vw:governmentscheme:pradhan-mantri-kisan-samman-nidhi  (alias -> Pradhan Mantri Kisan Samman Nidhi)
```

### Fuzzy has two routes, because typos and paraphrases fail differently

```python
blend = 0.5 * jaccard(query_tokens, title_tokens) + 0.5 * sequence_ratio
accept if blend >= fuzzy_threshold        (default 0.62)
    or if sequence_ratio >= 0.85          (STRING_SIMILARITY_FLOOR)
```

The blend catches a user with the right words in the wrong order or with extras.
It is useless against a typo: `"manufactring"` shares **no token** with
`"manufacturing"`, so its Jaccard is 0 and the blend lands near 0.48 no matter how
close the strings are.

So raw string similarity is accepted on its own at a stricter floor. A transposed
letter clears 0.85; two unrelated words do not.

```
$ python3 -m search.cli "Manufactring" --scope entity
  [FUZZY  0.96] entity  Manufacturing   string similarity 0.96 (probable typo)
```

### Turning approximation off

```bash
python3 -m search.cli "Manufactring" --mode EXACT      # no results, by design
curl 'localhost:8000/search?q=Manufactring&mode=EXACT'
```

Fuzzy is in the default ladder because a wrong *search result* is recoverable —
the user sees it and ignores it. That is a different kind of error from a wrong
*entity merge*, which is why the Resolver proposes and never merges (ADR-004) while
search happily approximates.

## Normalisation

`search.index.normalise()` lowercases, strips accents, folds `&` to ` and `, and
collapses punctuation to single spaces.

**Folding `&` is not cosmetic.** In v2.0 `Agriculture & Allied` and
`Agriculture and Allied` became two separate graph nodes, and a named query
silently returned nothing. `tests/test_regression.py` asserts no such pair exists.

**Parentheticals are kept**, which is the opposite of what
`knowledge_graph/resolution/resolver.py` does — deliberately:

| | Resolver | Search |
|---|---|---|
| `Manufacturing (Automotive)` | strips to `manufacturing` | keeps the qualifier |
| Why | one surface form must resolve to one entity | a user who types the qualified name means the qualified thing |

Collapsing them in the Resolver once scored `Manufacturing` against
`Manufacturing (Automotive)` at a false 1.000 — a parent and its child. Search
makes the other trade because its failure mode is visible.

## Filters

| CLI | API | Effect |
|---|---|---|
| `--scope` (repeatable) | `scope` | restrict to one or more scopes |
| `--mode` (repeatable) | `mode` | restrict to one or more match modes |
| `--type` | `type` | one entity type, or one relationship type |
| `--package` | `package` | one owning package |
| `--min-confidence` | `min_confidence` | integer floor |
| `--fuzzy-threshold` | `fuzzy_threshold` | override the blend floor for one call |
| `--limit` | `limit` | cap results |
| `--suggest` | — | type-ahead: `EXACT`, `ALIAS`, `PREFIX`, no fuzzy |
| `--json` | — | machine-readable output |

An unknown scope or mode raises a `ValueError` naming the valid options; over HTTP
that becomes a `400`, never a `500`.

A `--fuzzy-threshold` override applies to that call only and is restored in a
`finally` block, so a one-off loose search cannot leave the engine permanently
loose. `tests/test_search.py::test_threshold_override_does_not_leak` holds that.

## Result shape

```json
{
  "doc_id": "vw:crop:turmeric",
  "scope": "entity",
  "title": "Turmeric",
  "entity_id": "vw:crop:turmeric",
  "entity_type": "Crop",
  "source_package": "Package005_Agriculture",
  "confidence": 77,
  "verification_status": "VST-NEEDS_REVIEW",
  "match_mode": "EXACT",
  "score": 1.0,
  "matched_on": "canonical_name"
}
```

`matched_on` says *why* the result is there. For fuzzy hits it distinguishes the
two routes: `token+sequence similarity 0.71` versus
`string similarity 0.96 (probable typo)`.

**A search hit is not an endorsement.** Every result carries its
`verification_status`, and the CLI prints a count of unverified results after every
search. All 647 entities are currently `VST-NEEDS_REVIEW`.

## Architecture

```
search/index.py    SearchIndex: loads four sources into one Document shape
search/engine.py   SearchEngine: four matchers, ranking, filters
search/cli.py      command line
```

The index is built in memory at construction and is not shared with
`query_engine.GraphStore`. That is deliberate: GraphStore is optimised for
traversal (adjacency indexes), search needs a normalised-text index, and one
structure serving both would be slower and less clear. At 1,747 documents the
build costs milliseconds; when it stops doing so, `SearchIndex` is where a real
inverted index goes and nothing above it changes.

Adding a sixth searchable scope means adding a loader to `index.py` and a member to
`Scope`. The matchers need no change.

## Limitations

| Limitation | Note |
|---|---|
| No stemming or lemmatisation | `"processing"` does not match `"process"`. Prefix matching covers most of the gap. |
| No semantic or vector search | Out of scope for v2.2; would need embeddings and a model dependency. |
| No relevance tuning from usage | Nothing records what users click, so there is nothing to learn from. |
| Index is rebuilt per process | Fine for a CLI; a long-lived server holds one instance. |
| No highlighting of matched spans | `matched_on` explains the match instead. |
