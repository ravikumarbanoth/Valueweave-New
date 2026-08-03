# Admin, DevOps & Knowledge Operations

**Status: the highest-value subset is built and running. The rest is reviewed, sized and ordered.**

```bash
python3 -m ops.cli status            # the one-screen answer
python3 -m ops.cli quality --verbose # seven dimensions and their formulas
python3 -m ops.cli integrity         # what is broken
python3 -m ops.cli report --write    # the weekly report
python3 -m collection.cli queue      # ranked, most important first
python3 tests/run_all.py --suite operations
```

Everything reads committed artifacts. No new table, no migration, no query except
one for live search demand.

---

## 1. Architecture review

### The finding

**Thirty admin pages, and not one of them looks at the knowledge platform.**

| what the admin panel covers | what it does not |
|---|---|
| opportunities, collaborators, founder matches | the 647 entities and 865 relationships |
| page views, visitor sessions, search events | the eight knowledge packages |
| research articles, SEO, GEO, announcements | the vocabulary crosswalk |
| engagement, retention, notifications | the sync manifest and run log |
| districts / skills / schemes **CMS** (`public.kg_*`) | the collection queue and source registry |
| | the stewardship ledger |

Every table those pages read is `public.*` application data. The page called
"Graph Dashboard" reads `lib/knowledge-graph.js`, which is the older `public.kg_*`
CMS tables — not the `knowledge` schema the platform actually runs on.

So the operational half of ValueWeave was invisible from the panel it is
operated from. That is the gap this milestone closes, and it is why the answer
is **one page**, not twenty: the problem was never a shortage of admin screens.

### Three more findings, from looking rather than guessing

**Several admin pages render over tables with no writer.** `opportunity_views`,
`activity_log`, `weekly_digests`, `founder_matches` and `admin_notifications`
are read by admin pages and written by nothing outside `/admin`. That is the
same pattern as `search_events` before last milestone: a dashboard over an empty
table, indistinguishable from a dashboard over a quiet week.

**`knowledge-sync.yml` declared no `permissions:` block**, so it inherited the
repository's default token scope. Fixed in this milestone — see §8.

**There was no rate limiting anywhere**, including on `/api/search/suggest`,
which is the frontend's only public API and scans ~660 documents per request.
Fixed in this milestone — see §8.

---

## 2. Admin dashboard proposal — **built**

One page: `/admin/knowledge-ops`. Two sources and nothing else.

**The snapshot** — `frontend/lib/ops/snapshot.json`, composed by
`python3 -m ops.cli snapshot --write` from artifacts already in Git:
`graph_summary.json`, `validation_summary.json`, `crosswalk_summary.json`, the
sync manifest and log, `collection/state/*`, `compatibility_report.json`.

**Live search demand** — one query against `search_events`, the only thing on
the page that is about readers rather than about us, and the only thing that
changes by the hour.

Three consequences, each of them the reason for the design:

- **Every number is reproducible.** Anyone can run `python3 -m ops.cli status`
  and get the same figures. A dashboard whose numbers cannot be checked stops
  being trusted the third time it surprises somebody.
- **It needs no database change.** No RLS policy, no service role, no new
  table, no migration.
- **Staleness is visible.** The snapshot carries its generation time, the page
  says so out loud when it is more than two days old, and
  `ops.cli snapshot --check` fails a pull request whose graph changed without a
  regenerated snapshot. A dashboard showing yesterday's numbers is worse than
  one showing none, because it looks current.

It carries the whole of the brief's Part 2 list except the items that need
signals nothing writes yet (approved/rejected today — the ledger is empty; page
views per entity — no writer per entity). Those show as UNKNOWN, not zero.

---

## 3. DevOps improvements

### Done

| | |
|---|---|
| **Environment validation** | the source registry resolves every collector and parser at load, so a typo fails immediately with the offending string, not three stages later |
| **Health checks** | `ops.cli status` exits 2 on critical; `collection.cli health`; `scripts/health_check.sh` unchanged |
| **Generated artifact handling** | `ops.cli snapshot --check` fails CI on drift, matching `build_crosswalk.py --check` and `build_search_aliases.py --check` |
| **CI/CD** | two new workflows, both least-privilege, both ending at a pull request |
| **Migration verification** | unchanged and already good — `knowledge_sync/generate_migration.py` plus the dry-run default |

### Recommended, not done — with sizes

