# Post-Deployment Validation

**Nine surfaces, in the order a user meets them.** Run as a real user in a browser, not
with `curl` — most of what can go wrong is invisible to a status code.

**Every check names what "correct but empty" looks like.** On this platform an empty
panel is often the right answer, and a validation pass that cannot tell right-empty from
wrong-empty is worthless.

---

## 0. Two-minute gate

Fail any of these and stop; the rest will fail too.

```bash
psql "$DATABASE_URL" -c "select count(*) from knowledge.kg_entities;"      # 647
psql "$DATABASE_URL" -c "select count(*) from knowledge.kg_relationships;" # 865
psql "$DATABASE_URL" -c "select count(*) from public.kg_vocabulary_map;"   # 202
curl -sI https://<domain>/knowledge | head -1                              # HTTP/2 200
curl -sI https://<domain>/ | head -1                                       # HTTP/2 200
```

| Symptom | Cause |
|---|---|
| SQL returns rows, pages show nothing | **Schemas not exposed** — Guide §6 |
| `kg_vocabulary_map` is 0 | **Crosswalk not loaded** — Guide §7 |
| `kg_entities` is 0 | Sync has not run — Guide §8 |

- [ ] All five pass

---

## 1. Knowledge Explorer — `/knowledge`

The best first check: no auth, no personalisation, no vocabulary resolution. **If this
works, the projection is reachable.**

| Check | Expected |
|---|---|
| Type index | 7 package sections, each with counts |
| Districts | **61** · Skills **45** · Schemes **40** · Industries 78 · MSMEs 40 · Crops 45 |
| Source badges | Every section shows `PackageNNN · …` |
| `?type=skill` | 24 per page, pager below |
| `?type=skill&page=2` | Different rows; back button works |
| `?q=welding` | Filters; count updates |
| `?q=zzzzz` | `NO_MATCH` — *"a gap in our data, not in your query"* |
| Unverified notice | Present |

- [ ] Counts match · [ ] pagination works · [ ] every card links

> **Wrong-empty:** *"Knowledge base not connected yet"* → schemas not exposed.
> *"Knowledge base is empty"* → sync has not run.

---

## 2. Businesses — `/knowledge/business/[slug]`

```bash
psql "$DATABASE_URL" -c "select global_entity_id from knowledge.kg_entities
  where entity_type='BusinessOpportunity' limit 3;"
```
Take the slug after the second colon → `/knowledge/business/<slug>`.

| Check | Expected |
|---|---|
| Header | Name, type, confidence, source badge, provenance line |
| Details | Investment range, risk, employment — sentinels **never** shown |
| Connected knowledge | Grouped by type, each chip naming its relationship |
| Next steps | Up to 3 concrete hops |
| Unverified notice | Present — 0 of 2,299 rows are reviewed |

> **Right-empty: "Required skills" will be missing on 43 of 45 businesses.** Only 2 have
> a skill edge. Expect *"Nothing in the knowledge graph links to this record yet."*
> That is a data gap, documented, not a deployment failure.

- [ ] 3 businesses open · [ ] provenance visible · [ ] no sentinel strings

---

## 3. Skills — `/knowledge/skill/[slug]`

Try `/knowledge/skill/welding-mig-tig-arc`.

| Check | Expected |
|---|---|
| Attributes | NSQF level, duration, demand, automation risk |
| Related | Businesses, industries, schemes |
| `/skills` | Lists 45 researched skills with the *"researched skills"* note |
| `/skills/<slug>` | Redirects to `/knowledge/skill/<slug>` when the CMS is empty |

> **Right-empty:** training providers — only 3 `TRAINED_BY` edges exist in the whole
> graph. Certifications — all 30 are orphans.

- [ ] Skill page renders · [ ] `/skills` shows 45 · [ ] redirect works

---

## 4. Schemes — `/knowledge/scheme/[slug]`

| Check | Expected |
|---|---|
| Attributes | Ministry, assistance, subsidy, application mode |
| Portal | *"Apply on the official portal ↗"* where a URL exists |
| Related | Businesses, MSMEs, skills |
| `/schemes` | 40 researched schemes |

> **Right-empty: district coverage is empty on every scheme.** Zero
> `GovernmentScheme → District` edges exist; `RS2-VIA_DISTRICT` cannot fire. Phase 2 R1
> recovers 305 of them from a dataset already in the repository.

- [ ] Scheme renders · [ ] portal link opens · [ ] district section explains itself

---

## 5. Districts — `/district/[slug]` and `/knowledge/district/[slug]`

`/district/hyderabad` is the best-covered district in the graph.

| Check | Expected |
|---|---|
| Editorial profile | Unchanged from before deployment |
| Knowledge panel | Below it, up to 8 groups |
| Hyderabad | Institutions (12), MSMEs, industries |
| Depth line | *"N researched records … across M categories"* |
| A thin district | e.g. `/district/adilabad` — names the coverage gap |

