# ValueWeave — Knowledge Completion Master Plan

**Phase 1 · Knowledge Completion Mission** · Commit `da5d7aa` · 2026-07-26

Analysis only. No code, frontend, API, package data or test was modified.

---

## 0. The finding that changes the plan

The Version 1.0 Readiness Assessment concluded that the bottleneck was **missing
entities** — an apparent 108 unresolved skill terms, 22.8% onboarding resolution — and priced the
fix as "collect ~40 skills."

**That diagnosis was incomplete, and acting on it first would have wasted the effort.**

Tracing every recommendation failure to the graph shape that causes it produces a
different answer:

> ### The bottleneck is missing **relationships**, not missing entities.
>
> **Only 2 of 45 BusinessOpportunity entities have a skill edge.**
> **0 of 40 government schemes have a district edge.**
> **0 industries are linked to any district.**
>
> Every recommendation rule traverses **exactly one hop**
> (`KnowledgeSnapshot.neighbours`). The shortest path from a District to a
> BusinessOpportunity is **3 hops**. The graph contains the connection and the engine
> structurally cannot see it.

Collecting 40 new skills into a graph where 43 of 45 businesses carry no skill edge
adds vocabulary and no reach. The user resolves their skill, the engine finds the
Skill node, and there is nothing on the other side of it.

**Edges before entities.** That single reordering is the substance of this plan.

### The compounding failure

Two of the 21 recommendation rules are **structurally dead** — they cannot fire for any
user, in any district, ever:

| Rule | Requires | Edges that exist |
|---|---|---:|
| `RS2-VIA_DISTRICT` | `District -SUPPORTED_BY_SCHEME-> GovernmentScheme` | **0** |
| `RI3-VIA_DISTRICT` | `Industry -LOCATED_IN-> District` | **0** |

Both are **district** rules. District is the one attribute every user supplies and
which resolves at **100%** (33 of 33 terms).

So the platform's failure is not evenly distributed — it compounds:

```
User's skills don't resolve (77% of the time)
        └─► skill-path rules produce nothing
                └─► only the district path remains
                        └─► both district rules are dead
                                └─► 1 of 10 categories fills,
                                    from a static editorial file
```

**The one input that always works leads to the two rules that never do.** That is why
four of six simulated pilot profiles scored 0, and why 45 of 61 districts score under
30 with a median of 0.

### And district resolves at 100% only because of how it is counted

The 100% figure is real and it is narrower than it sounds:

```
district_crosswalk.csv:  33 terms  ->  19 distinct District entities
Districts a user cannot name at all:  42 of 61
```

All 33 *terms in the vocabulary* resolve. The vocabulary reaches **19 of 61 districts.**
Six districts with genuine graph substance — Chittoor, Hanumakonda, Krishna, Ranga Reddy,
Srikakulam, Prakasam — score **0** on `district_opportunity` purely because `DO1-RESOLVE`
cannot map their name. **Nalgonda and Chittoor have identical composite completeness
(18.7). Nalgonda scores 44 and Chittoor scores 0, and the only difference is a crosswalk
row.**

**Extending the crosswalk to all 61 districts is a two-hour mechanical `EXACT_NAME` match
against Package001's `district.csv`.** No research, no new entity, no new edge. It is the
highest return per hour in the programme and it was invisible until district completeness
was measured against the *vocabulary* rather than against the score.

Full analysis: `PILOT_DISTRICT_SELECTION.md` §3.

### What this reprices

| | Readiness assessment | This analysis |
|---|---|---|
| First action | Collect ~40 skills (3–4 d) | **Connect existing entities** (5 d) |
| Rationale | Raise resolution 22.8% → 80% | Resolution is useless without edges on the far side |
| Records to collect first | ~40 new skills | **0** — the entities already exist |
| Expected effect | Unlocks skill rules | Unlocks skill **and** both dead district rules |

Skill collection is still essential and still large. It is **second**, not first.

---

## 1. Graph shape — the evidence

647 entities · 865 edges · **1.34 edges per entity** · 27 distinct edge shapes.

### Connectivity is extremely uneven