| item | why it matters | size |
|---|---|---|
| **Structured logging** | `print()` throughout. Fine at this scale; the moment a scheduled run fails at 04:00 and somebody needs to know which source, a `logging` call with a source id is the difference between five minutes and an hour. `logging` with a JSON formatter, one config module. | S |
| **Configuration management** | `DATABASE_URL`, `SUPABASE_URL`, `NEXT_PUBLIC_*`, `ADMIN_EMAILS`, `PRODUCTION_URL` are read ad hoc in eight places. One `config.py`/`env.js` that validates at start and lists what is missing. | M |
| **Backup strategy** | **The most under-covered item on this list.** Git is the source of truth for knowledge and is backed up by being Git. `public.*` — profiles, opportunities, requests, search events — is not, and none of it can be rebuilt from Git. Supabase PITR plus a weekly `pg_dump` of the public schema to object storage. | M |
| **Disaster recovery checklist** | The knowledge half is genuinely recoverable: `sql/deploy_knowledge.sql` then `scripts/sync.sh --apply` rebuilds it from Git. Nobody has ever done it from cold. One rehearsal, written down. | S |
| **The artifact churn** | `knowledge_graph/*.csv`, `graph_summary.json` and `compatibility_report.json` regenerate on every test run, so `git status` is never clean and a real change hides among them. Deferred by you to an engineering cleanup sprint; it now also makes the ops snapshot check skip locally. | S |
| **Error reporting** | No Sentry, no alerting. The workflows fail loudly in Actions and that is all. Fine while one person operates this; not fine at three. | S |
| **Performance monitoring** | No timing anywhere except `collection`'s per-source `duration_ms`. Add the same to sync and to the search route. | S |
| **Developer documentation** | Genuinely strong — every module carries its reasoning. What is missing is a single `CONTRIBUTING.md` naming the five commands somebody needs on day one. | S |

---

## 4. Knowledge operations proposal — **built**

`ops/` composes what exists and adds the three things nobody computed.

```
ops/
├── metrics.py     the snapshot: overview, connectivity, freshness, demand
├── quality.py     the seven-dimension score
├── integrity.py   the operational checks the graph checks pass over
├── report.py      the weekly intelligence report
├── cli.py         status · quality · integrity · entities · snapshot · report
└── reports/       one markdown and one JSON per week, in Git
```

**Per-entity operational metadata** (Part 4) — `ops.cli entities`: created, last
updated, last reviewed, source, confidence, connected entities, popularity,
freshness, research status. Admin only; none of it is a public claim.

`last_reviewed` is **None on every row**, because `stewardship/review_ledger.csv`
holds only its header. That is a fact worth showing, not one worth filling in.

---

## 5. Feed prioritisation framework — **built**

`collection/priority.py`. Nine factors, each returning points **and a sentence**,
mapped to five star bands.

```
★★★★☆  GovernmentScheme — Margin Money Subsidy Scheme for micro enterprises
        GovernmentScheme is worth 34; reads as "subsidy"; a TG source
★★★☆☆  BusinessOpportunity — Solar rooftop installation opportunity in Medak
        BusinessOpportunity is worth 30; a TG source; names Medak
★☆☆☆☆  News — Office circular regarding holiday list
```

| factor | notes |
|---|---|
| category | a scheme a student can apply to outranks a report about their sector |
| impact | "policy", "mission", "launched" up; "office circular", "tender" down |
| source reliability | scaled to ±10 — it breaks ties, it does not promote a circular past a scheme |
| state and district | districts read **from the graph**, not hard-coded; both states have reorganised theirs recently |
| search demand | from the research backlog — the only factor connecting the queue to real users rather than to our own taxonomy |
| recency | capped at +6 and cannot lift an item a full star, or an hourly feed owns the top of the queue forever |
| duplicate | −40 |
| supersedes | +18 — an amendment is the most valuable thing this pipeline catches, because knowledge going stale is otherwise invisible |

Rules and not a model, for the reason that matters: a priority decides what
somebody spends their morning on, and if they cannot see **why**, they cannot
tell a good ranking from a broken one. The first time it is wrong and
unexplainable they go back to reading top to bottom, which is where we started.

Ranked over the **whole queue** after merging, so a four-star item from last
week does not sit below a two-star one collected this morning. The queue file is
written in that order, because it is read by people as well as by software.

---

