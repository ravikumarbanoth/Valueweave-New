# Impact Estimation

**Workstream 6** · Graph metrics before and after · measured baseline, derived projection

---

## 0. Method

**Before** figures are measured against commit `0d63a0a` — 647 entities, 865 edges — and
are reproducible.

**After** figures are derived from the 410 both-endpoint-verified edges in
`RELATIONSHIP_RECOVERY_REPORT.md` plus the 32 resolvable mappings in
`ENTITY_MATCHING_RULES.md`. They are arithmetic on verified joins, **not** estimates —
except where marked *(est.)*, which is limited to recommendation-count projections that
depend on user input.

---

## 1. Core graph metrics

| Metric | Before | After Stage A | After A+B | Δ |
|---|---:|---:|---:|---|
| Entities | 647 | 669 | 669 | +22 |
| **Edges** | **865** | **1,275** | **1,307** | **+51%** |
| Connected entities | 505 (78.1%) | 527 (78.8%) | **534 (79.8%)** | +29 |
| **Orphan entities** | **142 (21.9%)** | 138 (20.6%) | **135 (20.2%)** | **−7** |
| Average node degree | 2.64 | 3.81 | **3.90** | +48% |
| **Median node degree** | **1** | **2** | **2** | +1 |
| Edges per entity | 1.34 | 1.91 | **1.95** | +46% |
| Distinct edge shapes | 27 | 32 | 32 | +5 |
| Connected components | 150 | ~142 | ~139 | −11 |
| Largest component | 489 (75.6%) | ~525 (78%) | ~532 (80%) | +43 |

---

## 2. Reachability — where the value is

| Metric | Before | After | Δ |
|---|---:|---:|---|
| **Districts reaching a scheme in 1 hop** | **0 of 61** | **61 of 61** | **0 → 100%** |
| **Businesses with a skill edge** | **2 of 45** | **19 of 45** | **9.5×** |
| Skills reaching a business in 1 hop | 3 of 45 | **20 of 45** | 6.7× |
| Schemes with a district edge | 0 of 40 | 5 of 40 | +5 |
| Businesses with an MSME edge | 0 of 45 | 19 of 45 | +19 |
| Crops reaching a business | 0 of 45 | 17 of 45 | +17 |
| Districts with degree >1 | 27 of 61 | **61 of 61** | +34 |
| **Structurally dead rules** | **2** | **1** | −1 |

**Two rows carry this entire programme.**

`0 of 61 → 61 of 61` on district-to-scheme. Every district in both states gains its first
scheme edge, and `RS2-VIA_DISTRICT` — dead since the graph was first built — fires at one
hop for every user.

`2 of 45 → 19 of 45` on business-to-skill. The connection the recommendation engine most
depends on, improved 9.5× from a dataset that has been in `packages/` since Package005
was assembled.

**Both from zero new records.**

---

## 3. District coverage

| Metric | Before | After | Δ |
|---|---:|---:|---|
| Districts with degree 1 (state only) | **34** | **0** | −34 |
| Districts with ≥1 scheme edge | **0** | **61** | +61 |
| Districts with ≥1 institution | 27 | 27 | — |
| Districts with ≥1 MSME | 26 | 26 | — |
| Districts with ≥1 training centre | 0 | **~14** | +14 |
| Districts reaching an Industry | 2 | 2 | — |
| **Median district degree** | **1** | **6** | **6×** |

**All 34 degree-1 districts gain five scheme edges each.** They stop being "a name
attached to a state" and become a place with governed content — five schemes with
district-level agency and application channel recorded.

**Industry coverage does not move.** No dataset in the repository carries
`Industry → District`, so `RI3-VIA_DISTRICT` stays dead. That is Phase 1's E3 and needs
collection; Phase 2 does not claim it.

### Effect on `district_opportunity`

`DO1-RESOLVE` (vocabulary) · `DO2-DENSITY` (degree) · `DO3-DIVERSITY` (type variety).
Stage A moves DO2 and DO3 for every district.

| District band | Before | After *(est.)* |
|---|---:|---:|
| ≥70 | 1 | ~4 |
| 50–69 | 3 | ~10 |
| 30–49 | 12 | ~30 |
| **<30** | **45** | **~17** |
| **Median score** | **0** | **~34** |

*(est.)* — DO2/DO3 are relative to graph maxima, so exact values shift on rebuild. The
direction and rank order are determined by the edge counts.

**Still capped by vocabulary.** 42 of 61 districts cannot be named by a user
(`PILOT_DISTRICT_SELECTION.md` §3). A district can gain five scheme edges and still score
0 because `DO1-RESOLVE` fails. **The two-hour crosswalk extension is a prerequisite for
realising any of this**, and it is not part of Stage A.

---

## 4. Skill recommendation coverage

| Metric | Before | After A+B | After Package006 v1.1 |
|---|---:|---:|---:|
| Skill entities | 45 | 45 | 79 |
| Skills with a `REQUIRES_SKILL` edge | 40 | **42** | ~76 |
| Skills reaching a business | **3** | **20** | ~45 |
| Skills reaching a certification | **0** | **7** | ~24 |
| Skills reaching a training provider | 3 | 3 | ~25 |
| Onboarding resolution | 22.8% | 22.8% | **~86%** |

