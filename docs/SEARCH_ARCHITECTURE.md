# Search architecture

One box. Three languages. Every kind of content. And a plan for the three things
it will need next.

```bash
python3 tests/run_all.py --suite search search_experience search_routing multilingual universal
python3 scripts/build_search_aliases.py --check
```

---

## The pipeline, end to end

```
 what someone types
        │
        ▼
 lib/search/multilingual.js      Telugu script → Latin, Tanglish → concept.
        │                        Three layers: exact alias, transliteration,
        │                        phonetic key. Data in vocabulary/concepts.js.
        ▼
 lib/search-vocabulary.js        expandQuery: corrections, acronyms, domain
        │                        expansions, and the terms multilingual
        │                        resolved. One list of {term, weight, kind}.
        ▼
 lib/knowledge-search.js         rankEntities: EXACT ▸ PREFIX ▸ WORD ▸
        │                        CONTAINS ▸ RELATED ▸ FUZZY, over names,
        │                        aliases and type labels. Then diversify.
        ▼
 lib/search/universal.js         The index is the union of every live source.
        │                        groupResults arranges the ranked list;
        │                        guidance answers the absence of one.
        ├──────────────► app/api/search/suggest   →  components/search/LiveSearch
        └──────────────► app/knowledge/page.js    →  GroupedResults · NoResultsGuide
```

Everything above `universal.js` predates this milestone and is unchanged. The
ladder, the typo budget, `MIN_SUBSTRING_LENGTH`, the acronym table and the
per-term diversify cap all still do exactly what they did — the additions are a
resolver in front and a wider corpus underneath.

---

## The corpus

`lib/search/registry.js` is the list of everything one box can reach.

| source | status | where it comes from |
|---|---|---|
| Researched knowledge | live | `knowledge.kg_entities` — 19 entity types, 647 rows |
| Research articles & editorial guides | live | `research_articles` ∪ `content/research/*.mdx` |
| Blog posts | planned | — |
| News & updates | planned | — |
| Mentors | planned | — |
| Courses | planned | — |
| Success stories | planned | — |
| Opportunity reports | planned | — |

A planned source has **no loader** and returns nothing. It is declared so the
product can say "mentors are coming" by name instead of showing a reader an
empty page, and so the next person can see the shape a new source has to fit. A
test fails if a planned source acquires a loader — a loader that returned three
plausible mentors would be the most damaging thing that file could do.

**Adding a source is one object and one function.** It is not a change to the
ranker, the route, the grouping or any page.

### Documents

Everything is projected into the shape `rankEntities` already scores:

```js
{ global_entity_id, entity_type, canonical_name, confidence_score,
  _aliases: ["PMEGP", "Entrepreneurship"],   // optional: other names it answers to
  _href: "/knowledge/scheme/…" }
```

An article becomes a document; the ranker was not taught about articles. One
ladder, one set of rules about what beats what, for every kind of content.

`_aliases` is matched **after** the name and **before** the type, at 0.9× the
rung it earns. So an article tagged `warangal` is findable by "Warangal" and can
never outrank the district Warangal.

---

## The vocabulary, in two halves

**Curated** — `lib/search/vocabulary/concepts.js`. What a person *means*.
English synonyms, Telugu script, Tanglish. 53 concepts. Judgement, so a human
writes it. See the README next to it before editing; four rules are enforced by
tests, including "no districts" (transliteration covers all 61 without a row).

**Generated** — `lib/search/vocabulary/entity_aliases.js`, from
`scripts/build_search_aliases.py`. What the packages *already say*: a scheme's
`short_name`, the `original_china_concept` a business was adapted from, the
category a row was filed under. Nothing invented, nothing translated — a test
asserts every alias appears verbatim in a dataset. `--check` fails the build if
it has drifted, so a package release that adds a scheme cannot leave its
abbreviation unsearchable.

### A data defect this surfaced, reported not fixed

`packages/Package006_Skills_and_Training/datasets/skills.csv` files **42 of its
45 skills under `Soft Skills & Communication`** — Python Programming, Full Stack
Web Development, Electrician, Welding — all sharing one `category_id`. Three
rows carry a real category (Electronics, Agriculture, Food Processing).

Importing that would have made a search for "communication" return Python
Programming with the platform's badge on it, so the generator drops any category
that covers more than 40% of a dataset **which has other categories**. A column
with one value throughout is a scoped dataset, not a defect — every row of
`construction_skilled_trade_services.csv` is construction, and that alias is
kept and useful.

The filter is a filter. The rows are research data and correcting them is the
research team's call, not a search milestone's. Same for
`food_agro_processing_micro_enterprises.csv:category` and
`government_hospitals_telangana_andhra_pradesh.csv:category`, both flagged by
the same rule.

---

## Ranking, and where personalisation will go

`rankEntities(entities, query, { limit, entityType, boost })`.

`boost(entity)` returns a **multiplier** and defaults to 1 — today's exact
behaviour. Nothing supplies one. When something does, ranking differently for a
student, an entrepreneur, an investor, a farmer or a working professional is a
function passed at the call site, not a rewrite of the ranker, and the ranker
never learns who the reader is.

