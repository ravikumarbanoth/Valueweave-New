# Knowledge Collection Queue

**Workstream 6** · Prioritised roadmap · **~233 records · ~2,425 relationships · 23 days**

---

## 0. The ratio that defines this queue

| | Packages 001–008 (built) | This queue |
|---|---:|---:|
| Records | 2,299 | **233** |
| Relationships | 865 | **~2,425** |
| Ratio | **0.38 edges per record** | **10.4 edges per record** |

The packages were built record-first. **A record nobody can reach from anywhere is
inventory, not knowledge**, and 142 orphan entities plus two structurally dead rules are
what that produces. This queue inverts the ratio.

---

## 1. Prerequisites — 4 hours, before any collection

Four defects that would corrupt or waste the work below. Two are builder bugs, two are
package hygiene.

| # | Item | Effort | Why it blocks |
|---|---|---:|---|
| **P1** | **Log silently-dropped mapping rows** in `build_graph.py` | 2 h | 27 of 30 `skill_business_mapping` rows vanish with no log entry, while the certification path logs all 122 of its failures. **The inconsistency is the bug** — a failure log that looks complete and isn't will hide every mapping error in this queue |
| **P2** | **Register `training_centres.csv`** in the builder | 1 h | 22 rows with `district_id` and trades offered have never been read |
| **P3** | **Package006 `validate.py`** + fix the category defect | *in W2* | 42 of 45 skills are labelled "Soft Skills & Communication", which makes `RC2`'s category fallback actively misleading |
| **P4** | **District vocabulary → all 61** | 2 h | 42 districts cannot be named by a user; six with real data score 0 |

**P4 is the single highest return per hour in the programme.** Mechanical `EXACT_NAME`
matching against Package001's `district.csv`. No research.

---

## 2. The five waves

| Wave | Work | Records | Edges | Days | Resolution | Districts ≥50 | Orphans |
|---|---|---:|---:|---:|---:|---:|---:|
| — | *baseline* | — | — | — | 22.8% | **4** | **142** |
| **W1** | Connect what exists | **0** | **~1,255** | **5** | 22.8% | **~14** | **~18** |
| **W2** | Package006 v1.1 | 34 | ~180 | 6 | **~86%** | ~16 | ~18 |
| **W3** | Scheme classification | 0 | ~350 † | 3 | 86% | ~20 | ~18 |
| **W4** | Healthcare | 137 | ~240 | 4 | 86% | ~24 | ~26 |
| **W5** | District deepening | ~62 | ~400 | 5 | 86% | **~30** | ~26 |
| | **Total** | **233** | **~2,425** | **23** | | | |

† W3's E4 edges are counted in W1; W3 adds the `ENTERPRISE` scheme links.

---

## W1 · Connect what exists — 5 days · **zero new records**

**The highest-impact wave, and it collects nothing.** Every edge joins entities that are
already researched, sourced and validated.

| # | Task | Edges | Days | Research? |
|---|---|---:|---:|---|
| **E4** | Scheme → District, from `jurisdiction` | ~350 | 0.5 | **No** |
| **E5** | Certification → Skill, reconcile 122 labels | ~30 | 0.5 | **No** |
| **E6** | Provider → Skill/District, from `training_centres.csv` | ~90 | 0.5 | **No** |
| **E1** | Business → Skill, reconcile 25 business names | ~135 | 1.5 | Partly |
| **E2** | Business → District suitability | ~450 | 1.5 | **Yes** |
| **E3** | Industry → District presence | ~200 | 1.0 | **Yes** |

**Start with E4, E5, E6 — 1.5 days, ~470 edges, no research.** They bring
`RS2-VIA_DISTRICT` from dead to live, clear **52 orphans**, and give the `courses`
category its first real evidence base.

**Expected effect**

| | Before | After |
|---|---:|---:|
| Edges per entity | **1.34** | **~3.3** |
| Orphans | 142 | **~18** |
| Structurally dead rules | **2** | **0** |
| Businesses with a skill edge | **2 of 45** | **45 of 45** |
| Schemes with a district link | **0 of 40** | **40 of 40** |
| Districts scoring ≥50 | 4 | **~14** |
| Profiles filling ≥3 of 10 categories | 2 of 6 | **~5 of 6** |

**Skill resolution does not move.** That is the point: recommendation quality improves
substantially without a single new skill, because the failure was reach and not
vocabulary.

---

## W2 · Package006 v1.1 — 6 days · 34 records

Detail: `PACKAGE006_BACKLOG.md`.