**Resolution does not move in Phase 2, and reachability moves 6.7×.** A user whose skill
already resolves goes from "matched to a dead node" to "matched to 20 of 45 businesses."

Phase 2 fixes the far side of the match. Package006 v1.1 fixes the near side. **Neither
alone is sufficient, and Phase 2 is the cheaper half** — 4 days against 6, and no
research.

---

## 5. Reachable recommendations

Projected against the six profiles in `VERSION1_READINESS_REPORT.md` §0.

| Profile | Now | After Phase 2 *(est.)* | + Package006 v1.1 *(est.)* |
|---|---:|---:|---:|
| Student — commerce | **1 of 10** | **3** | 6 |
| Student — ITI trades | 4 | **7** | 7 |
| Student — arts | **2** | **4** | 6 |
| Entrepreneur — agri | 2 | **6** | 6 |
| Faculty — no skills | **1** | **4** | 4 |
| Best case | 5 | **8** | 8 |

**Every profile gains, including the two that enter no usable skill.** Both dead rules
were district rules, and R1 revives one of them for everyone.

**The agri profile gains most** (2 → 6): R4, R5 and R6 all come from
`agri_business_mapping`, which connects crops, businesses and skills in a single dataset.

### By category

| Category | Before | After Phase 2 | Driver |
|---|---|---|---|
| `government_schemes` | 1 of 3 rules live | **3 of 3** | **R1** |
| `business_ideas` | Editorial only | Editorial + **19 graph-backed** | R5, M1 |
| `msmes` | Working | +19 business links | R3 |
| `courses` | Near-empty | **7 real certification links** | M2 |
| `industries` | 2 of 3 rules | 2 of 3 | **`RI3` needs E3** |
| `markets` · `research` · `collaborators` | Working | Unchanged | — |
| `mentors` · `events` | `NO_DATA_SOURCE` | **`NO_DATA_SOURCE`** | No source exists |

---

## 6. Where the estimates could be wrong

**Stated plainly, because the figures above are otherwise arithmetic.**

| Risk | Effect | Confidence |
|---|---|---|
| Duplicate edges between R5 and M1 | Edge count over-stated by ≤10 | **High** it happens. G12 catches it |
| `DO2`/`DO3` normalise against graph maxima | Every district gains, so relative gain compresses | Medium — the band table could be optimistic |
| Recommendation counts depend on user input | The six profiles are synthetic | Medium — direction is safe, magnitude is not |
| M1 curation may resolve fewer than 10 | Up to 10 fewer edges | Low |
| District vocabulary not extended | **`DO1-RESOLVE` fails and most of §3 does not materialise** | **This is the big one** |

**The last row is the dependency to manage.** Stage A can land in full and 42 of 61
districts still score 0, because the user cannot name them. Two hours of crosswalk work
gates a large share of the projected benefit, and it sits in a different plan.

---

## 7. Cost and return

| Stage | Days | Records | Edges | Headline |
|---|---:|---:|---:|---|
| P0 · logging fix | 0.25 | 0 | 0 | Makes everything else verifiable |
| **A · registrations** | **1.5** | **0** | **+410** | **`RS2` revived; 0→61 districts** |
| B · entity resolution | 1.5 | 0 | +32 | 7 orphans cleared |
| C · validation | 0.5 | 0 | 0 | G12–G15 |
| D · one typed 2-hop | 0.5 | 0 | 0 | `RS4`, 21 districts |
| **Total** | **4.25** | **0** | **+442** | |

**442 edges, zero records, 4.25 days.**

| Comparison | Records | Edges | Days | Edges/day |
|---|---:|---:|---:|---:|
| Packages 001–008 as built | 2,299 | 865 | months | — |
| Phase 1 Wave 1 estimate | 0 | ~1,255 | 5 | 251 |
| **Phase 2 measured** | **0** | **442** | **4.25** | **104** |

Phase 2 recovers fewer edges than Phase 1 projected because Phase 1 counted E2 (~450
business→district) and E3 (~200 industry→district) as recoverable. **They are not** — no
dataset in the repository carries either shape, and both require collection.

**Phase 2's 442 are verified. Phase 1's 1,255 included 650 that were aspirational.**
Correcting that is more useful than matching the earlier number.

---

## 8. Gate

| # | Metric | Before | Required |
|---|---|---:|---:|
| G1 | Edges | 865 | **≥1,275** |
| G2 | Districts reaching a scheme in 1 hop | **0** | **61** |
| G3 | Businesses with a skill edge | 2 | **≥19** |
| G4 | Median node degree | 1 | **≥2** |
| G5 | Dead rules | 2 | **1** |
| G6 | Duplicate edges / self-loops / dangling | 0/0/0 | **0/0/0** |
| G7 | Unresolved mapping rows logged | partial | **100%** |
| G8 | Orphans | 142 | **≤138** |
| G9 | Rebuild idempotent | pass | pass |
| G10 | Every new edge carries package/dataset/row | — | **100%** |

**G8 is deliberately unambitious.** Phase 1 set `<20`; the measurement says relationship
recovery clears **4**. Carrying the old target forward would fail a gate that the work
was never going to meet, and hide the real result — which is that reach improved
enormously while the orphan count barely moved, because they are different problems.

**G7 is the one that protects the rest.** Six new registrations into a builder that hides
its failures means the next mapping error is as invisible as the last, and
`unresolved_endpoints.csv` will still look complete.