> **Right-empty: no district shows industries.** Zero `Industry → District` edges;
> `RI3-VIA_DISTRICT` is structurally dead. **34 of 61 districts have exactly one edge.**

- [ ] Hyderabad populated · [ ] a thin district explains itself · [ ] cards link

---

## 6. Search

On any page carrying `KnowledgeSearch`.

| Check | Expected |
|---|---|
| `weld` | Results within ~250 ms |
| Grouping | Static results and `search-researched` are separate groups |
| Filters | 7 chips; selecting one re-queries |
| Result click | Opens the detail page |
| `zzzzz` | Empty, no error |

> Search is a Postgres `ILIKE '%q%'` scan without a trigram index. Fine at 647 rows;
> re-measure at ~5,000. It does **not** use the Python `SearchEngine`, which is not
> deployed.

- [ ] Debounce works · [ ] filters narrow · [ ] results link

---

## 7. Dashboard — signed in

**Run this twice.** The second run is the honest test.

### 7a · Resolving skills — `Welding, Food Processing, Tailoring`

| Check | Expected |
|---|---|
| Feed | Renders (500 seeded rows, if kept) |
| Rails | 6 present |
| Populated | **At least one**, typically business ideas + schemes |
| Card links | Every card reaches a detail page |
| Reason | Every card shows why |
| Intelligence summary | 8 scores; `—` never `0` for unavailable |
| Latest knowledge | 6 most recently synced rows |

### 7b · Non-resolving skills — `Digital Marketing, Accounting, Data Entry`

| Check | Expected |
|---|---|
| Rails | Present, most reporting `NO_SIGNAL` **with a named reason** |
| Skill score | **0 or `—`, and this is correct** — 22.8% resolve rate |
| Explorer | Still reachable and fully populated |

> **This is the launch decision, not a bug hunt.** If 7b reads as a broken product rather
> than an incomplete one, read `PILOT_PLAN.md` before inviting a general cohort. It is
> what ~3 in 4 real users will see.

> **Right-empty:** if the intelligence pipeline (Guide §9) has not been built, **all**
> rails show `NOT_COMPUTED`. Expected until it exists.

- [ ] 7a populated · [ ] 7b degrades honestly · [ ] cards link · [ ] scores show `—`

---

## 8. Recommendations — the four required elements

Open any recommendation card and confirm all four:

| Element | Where |
|---|---|
| **Reason** | On the card, never truncated |
| **Confidence** | Badge; tooltip says it scores *source strength* |
| **Supporting entities** | On the detail page, each naming its relationship |
| **Knowledge source** | Provenance line: package · dataset · row |

- [ ] All four present on at least 3 cards across 2 categories

---

## 9. Connections

| Check | Expected |
|---|---|
| Page loads | Tabs render |
| Skill overlap | Shown for **accepted** connections only |
| Pending | **No** skills shown — acceptance gates it |
| Collaborators rail | Renders or explains its absence |

> **Right-empty:** with fewer than ~10 users there is nothing to match. Teams and
> projects do not exist as features.

- [ ] Loads · [ ] overlap gated by acceptance

---

## 10. Security spot-check

As an **anonymous** client, not service role:

```sql
select * from user_intelligence.user_skill_profile;               -- 0 rows
select count(*) from knowledge.kg_entities;                       -- 647
insert into knowledge.kg_entities (global_entity_id) values ('x'); -- DENIED
```

- [ ] Another user's intelligence invisible
- [ ] `knowledge` readable
- [ ] **Any** write to `knowledge` denied
- [ ] `/dashboard`, `/profile`, `/connections`, `/admin` redirect when signed out
- [ ] `/knowledge` works signed out — public reference data, intended

---

## 11. Result

| Surface | ✅ / ⚠️ / ❌ | Note |
|---|---|---|
| Knowledge Explorer | | |
| Businesses | | |
| Skills | | |
| Schemes | | |
| Districts | | |
| Search | | |
| Dashboard (resolving) | | |
| Dashboard (non-resolving) | | |
| Recommendations | | |
| Connections | | |
| Security | | |

### Known-correct empties — do not raise these as defects

| Surface | Empty | Because |
|---|---|---|
| Business → required skills | 43 of 45 | 2 businesses have a skill edge |
| Scheme → districts | all 40 | 0 scheme→district edges |
| District → industries | all 61 | 0 industry→district edges |
| Skill → training providers | most | 3 `TRAINED_BY` edges total |
| Skill → certifications | all | 30 orphan certifications |
| Mentors, events | always | No source exists anywhere |
| All rails | all users | Only if the §9 pipeline is not built |

**Everything else empty is a deployment problem.** Check schema exposure first — it is
the failure that produces no error anywhere.

| | |
|---|---|
| Validated by / date | |
| Go / No-Go | |
