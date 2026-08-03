# Automated collection

The front of the knowledge pipeline. Sources in, a review queue out.

```bash
python3 -m collection.cli sources          # what we monitor, and its state
python3 -m collection.cli run --force      # a dry run over every active source
python3 -m collection.cli run --write      # record the queue and the fetch state
python3 -m collection.cli queue            # what is waiting for a person
python3 -m collection.cli health           # feed health, dashboard-ready
python3 -m collection.cli verify <id>      # prove a candidate URL is reachable
python3 tests/run_all.py --suite collection
```

---

## The one thing to know

**Nothing in this package can publish.** There is no path from a feed to
`packages/`, to the knowledge graph or to Supabase — a test asserts the strings
are not even present in the code. The entire output is a JSONL file in Git that
a person reads, and the scheduled workflow's last act is opening a pull request.

Approving a candidate happens where it already happened before this existed:

```bash
python3 -m stewardship.cli review <entity_id> --actor NAME --evidence URL
python3 -m stewardship.cli approve <entity_id> --actor NAME
```

`stewardship/lifecycle.py` states the rule and enforces it: *APPROVED is the
only state a machine may not enter.*

---

## What it does, in order

| stage | file | what it decides |
|---|---|---|
| registry | `registry.py` | what to check, how often, and whether it may be checked at all |
| fetch | `runner.py` + `knowledge_engine/collectors/` | conditional HTTP — `If-None-Match` out, `304` back |
| parse | `knowledge_engine/parsers/` | the registry names the parser; nothing sniffs |
| detect | `detect.py` | NEW / UPDATED / UNCHANGED / DISAPPEARED, **per item** |
| classify | `classify.py` | which knowledge type, and the words that decided |
| dedupe | `dedupe.py` | exact, near, and version-update, within a run and against the queue |
| queue | `review.py` | COLLECTED → NEEDS_REVIEW, keeping decisions already made |
| monitor | `monitor.py` | dead, failing, stale, never-verified, duplicate spikes |
| backlog | `backlog.py` | what people searched for and we do not have |

---

## Adding a source

It is a data change. No code.

1. Add a row to `collection/registry/monitored_sources.csv`.
2. `python3 -m collection.cli verify <source_id>` — from a network that can
   reach it. This fetches once, prints the first records as the pipeline sees
   them, and **does not edit the registry**.
3. If it worked, change `status` from `PENDING_VERIFICATION` to `ACTIVE` and
   open a pull request. A reviewer sees a one-line diff.

The columns:

| column | what it is |
|---|---|
| `source_id` | stable key. Never reuse one. |
| `name`, `category`, `state`, `country` | what a person reads. Categories are listed in `registry.py`. |
| `url` | the feed, API or file. |
| `source_type` | `RSS` `ATOM` `JSON_FEED` `XML` `REST_API` `CSV` `DATASET`. A test asserts this agrees with the parser. |
| `collector`, `parser` | dotted paths into `knowledge_engine`. Resolved at load, so a typo fails immediately. |
| `frequency` | `HOURLY` … `ANNUAL`. Drives both the schedule and the staleness threshold. |
| `reliability` | 0–100, declared. A tier, not a measurement. |
| `status` | `ACTIVE` `PENDING_VERIFICATION` `PAUSED` `RETIRED`. |
| `tags` | `;`-separated, free. |
| `item_key` | the field that identifies one item — `guid` for RSS, `id` for Atom and JSON Feed, a real primary key for a register. **Get this right**: it is what makes change detection per-record rather than per-feed. |
| `classify_as` | force a type. Use when the source IS one kind of thing — a register of training providers is a list of training providers, and making the classifier re-derive that from prose it does not contain is guessing where the source already told us. |
| `notes` | why this source, and anything a future reader needs. |

`last_checked`, `last_ok`, `etag`, `content_hash` are **not** columns. They live
in `collection/state/fetch_state.json`, because every scheduled run writes them
and a run that dirtied a human-authored file would bury the one real edit in a
diff of forty timestamps.

---

## `PENDING_VERIFICATION`

Six of the ten shipped sources are real government feeds in this state. They are
never fetched on a schedule and the health check reports them as unverified.

That is not a defect, it is the point. This sandbox cannot reach
`pib.gov.in` — the outbound proxy answers 403 — so nobody has proved those URLs
work. A URL somebody typed is not a URL somebody checked, and marking one ACTIVE
without evidence puts a dead feed on a dashboard as green. It is the same
sentinel the packages use for a fact that cannot be sourced, applied to a source.

Run `verify` from a machine with access, then flip the status in a pull request.

---

## The four fixtures

`collection/fixtures/` holds an RSS 2.0 feed, an Atom feed, a JSON Feed 1.1
document and a CSV register. They are **fixtures, not captures** — every item is
invented and every title says `FIXTURE`, so a row escaping into a package would
be obvious rather than plausible. The shapes are real; the content is not a
claim about anything.

They exist so that `collection.cli run` does something on a laptop with no
network, so the scheduled workflow exercises its own path before a real feed is
ever pointed at it, and so the classifier's behaviour is pinned by tests against
material that will not change under it.

`scripts/dev/fake_feed_server.py` serves them over HTTP with real `ETag` and
`Last-Modified` headers and a `/_mutate` endpoint, which is how the conditional
fetch is actually tested — you cannot ask a live government feed to change on
command.

---

## Reading the queue

`collection/state/review_queue.jsonl`, one candidate per line:

```json
{"candidate_id": "fix-rss-001:fixture-scheme-0001",
 "classified_as": "GovernmentScheme",
 "classified_reason": "matched “subsidy”, “scheme”",
 "state": "NEEDS_REVIEW",
 "raw": { … the parsed record, verbatim … }}
```

`raw` is the whole record as the source published it. A reviewer must be able to
see what was actually said, not a summary of it — and provenance requires the
original claim to survive to the point of approval.

A candidate marked `DUPLICATE` carries `duplicate_of` and the measured reason.
One marked with `supersedes` looks like an amendment of something already in the
queue, which is the single most important thing this pipeline can catch.

---

## What is deliberately not here

**No AI.** Not in the collectors, not in the classifier, not in the deduper.
`knowledge_engine/docs/ai_integration_plan.md` describes where it would go —
PDF extraction, long-report summarisation, entity extraction — and the rule that
survives it: anything AI proposes enters this same queue, as a candidate, for
the same human approval. See `docs/COLLECTION_ARCHITECTURE.md` §10.

**No auto-approval, no auto-publish, no schedule that reaches Supabase.**
`knowledge-collect.yml` opens a pull request and stops. `knowledge-sync.yml`
runs on a push to main. The gap between them is a person.

**No hundreds of feeds.** Four fixtures and six candidates. The framework is the
deliverable; the feeds come next, one reviewed pull request at a time.
