# Automated Knowledge Collection & Continuous Update Framework

**Status: built and running against local fixtures. No live feed is active.**

```bash
python3 -m collection.cli sources
python3 -m collection.cli run --force
python3 -m collection.cli health
python3 tests/run_all.py --suite collection      # 54 tests
```

---

## 1. Architecture review — what already existed

The most useful thing this milestone could do was find out what was already
built, because most of it was. Building a second collection framework beside the
first would have been the repository's own worst mistake — two search
implementations — repeated at platform scale.

| Brief phase | Already existed? | Where | What was actually missing |
|---|---|---|---|
| 1 · Source registry | **Partly** | `source_registry/sources.csv`, 605 rows | It is *derived* — regenerated from every URL the eight packages cite — so it inventories what published data depends on, not what we monitor. No feed URLs, no schedule state, no category/state/tags. 604 of 605 rows name the same collector/parser pair because the assignment is a routing guess, and the builder says so in its own docstring. |
| 2 · Feed engine | **Yes** | `knowledge_engine/collectors/` (api, csv, json, rss, xml), `parsers/` (csv, html_table, json, pdf, rss, xml) | Nothing had ever called it. Its own README: *"no source has yet been collected by this engine."* And no conditional-request support, so every fetch downloaded everything. |
| 3 · Change detection | **Partly** | `knowledge_sync/changes.py` — manifest + row hash, for Git → Supabase | Nothing for source → Git. `update_engine.default_change_detector` is `previous != current` on the whole list. |
| 4 · Classification | **No** | — | Nothing classified an incoming item. |
| 5 · Deduplication | **No** | — | Nothing. |
| 6 · Human review | **Yes** | `stewardship/` — seven-state lifecycle, append-only ledger, CLI, store | Complete and unused. `stewardship/review_ledger.csv` holds one line: the header. |
| 7 · Research backlog | **No** | `search_events` table + `lib/search-tracking.js` | **`trackSearch` had zero callers.** Every no-result search since launch was discarded at the moment it happened. `/admin/search-intelligence` renders a "content gaps" panel over an empty table and says so in its own copy. |
| 8 · Monitoring | **Partly** | `knowledge_sync/metrics.py`, `scripts/health_check.sh` | Both watch the sync. Nothing watched a feed. |
| 9 · Plug-and-play | **Partly** | `CollectorRegistry` | No declarative source → run path. |
| 10 · Future AI | **Yes, as a document** | `knowledge_engine/docs/ai_integration_plan.md` | Nothing to build. It needed to stay honest. |

**Conclusion: this was a wiring problem, not a building problem.** Roughly 70%
of the machinery existed; what was missing was the spine connecting the registry
to the engine to the ledger, and four genuinely new components (change
detection at the source, classification, deduplication, the backlog).

---

## 2. Data-flow findings

**The engine had no caller.** Seventeen modules and 117 passing tests, and the
first line of its README recording that none of it had ever run. A test suite on
a library nobody invokes proves the library works, not the product — this
repository already paid for that lesson once, in the search outage where a
ranking engine with no caller sat beside an `ilike` everybody used.

**The review ledger was empty.** All 647 entities are `PUBLISHED` having never
passed through `REVIEWED` or `APPROVED`, because no steward existed to perform
those transitions. `lifecycle.effective_state()` reports that gap rather than
hiding it. Automation makes this urgent: a pipeline that adds candidates faster
than anyone reviews them turns an empty ledger into a growing one.

**Two files would have been called a "source registry".** The existing one is
derived and answers *what does our published knowledge cite?* The new one is
authored and answers *what do we check for changes?* They are different
questions and both are worth answering, so they are separate files with
different names and a documented relationship — monitoring is the front of the
pipe, citation is the back.

**Configuration and state were listed together in the brief.** "Name" and "URL"
are decisions reviewed in a diff. "Last checked" is a fact a machine writes every
run. In one file, every scheduled run dirties the file a human authored, and the
diff that should read *someone added a source* instead shows forty timestamps
with one real edit hidden among them. They are split; `registry.load()` joins
them so a caller sees all twelve fields as one object.

**A feed that stops publishing looks exactly like a feed that is up to date.**
Both produce zero new items. The difference is only visible in the *source's*
state, never in the output — which is why every metric in `monitor.py` is about
sources rather than records.

