# Package006 — v1.1 Backlog

**Workstream 1** · Target: onboarding skill resolution **22.8% → 80%+**

*(Satisfies the `PACKAGE006_V1_1_BACKLOG.md` deliverable named in Workstream 1.)*

---

## 0. Three corrections to the readiness assessment

Measuring the backlog properly changed three of its numbers. All three make the job
smaller, and one makes it different in kind.

| | Readiness assessment | Measured | Why |
|---|---|---|---|
| Backlog size | "108 skill terms" | **54 distinct terms** | 108 counted *rows* across three source vocabularies; 54 are distinct skills. The same term appears in onboarding and in the idea library. |
| Skills to research | ~40 | **34 research + 11 crosswalk + 9 curated** | 11 backlog terms are synonyms of skills that already exist and need a crosswalk row, not a research task. |
| Nature of the work | "collect more skills" | **collect a different *kind* of skill** | Package006 researched technical trades. The blocked terms are commercial and operational. |

---

## 1. Root cause — the package researched the wrong half

`skill_categories.csv` declares **24 categories**, and they are the right 24: Retail,
Business & Finance, Logistics & Supply Chain, Creative Arts & Media, Hospitality,
Entrepreneurship, Soft Skills & Communication, alongside the technical ones.

`skills.csv` holds 45 skills. Reading them against the taxonomy:

| Category group | Skills researched | Backlog terms blocked |
|---|---:|---:|
| Technical — mechanical, electrical, electronics, IT, agri, food | **45** | 12 |
| **Commercial** — retail, sales, business & finance, procurement | **0** | **19** |
| **Operational** — logistics, ops, inventory, packaging | **0** | **9** |
| **Creative & media** | **0** | **8** |
| **Services** — teaching, beauty, housekeeping, lab | **0** | **6** |

**The taxonomy was scoped correctly and only the technical half was collected.** That
single fact explains the entire resolution gap, and it means the collection brief is
already written — fill the categories that exist and are empty.

### Two defects found while measuring

**Defect 1 — 42 of 45 skills are categorised as "Soft Skills & Communication."**

```
Python Programming          -> Soft Skills & Communication
Welding (MIG/TIG/Arc)       -> Soft Skills & Communication
CNC Machine Operator        -> Soft Skills & Communication
```

One `category_id` (`e02aa4f6…`) is repeated across 42 rows. The foreign key joins, so
nothing structural fails — the *values* are wrong. Only 3 skills (Electronics,
Agriculture, Food Processing) are correctly categorised.

**This has a live product consequence.** `RC2-PROVIDER_IN_DISTRICT` falls back to
recommending *"a certification in the same category as your gap skill."* With 42 skills
in one category, that fallback will offer a beautician certification to someone whose
gap skill is Python — and it will do so with a reason string that sounds authoritative.

**Defect 2 — the package has no validator.** `validate.py` is absent, along with
`VERSION`, `README.md`, `CHANGELOG.md` and `package_manifest.json`; `metadata/` and
`registry/` are empty directories. Defect 1 is exactly what a validator catches. It went
undetected for the same reason it can recur.

**Fix Defect 2 before collecting anything.** Otherwise 34 new skills land in the one
package with no quality harness, and the next defect is also invisible.

---

## 2. Ranking — measured, not judged

The 122 editorial ideas declare `skills_needed`, which gives a real demand signal:
**how many business ideas each skill unlocks.**

| Rank | Skill | Ideas | Onboarding | Category to fill | Tier |
|---:|---|---:|:---:|---|---|
| 1 | **Customer Handling** | **64** | ✓ | Soft Skills | **P0** |
| 2 | **Sales** | **42** | ✓ | Retail | **P0** |
| 3 | Operations Coordination | 28 | ✓ | Entrepreneurship | **P0** |
| 4 | Vendor Management | 28 | ✓ | Business & Finance | **P0** |
| 5 | Digital Marketing | 19 | ✓ | Digital Skills | **P0** |
| 6 | Content Writing | 17 | ✓ | Creative Arts | **P0** |
| 7 | Inventory Management | 17 | ✓ | Logistics | **P0** |
| 8 | Social Media Management | 17 | ✓ | Digital Skills | **P0** |
| 9 | Team Management | 17 | ✓ | Soft Skills | **P0** |
| 10 | Field Marketing | 16 | ✓ | Retail | **P0** |
| 11 | Local Sales | 16 | — | Retail | P1 |
| 12 | Teaching | 16 | — | Soft Skills | P1 |
| 13 | Event Management | 12 | ✓ | Hospitality | **P0** |
| 14 | Packaging | 12 | ✓ | Logistics | **P0** |
| 15 | Logistics | 10 | — | Logistics | P1 |
| 16 | Graphic Design | 7 | ✓ | Creative Arts | **P0** |
| 17 | Construction Supervision | 7 | — | Construction | P1 |
| 18 | Mechanical Work | 7 | — | Mechanical | P1 † |
| 19 | Accounting | 6 | ✓ | Business & Finance | **P0** |
| 20 | AI Engineering | 5 | ✓ | AI & Data | P1 † |
| 21 | Photography | 5 | ✓ | Creative Arts | **P0** |
| 22 | Lab Operations | 5 | — | Healthcare Support | P1 |
| 23 | Beautician Services | 4 | ✓ | Services | **P0** |
| 24 | UI/UX Design | 4 | ✓ | Digital Skills | **P0** |
| 25 | Retail Operations | 4 | — | Retail | P1 |
| 26 | SEO | 3 | ✓ | Digital Skills | **P0** |
| 27 | Voice Over | 2 | ✓ | Creative Arts | P1 |
| 28 | Agriculture | 2 | — | Agriculture | P1 † |
| 29 | CCTV Installation | 1 | ✓ | Electronics | P1 |
| 30 | Dairy Management | 1 | ✓ | Agriculture | P1 |
| 31 | Soil Testing | 1 | ✓ | Agriculture | P1 |
| 32 | Community Driven Sales | 1 | — | Retail | P2 |
| 33 | Printing | 1 | — | Mechanical | P2 |