| Stage | Work | Records | Edges | Days |
|---|---|---:|---:|---:|
| 0 | Complete the package; fix the category defect | 0 | 0 | 1.0 |
| 1 | 11 crosswalk + 9 curated entries | 0 | 0 | 0.25 |
| 2 | **P0** — 20 commercial/creative skills | 20 | ~110 | 3.0 |
| 3 | **P1** — 14 skills | 14 | ~70 | 2.0 |
| 4 | Validate, rebuild, promote v1.1.0 | 0 | 0 | 0.5 |

**Ranked by measured demand** — how many of the 122 editorial ideas each skill unlocks:

| Skill | Ideas blocked |
|---|---:|
| Customer Handling | **64** |
| Sales | **42** |
| Operations Coordination · Vendor Management | 28 each |
| Digital Marketing | 19 |
| Content Writing · Inventory · Social Media · Team Management | 17 each |

**397 of 459 idea-skill slots (86.5%) are blocked.** *Customer Handling* alone blocks 64
of 122 ideas.

**Definition of done: every new skill ships with ≥2 edges.** A skill with none is a
vocabulary entry pretending to be knowledge, and the user experience is worse than an
honest `NO_COUNTERPART` — the platform stops saying "we haven't researched this" and
starts saying nothing.

**Resolution: 22.8% → ~86%.** Ceiling is 86%, not 100%: four terms are genuinely
ambiguous and four have no NSQF pathway in either state.

---

## W3 · Scheme classification — 3 days · zero new records

| # | Task | Edges | Days |
|---|---|---:|---:|
| S1 | Add `scheme_class` — `ENTERPRISE` / `WELFARE` / `EDUCATION` | 0 | 0.5 |
| S2 | Industry links for the 19 `ENTERPRISE` schemes | ~40 | 0.75 |
| S3 | Skill links (11 edges today) | ~35 | 0.75 |
| S4 | MSME links beyond the current 13 schemes | ~25 | 0.5 |
| S5 | Business-model eligibility | ~30 | 0.5 |

**The 21 orphan schemes are not a linking problem.** Reading their names — Atal Pension
Yojana, Ayushman Bharat, MGNREGS, PDS, PM Awas Yojana, Jan Dhan, PM-KISAN, four
scholarships — they are **citizen-welfare schemes**. They have no business relationship
because they are not business schemes.

**Linking MGNREGS to an MSME would invent a relationship that does not exist.** These
schemes need district + demographic eligibility, which E4 already gives them. A
*"benefits you may be eligible for"* surface is v1.2 **product** work and is not in this
queue.

---

## W4 · Healthcare — 4 days · 137 records

Detail: `PACKAGE003_INTEGRATION_PLAN.md`.

| Stage | Work | Records | Edges | Days |
|---|---|---:|---:|---:|
| 1 | ADR-006 governance; register types | 0 | 0 | 0.5 |
| 2 | `also_in_package`, `dist_ref` foreign keys | 0 | 0 | 1.0 |
| 3 | Builder: `Hospital` 55, `RegulatoryBody` 24, `Institution` +58 | 137 | ~240 | 1.5 |
| 4 | Validate; add `kg_hospitals` to sync | 0 | 0 | 1.0 |

146 researched rows — **6.4% of everything collected** — are currently invisible.

**After W1, deliberately.** Two of its five recommendation benefits depend on E3 and E4.
Done first it would add 137 entities and 240 edges and move nothing a user sees.

**Watch the orphan budget.** ~8 of 24 regulatory bodies will have no edge, against
~2 of headroom under the <20 target. Either cap the type or accept 26.

**H8 excluded on purpose.** Inferring "healthcare is present in this district" from a
hospital's address is reasonable and still an inference; presented as a researched edge it
would carry provenance it has not earned.

---

## W5 · District deepening — 5 days · ~62 records

| # | Task | Records | Edges | Days |
|---|---|---:|---:|---:|
| D1 | Industrial profiles, 12 pilot districts | ~12 | ~150 | 1.5 |
| D2 | MSME clusters in tier-2 districts | ~24 | ~120 | 1.5 |
| D3 | 6 backlog **sectors** into Package004 | 6 | ~40 | 1.0 |
| D4 | Mandal geography (`mandal.csv` is header-only) | ~20 | ~90 | 1.0 |

**D3 is Package004's, not Package006's:** Beauty & Wellness, Climate Tech, Drone Tech,
Events & Entertainment, Repair Economy, Sports & Fitness — the six unresolved sector
terms, at 50% sector resolution.