---

## 3. The framework

```
 public source
      │  RSS · Atom · JSON Feed · XML · REST · CSV · dataset
      ▼
 collection/registry.py          what to check, how often, may it be checked
      │                          ├─ monitored_sources.csv   configuration (human)
      │                          └─ state/fetch_state.json  state (machine)
      ▼
 knowledge_engine/collectors/    conditional HTTP: If-None-Match ▸ 304 ▸ stop
      ▼
 knowledge_engine/parsers/       named by the registry; nothing sniffs
      ▼
 collection/detect.py            NEW · UPDATED · UNCHANGED · DISAPPEARED, per item
      ▼
 collection/classify.py          which type, and the words that decided
      ▼
 collection/dedupe.py            exact · near · version-update
      ▼
 collection/review.py            COLLECTED ▸ NEEDS_REVIEW      ← the queue, in Git
      ▼
 ─────────────────────────  a person  ─────────────────────────
      ▼
 stewardship/                    REVIEWED ▸ APPROVED, with an actor and evidence
      ▼
 packages/                       a package release, by hand
      ▼
 knowledge_sync/                 Git ▸ Supabase, existing workflow
      ▼
 search
```

Everything above the dashed line is automated. Nothing crosses it without a
person. The two GitHub workflows are deliberately not joined: `knowledge-collect`
ends at a pull request, `knowledge-sync` starts at a push to main, and the gap
between them is the approval.

---

## 4. Folder structure

```
collection/
├── README.md                       how to add a source; what this cannot do
├── __init__.py
├── registry.py                     the registry, its schema, and fetch state
├── registry/
│   └── monitored_sources.csv       CONFIGURATION — human-authored, reviewed in PRs
├── state/                          MACHINE-WRITTEN — committed, reviewed in the PR
│   ├── fetch_state.json            etag, last-modified, content hash, item hashes
│   ├── review_queue.jsonl          the candidates. The diff IS the queue.
│   ├── last_run.json               what the last run did, for the monitor
│   └── research_backlog.json       gaps, not knowledge
├── fixtures/                       four local feeds — RSS, Atom, JSON Feed, CSV
├── detect.py                       change detection, transport and per item
├── classify.py                     the taxonomy, as data
├── dedupe.py                       exact, near, version
├── review.py                       the candidate queue
├── backlog.py                      what people searched for and we lack
├── monitor.py                      feed health
├── runner.py                       the sequencing, and nothing else
└── cli.py                          one entry point

scripts/dev/fake_feed_server.py     real ETag/304 semantics, for the tests
.github/workflows/knowledge-collect.yml
tests/test_collection.py            54 tests
docs/COLLECTION_ARCHITECTURE.md     this file
```

**Unchanged:** `packages/`, `knowledge_graph/`, `knowledge_sync/`,
`stewardship/`, `governance/`, `source_registry/`, `search/`, `frontend/lib/`.

**Changed, additively:** `knowledge_engine/collectors/_io.py` gained conditional
requests (ETag and Last-Modified returned in metadata; a `304` is a success with
`not_modified: True`, not an error), and four collectors thread `headers` and
`timeout` through — one line each. All 117 engine tests pass unchanged.

---

## 5. Components built

| component | ~lines | what it decides |
|---|---:|---|
| `registry.py` | 300 | validation, schedule, `runnable`, config/state join, dotted-path resolution |
| `detect.py` | 170 | per-item identity and hashing; four outcomes; volatile-field exclusion |
| `classify.py` | 200 | 18 rules over 13 entity types and 5 non-entity kinds, each carrying its evidence |
| `dedupe.py` | 190 | normalisation, Jaccard over significant tokens, version markers, grouping |
| `review.py` | 190 | the candidate model, merge-without-losing-decisions, the one permitted transition |
| `backlog.py` | 180 | failed searches + open requests → ranked research suggestions |
| `monitor.py` | 210 | six checks with stated thresholds; UNKNOWN where a number cannot be computed |
| `runner.py` | 240 | sequencing; dry-run by default |
| `cli.py` | 240 | six commands |

---

## 6. Database impact

**None. No migration, no new table, no schema change.**

