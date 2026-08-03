# Production Monitoring

**Five metric families**, each with a source you can query today, a threshold, and what
to do when it trips.

> **The hardest monitoring problem on this platform is that its worst failure is
> silent.** If the `knowledge` schema is not exposed, every query fails, `safe()` returns
> `[]`, and the application serves 200s with empty panels. No error rate moves. No log
> line appears. **Uptime monitoring will report everything healthy.**
>
> §1 exists specifically to catch that, and `scripts/health_check.sh` is its
> implementation — JSON out, using the **anon key** so that an unexposed schema reports
> failed rather than healthy. Point the monitor at that, not at a status code.
>
> **Run it with `--strict` from a monitor.** The default exit code is `2` on a critical
> finding and `0` otherwise, because the deployment gate in CI uses the same script and
> a warning there — intelligence not yet computed, `PRODUCTION_URL` unset — is not a
> reason to fail a good deploy. A monitor wants the opposite: `--strict` restores
> `0` healthy / `1` degraded / `2` failed. The JSON `status` field says
> `healthy`/`degraded`/`critical` in both modes, so a monitor reading the body rather
> than the exit code needs no flag at all.

---

## 0. The one-query health check

Run every 5 minutes from outside the app, **as the anon client** — not service role.
Service role bypasses RLS and would pass while every real user saw nothing.

```sql
select
  (select count(*) from knowledge.kg_entities)            as entities,      -- 647
  (select count(*) from knowledge.kg_relationships)       as edges,         -- 865
  (select count(*) from knowledge.kg_vocabulary_map)      as vocabulary,    -- 202
  (select count(*) from user_intelligence.user_activity_summary) as users;
```

| Result | Meaning | Severity |
|---|---|---|
| Query **errors** | Schema not exposed, or dropped | **P1** |
| `entities = 0` | Sync never ran, or projection wiped | **P1** |
| `entities < 647` | Partial sync | **P2** |
| `vocabulary = 0` | Crosswalk not loaded — nothing resolves | **P2** |
| `users = 0` | Intelligence pipeline not running | P3 |
| All at expected | Healthy | — |

**Anon-client, not service-role, is the whole point of this check.**

---

## 1. Sync success

**Sources:** `knowledge_sync/state/sync_log.jsonl` (one JSON object per run) and
`knowledge.sync_runs`.

| Metric | Expected | Alert | Severity |
|---|---|---|---|
| `outcome` | `SUCCESS` / `DRY_RUN` | anything else | **P2** |
| Hours since last `SUCCESS` | < release cadence | > 168 h | P3 |
| `validation_errors` | **0** | > 0 | **P2** |
| Governed warnings | **exactly 4** | ≠ 4 | **P2** |
| `rows_soft_deleted` | 0 in steady state | > 50 | **P2** |
| `coverage[*].complete` | `true` on all 8 | any `false` | **P2** |
| Second-run idempotency | `0 inserted, 0 updated` | any change | **P2** |

```bash
tail -1 knowledge_sync/state/sync_log.jsonl | python3 -m json.tool
python3 -m knowledge_sync history --limit 10
```

**`coverage` is the one that catches silent partial failure** — it compares rows in the
target against rows Git produces, per table. A sync can report `SUCCESS` having written
seven tables of eight.

**A large `rows_soft_deleted` is almost never retired facts.** It is a renamed dataset or
a changed key column. Run `plan` and read the list before applying.

---

## 2. Graph size

**Source:** `knowledge_graph/graph_summary.json`, written by every build.

| Metric | Baseline | Alert |
|---|---:|---|
| `entity_count` | **647** | ±5% unexplained |
| `relationship_count` | **865** | any drop |
| `unresolved_endpoints` | **132** | rising |
| Orphans (validator G10) | **142** | rising |
| `entity_types_populated` | 19/19 | < 19 |
| `relationship_types_populated` | 15/19 | < 15 |
| Connectivity | **78.05%** | < 75% |

```bash
python3 knowledge_graph/validate_graph.py | tail -6
python3 -c "import json;d=json.load(open('knowledge_graph/graph_summary.json'));\
print(d['entity_count'], d['relationship_count'], d['unresolved_endpoints'])"
```

> **Track direction, not the absolute number.** 142 orphans and 132 unresolved endpoints
> are today's known state, documented in `GRAPH_VALIDATION_REPORT.md`. **A rise is the
> signal** — it means a mapping stopped joining or entities were added without edges,
> which is exactly how the graph reached 21.9% orphans.

**An entity-count drop with no package change means a rename.** A renamed entity gets a
new id and orphans the old one; the count can stay flat while every reference breaks.

---

## 3. Recommendation count

**Source:** the `user_intelligence` tables.

```sql
select count(distinct user_id)                       as users_with_intelligence,
       count(*)                                      as total_recommendations,
       round(avg(match_score), 1)                    as avg_match,
       count(*) filter (where confidence = 0)        as editorial_rows
  from user_intelligence.user_recommendations
 where rules_version = '1.0.0';

select category, count(*), count(distinct user_id)
  from user_intelligence.user_recommendations
 group by 1 order by 2 desc;
```