## 6. Editorial workflow review — **reviewed, not rebuilt**

The brief's workflow and the one in the repository are the same:

```
brief        Collected → Needs Review → Approved → Rejected → Needs Update → Published
lifecycle    COLLECTED → VALIDATED   → REVIEWED → APPROVED → PUBLISHED → ARCHIVED
```

`stewardship/` implements it with an append-only ledger, an actor and evidence on
every transition, and the rule that `APPROVED` is the only state a machine may
not enter. It is complete and it has never been used.

**So the gap is not the workflow. It is that nobody has run it once.**

Building a second review UI before the first review has happened would be
building for a user who does not exist yet. What this milestone did instead:
made the queue **ranked** and **explained**, so the first reviewer starts with
the right item and can see why.

What a reviewer can see today, from `collection.cli queue` and the queue file:
source, original URL, the raw record verbatim, the classification and the words
that produced it, duplicate probability with the measured overlap, whether it
supersedes something, and the priority with its reasons.

What is missing, in order of value:

1. **Compare with existing knowledge** — show the nearest existing entities
   beside a candidate. The search engine already does this; it needs wiring, not
   inventing. **M.**
2. **Send back / needs update** — the ledger supports it; the CLI has no verb. **S.**
3. **A web review surface** — after a human has run the CLI loop end to end at
   least once. Building it first guesses at what a reviewer needs.

---

## 7. Monitoring improvements — **built**

`ops/integrity.py`, seven checks, none duplicating the eleven G-checks. Those are
**correctness** checks and they pass; these are the failures that pass them.

| check | severity | threshold | rationale |
|---|---|---|---|
| `broken_references` | CRITICAL | any | an edge pointing at nothing |
| `data_drop` | CRITICAL | >15% against the sync manifest | **the most dangerous silent failure here** — the sync soft-deletes, the site keeps working, the graph validates, and nobody finds out |
| `graph_validation` | CRITICAL | last result ≠ PASS | |
| `isolated_entities` | WARN / CRITICAL | >10% / >25% | findable by search, leading nowhere |
| `missing_relationships` | WARN | a type with zero edges | a builder step that was never written |
| `crosswalk_health` | WARN | <40% resolved | personalised features degrade with no error |
| `malformed_source_urls` | WARN | any | shape, not reachability — offline by design |

Plus the seven feed checks from `collection/monitor.py`.

**What it found on the real graph, today:**

- **142 of 647 entities (22%) connect to nothing** — Certification (30),
  TrainingProvider (22), GovernmentScheme and others.
- **Certification has zero edges of any kind.** Thirty certifications, and
  nothing about a skill can ever lead to the certificate that proves it.
- **30 `source_url` values are not URLs** — "Internal package mapping" in a
  column meant for a citation.

Still not monitored, and honestly: Supabase status (no health endpoint is
polled), search index health (the index is built per process and never
observed), and sync duration (nothing times it).

---

## 8. Security recommendations

### Fixed in this milestone

**`knowledge-sync.yml` declared no `permissions:`**, so it ran with the
repository's default token scope. It reads a checkout and writes to Supabase
with a secret; it had no reason to be able to push a commit, and a workflow that
*can* push is a workflow that can be made to push. Now `contents: read`. The two
newer workflows declare `contents: write` + `pull-requests: write` because they
genuinely open pull requests, and nothing more.

**`/api/search/suggest` had no rate limit.** It is the frontend's only public API
and every request scans ~660 documents. Now 60 requests per 10 seconds per
address — generous against real use, since the box debounces at 140ms and a fast
typist makes about seven in ten seconds. In-process and deliberately so: a shared
store would be correct across instances and would cost a Redis or a Supabase
round trip per keystroke, which is more than the abuse it prevents. A 429 returns
an empty list, so a limited visitor keeps their last suggestions and a working
Search button instead of an error.

### Reviewed and sound

| | |
|---|---|
| **RLS** | 23 of 23 `public` tables enable it. `knowledge.*` enables it on every projected table in `sql/deploy_knowledge.sql`, with anon granted `select` only. |
| **Service role** | never appears in `frontend/`. CI secret and server-side only, as the standing rule requires. |
| **Admin gate** | `profiles.is_admin` with an `ADMIN_EMAILS` bootstrap. The dev bypass is keyed on `NODE_ENV === "development"`, which `next build` sets to production — safe. RLS is the real boundary and the gate is for routing. |
| **Secrets** | four, all in Actions, none in a file. |