That is a design decision, not an omission. Git is the source of truth for
knowledge; Supabase is a read-optimised cache. A *candidate* is proposed
knowledge, so it belongs in Git. Putting the queue in a table would have needed a
migration, an RLS policy and an admin screen before the first candidate could be
looked at — and would have made the proposal invisible to the review mechanism
the project actually uses, which is a pull request.

Two existing tables are **read** by the backlog and neither is altered:

| table | since | used for | change |
|---|---|---|---|
| `public.search_events` | migration 004 | failed searches | none — it now receives rows for the first time |
| `public.user_requests` | migration 004 | "Request this topic" | none |

The one frontend change is a single call in `components/search/LiveSearch.jsx`:
`trackSearch({ query, page, resultsCount })`, fired on the settled query after
the debounce, so "electrician" produces one event rather than eleven.

---

## 7. Git workflow impact

Unchanged for everything that exists today. One workflow is added.

| | `knowledge-sync.yml` (existing) | `knowledge-collect.yml` (new) |
|---|---|---|
| trigger | push to main, Monday 03:00, manual | daily 04:00, manual, and on PRs touching `collection/` |
| reads | `packages/` | the monitored registry |
| writes | Supabase | `collection/state/*` |
| ends at | a live projection | **a pull request** |

The collection workflow:

- **never commits to main** — one long-lived `collection/review-queue` branch
  that accumulates until somebody merges it, rather than a pull request per run.
  Twelve open PRs is a queue nobody reads, which is the failure this whole
  design exists to avoid.
- **never calls the sync.** A test asserts the string `knowledge_sync` does not
  appear in it. Joining them would put unreviewed material one cron away from
  the live site.
- **runs a dry run on every trigger**, including pull requests, so the reviewer
  adding a source sees what it collects in the same PR that adds it.
- runs at 04:00 against the sync's 03:00, so the two never contend for a
  checkout on the day they coincide, and uses a `concurrency` group so two runs
  cannot both merge into the queue and lose one another's candidates.

**Merging the pull request publishes nothing.** It records what was collected.
Promoting a candidate into a package remains a manual, reviewed act.

---

## 8. Human review workflow

The brief's workflow and the lifecycle that already exists are the same thing:

```
brief          Collected  →  Needs Review  →  Approved  →  Package  →  Git  →  Sync
lifecycle      COLLECTED  →   VALIDATED    →  REVIEWED  →  APPROVED  →  PUBLISHED
```

So this milestone produces `COLLECTED` records and hands them to the machinery
in `stewardship/`, which `governance/DATA_STEWARDSHIP.md` specifies and
`tests/test_stewardship.py` (31 tests) already holds. Three rules from
`lifecycle.py` carry the weight:

1. **No backward transitions.** A published record found wrong is corrected by a
   new package version, never by rewinding state — rewinding destroys the audit
   trail that is the point of tracking state.
2. **Every transition needs an actor.** `VALIDATED → REVIEWED` without a named
   reviewer is a checkbox, not a review.
3. **`APPROVED` is the only state a machine may not enter.**

The collection layer performs exactly one transition — `COLLECTED →
NEEDS_REVIEW` — and a test asserts it cannot reach `APPROVED`. Two more rules
are specific to a queue:

- **A decided candidate is never offered again.** A queue that re-presents
  decided material trains the people reading it to skim.
- **An `UPDATED` item reopens a decided candidate**, because the thing that was
  approved is not the thing that is there now.

A `DUPLICATE` never reaches a reviewer at all.

### The reviewer's loop

```bash
python3 -m collection.cli queue                  # what is waiting, and why
# read collection/state/review_queue.jsonl — `raw` is the record verbatim
python3 -m stewardship.cli review <entity_id> --actor NAME --evidence URL
python3 -m stewardship.cli approve <entity_id> --actor NAME
python3 -m stewardship.cli apply --write         # only this touches a package
```

---

## 9. Monitoring architecture

`python3 -m collection.cli health --json` returns one object: `status`
(`healthy` / `degraded` / `critical`, matching `scripts/health_check.sh`),
`totals`, `findings`, and a per-source table.