| Entity type | Count | Edge shapes | Connected | Median degree |
|---|---:|---:|---:|---:|
| **MSME** | 40 | **10** | 100% | **6** |
| Crop | 45 | 6 | 100% | — |
| Industry | 78 | 5 | 78% | 1 |
| District | 61 | **3** | 100% | **1** |
| **BusinessOpportunity** | 45 | **3** | 100% | **1** |
| GovernmentScheme | 40 | 2 | **47.5%** | **0** |
| Skill | 45 | 3 | 89% | 2 |
| TrainingProvider | 25 | 1 | 12% | 0 |
| **Certification** | 30 | **0** | **0%** | **0** |

**`MSME` carries the graph.** It is the only richly-connected type — 10 shapes, 300+
edges — and it is the reason anything works at all.

**`BusinessOpportunity` is nearly a leaf**, despite being the product's core value
proposition. Three shapes: `PART_OF→Industry` (45), `SUPPORTED_BY_SCHEME` (12),
`REQUIRES_SKILL` (**3**).

**`District` is nearly a leaf.** Three shapes, and 34 of 61 districts have degree
**1** — their only edge is `LOCATED_IN` their own state.

### The graph is two halves joined at one hinge

```
GEOGRAPHY / EDUCATION                     OPPORTUNITY / SKILL
  State ──61── District                     BusinessOpportunity ──45── Industry
              ▲   ▲                                   │                   │
              │58 │32                                 │12                 │37
        Institution │                          GovernmentScheme      Skill
                    │                                 ▲
                    └────── MSME ──57─────────────────┘
                             ▲ the only hinge
                             │ 46 REQUIRES_SKILL
                           Skill
```

Everything a user *is* (district) lives on the left. Everything a user *could do*
(business opportunity) lives on the right. The only bridge is **MSME**, and it is
3 hops from a district to a business through it.

**Six edge shapes are absent and required by the rules:**

| # | Missing shape | Rules it unblocks | Est. edges |
|---|---|---|---:|
| **E1** | `BusinessOpportunity -REQUIRES_SKILL-> Skill` | RB1, BR1, RI1, SK4 | ~135 |
| **E2** | `BusinessOpportunity -SUITABLE_FOR-> District` | RB2, DO2, DO3 | ~450 |
| **E3** | `Industry -LOCATED_IN-> District` | **RI3 (dead)** | ~200 |
| **E4** | `GovernmentScheme -AVAILABLE_IN-> District` | **RS2 (dead)**, FR1 | ~350 |
| **E5** | `Certification -CERTIFIES-> Skill` | RC1, RC2, LR2 | ~30 |
| **E6** | `TrainingProvider -TRAINS-> Skill` / `-LOCATED_IN-> District` | LR3, RC2 | ~90 |

**≈1,255 relationships across zero new entities.** Detail and derivation:
`GRAPH_CONNECTIVITY_PLAN.md`.

---

## 2. Every recommendation failure, traced to its cause

The six workstreams exist because these are the six distinct causes. Each failure is
attributed to exactly one, so no work is duplicated across streams.

| # | Observed failure | Root cause | Missing | WS |
|---|---|---|---|---|
| F1 | 4 of 6 profiles score **0** on `skill_profile` | 77% of skills hit `NO_COUNTERPART` | **Entities** — 54 distinct skill terms | 1 |
| F2 | Resolved skills still recommend nothing | 43 of 45 businesses have no skill edge | **Relationships** — E1 | 2 |
| F3 | `RS2-VIA_DISTRICT` never fires | No scheme→district edge | **Relationships** — E4 | 2, 4 |
| F4 | `RI3-VIA_DISTRICT` never fires | No industry→district edge | **Relationships** — E3 | 2, 5 |
| F5 | 45 of 61 districts score <30, median 0 | 34 districts have degree 1 | **Relationships** — E2, E3, E4 | 2, 5 |
| F6 | `courses` returns near-nothing | 30 certifications have **0 edges**; 3 `TRAINED_BY` in total | **Relationships** — E5, E6 | 2 |
| F7 | 21 of 40 schemes unrecommendable | They are welfare schemes with no business link — see §4 | **Classification**, not edges | 4 |
| F8 | Healthcare invisible: 146 rows, 0 entities | No entity type registered; 3 of 4 datasets collide with owned types | **Package content** + model | 3 |
| F9 | `business_ideas` only ever fills from a static file | The graph cannot answer it — E1 and E2 absent | **Relationships** — E1, E2 | 2 |
| F10 | `mentors`, `events` always `NO_DATA_SOURCE` | No source exists anywhere | **Application data** | 6 |
| F11 | `LR3-PROVIDER` reports its own gap | 3 `TRAINED_BY` edges for 25 providers | **Relationships** — E6 | 2 |
| F12 | Sector interest resolves at 50% | 6 sectors absent from the taxonomy | **Entities** — sectors | 1, 6 |
| F13 | 6 districts with real data score **0** | Onboarding vocabulary reaches 19 of 61 districts | **Vocabulary** — a crosswalk row | 5 |

