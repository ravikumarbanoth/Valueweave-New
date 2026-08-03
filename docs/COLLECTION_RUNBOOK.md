# Collection Runbook

How to take a public feed and turn it into knowledge a student can find — one
source at a time, with a named person responsible for every fact.

This is the operating manual, not the design document. The reasoning behind the
architecture is in [`COLLECTION_ARCHITECTURE.md`](COLLECTION_ARCHITECTURE.md);
what follows is what to type.

---

## The chain

```
  RSS / Atom / JSON Feed / CSV / REST API
        │
        │  collection.cli verify        ── does it answer? does it parse?
        │  collection.cli run --write   ── fetch, detect changes, classify, de-duplicate
        ▼
  collection/state/review_queue.jsonl        a candidate, not a fact
        │
        │  collection.cli queue         ── a person reads it
        │  collection.cli review        ── a person has read it
        │  collection.cli approve       ── a person takes responsibility for it
        ▼
  stewardship/review_ledger.csv               append-only, names the person
        │
        │  collection.cli promote --write
        ▼
  packages/PackageNNN/datasets/*.csv          Git — the source of truth
        │
        │  knowledge_graph/build_graph.py
        ▼
  knowledge_graph/entities/entities.csv
        │
        │  scripts/run_sync.sh
        ▼
  Supabase `knowledge` schema                 a read-optimised cache
        │
        ▼
  search + /knowledge/<type>/<slug>
```

Four rules hold this together, and none of them is negotiable:

1. **Git is the source of truth.** Supabase is a cache that can be rebuilt from
   Git at any time. Never edit package data in Supabase.
2. **No machine may approve.** `APPROVED` is the one lifecycle state no
   automated step can enter. `--actor` is required on every decision because a
   transition without a named person is a checkbox, not a review.
3. **Never invent a value.** Anything the feed does not supply is written as
   `PENDING_VERIFICATION` and waits for research against a public source.
4. **Every write is a dry run by default.** `run`, `promote` and the sync all
   show you what they would do until you pass `--write`.

---

## Part 1 — Adding a new source

### 1.1 Register it

Sources live in `collection/registry/monitored_sources.csv`, one row each. Add
yours with `status,PENDING_VERIFICATION` — a pending source is never fetched on
a schedule, so registering one is safe.

```csv
source_id,name,url,source_type,category,frequency,reliability,status,owner,notes
ncs-jobs-001,National Career Service — job and training notices,https://www.ncs.gov.in/rss/notices.xml,RSS,Employment,DAILY,80,PENDING_VERIFICATION,r.banoth,central government job board
```

| column | what it does |
|---|---|
| `source_id` | stable key. It prefixes every candidate id, so never reuse or rename one. |
| `source_type` | `RSS`, `ATOM`, `JSON_FEED`, `CSV`, `REST_API`, `HTML` |
| `category` | routes the classifier's priority scoring |
| `frequency` | `HOURLY` `DAILY` `WEEKLY` `MONTHLY` — how often `run` considers it due |
| `reliability` | 0–100. A government primary source is 85+; an aggregator is not. |
| `status` | `PENDING_VERIFICATION` → `ACTIVE` → `PAUSED` / `RETIRED` |

Check it parsed:

```bash
python3 -m collection.cli sources
```

### 1.2 Verify it

```bash
python3 -m collection.cli verify ncs-jobs-001
```

This fetches the URL once, ignoring the schedule and ignoring conditional
headers, and shows you the first three records **as the pipeline sees them** —
including what the classifier made of each one:

```
  status        ok
  http          200
  took          164 ms
  records       100

  first records as the pipeline sees them:
    · [GovernmentScheme] Margin Money Subsidy Scheme for micro enterprises
      GovernmentScheme is worth 34; reads as “subsidy”; a TG source
```

Read the classifications before you go further. `[UNCLASSIFIED]` on every record
means the feed is real but is not ValueWeave knowledge, and the right answer is
usually to not activate it. Wrong classifications mean a rule in
`collection/classify.py` needs a term — fix that first, with a test.

`verify` **does not edit the registry.** It prints the edit to make, because
activating a source is a decision that belongs in a pull request where somebody
can see it.

### 1.3 Activate it

Edit the row: `PENDING_VERIFICATION` → `ACTIVE`. Commit it on a branch and open
a pull request. One source per pull request — that is what makes the decision
reviewable.

---

## Part 2 — Running a collection

### 2.1 Dry run first

```bash
python3 -m collection.cli run --only ncs-jobs-001 --force
```

`--force` ignores the schedule; `--only` limits it to named sources. Neither is
needed in normal operation:

```bash
python3 -m collection.cli run          # everything that is due, dry
python3 -m collection.cli run --write  # …and record it
```

Output:

```
source_id            status          recs  new  upd  dup  queued  classified
----------------------------------------------------------------------------
ncs-jobs-001         ok               100    3    1    0       4  GovernmentScheme×3, Skill×1

  queue: +4 new · 0 reopened · 0 already decided · 4 moved to NEEDS_REVIEW
  16 candidates total — {'NEEDS_REVIEW': 15, 'DUPLICATE': 1}

  DRY RUN — nothing was written. Pass --write to record the queue and state.
```