| check | severity | threshold | why that threshold |
|---|---|---|---|
| `dead_feed` | CRITICAL | 5 consecutive failures | two is a bad afternoon; five is a dead URL |
| `failing` | WARN | 2 consecutive failures | early warning without paging at 3am for a transient outage |
| `stale` | WARN | 4× the source's own declared interval | "nothing for a week" is alarming for an hourly feed and normal for an annual one |
| `never_verified` | WARN | `PENDING_VERIFICATION` with no successful fetch | the honest state for a URL nobody has proved |
| `never_checked` | WARN | `ACTIVE`, never checked | has the schedule ever actually run? |
| `duplicate_spike` | WARN | >50% of a run, min 6 items | a republishing source, or `item_key` is not identifying items |
| `parser_failure` | WARN | fetched, could not be read | the feed changed shape |

**Freshness for a source never successfully fetched is `UNKNOWN`, not stale.**
`knowledge_sync/metrics.py` states the rule — *a dashboard with an invented
number is worse than one with a missing panel* — and it applies with more force
here, because the entire purpose of this module is to say truthfully whether an
automated system is running.

---

## 10. Future extensibility

**A new feed is a row.** Adding one requires no pipeline code: name a collector
and a parser as dotted paths, declare the type, frequency and item key, verify,
flip the status. The dotted paths are resolved at load, so a typo fails
immediately with the offending string in the message.

**A new category is a string.** `CATEGORIES` in `registry.py`.

**A new classification target is one `Rule`.** No retraining, no migration. A
test asserts every entity target exists in the live graph, so a category cannot
be added that nothing downstream can consume.

**A new source *kind* is one object in `SOURCES`** plus a loader — the same
shape the search source registry uses, deliberately, so the two read alike.

### Future AI — architecture only, nothing implemented

`knowledge_engine/docs/ai_integration_plan.md` already sets the boundary and this
framework preserves it. Where AI would attach, and what stays true:

| capability | where it attaches | what does not change |
|---|---|---|
| PDF extraction | a collector/parser pair named in the registry like any other | its output is records, entering `detect` |
| Long-report summarisation | a field on a candidate, never a replacement for `raw` | the raw record survives to approval |
| Entity extraction | an additional classifier alongside `classify.py` | it must carry its evidence, as the rules do |
| Relationship suggestions | a new candidate kind | proposed, never written to the graph |
| Classification assistance | a `Rule`-shaped adapter | `UNCLASSIFIED` stays a legitimate answer |
| Research assistance | reads `research_backlog.json` | it may not close a gap by inventing one |

Three properties make that safe and they are already enforced: everything enters
the same queue; the queue cannot approve; the raw record is carried verbatim. An
AI proposal is a candidate with a different author, not a different pathway.

---

## 11. Risks

| risk | severity | mitigation now | still open |
|---|---|---|---|
| **Queue outgrows reviewers.** Automation adds candidates faster than people read them; the ledger is empty today. | **High** | duplicates never queue; decided candidates never return; the queue is one PR, not many | No reviewer is assigned. This is an operational commitment, not a code change — and it is the single biggest risk on this list. |
| **A wrong classification is approved.** | Medium | every classification shows the words that fired, so a reviewer can disagree with the reason | Reviewer discipline. |
| **A source changes shape silently.** A feed switches format; the parser returns nothing; zero new items looks like a quiet week. | Medium | `parser_failure` and `stale` checks; `stale` is relative to the source's own cadence | A feed that returns *plausible but wrong* records is not detectable here. |
| **Duplicate merges two real things.** | Medium | threshold 0.8, minimum 3 significant tokens, and **nothing is ever deleted** — duplicates are grouped and marked | Judgement. |
| **A candidate URL is dead.** Six shipped sources are unverified. | Low | `PENDING_VERIFICATION` is never fetched; the monitor reports it | Someone must run `verify` from a network with access. |
| **Fetch state churn.** Every run rewrites `fetch_state.json`. | Low | it is a separate file from the registry; the workflow commits it in the same PR as the queue | Noisy diffs. Accepted, following `knowledge_sync/state/manifest.json`. |
| **Rate limiting / politeness.** | Low | conditional requests mean an unchanged feed costs one bodyless request; frequency is per source | No global rate limiter, no `robots.txt` check, no backoff-with-jitter. Needed before a hundred sources. |
| **Secrets for authenticated APIs.** `data-gov-001` needs a key. | Low | not activated | No secret-injection path yet. |

---

## 12. Before vs after