**Re-scope D1 and D2 after the pilot.** Deepening districts chosen from a list written
today is guessing; the pilot's ranked list of where students actually are is the input
this wave should use.

---

## 3. Expected recommendation improvement

Measured against the six-profile simulation in `VERSION1_READINESS_REPORT.md` §0.

| Profile | Now | W1 | W2 | Target |
|---|---:|---:|---:|---:|
| Student — commerce | **1 of 10** | 3 | **6** | ≥3 |
| Student — ITI trades | 4 | **7** | 7 | ≥3 |
| Student — arts | **2** | 3 | **6** | ≥3 |
| Entrepreneur — agri | **2** | 4 | **6** | ≥3 |
| Faculty — no skills | **1** | **4** | 4 | ≥3 |
| Best case | 5 | **8** | 8 | ≥3 |
| **Profiles scoring 0 on skills** | **4 of 6** | 4 of 6 | **0 of 6** | **0** |

**W1 fixes the district-only profiles. W2 fixes the unresolved-skill profiles.** Neither
alone clears the gate; together they do.

Note the faculty profile — no skills entered at all — going from 1 to 4 categories in W1
**without any skill work**. Both dead rules were district rules, and district is the one
input that always resolves.

### Per-category

| Category | Now | After W1+W2 | Driver |
|---|---|---|---|
| `business_ideas` | Editorial only, confidence 0 | **Graph-backed** | E1, E2 |
| `government_schemes` | 1 of 3 rules live | **3 of 3** | E4 |
| `industries` | 2 of 3 rules live | **3 of 3** | E3 |
| `courses` | Near-empty | Real | E5, E6 |
| `msmes` · `markets` · `collaborators` | Working | Improved | E1, E8 |
| `research` | Working | Unchanged | — |
| `mentors` · `events` | `NO_DATA_SOURCE` | **`NO_DATA_SOURCE`** | No source exists |

`mentors` and `events` stay empty. No source exists for either, and a seeded mentor is an
unsourced claim about a person — `MISSING_FEATURES.md` §1.

---

## 4. Sequencing

```
P1–P4  Prerequisites          ▌                          0.5 d
W1     Connect what exists    ████████                     5 d   ← start here
W2     Package006 v1.1            ██████████               6 d
W3     Scheme classification              ██████           3 d
W4     Healthcare                              ████████    4 d
W5     District deepening                          █████   5 d
                                                          ──────
                                                          23.5 d
```

**W1 before W2 is this queue's one non-obvious claim.** Doing W2 first means 34 new Skill
entities landing where 43 of 45 businesses have no skill edge: users resolve their skills
and still see nothing, and six days move a metric no user experiences.

W3, W4, W5 are independent of each other and of W2. **W1 gates everything worth doing.**

---

## 5. Gate

Not the metrics — the simulation.

| Gate | Requirement |
|---|---|
| **G1** | Every one of the six profiles fills **≥3 of 10** categories |
| **G2** | **No** profile scores 0 on `skill_profile` |
| **G3** | Every profile has **≥1 non-editorial** category filled |
| **G4** | Orphan entities **<20** |
| **G5** | Structurally dead rules **= 0** |
| **G6** | Edges per entity **≥3.0** |
| **G7** | `validate_graph.py` clean, including G11 ownership |
| **G8** | Every new record carries all six provenance columns |

**G3 is the one that matters.** Today `business_ideas` fills for every profile from a
static editorial file at `confidence = 0`. A platform whose only universal answer is
editorial content is a content site with a knowledge base attached. G3 inverts that.

---

## 6. Out of scope, and why

| Not doing | Reason |
|---|---|
| Mentor entities | No source. A fabricated mentor is an unsourced claim about a person |
| Event entities | No source. Scheme-deadline collection is a W6 candidate |
| Linking 21 welfare schemes to businesses | The relationship does not exist in the world |
| H8 healthcare-district inference | An inference wearing researched provenance |
| Forcing the 4 ambiguous skill terms | A confident wrong answer beats no answer only for the platform, never for the user |
| Animation, Voice Over, Influencer Marketing, Community Driven Sales | No NSQF pathway in either state; every meaningful column would be `PENDING_VERIFICATION` |
| Human review of 2,299 rows | Real and separate. `VERSION1_READINESS_REPORT.md` K2 — 2 days for the top 40 |
| Any new table, engine, rule or endpoint | The mission's premise, and it held: **every gap here closes with package data and a graph rebuild** |