**Nine of thirteen failures are relationship failures.** Two are entity failures, one is
a classification failure, and one is a two-hour vocabulary gap. **Not one is an infrastructure failure** — which confirms the
mission's premise.

---

## 3. Workstream 1 — Package006 and skill resolution

Full detail: **`PACKAGE006_BACKLOG.md`**

### Ranking is measurable, not a judgement call

The 122 editorial ideas declare `skills_needed`. That gives a real frequency signal:

| Unresolved skill | Ideas requiring it | In onboarding? |
|---|---:|---|
| **Customer Handling** | **64 of 122** | ✓ |
| **Sales** | **42** | ✓ |
| Vendor Management | 28 | ✓ |
| Operations Coordination | 28 | ✓ |
| Digital Marketing | 19 | ✓ |
| Inventory Management | 17 | ✓ |
| Team Management | 17 | ✓ |
| Content Writing | 17 | ✓ |
| Social Media Management | 17 | ✓ |
| Field Marketing | 16 | ✓ |
| Teaching | 16 | — |
| Local Sales | 16 | — |

**397 of 459 idea-skill slots (86.5%) are blocked by an unresolved skill.** One term —
*Customer Handling* — blocks 64 of 122 ideas on its own.

### The cluster nobody researched

Every top-ranked term is a **generic commercial or operational** skill: selling,
handling customers, coordinating suppliers, managing stock, marketing. Package006's 45
skills are almost entirely **technical**: CNC operation, PCB assembly, solar
installation, Python, CAD/CAM.

**The package researched what a factory needs and the platform serves people who want
to run a small business.** That is the gap in one sentence, and it explains why the
commerce-student profile is the emptiest in the platform.

### Target and honest ceiling

| | Current | Target | Achievable |
|---|---:|---:|---:|
| Onboarding skill resolution | **22.8%** | **80%** | **86%** (49 of 57) |
| Skill vocabulary overall | 26.5% | 80% | 82% |
| Idea-skill slots resolvable | 13.5% | — | **94%** |

80% is reachable. Reaching it requires **34 new skills** plus 9 curated mappings —
**not** the 40 the readiness assessment estimated, because 11 of the backlog terms are
synonyms of skills that already exist and need a crosswalk entry rather than research.

**Package006 must be completed first (K5).** It has no `VERSION`, `README`,
`CHANGELOG`, `package_manifest.json` or `validate.py`, and `metadata/` and `registry/`
are empty directories. New skills would land in the one package with no quality
harness.

---

## 4. Workstream 4 — Government schemes

Full detail in **`GRAPH_CONNECTIVITY_PLAN.md` §4**.

### The 21 orphans are not a linking problem

Reading the actual names changes the task:

> Atal Pension Yojana · Ayushman Bharat PM-JAY · MGNREGS · National Food Security Act
> (PDS) · PM Awas Yojana (Gramin and Urban) · PM Jan Dhan Yojana · PM Jeevan Jyoti Bima
> · PM Suraksha Bima · PM-KISAN · PM Matru Vandana · PM Poshan Shakti Nirman · Samagra
> Shiksha · National Social Assistance Programme · four scholarship schemes · Soil
> Health Card

**These are citizen-welfare schemes — pension, health insurance, food security,
housing, scholarships, maternity benefit.** They have no natural
`REQUIRES_SKILL` or `SUPPORTED_BY_SCHEME` relationship to a business, because they are
not business schemes.

**Linking MGNREGS to an MSME would be inventing a relationship**, which the platform's
own governance forbids. The 21 are not badly connected; they are **miscategorised as
business content**.

### Recommendation: classify, then connect what belongs

**Step 1 — add `scheme_class` to Package007** (a column, not new rows):