### Recommended

| item | severity | size |
|---|---|---|
| **`next dev` on a public port is wide open** — the admin bypass is unconditional in development. Add a `VW_ALLOW_DEV_ADMIN` opt-in so the bypass needs two things to be true. | Medium | S |
| **Audit logging** — the stewardship ledger covers knowledge decisions. Nothing records who read or changed `public.*` from `/admin`. | Medium | M |
| **Distributed rate limiting** — the in-process limiter stops a script, not a botnet. A CDN or WAF rule is the right layer. | Low today | M |
| **Dependency scanning** — no Dependabot, no `pip-audit`, no `npm audit` in CI. | Medium | S |
| **Pin action SHAs** — `peter-evans/create-pull-request@v6` is a moving tag with write permissions. | Medium | S |

---

## 9. Scalability recommendations

| scale | what breaks first | when to act |
|---|---|---|
| **10,000 entities** | Nothing structural. The in-memory search index becomes ~1 MB per process and the ops snapshot ~2 MB; both fine. The admin snapshot should stop embedding per-entity rows. | comfortable |
| **100,000 entities** | **The in-memory search index.** Ranking 100k documents per keystroke is 50–100ms of CPU per request and the index is rebuilt per process. Move to Postgres full-text plus `pg_trgm` — which the search was explicitly designed to defer, not to avoid. The vocabulary and multilingual layers keep working unchanged; only the ranking substrate moves. |
| | The CSV-based graph build. `entities.csv` at 100k rows is ~15 MB and every tool reads it whole. Parquet, or build directly to the database. |
| | `git status` and diffs on package CSVs. Split datasets per district or per year. |
| **1,000,000 entities** | Everything above, plus the sync's full-manifest comparison — 1M row hashes in one JSON file is not a manifest, it is a database. Move to a `sync_state` table, keeping the "compare against what we wrote, not against the target" rule. |
| **More feeds** | **~20 sources.** Politeness first: per-host rate limiting, `robots.txt`, backoff with jitter. Then the collection run needs to be concurrent — it is sequential today and 200 sources at 400ms each is 80 seconds, which is fine, until one hangs. |
| **More reviewers** | **Two.** The queue is one JSONL file in one branch; two reviewers merging simultaneously conflict. Split by `classified_as` or by source, one branch each. |
| **Regional teams** | The registry already carries `state` and `country`. What is missing is ownership: nothing says who reviews Telangana. One column, plus a filter in the CLI. |
| **International** | The genuine blocker is the multilingual concept table, which is Telugu-specific by design. The *architecture* generalises — transliteration is a character pass and the phonetic key is script-agnostic — but every new language needs its own transliteration table and its own curated concepts. Budget a month per language, not a sprint. |

**The honest headline: none of these is the binding constraint today. The
binding constraint is reviewer time**, which is why this milestone spent its
budget on ranking the queue rather than on scaling anything.

---

## 10. Risks

| risk | severity | mitigation | still open |
|---|---|---|---|
| **The review loop has never run.** The ledger is empty, all 647 entities are PUBLISHED having never been REVIEWED, and automation now adds candidates. | **High** | the queue is ranked and explained, so the first reviewer starts well | Nobody is assigned. Unchanged from last milestone and still the top risk. |
| **The snapshot goes stale and nobody notices.** | Medium | the page says its age out loud above two days; `--check` fails a PR | Depends on the workflow running. |
| **A quality score becomes a target.** 73 (B) invites "get it to 80", and the cheapest way to move it is not the most valuable work. | Medium | the seven dimensions are always shown beside it, each with its formula | Judgement. |
| **Priority rules drift from what reviewers actually want.** | Medium | every score shows its reasons, so disagreement is visible | No feedback loop from a reviewer's decisions back into the weights. |
| **Backups.** `public.*` cannot be rebuilt from Git and is not backed up. | **High** | none | §3. The largest un-mitigated risk in the repository. |
| **Dashboards over tables with no writer.** Five admin pages read tables nothing writes. | Low | documented in §1 | Each is a small wiring job or a deletion. |

---

## 11. Before vs after