```
BEFORE                                    AFTER

 human research                            human research     scheduled collection
      │                                         │                     │
      │                                         │             registry ▸ conditional fetch
      │                                         │             ▸ detect ▸ classify ▸ dedupe
      │                                         │                     │
      │                                         │              review queue (Git)
      │                                         │                     │
      └───────────┬─────────────────────────────┴──────────┬──────────┘
                  ▼                                        ▼
             packages/                            a person reviews and approves
                  │                                        │
             knowledge_sync                                ▼
                  │                                   packages/
             Supabase                                      │
                  │                                   knowledge_sync
              search                                       │
                                                      Supabase
                                                           │
                                                        search
 knowledge_engine/  ── 17 modules, 117 tests,      knowledge_engine/ ── called, daily
                       zero callers
 stewardship/      ── complete, ledger empty       stewardship/ ── the approval gate
 search_events     ── table exists, no writer      search_events ── written, and read
                                                                    by the backlog
```

| | before | after |
|---|---|---|
| sources monitored | 0 | 10 registered · 4 active · 6 awaiting verification |
| source formats exercised | 0 | 4 (RSS, Atom, JSON Feed, CSV) |
| unchanged feed costs | full download | one request, no body |
| change granularity | whole payload | per item |
| classification | none | 18 rules, each carrying its evidence |
| deduplication | none | exact · near · version, grouped never deleted |
| review queue | none | JSONL in Git, one pull request |
| no-result searches | discarded | recorded and ranked |
| feed monitoring | none | 7 checks, dashboard-ready |
| tests | 883 | 937 |

---

## 13. Implementation roadmap

**Done — this milestone.** Registry, conditional fetch, per-item change
detection, classification, deduplication, review queue, backlog, monitoring,
scheduled workflow, 54 tests.

**Next, in order:**

1. **Verify and activate two real feeds.** Run `collection.cli verify` on
   `pib-msme-001` and `tg-industries-001` from a network with access; flip the
   status in a pull request. *One person, one afternoon.* This is the step that
   turns a framework into a pipeline, and doing two rather than twenty is
   deliberate — the first real feed will teach things the fixtures cannot.
2. **Assign a reviewer and run the loop once, end to end**, from a collected
   candidate to an entity in a package. Until that has happened once, the
   pipeline's second half is untested by anything but its own unit tests. *This
   is the highest-value item on the list and it is not a coding task.*
3. **Politeness before scale** — a per-host rate limiter, `robots.txt`, and
   backoff with jitter. Needed before roughly twenty sources, not before three.
4. **Candidate → package draft.** Today a reviewer reads `raw` and writes the
   dataset row. `knowledge_engine/package_builder/` exists to generate that
   draft and has never been called either. *The natural next wiring job.*
5. **Backlog into the admin UI.** `/admin/search-intelligence` already has the
   panel; point it at `research_backlog.json`.
6. **Secrets for authenticated APIs** (`data-gov-001`).
7. **Then, and only then, more feeds** — universities, companies, industry
   associations, district industries centres — one reviewed pull request each.

**Explicitly not on this roadmap:** any AI component, until items 1–4 have run
for a month and the review loop is demonstrably keeping up.

---

## 14. What this does not do

Stated plainly, because a framework that overstates itself is worse than one
that does less:

- **No live feed has been collected.** Four local fixtures have. The sandbox
  cannot reach `pib.gov.in`, `msme.gov.in` or `data.gov.in` — the outbound proxy
  answers 403 — so the six real sources are `PENDING_VERIFICATION` and are not
  fetched. Conditional requests, 304 handling and change-on-mutation are tested
  over real HTTP against `scripts/dev/fake_feed_server.py`, which is a stricter
  test than a live feed permits because a live feed cannot be asked to change
  on command.
- **No candidate has been reviewed by a person.** The queue holds 12 fixture
  candidates. `stewardship/review_ledger.csv` still holds only its header.
- **Nothing has been promoted into a package.** That path is manual by design
  and `package_builder/` is still uncalled.
- **The classifier is rules, and rules are wrong sometimes.** Five corrections
  were needed on the first run against the fixtures and are now regression
  tests. It is meant to sort a reviewer's inbox, not to be right.
- **No rate limiting, no `robots.txt`, no backoff.** Fine for four sources,
  not for forty.