| Class | Est. | Treatment |
|---|---:|---|
| `ENTERPRISE` | ~19 | Connect to industries, skills, MSMEs, districts |
| `WELFARE` | ~17 | Eligibility model — district + demographic, **not** business |
| `EDUCATION` | ~4 | Link to Institution, not to business |

**Step 2 — the four dimensions the mission asks about, measured:**

| Dimension | Schemes with ≥1 link | of 40 |
|---|---:|---:|
| MSME | 13 | 32.5% |
| BusinessOpportunity | 7 | 17.5% |
| FinancialInstitution | 7 | 17.5% |
| Skill | 5 | 12.5% |
| **Industry** | **0** | **0%** |
| **District** | **0** | **0%** |

**Industry and district are at zero.** Those two absences kill `RS2` and starve `FR1`.
For a `WELFARE` scheme the district link is the *only* useful one — which is why E4
serves both classes and is the highest-value scheme work.

**Step 3 — a second surface.** Welfare schemes are genuinely valuable to a student:
Jan Dhan, Ayushman Bharat and a post-matric scholarship all matter. They belong in a
*"benefits you may be eligible for"* surface keyed on district and demographics, not
mixed into business recommendations. That is a v1.2 product item; the classification
that enables it is a v1.1 data item.

---

## 5. Workstream 3 — Package003 Healthcare

Full detail: **`PACKAGE003_INTEGRATION_PLAN.md`**

146 rows, Stable v1.0.0, **0 entities, 0 edges**. The cause is not neglect —
`build_graph.py` registers 19 entity types and none maps to Package003.

**Why it was skipped is the interesting part.** Three of its four datasets collide with
types another package already owns:

| Dataset | Rows | Natural type | Owner |
|---|---:|---|---|
| `government_hospitals_*` | 55 | **none exists** | — |
| `medical_colleges_*` | 58 | `Institution` | **Package002** |
| `government_health_insurance_schemes` | 9 | `GovernmentScheme` | **Package007** |
| `medical_regulatory_bodies_*` | 24 | `Institution`-ish | ambiguous |

`knowledge_graph/ownership/known_overlaps.csv` **already governs the scheme overlap**
under ADR-003 — Package003's schemes are among the 79 domain rows carrying
`package007_scheme_id` and `scheme_ownership`. So the hardest question is answered; the
remaining work is a model decision plus a builder change.

Recommended: **one new entity type (`Hospital`, 55)**, medical colleges as
`Institution` under Package002's ownership with `also_in_package`, schemes deferred to
the existing ADR-003 crosswalk, regulatory bodies as `RegulatoryBody` (24).

**≈79 new entities and ≈240 new edges** — and it makes healthcare the **fourth**
industry with real district coverage, which matters directly to Workstream 5.

---

## 6. Workstream 5 — Pilot districts

Full detail: **`PILOT_DISTRICT_SELECTION.md`**

Measured across five dimensions. The distribution is stark:

| | |
|---|---:|
| Districts with degree 1 (only their state) | **34 of 61** |
| Districts with ≥1 Institution | 27 |
| Districts with ≥1 MSME | 26 |
| Districts with ≥1 Industry link | **0** |
| Districts with a reachable BusinessOpportunity within 1 hop | **0** |
| `district_opportunity` ≥50 | **4** |
| Median `district_opportunity` | **0** |

**Recommended pilot districts — 4, not 12:** Hyderabad (85), Guntur (59), Tirupati
(51), Visakhapatnam (50). They are also where the institutions are — Hyderabad 12,
Tirupati 7, Guntur 6, Visakhapatnam 3 — so coverage and recruitment are the same
problem.

**Two tiers after the edge work lands:** the same 4 plus Nizamabad, Nalgonda, Kurnool,
Karimnagar, Sangareddy, East and West Godavari, Krishna — 12 districts covering an
estimated 60% of the likely student population.

---

## 7. Workstream 6 — Collection queue

Full detail: **`KNOWLEDGE_COLLECTION_QUEUE.md`**

