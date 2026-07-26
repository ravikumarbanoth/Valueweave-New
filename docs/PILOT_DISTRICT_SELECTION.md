# Pilot District Selection

**Workstream 5** · 61 districts ranked on five dimensions of completeness

---

## 0. Recommendation

| Tier | Districts | When | Composite |
|---|---|---|---|
| **Tier 1 — launch** | **Hyderabad, Guntur, Visakhapatnam, Tirupati** | Now | 100 · 34 · 26 · 24 |
| **Tier 2 — after Wave 1** | + Nizamabad, Nalgonda, Kurnool, Sangareddy, Karimnagar, East & West Godavari, Krishna | +5 days | 11–19 |
| **Tier 3** | + Chittoor, Hanumakonda, Ranga Reddy, Srikakulam, Prakasam, Mahabubnagar | +2 hours ‡ | 11–19 |
| **Not viable** | The remaining 35 | — | **0** |

‡ Tier 3 costs **two hours**, not five days — see §3. It is the cheapest work in the
entire programme.

**Launch on Tier 1 only.** Hyderabad scores **100**; the next district scores **34**.
That is not a ranking, it is a cliff.

---

## 1. The five dimensions, measured

Composite weighting: knowledge 30% · industry 15% · skill 15% · business 20% ·
opportunity 20%. Proxied by graph degree, 2-hop industry reach, 2-hop skill reach, MSME
count and Institution count.

| # | District | Deg | Inst | MSME | Ind | Skill | DO | **Composite** |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | **Hyderabad** | 17 | 12 | 5 | 7 | 8 | 85 | **100.0** |
| 2 | **Guntur** | 8 | 6 | 2 | 0 | 1 | 59 | **34.0** |
| 3 | **Visakhapatnam** | 5 | 3 | 2 | 0 | 2 | 50 | **25.6** |
| 4 | **Tirupati** | 7 | 7 | 0 | 0 | 0 | 51 | **24.0** |
| 5 | Chittoor | 3 | 1 | 2 | 0 | 2 | **0** ‡ | 18.7 |
| 6 | Nalgonda | 3 | 1 | 2 | 0 | 2 | 44 | 18.7 |
| 7 | Hanumakonda | 4 | 4 | 0 | 2 | 0 | **0** ‡ | 18.0 |
| 8 | Krishna | 4 | 3 | 1 | 0 | 1 | **0** ‡ | 17.9 |
| 9 | Sangareddy | 4 | 3 | 1 | 0 | 1 | 47 | 17.9 |
| 10 | Kurnool | 3 | 1 | 2 | 0 | 1 | 44 | 16.8 |
| 11 | Nizamabad | 3 | 1 | 2 | 0 | 1 | 44 | 16.8 |
| 12 | Ranga Reddy | 2 | 0 | 2 | 0 | 2 | **0** ‡ | 15.3 |
| 13 | East Godavari | 3 | 2 | 1 | 0 | 1 | 44 | 14.5 |
| 14 | West Godavari | 3 | 2 | 1 | 0 | 1 | 44 | 14.5 |
| 15 | Srikakulam | 3 | 2 | 1 | 0 | 0 | **0** ‡ | 12.6 |
| 16 | Karimnagar | 2 | 1 | 1 | 0 | 1 | 41 | 11.1 |
| 17 | Mahabubnagar | 2 | 1 | 1 | 0 | 1 | 41 | 11.1 |
| 18 | Prakasam | 2 | 1 | 1 | 0 | 1 | **0** ‡ | 11.1 |
| 19–26 | *8 districts* | 1 | 0 | 1 | 0 | 1 | 0 | 7.6 |
| **27–61** | **35 districts** | **0** | **0** | **0** | **0** | **0** | **0** | **0.0** |

**Median composite across all 61: 0.0.**

### Per-dimension summary