† **Crosswalk, not research** — see §3.

### Onboarding-suggested with zero idea demand — 21 terms

These are offered to users in the onboarding form but no editorial idea requires them.
Still **P1**, because a user who types one and gets nothing has a worse experience than
one who was never offered it.

> Agri Equipment Handling · Animation · Business Development · Crop Advisory ·
> **Data Entry** · Financial Planning · Furniture Manufacturing · **GST Filing** ·
> Housekeeping Services · Influencer Marketing · Irrigation Systems ·
> Legal Documentation · Loan Documentation · Local Advertising · Machine Operations † ·
> Poultry Management · Printing Operations · Procurement · **Retail Management** ·
> Seed Management · Textile Production †

**Data Entry, GST Filing and Retail Management deserve promotion to P0** on user value
rather than idea frequency: they are among the most common real skills in the target
audience and the most likely to be typed by a commerce student, which the six-profile
simulation confirmed is the emptiest experience in the platform.

### The number that frames the whole workstream

**397 of 459 idea-skill slots (86.5%) are blocked by an unresolved skill.**
*Customer Handling* alone blocks **64 of 122 ideas**.

---

## 3. Eleven terms that need a crosswalk row, not research

| Backlog term | Existing entity | Method |
|---|---|---|
| Mechanical Work | Lathe Operation *(multi)* | `_multi_candidate` |
| Machine Operations | CNC Machine Operator *(multi)* | `_multi_candidate` |
| Agriculture | Modern Farming Techniques *(multi)* | `_multi_candidate` |
| AI Engineering | AI Model Training *(multi)* | `_multi_candidate` |
| Textile Production | Garment Manufacturing (Stitching) | `CURATED` |
| Video Production | Video Editing & Content Creation | `CURATED` |
| Cloud Administration | AWS/Azure Cloud Administration | `PREFIX` |
| Web Development | Full Stack Web Development | `PREFIX` |
| Data Analysis | Big Data Analysis | `PREFIX` |
| Nursing | Nursing Assistant / MPHW | `PREFIX` |
| Hotel Management | Hotel Management & Front Office | `PREFIX` |

**Four are genuinely ambiguous** and must stay `NO_COUNTERPART` with a `MULTI:` note —
forcing "Mechanical Work" onto one of Lathe Operation, CNC or Welding would assert
something the user did not say. Step 0's `_multi_candidate` mechanism exists for this.

**Cost: ~2 hours.** These 11 terms move resolution by ~19 percentage points on their own.

---

## 4. The trap: resolution without reach

**Raising resolution to 80% changes nothing on its own.**

| | |
|---|---:|
| BusinessOpportunity entities with a skill edge | **2 of 45** |
| Skill entities with no `REQUIRES_SKILL` edge | 5 of 45 |
| `Certification -CERTIFIES-> Skill` edges | **0** |
| `Skill -TRAINED_BY-> TrainingProvider` edges | **3** |

A resolved skill leads to a Skill node. If nothing hangs off that node, the user has
been matched to a dead end — and the experience is identical to not resolving at all,
except now the platform looks like it understood and still had nothing.

**Every new skill must ship with its edges**, or it is a vocabulary entry pretending to
be knowledge:

| Edge | Per new skill | Source |
|---|---:|---|
| `Industry -REQUIRES_SKILL->` | 1–2 | `industry_skill_mapping.csv` |
| `BusinessOpportunity -REQUIRES_SKILL->` | 1–3 | `skill_business_mapping.csv` |
| `Certification -CERTIFIES->` | 0–1 | `certifications.csv` |
| `Skill -TRAINED_BY->` | 0–1 | `training_providers.csv` |

