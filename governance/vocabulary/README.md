# Vocabulary Crosswalk — Platform v3.0, Step 0

**Status: built.** The join between what users type and what the knowledge graph knows.

```bash
python3 governance/vocabulary/build_crosswalk.py           # rebuild + report
python3 governance/vocabulary/build_crosswalk.py --check   # CI: exit 1 on drift
python3 -m unittest tests.test_vocabulary                  # 24 tests
```

---

## Why

`profiles.skills` is free text. The graph names skills differently. Before this existed,
**7 of the 57 skills the onboarding form suggests resolved to a graph Skill** — so
Recommended Skills, Skill Gap Analysis and Business Match would all have returned nothing
for most users, silently, as an empty panel rather than an error.

## Results

| Vocabulary | Terms | Resolved | Rate | Before |
|---|---:|---:|---:|---:|
| District | 33 | 33 | **100%** | 84.8% |
| Sector | 22 | 11 | 50.0% | 27.3% |
| Skill | 147 | 39 | 26.5% | 14.3% |
| **Total** | **202** | **83** | **41.1%** | 27.2% |
| **Onboarding skills** *(the rate a real profile joins at)* | **57** | **13** | **22.8%** | **12.3%** |

Matchers that produced them: `EXACT_NAME` 39, `CURATED` 28, `PREFIX` 16, `FUZZY` 0.

**Zero fuzzy matches cleared the 0.88 threshold unambiguously.** The vocabularies are not
near-misses of each other; they are different vocabularies. That is why curation carried
more rows than every automatic matcher except exact naming.

## The remaining gap is data, not matching

119 terms are unresolved, and they split into two kinds:

**110 have no counterpart in the knowledge base at all.** `Accounting`, `Data Entry`,
`Digital Marketing`, `SEO`, `Graphic Design`, `Beautician Services`, `CCTV Installation`,
`Housekeeping Services`, `Teaching`, `Photography` — 50 skills the onboarding form actively
nudges users to claim, that Package006 does not cover. No similarity threshold conjures a
row that does not exist, so lowering the threshold would only produce confident wrong
answers.

**9 span more than one entity** and are recorded as such rather than forced to one:
`EV & Energy` covers Electric Vehicles, Renewable Energy and Power & Utilities;
`AI Engineering` could be Machine Learning Engineer or AI Model Training. The crosswalk is
1:1 by construction, so a partial mapping would silently drop half the meaning. The
candidates are recorded in `notes` so the UI can offer them and a steward can decide.

The unresolved list is therefore two useful things at once: **the honest empty state for
the UI**, and **the Package006 collection backlog** — read it from
`crosswalk_summary.json → collection_backlog`.

Reaching the roadmap's 60% onboarding target requires collecting roughly 30 more skills
into Package006. It is not reachable by editing this crosswalk.

## Design

Five matchers, decreasing evidential strength, first hit wins:

| Method | Fires when |
|---|---|
| `EXACT_NAME` | normalised names identical |
| `ALIAS` | matches a registered graph alias |
| `PREFIX` | exactly one entity name starts with the term |
| `FUZZY` | similarity ≥ 0.88 **and exactly one** candidate clears it |
| `CURATED` | a human decision in `curated_overrides.json`, with a reason |
| `NO_COUNTERPART` | none of the above |

Two candidates above the fuzzy threshold is ambiguity, not a hint — the matcher refuses.
This is the ADR-003 discipline applied to a second problem, for the same reason: a wrong
crosswalk row silently redirects a user and nothing downstream can detect it, whereas a
missing row is visible.

Every curated entry carries a `reason`, because a curated row is a person's assertion and
should be reviewable as one. `Vijayawada → NTR` says outright that it is a city mapped to
its administrative district, not a district.

## Files

| Path | Contents |
|---|---|
| `build_crosswalk.py` | Matchers, extraction, `--check` mode |
| `curated_overrides.json` | Human decisions + multi-target terms, each with a reason |
| `skill_crosswalk.csv` | 147 rows |
| `sector_crosswalk.csv` | 22 rows |
| `district_crosswalk.csv` | 33 rows |
| `crosswalk_summary.json` | Every figure quoted above, plus the backlog |
| `frontend/migrations/009_vocabulary_crosswalk.sql` | The Postgres projection (**not yet applied**) |

Term sources are read directly from the frontend, so the crosswalk cannot drift from what
the app actually offers: `app/onboarding/page.js` (`SKILL_SUGGESTIONS`),
`lib/idea-library/{ideas,sectors,skills}.json`, `lib/districts-data.js`.

## Maintenance

Rebuild whenever the graph changes or a term is added to the app. `--check` in CI fails on
drift. The build **aborts** if a curated override points at a missing entity or the wrong
entity type — it will not write a broken crosswalk.

Adding a mapping means editing `curated_overrides.json` with a reason and rebuilding.
Adding a *skill* means collecting it into Package006 first; the crosswalk can only point
at rows that exist.