```
BEFORE                                  AFTER

 admin panel                             admin panel
 ├─ 30 pages                             ├─ 30 pages, unchanged
 └─ all reading public.* app data        └─ + /admin/knowledge-ops
                                            reading a committed snapshot
 knowledge platform
 ├─ 647 entities        ─┐               knowledge platform
 ├─ 8 packages           │               ├─ quality 73 (B) over 7 dimensions
 ├─ crosswalk            ├─ no admin     ├─ 7 integrity checks, 3 findings
 ├─ sync manifest        │  view at      ├─ per-entity operational metadata
 ├─ collection queue     │  all          ├─ weekly report, in Git, a series
 └─ stewardship ledger  ─┘               └─ one screen showing all of it

 review queue                            review queue
 └─ chronological, unexplained           └─ ★-ranked over the whole queue,
                                            every score showing its reasons

 monitoring                              monitoring
 ├─ sync health                          ├─ sync health
 └─ feed health                          ├─ feed health
                                         └─ + graph operational integrity

 security                                security
 ├─ sync workflow: inherited token       ├─ sync workflow: contents: read
 └─ public API: no rate limit            └─ public API: 60 per 10s per address
```

| | before | after |
|---|---|---|
| admin views of the knowledge platform | 0 | 1 |
| operational metrics computed | 0 | 7 quality dimensions + 7 integrity checks |
| review queue ordering | arrival | priority, explained |
| weekly reporting | none | markdown + JSON in Git, diffable |
| workflows with declared permissions | 0 of 1 | 3 of 3 |
| public API rate limiting | none | 60 / 10s / address |
| database changes | — | **none** |
| tests | 937 | 976 |

---

## 12. Recommended implementation order

**Done — this milestone.** Feed priority (Part 1), the knowledge-ops dashboard
(Part 2), operational metadata (Part 4), the weekly report (Part 5), gap
intelligence extended with priority (Part 7), operational monitoring (Part 8),
the quality score (Part 9), and two security fixes.

**Next, in order, and the first one is not a coding task:**

1. **Run the review loop once, end to end.** One person, one afternoon, from a
   ranked candidate to an entity in a package. Everything else on this list is a
   guess until that has happened. *Highest value on the list.*
2. **Back up `public.*`.** PITR plus a weekly `pg_dump`. **M.** The largest
   un-mitigated risk in the repository.
3. **Fix what integrity found.** Certification has no edges — that is a builder
   step, and it makes 30 rows unreachable. **M.**
4. **Compare-with-existing in the review queue.** The search engine already does
   the work. **M.**
5. **Structured logging and one config module.** **S + M.**
6. **Pin action SHAs, add dependency scanning, gate the dev admin bypass.** **S.**
7. **Politeness before scale** — per-host limits, `robots.txt`, backoff — before
   the twentieth feed. **M.**
8. **Then** a web review surface, and only then.

**Explicitly not on this list:** any AI component, and any scaling work. Neither
is the binding constraint, and both would consume the budget the first item
needs.

---

## 13. Future AI readiness — architecture only

Nothing implemented, and the boundary is already enforced by the tests written
in the collection milestone:

| capability | where it attaches | what does not change |
|---|---|---|
| Research summarisation | a field on a candidate | `raw` survives verbatim to approval |
| Entity extraction | a classifier beside `classify.py` | it must carry its evidence, as the rules do |
| Relationship suggestions | a new candidate kind | proposed, never written to the graph |
| Classification | a `Rule`-shaped adapter | `UNCLASSIFIED` stays a legitimate answer |
| Duplicate detection | a scorer beside `dedupe.py` | nothing is ever deleted, only grouped |
| Content recommendations | reads the snapshot | it may not close a gap by inventing one |
| Editorial assistance | reads the queue | it cannot enter `APPROVED` |

Three properties make it safe, all of them already true and already tested:
everything enters the same queue; the queue cannot approve; the raw record is
carried verbatim. **An AI proposal is a candidate with a different author, not a
different pathway.**

---

## What this milestone does not do

- **No reviewer has used any of it.** The queue is ranked; nobody has read it.
- **No live feed is collected**, so the priority scores rank fixtures.
- **`popularity` is UNKNOWN on every entity.** Per-entity view counts have no
  writer; the score excludes the dimension rather than scoring it zero.
- **`last_reviewed` is None on every entity**, because it truthfully is.
- **The dashboard is one page, not twenty.** Parts of the brief's Part 2 list
  that need signals nothing writes yet — approved today, rejected today — are
  absent rather than shown as zero.
- **No AI, no scaling work, no second review UI.**