Multiplier and not an additive bonus, deliberately: adding points could lift a
FUZZY hit above an EXACT one and make a personalised search return the wrong
thing *confidently*, which is the failure that would cost the most trust.
Scaling preserves the ladder — the rungs (1000 / 700 / 500 / 300 / 220 / 120)
are far enough apart that a sane boost cannot cross one.

The audience vocabulary already exists in `lib/audiences.js` and `/start/[audience]`.
The natural first implementation is a per-audience `entity_type` weighting —
farmer favours Crop and GovernmentScheme, entrepreneur favours
BusinessOpportunity and FinancialInstitution — read from the profile the
onboarding flow already collects. **No code for that has been written.**

---

## Voice search — what is already true

Voice arrives as a transcript, so it enters the pipeline at exactly the point
typing does. Three things that had to be right for it are:

- **Telugu is resolved, not just tolerated.** `"మెదక్‌లో ఎలక్ట్రిషియన్ అవకాశాలు"`
  transliterates and resolves per word, and word-level resolution runs whenever
  the whole phrase does not land on a concept — which is what a spoken sentence
  looks like.
- **Stop words are stripped** for the postpositions that appear as separate
  tokens (`lo`, `ki`, `ku`, `na`, `in`, `for`, `of`).
- **Multi-word queries fall back to their words.** "lift technician" finds
  "Forklift and Material Handling Equipment" through "lift" alone, because the
  phrase rule needs every word present and half an answer beats a blank page.

What is missing is only the microphone: a `SpeechRecognition` capture that sets
the same state `LiveSearch` already sets from the keyboard. **Not implemented.**

---

## An AI search assistant — what it would need

*"I completed Intermediate MPC. What business can I start in Medak with ₹5 lakh?"*

Three of the four pieces exist:

1. **Resolution** — `resolveQuery` already turns a sentence into concepts plus
   the English terms behind them, in any of the three languages.
2. **Retrieval** — `universalSearch` already ranks one corpus spanning
   districts, businesses, schemes, skills, articles and training, and
   `groupResults` already separates them by kind, which is the shape a prompt
   wants.
3. **Provenance** — every document carries `source_package`,
   `confidence_score` and `verification_status`, so an answer can cite what it
   was built from, which is the difference between an assistant and a
   plausible-sounding liar.

What is missing is the composition step: constraint extraction (₹5 lakh,
Intermediate MPC, Medak) and a generator. Both are new work, and neither belongs
in the search path — the right shape is a caller that runs `universalSearch`
several times and composes, exactly as `guidance` composes today. **Not
implemented.**

---

## Cost

| | |
|---|---|
| Index build | once per server process; ~660 documents |
| Ranking | in memory, sub-millisecond; no query per keystroke |
| Suggest wire | ~2 KB out per request, debounced at 140 ms, after 2 characters |
| Suggest cache | `s-maxage=60, stale-while-revalidate=300`; nothing in the answer depends on the visitor |
| Browser payload | the index never leaves the server — that is why the route exists |

The 400 ms-per-keystroke round trip the in-memory ranker was built to avoid has
not come back: `/api/search/suggest` ranks an index that is already in memory
and returns eight rows.

---

## Failure behaviour

Every layer fails to *empty*, never to an error, matching the contract
`lib/knowledge.js` has used since Step 2.

- A source whose loader throws contributes nothing; the rest of search works.
- The index is **not** cached when empty, so one cold start cannot leave search
  blank for the life of the process.
- `/api/search/suggest` returns `{items: []}` with status 200 on any exception.
  A search box that errors while you type is worse than one that finds nothing:
  it is the only signal the reader gets and it says the site is broken.
- With the route unreachable the box degrades to the plain form it used to be —
  the Search button still navigates to `/knowledge?q=…`.

---

## Never a dead end

`guidance(query)` runs when a search returns nothing **and when it returns
fewer than three results**, because one row is a coverage gap wearing the
costume of an answer.

It offers, in this order: a correction (`didYouMean`, by edit distance *and*
phonetic key, since spelling by ear is the more common mistake here and no typo
budget reaches it); related rows grouped and labelled with the term that reached
them; the search terms that would have worked; and a one-tap request that writes
to `user_requests` — the queue the research work already runs from.

Everything offered is checked against the index before it is rendered. A
suggestion that leads to a second empty page is a second dead end and worse than
silence.

---

## Known gaps

- **Content, not search.** "Lift Technician" has no entity and no article;
  "Dairy" has one adjacent row. Search now says so and offers to research it.
  Those are collection tasks, not ranking bugs.
- **`research_articles` is not in the `knowledge` schema** and is read with a
  second Supabase client. Deliberate — it is application content with its own
  RLS — but it means article search and knowledge search have different
  freshness.
- **No browser test in CI.** The keyboard navigation, the highlight and the
  panel layout were verified in Chromium at 390px by hand against a production
  build. The suite asserts their source, which would catch removal but not a
  rendering fault.