`new`/`upd` are **per item**, not per payload. A feed whose 100 items are
unchanged but whose build timestamp moved reports 0 new, 0 updated — that is the
change detector working, not a broken fetch.

Second and later runs send `If-None-Match` / `If-Modified-Since`. A well-behaved
server answers `304 Not Modified` with no body, and the run is nearly free.

### 2.2 Check the feeds are healthy

```bash
python3 -m collection.cli health
```

Seven checks: dead sources, stale sources, sources that have never succeeded,
schedule drift, empty responses, classification collapse, and error streaks.
Exit code 2 on `critical`.

---

## Part 3 — Reviewing

This is the part that cannot be automated, and the part the whole design exists
to protect.

### 3.1 Read the queue

```bash
python3 -m collection.cli queue
python3 -m collection.cli queue --state NEEDS_REVIEW --limit 10
```

```
       state          type                 source             title
--------------------------------------------------------------------------
★★★★☆  NEEDS_REVIEW   GovernmentScheme     fix-rss-001        Margin Money Subsidy Scheme…
       └─ GovernmentScheme is worth 34; reads as “subsidy”; a TG source
```

Stars are a reading order, not a verdict. The reason line always says why —
`collection/priority.py` scores category, impact language, whether a Telangana
or Andhra Pradesh district is named, and demand from the research backlog.

To see everything the source actually said, including the raw record:

```bash
python3 -m collection.cli queue --json --limit 5
```

### 3.2 Decide

Three verbs, all requiring `--actor`:

```bash
# a person has read it and checked the claim against the source
python3 -m collection.cli review fix-rss-001:fixture-scheme-0001 \
    --actor r.banoth \
    --evidence https://msme.gov.in/schemes/margin-money

# a person takes responsibility for publishing it
python3 -m collection.cli approve fix-rss-001:fixture-scheme-0001 \
    --actor r.banoth

# or archive it, with a reason
python3 -m collection.cli reject fix-rss-001:fixture-scheme-0001 \
    --actor r.banoth --notes "duplicate of an existing scheme row"
```

`review` walks the candidate through the intermediate lifecycle states it has
not yet passed, recording the machine ones (`COLLECTED`, `VALIDATED`) with no
actor and an explanation of what performed them, and the human ones against
your name. Every step lands in `stewardship/review_ledger.csv`, which is
append-only.

**`approve` is the point of no return for responsibility.** The ledger will
carry that name for as long as the row exists.

---

## Part 4 — Promotion into a package

### 4.1 See the row it becomes

```bash
python3 -m collection.cli promote
```

```
  fix-rss-001:fixture-scheme-0001
  -> packages/Package007_Government_Schemes/datasets/government_schemes.csv
       scheme_id                sch-041
       scheme_name              Margin Money Subsidy Scheme for micro enterprises
       source_url               https://msme.gov.in/schemes/margin-money
       …
                                … and 16 column(s) as PENDING_VERIFICATION, awaiting research
```

Only four types promote today, because those are the four with a dataset whose
shape a feed can partially fill:

| classified as | package | dataset |
|---|---|---|
| `GovernmentScheme` | Package007_Government_Schemes | `government_schemes.csv` |
| `Skill` | Package006_Skills_and_Training | `skills.csv` |
| `MSME` | Package008_MSME | `msme_businesses.csv` |
| `Crop` | Package005_Agriculture | `crops.csv` |

Anything else is reported under `SKIPPED` with the reason. That is not a
failure — it means the candidate needs a person to research it into a package by
hand, which is the normal path for a `BusinessOpportunity` or a
`TrainingProvider`.

A feed supplies a name, a URL, a date and a description. **Every other column is
written as `PENDING_VERIFICATION`**, and the row is honest about being
incomplete rather than plausible and wrong.

### 4.2 Write it

```bash
python3 -m collection.cli promote --write
```

The id is allocated from the dataset's own sequence, so it never collides.

---

## Part 5 — Into the graph, and into search

`promote --write` prints these rather than running them, because rebuilding
648 entities as a side effect of writing one row would bury that row in a diff
nobody could read.

```bash
# 1. rebuild the graph from the packages
python3 knowledge_graph/build_graph.py

# 2. check it is still well-formed (G1–G11)
python3 knowledge_graph/validate_graph.py

# 3. see what the sync would change
./scripts/run_sync.sh --plan-only

# 4. apply it
./scripts/run_sync.sh

# 5. confirm the target holds what Git holds
./scripts/health_check.sh
```

`run_sync.sh` reads its expected counts from `knowledge_graph/graph_summary.json`,
so a package that legitimately grew does not trip a warning.

Then check the thing that actually matters — that a person can find it:

```bash
# search
curl -s 'http://localhost:3000/api/search/suggest?q=margin+money' | head

# the detail page
curl -s -o /dev/null -w '%{http_code}\n' \
    http://localhost:3000/knowledge/scheme/vw:governmentscheme:margin-money-subsidy-scheme
```