| Dimension | Districts with any coverage | Best |
|---|---:|---|
| Knowledge (degree >1) | **27 of 61** | Hyderabad, 17 |
| Business (≥1 MSME) | 26 | Hyderabad, 5 |
| Skill (2-hop) | 25 | Hyderabad, 8 |
| Opportunity (`district_opportunity` ≥30) | 16 | Hyderabad, 85 |
| **Industry (2-hop)** | **2** | Hyderabad, 7 |

**Industry coverage is effectively zero.** Only Hyderabad and Hanumakonda reach any
Industry within two hops, because **no `Industry -LOCATED_IN-> District` edge exists at
all** (`GRAPH_CONNECTIVITY_PLAN.md` E3). Industry completeness is not unevenly
distributed — it is absent.

**34 of 61 districts have degree 1**: their only edge is `LOCATED_IN` their own state.
Nothing is known about them beyond which state they are in.

---

## 2. Hyderabad is the pilot, and that is a finding not a preference

| | Hyderabad | Rest of top 4 | The other 57 |
|---|---:|---:|---:|
| Composite | **100** | 24–34 | 0–19 |
| Institutions | **12** | 3–7 | 0–4 |
| Industries within 2 hops | **7** | **0** | 0–2 |
| Skills within 2 hops | **8** | 0–2 | 0–2 |
| Recommendation rows | **25** | 25 | **6** |

**Hyderabad is the only district where the knowledge graph can answer an industry
question.** Everywhere else, `industries` recommendations come from sector interest
matching, not from location.

The recommendation-row figure is the one to hold onto: **25 rows in a covered district,
6 in an empty one.** A student in one of the 35 zero-composite districts gets six rows,
almost all from the static editorial file.

---

## 3. Six districts score 0 and should not — a two-hour fix

Chittoor, Hanumakonda, Krishna, Ranga Reddy, Srikakulam and Prakasam have **real graph
substance** — composites of 11 to 19, institutions, MSMEs, reachable skills — and score
**0** on `district_opportunity`.

**They are not in the onboarding district vocabulary.**

```
district_crosswalk.csv:  33 terms  ->  19 distinct District entities
Districts unreachable from the onboarding vocabulary:  42 of 61
```

`DO1-RESOLVE` fails, so the whole score collapses to 0 regardless of what the graph
knows about the place. A student in Chittoor types their district and the platform
cannot map it to the entity it already holds data for.

| District | Composite | DO | Reachable? |
|---|---:|---:|---|
| Chittoor | 18.7 | **0** | **No** |
| Hanumakonda | 18.0 | **0** | **No** |
| Krishna | 17.9 | **0** | **No** |
| Ranga Reddy | 15.3 | **0** | **No** |
| Srikakulam | 12.6 | **0** | **No** |
| Prakasam | 11.1 | **0** | **No** |
| *Nalgonda (for contrast)* | 18.7 | **44** | Yes |

Nalgonda and Chittoor have **identical composites**. Nalgonda scores 44 and Chittoor
scores 0, and the only difference is a crosswalk row.

> **Extend `district_crosswalk.csv` to all 61 districts. Two hours.**
> It is a mechanical `EXACT_NAME` match against Package001's `district.csv` — the
> entities exist, the names are canonical, no research is required. It moves six
> districts from unusable to tier-2 and removes a silent failure for the 42 districts
> that cannot currently be named at all.

**This is the highest return per hour anywhere in the programme** and it was invisible
until district completeness was measured against the vocabulary rather than against the
score.

---

## 4. What Wave 1 does to the ranking

Projected from the edge counts in `GRAPH_CONNECTIVITY_PLAN.md`.