| Wave | Work | New records | New edges | Days | Resolution | Districts ≥50 |
|---|---|---:|---:|---:|---:|---:|
| — | *baseline* | — | — | — | **22.8%** | **4** |
| **W0** | Prerequisites — incl. district vocabulary → 61 | **0** | 0 | 0.5 | 22.8% | 4 |
| **W1** | Connect what exists (E1–E6) | **0** | **~1,255** | 5 | 22.8% | **~14** |
| **W2** | Package006 completion + 34 skills | 34 | ~180 | 6 | **~80%** | ~16 |
| **W3** | Scheme classification + E4 | 0 | ~350 | 3 | 80% | ~20 |
| **W4** | Healthcare integration | 79 | ~240 | 4 | 80% | ~24 |
| **W5** | District deepening, 12 pilot districts | ~120 | ~400 | 5 | 80% | ~30 |
| **Total** | | **~233** | **~2,425** | **23.5** | | |

**Ratio: 10 relationships per new record.** The inverse of how the packages were built,
and the correction this plan exists to make.

**Wave 1 adds zero records and is the highest-impact wave.** It brings both dead rules
to life and roughly triples the number of viable pilot districts, using entities that
are already researched, sourced and validated.

---

## 8. Sequencing

```
W0  Prerequisites               ▌                           0.5 d ← 4 hours, do first
W1  Connect what exists         ████████                    5 d   ← start here
W2  Package006 + 34 skills          ██████████              6 d   (K5 gates it)
W3  Scheme classification                   ██████          3 d
W4  Healthcare integration                       ████████   4 d
W5  District deepening                              █████   5 d
```

**W1 before W2 is the plan's one non-obvious claim, so here it is plainly:** doing W2
first means 34 new Skill entities landing in a graph where 43 of 45 businesses have no
skill edge. Users would resolve their skills and still see nothing, and the platform
would have spent six days to move one metric that no user experiences directly.

W1 and W2 are independent of W3–W5, which can run in any order.

---

## 9. Success criteria

Re-measure with the six-profile simulation in `VERSION1_READINESS_REPORT.md` §0.

| Metric | Baseline | After W1 | After W2 | Target |
|---|---:|---:|---:|---:|
| Onboarding skill resolution | 22.8% | 22.8% | ~80% | **80%** |
| Orphan entities | 142 | **~18** | ~18 | **<20** |
| Structurally dead rules | **2** | **0** | 0 | **0** |
| Businesses with a skill edge | 2 of 45 | **45 of 45** | 45 | 45 |
| Schemes with a district link | 0 of 40 | 40 of 40 | 40 | 40 |
| Districts scoring ≥50 | 4 | ~14 | ~16 | **≥12** |
| Districts a user can name | **19 of 61** | 61 | 61 | **61** |
| Profiles filling ≥3 of 10 categories | 2 of 6 | ~5 of 6 | **6 of 6** | **6 of 6** |
| Profiles scoring 0 on skills | 4 of 6 | 4 of 6 | **0 of 6** | **0** |
| Edges per entity | 1.34 | ~3.3 | ~3.4 | **≥3.0** |

**The gate is the simulation, not the metrics.** Every profile fills at least three
categories and at least one is non-editorial. Metrics that move without moving that are
not progress.

---

## 10. What this plan deliberately does not do

**It does not propose new infrastructure.** Every gap named here is closed by data in
`packages/` and a rebuild of the graph. No new table, engine, rule or endpoint appears
in any of the six documents.

**It does not propose fabricating relationships.** Every edge in W1 is derivable from a
column that already exists in a package CSV — `district_fit`, `skills_needed`,
`jurisdiction`, an NSQF qualification pack code — or is a documented research task with
a source. `GRAPH_CONNECTIVITY_PLAN.md` names the derivation for each of the six shapes,
and the ones that cannot be derived are listed as collection tasks rather than inferred.

**It does not propose linking the 21 welfare schemes to businesses.** The relationship
does not exist in the world, so it must not exist in the graph. Classifying them and
building a separate eligibility surface is the honest answer, and it is slower.

**It does not add a Mentor or Event entity type.** No source exists for either. They
stay `NO_DATA_SOURCE` until one does — `MISSING_FEATURES.md` §1 explains why a seeded
mentor is worse than an empty category.

---

**Companion documents:** `PACKAGE006_BACKLOG.md` · `PACKAGE003_INTEGRATION_PLAN.md` ·
`GRAPH_CONNECTIVITY_PLAN.md` · `PILOT_DISTRICT_SELECTION.md` ·
`KNOWLEDGE_COLLECTION_QUEUE.md`