### Commit

The package row, the rebuilt graph and the ledger entry belong in one commit —
they are one decision.

```bash
git add packages/ knowledge_graph/ stewardship/review_ledger.csv collection/state/
git commit -m "knowledge: add Margin Money Subsidy Scheme from ncs-jobs-001

Approved by r.banoth against https://msme.gov.in/schemes/margin-money.
16 columns remain PENDING_VERIFICATION."
```

---

## Part 6 — The whole thing, end to end

Copy-paste, using the committed fixtures so it works with no network:

```bash
python3 -m collection.cli run --only fix-rss-001 --force --write
python3 -m collection.cli queue --state NEEDS_REVIEW --limit 5

python3 -m collection.cli review  fix-rss-001:fixture-scheme-0001 \
    --actor YOUR.NAME --evidence https://example.gov.in/the-page-you-read
python3 -m collection.cli approve fix-rss-001:fixture-scheme-0001 \
    --actor YOUR.NAME

python3 -m collection.cli promote            # read it
python3 -m collection.cli promote --write    # write it

python3 knowledge_graph/build_graph.py
python3 knowledge_graph/validate_graph.py
./scripts/run_sync.sh --plan-only
```

To undo all of it before committing:

```bash
git checkout -- packages/ knowledge_graph/ stewardship/review_ledger.csv collection/state/
```

---

## Part 7 — When it goes wrong

| what you see | what it means | what to do |
|---|---|---|
| `status http_error · 403` | the network cannot reach the host | Government hosts are commonly blocked from CI and sandboxes. Verify from a network that can reach them; leave the source `PENDING_VERIFICATION` until then. |
| `records 0`, status ok | fetched, parsed, nothing in it | Check `source_type` matches the actual format — an Atom feed registered as `RSS` parses to zero records without erroring. |
| every record `[UNCLASSIFIED]` | the classifier recognises nothing | Usually correct: the feed is not ValueWeave knowledge. If it genuinely is, add a rule to `collection/classify.py` **with a test**. |
| the wrong type on a record | a rule matched a term it should not | Fix the rule and add the record as a regression test. Four such misfires were found and fixed on the first fixture run; that is the expected way to find them. |
| `PromotionError: ... skips a state` | you approved without reviewing | The lifecycle is ordered. Run `review` first. |
| `SKIPPED — no package target` | the type has no dataset to promote into | Expected. Research it into a package by hand. |
| `data_drop CRITICAL` in ops | a dataset regenerated with fewer rows | **Stop.** Do not sync. This is the most dangerous silent failure in the architecture — the sync would soft-delete the missing rows and the site would keep working. |
| `--plan-only` shows `skip=` where you expected `insert=` | the plan compares against `knowledge_sync/state/manifest.json` — your local record of what was last projected — and a previous run already covered these rows | Expected. That file is untracked local state, not part of the repository. Delete it to re-plan from nothing. |
| sync says `psycopg not installed` | the optional driver is missing | `pip install "psycopg[binary]"`. Everything except a live sync works without it. |

---

## Part 8 — Rules that do not bend

- `SUPABASE_SERVICE_ROLE_KEY` bypasses row-level security. **CI secret or
  server-side environment variable only.** Never in a `NEXT_PUBLIC_*` variable,
  never in a client component, never in a committed file, never on a shell
  command line where it lands in history. Source a gitignored `.env`.
- **Never edit package data inside Supabase.** It is a cache. The next sync
  overwrites you and the change is lost with no record that it happened.
- **Never touch** `auth.users`, `profiles`, `connections`, `messages`, `teams`,
  `projects`, `idea_library`, `bookmarks`, `notifications`,
  `assessment_results`, or any other application table. The sync's allowlist
  refuses them, and that refusal is checked before the driver is even imported.
- **Never fabricate a value.** `PENDING_VERIFICATION` is always the right answer
  where official public data cannot be confirmed.
- **One source per pull request.** The point of the registry is that somebody
  can see what was added.

---

## Reference

| command | what it does | writes? |
|---|---|---|
| `sources` | what we monitor | no |
| `verify <id>` | prove a source is reachable and parseable | no |
| `run` | fetch, detect, classify, de-duplicate, queue | only with `--write` |
| `queue` | candidates awaiting a person | no |
| `health` | feed health, 7 checks | no |
| `review <id> --actor` | record that a person has read it | ledger |
| `approve <id> --actor` | accept responsibility | ledger |
| `reject <id> --actor` | archive with a reason | ledger |
| `promote` | approved candidates → package rows | only with `--write` |
| `backlog` | topics people searched for and we lack | only with `--write` |

Every command takes `--json`.

| file | what it holds |
|---|---|
| `collection/registry/monitored_sources.csv` | what we monitor — configuration |
| `collection/state/fetch_state.json` | ETags, timestamps, hashes — state |
| `collection/state/review_queue.jsonl` | candidates |
| `collection/state/last_run.json` | the last run, for `health` |
| `stewardship/review_ledger.csv` | every decision, append-only |
| `collection/state/research_backlog.json` | gaps — **not knowledge** |