**Definition of done for a new skill: ≥2 edges.** A skill with 0 edges must not be
merged. `GRAPH_CONNECTIVITY_PLAN.md` covers the existing 45.

### A defect this exposes

`skill_business_mapping.csv` already holds **30 researched skill→business mappings.**
The graph contains **3**. Of the 25 business names it references, **23 do not exist as
BusinessOpportunity entities** — Package006 mapped skills to *generic* business types
("E-commerce Store", "Bakery Business", "Plumbing Service") while Package004 researched
*specific* opportunities. The builder's guard drops the mismatches **silently**, without
even a row in `unresolved_endpoints.csv`.

**Reconciling those 25 names is worth more than 10 new skills**, and it is a mapping
task rather than a research one. `GRAPH_CONNECTIVITY_PLAN.md` §1 owns it.

---

## 5. Plan

### Stage 0 — complete the package · 1 day · **blocks everything**

- [ ] `VERSION` → `1.1.0-RC1`
- [ ] `README.md`, `CHANGELOG.md`, `package_manifest.json` to the Package008 standard
- [ ] **`validate.py`** — schema, provenance, sentinels, **and a category-distribution
      check that would have caught Defect 1**
- [ ] Populate `metadata/` and `registry/`
- [ ] **Fix Defect 1** — recategorise 42 skills across the 24 declared categories
- [ ] Delete the empty `packages/Package006_Skills/` duplicate

### Stage 1 — crosswalk the 11 · 2 hours

- [ ] 7 curated/prefix entries in `curated_overrides.json`, each with a reason
- [ ] 4 `_multi_candidate` entries
- [ ] Rebuild; expect resolution **22.8% → ~42%**

### Stage 2 — collect P0 · 3 days · 20 skills

Fill the five empty commercial and creative categories. Every row needs the full
provenance six, and every skill needs its ≥2 edges. NSQF/NCVET qualification packs
exist for most — `Domestic Data Entry Operator SSC/Q2212` and
`Trainee Beautician BWS/Q0108` are already in `certifications.csv`.

- [ ] Retail (5) · Business & Finance (4) · Soft Skills (3) · Digital (4) · Creative (4)
- [ ] Expect resolution **~42% → ~72%**

### Stage 3 — collect P1 · 2 days · 14 skills

- [ ] Logistics (3) · Services (4) · Agriculture (4) · Healthcare Support (1) ·
      Construction (1) · Electronics (1)
- [ ] Expect resolution **~72% → ~86%**

### Stage 4 — promote · 0.5 day

- [ ] `validate.py` clean · rebuild graph · re-run the six-profile simulation
- [ ] Promote to Stable **v1.1.0**

**Total: 6.5 days · 34 new skills · 20 crosswalk entries · ~180 new edges**

---

## 6. Target vs ceiling

| Metric | Now | Stage 1 | Stage 2 | Stage 3 | Target |
|---|---:|---:|---:|---:|---:|
| **Onboarding resolution** | **22.8%** | ~42% | ~72% | **~86%** | **80%** |
| Skill vocabulary overall | 26.5% | ~40% | ~68% | **~82%** | 80% |
| Idea-skill slots resolvable | 13.5% | 31% | 78% | **~94%** | — |
| Skill entities | 45 | 45 | 65 | **79** | — |
| Categories with ≥1 skill | **3 of 24** | 3 | 14 | **22 of 24** | — |

**80% is reached during Stage 3, and the ceiling is 86%** — 49 of 57 onboarding terms.
The last 8 stay unresolved on purpose: 4 are genuinely ambiguous multi-target terms, and
4 (Animation, Voice Over, Influencer Marketing, Community Driven Sales) have no NSQF
qualification pack or training pathway in either state, so a researched row would carry
`PENDING_VERIFICATION` in every meaningful column.

**Claiming 100% would mean inventing four skills and forcing four ambiguous ones.**

---

## 7. What this backlog will not do

**It will not add a skill without edges.** A vocabulary entry that resolves to a dead
node is worse than an honest `NO_COUNTERPART`, because the platform stops saying "we
haven't researched this" and starts saying nothing at all.

**It will not force the four ambiguous terms.** They keep a `MULTI:` note listing their
candidates, which is a better answer than a confident wrong one.

**It will not collect the 6 backlog sectors.** Beauty & Wellness, Climate Tech, Drone
Tech, Events & Entertainment, Repair Economy and Sports & Fitness belong to
Package004's Industry taxonomy, not to Package006. Tracked in
`KNOWLEDGE_COLLECTION_QUEUE.md` W5.