| District | Now | + vocabulary | + E4 | + E2/E3 | Tier |
|---|---:|---:|---:|---:|---|
| Hyderabad | 85 | 85 | 88 | **92** | 1 |
| Guntur | 59 | 59 | 65 | **78** | 1 |
| Tirupati | 51 | 51 | 58 | **72** | 1 |
| Visakhapatnam | 50 | 50 | 57 | **74** | 1 |
| Nizamabad | 44 | 44 | 52 | **66** | 2 |
| Nalgonda | 44 | 44 | 52 | **66** | 2 |
| Kurnool | 44 | 44 | 52 | **64** | 2 |
| Sangareddy | 47 | 47 | 54 | **64** | 2 |
| East / West Godavari | 44 | 44 | 51 | **62** | 2 |
| Karimnagar | 41 | 41 | 48 | **60** | 2 |
| **Chittoor** | **0** | **~40** | ~48 | **~60** | **3** |
| **Krishna** | **0** | **~40** | ~47 | **~59** | **3** |
| **Hanumakonda** | **0** | **~38** | ~45 | **~58** | **3** |
| **Ranga Reddy** | **0** | **~36** | ~43 | **~56** | **3** |
| **Srikakulam** | **0** | **~32** | ~40 | **~52** | **3** |
| **Prakasam** | **0** | **~32** | ~39 | **~51** | **3** |
| 35 zero-composite districts | 0 | ~15 | ~25 | **~35** | — |

| | Now | After Wave 1 |
|---|---:|---:|
| Districts scoring ≥50 | **4** | **~18** |
| Districts scoring ≥30 | 16 | **~53** |
| Districts scoring 0 | **45** | **0** |

**Wave 1 adds no new district records** — E4 expands `jurisdiction` that is already
recorded, and the vocabulary fix matches names that already exist. Even the 35
zero-composite districts reach ~35, because a national scheme genuinely *is* available
there and the graph will finally say so.

---

## 5. Pilot allocation

### Now — Tier 1, 130 people

| District | Students | Composite | Institutions | Rationale |
|---|---:|---:|---:|---|
| Hyderabad | **40** | 100 | 12 | Only district with industry-level knowledge |
| Guntur | 20 | 34 | 6 | Best AP coverage |
| Tirupati | 20 | 24 | 7 | Second-highest institution count |
| Visakhapatnam | 20 | 26 | 3 | Industrial base, weakest institution link |

Faculty and entrepreneurs from the same four. Institution counts are the recruitment
channel, and they line up with knowledge coverage — the districts with the most data are
the districts with the most colleges.

### After Wave 1 — 12 districts

Tier 1 + Nizamabad, Nalgonda, Kurnool, Sangareddy, Karimnagar, East Godavari, West
Godavari, Krishna. All projected ≥59. Estimated ~60% of the likely student population of
the two states.

### Never on current data — 35 districts

Adilabad, Kumuram Bheem Asifabad, Mancherial, Nirmal, Jagtial, Peddapalli, Kamareddy,
Rajanna Sircilla and 27 others. Composite **0**, `district_opportunity` **0**, six
recommendation rows.

**A student recruited here would see honest empty states and read them as a broken
product.** After Wave 1 they reach ~35 — usable, not good. Deepening them is Wave 5 and
should be driven by where pilot students actually turn out to be, not by a list written
now.

---

## 6. Selection criteria, for the next time

| Criterion | Threshold | Why |
|---|---|---|
| `district_opportunity` ≥ 50 | Hard | Below this, recommendations are editorial-only |
| Composite ≥ 20 | Hard | Below this the graph knows almost nothing |
| **In the district vocabulary** | **Hard** | §3 — otherwise every score is 0 regardless |
| ≥3 institutions | Soft | Recruitment channel |
| ≥2 MSMEs | Soft | `RN1`/`RN2` need something to match |
| ≥1 Industry within 2 hops | Aspirational | Only Hyderabad clears it today |

**The vocabulary criterion is the one that would have been missed.** A district can pass
every knowledge test and still score 0 because the user cannot name it in a way the
platform recognises — and nothing in the score or the graph reveals that. It is the
cheapest possible failure and the hardest to see.