| Metric | Expected today | Alert |
|---|---|---|
| Users with ≥1 recommendation | > 80% of active | < 60% |
| Median categories filled | **1–5 of 10** | 0 for a resolving user |
| `mentors`, `events` | **always 0** | any row — that would be fabricated |
| Editorial share (`confidence = 0`) | high | rising toward 100% |
| Rows with `rules_version ≠ 1.0.0` | 0 | any, without a bump |

> **A user with zero recommendations is not automatically a bug.** At a 22.8% skill
> resolve rate, most users legitimately fill 1–2 categories. Alert on *resolving* users
> getting nothing, not on the median.
>
> **The editorial share is the metric that matters most for product health.** If
> `confidence = 0` rows approach 100%, the graph has stopped contributing and the
> platform is a content site with a knowledge base attached.

**Never alert on `mentors` or `events` being empty.** They have no source; a row there
would mean something fabricated one.

---

## 4. Search response

**Source:** Postgres statistics. There is no application-level timing today.

```sql
select mean_exec_time, calls, query
  from pg_stat_statements
 where query ilike '%kg_entities%canonical_name%'
 order by mean_exec_time desc limit 5;
```

| Metric | Expected at 647 rows | Alert |
|---|---|---|
| Mean search latency | < 50 ms | > 200 ms |
| p95 | < 150 ms | > 500 ms |
| Rows scanned | 647 (full scan) | — |

> **Search is a sequential scan and always will be until `pg_trgm` lands.**
> `.ilike("canonical_name", '%q%')` cannot use the existing btree, and `pg_trgm` appears
> in no migration — it was scoped to the abandoned migration 008. Backlog P1.
>
> Invisible at 647 rows. **Re-measure when `kg_entities` passes ~5,000.** The 250 ms
> debounce and the type filter both reduce the load; neither fixes the scan.

Also worth watching: `/ideas/[slug]` issues one scheme query per matched business,
capped at 6 (~9 queries). If it becomes slow, the fix is a materialised view, not a
client cache.

---

## 5. Broken links

Two classes, and only one is a bug.

### 5a · Real broken links

```bash
# every route the build produced must respond
npx next build 2>&1 | grep -E "^├|^└" | grep -oE "/[a-z0-9/_\[\]-]+" | sort -u \
  | while read -r r; do
      case "$r" in *"["*) continue;; esac
      code=$(curl -s -o /dev/null -w '%{http_code}' "https://<domain>$r")
      [ "$code" = "200" ] || echo "$code $r"
    done
```

| Metric | Expected | Alert |
|---|---|---|
| Static routes returning 200 | **214/214** | any non-200 |
| 5xx rate | 0 | > 0.1% |

### 5b · Dead-end entities — not broken, but worth tracking

```sql
select count(*) from knowledge.kg_entities e
 where not exists (select 1 from knowledge.kg_relationships r
                    where r.from_entity = e.global_entity_id
                       or r.to_entity   = e.global_entity_id);
```

**Expected: 142 (21.9%).** Those detail pages render a header, attributes, and an honest
note that nothing links to them yet. **Track the direction.**

### 5c · Recommendations pointing nowhere

```sql
select count(*) from user_intelligence.user_recommendations ur
 where ur.item_id like 'vw:%'
   and not exists (select 1 from knowledge.kg_entities e
                    where e.global_entity_id = ur.item_id);
```

**Expected: 0.** Anything else means intelligence was computed against a graph version
the projection no longer holds — recompute after any `sync --full`.

---

## 6. Dashboard

| Panel | Query | Refresh |
|---|---|---|
| Health | §0 | 5 min |
| Last sync | `sync_log.jsonl` tail | 15 min |
| Graph size | `graph_summary.json` | on build |
| Orphans / unresolved | validator | on build |
| Recommendations by category | §3 | hourly |
| Editorial share | §3 | daily |
| Route health | §5a | hourly |
| Search p95 | §4 | 15 min |

---

## 7. Alert routing

| Severity | Condition | Route |
|---|---|---|
| **P1** | Health query errors · `entities = 0` · 5xx > 1% | Page |
| **P2** | Sync failed · validation errors · coverage incomplete · vocabulary 0 | Ticket, same day |
| **P3** | No sync in 7 days · users with 0 recommendations rising | Weekly review |
| **P4** | Orphans rising · editorial share rising · search p95 up | Monthly |

**Do not page on empty panels.** Most of them are correct — the known-correct list is in
`POST_DEPLOYMENT_VALIDATION.md` §11, and paging on a documented data gap is how a team
learns to ignore its alerts.

---

## 8. What is not monitored, and why

| Not monitored | Why |
|---|---|
| Python API uptime | Not deployed. 10 endpoints, 29 tests, no deployment target |
| Python `SearchEngine` | Not deployed; the frontend uses Postgres `ILIKE` |
| Per-user recommendation quality | **Nothing records whether one was useful.** The pilot's rating capture is the first chance to create that signal — `PILOT_PLAN.md` §5 |
| Data freshness vs the real world | A scheme's benefit can change without anything here noticing. That is a stewardship problem: **0 of 2,299 rows are human-reviewed** |
| Frontend Core Web Vitals | No RUM. Vercel Analytics is available and unconfigured |

**The second and fourth rows are the honest gaps.** Recommendation quality cannot be
monitored because it is not measured, and data accuracy cannot be monitored because
accuracy is not something a query can check. Both need people, not dashboards.
