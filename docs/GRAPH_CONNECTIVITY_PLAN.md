# Graph Connectivity Plan

**Workstream 2 & 4** · Target: orphan entities **142 → <20**, structurally dead rules
**2 → 0**

---

## 0. Headline

**~1,255 new relationships. Zero new entities. Five days.**

Of those, **~470 need no research at all** — they are already researched, already in a
package CSV, and the graph builder is dropping them. Two of the six missing edge shapes
are reconciliation tasks, not collection tasks.

| Finding | Evidence |
|---|---|
| The builder logs 132 failures and **122 are Package006 certifications** | `knowledge_graph/relationships/unresolved_endpoints.csv` |
| `skill_business_mapping.csv` holds 30 mappings; the graph has **3** | 23 of 25 business names match no entity |
| Those 27 losses are **not logged anywhere** | Only 132 rows in the failure log, none from this dataset |

---

## 1. The two dead rules

Two of 21 recommendation rules cannot fire for any user, in any district, ever.

| Rule | Traversal | Edges |
|---|---|---:|
| `RS2-VIA_DISTRICT` | `neighbours(district, "SUPPORTED_BY_SCHEME", "in")` | **0** |
| `RI3-VIA_DISTRICT` | `neighbours(district, "LOCATED_IN", "in", "Industry")` | **0** |

Both are **district** rules, and district is the one input that resolves at 100%.
`KnowledgeSnapshot.neighbours()` reads a single edge list, so every rule is strictly
1-hop. Measured shortest path from a District to a BusinessOpportunity: **3 hops for 22
districts, 5 for the other 39.** The connection exists and no rule can see it.

**This is why a user whose skills don't resolve gets nothing.** The skill path fails on
vocabulary, and the district fallback is structurally dead.

---

## 2. The 142 orphans

| Type | Orphans | of total | Root cause | Fix |
|---|---:|---:|---|---|
| **Certification** | **30** | 30 (100%) | `related_skill_names` uses free-text labels absent from `skills.csv` | **E5** — reconcile |
| **TrainingProvider** | **22** | 25 (88%) | No `TRAINS` shape; 3 `TRAINED_BY` in total | **E6** |
| **GovernmentScheme** | **21** | 40 (53%) | **Not entrepreneurship schemes** — §4 | **Classify**, then E4 |
| Industry | 17 | 78 (22%) | 6 are `AI Tooling:` pseudo-industries | E3 + taxonomy |
| FinancialInstitution | 13 | 21 (62%) | Named in prose, never mapped | E7 |
| Market | 10 | 11 (91%) | Only reachable via MSME `SELLS_TO` | E8 |
| Institution | 8 | 66 (12%) | `district` cell empty or unmatched | Repair E9 |
| Machinery | 8 | 69 (12%) | Agri machinery with no crop link | E10 |
| ExportCountry | 7 | 29 (24%) | Parsed from free text | Accept |
| Skill | 5 | 45 (11%) | Emerging-tech skills with no business | E1 |
| Soil | 1 | 10 (10%) | Saline soil, no crop | Accept |

**After E1–E6: 142 → ~18.** The residue is 7 ExportCountries, 1 soil type and ~10
`AI Tooling:` pseudo-industries that should be resolved as a taxonomy decision rather
than by adding edges.

---

## 3. The six missing edge shapes

### E1 · `BusinessOpportunity -REQUIRES_SKILL-> Skill` — ~135 edges · **highest impact**

**Only 2 of 45 businesses have a skill edge**: Cybersecurity Consulting and Digital
Marketing Agency.

**Not a research task.** `skill_business_mapping.csv` already holds 30 researched,
sourced mappings. The builder consumes it at `build_graph.py:501`:

```python
if sk and opp and E("BusinessOpportunity", opp):
    edge("REQUIRES_SKILL", ...)
```

`E("BusinessOpportunity", opp)` fails for 23 of 25 names and the row is discarded
**silently** — no exception, no row in `unresolved_endpoints.csv`.

The cause is a **granularity mismatch between two packages**: Package006 mapped skills
to generic business types, Package004 researched specific opportunities.

| Package006 says | Package004 has |
|---|---|
| E-commerce Store | *(generic — spans several)* |
| Bakery Business | Bakery & Confectionery Unit |
| Plumbing Service | Plumbing & Sanitary Services |
| Metal Fabrication Service | Fabrication & Welding Workshop |
| Agro-Processing Unit | *(several specific units)* |

**Work:** map 25 generic names to the 45 specific opportunities — many-to-many, in
`governance/vocabulary/` alongside the Step 0 crosswalks, using the same conservative
ladder (`EXACT → PREFIX → CURATED → NO_COUNTERPART`). Then extend the mapping to cover
all 45.

**Also fix the silent drop.** A mapping row that resolves to nothing must be logged,
exactly as the certification path already does. That is a builder change, out of scope
here, and recorded in `KNOWLEDGE_COLLECTION_QUEUE.md` as a prerequisite.

**Unblocks:** `RB1-SKILL_MATCH`, `BR1-SKILL_COVERAGE`, `RI1-VIA_SKILL`, `SK4-DEMAND`
— and makes `business_ideas` answerable from the graph rather than only from the static
editorial file.

**Effort: 1.5 days.**

---

### E2 · `BusinessOpportunity -SUITABLE_FOR-> District` — ~450 edges

**Zero district→business edges of any kind.** This is why 45 of 61 districts score under
30.

**Partly derivable.** The 122 editorial ideas carry `district_fit`, and Package004's
opportunities carry district suitability in prose. Neither is a foreign key today.

| Source | Coverage |
|---|---|
| `idea-library/ideas.json` → `district_fit` | 122 ideas, 19 district names |
| Package004 opportunity prose | 45 opportunities, unstructured |
| Package008 `district_business_mapping.csv` | MSME→district only (the existing 32) |

**Work:** add `district_suitability` to Package004's opportunity dataset as a
semicolon-separated list of `dist_ref` values. ~10 districts per opportunity × 45 = ~450
edges. Where suitability genuinely cannot be established, the cell takes
`PENDING_VERIFICATION` rather than a guess.

**Do not derive this from `district_fit` alone** — the editorial list names 19 districts
including two city names ("Vijayawada", "Anantapur") and would silently exclude 42
districts, reproducing the coverage gap it is meant to fix.

**Unblocks:** `RB2-DISTRICT_FIT`, `DO2-DENSITY`, `DO3-DIVERSITY`.
**Effort: 1.5 days.**

---

### E3 · `Industry -LOCATED_IN-> District` — ~200 edges · **revives RI3**

Zero edges. `RI3-VIA_DISTRICT` looks for exactly this shape.

**Derivable from data already in the graph.** 32 `MSME -GENERATES_EMPLOYMENT-> District`
edges plus 45 `BusinessOpportunity -PART_OF-> Industry`, so an industry's district
presence can be inferred from its MSMEs. **Inference is not evidence**, so this must be
a declared dataset with a source — a district industrial profile from the state
industries department — not a derived edge presented as researched.

**Work:** `industry_district_presence.csv` in Package004; ~200 rows for the 24 real
industries across 61 districts, sourced from TS-iPASS and AP industrial profiles.

**Effort: 1 day** (0.5 if scoped to the 12 pilot districts first).

---

### E4 · `GovernmentScheme -AVAILABLE_IN-> District` — ~350 edges · **revives RS2**

**0 of 40 schemes have a district link.** See §4 — this serves both scheme classes and
is the single most valuable scheme edge.

**Largely mechanical.** Package007's `government_schemes.csv` carries `jurisdiction`:

| Jurisdiction | Districts | Schemes |
|---|---:|---:|
| National | all 61 | ~24 |
| Telangana | 33 | ~9 |
| Andhra Pradesh | 28 | ~7 |

A national scheme is available in all 61 districts — that is a fact, not an inference.
Expanding jurisdiction gives ~1,800 edges, which is correct but noisy.

**Recommended: store the rule, not the expansion.** Add `available_in_districts` to
Package007 holding `ALL | TELANGANA | ANDHRA_PRADESH | <explicit list>`, and let the
builder expand it. ~350 edges materialise for the 12 pilot districts; the rest expand
when needed. Schemes with genuine district restrictions get an explicit list.

**Unblocks:** `RS2-VIA_DISTRICT` (dead → live), `FR1-SCHEME_REACH`.
**Effort: 0.5 day.**

---

### E5 · `Certification -CERTIFIES-> Skill` — ~30 edges · **zero research**

**All 30 certifications are orphans, and the builder already knows why.** From
`build_graph.py:669`:

> *"Package006 certifications use descriptive skill labels rather than the canonical
> skill_name vocabulary in its own skills.csv"*

**122 of the 132 rows in `unresolved_endpoints.csv` are these certifications.** Every
one of the 30 has `related_skill_names` populated — 122 skill references — and none
resolves, because the labels are things like *"Vocational Training"*, *"Employability
Skills"*, *"Sector-Specific Training"*.

**Work:** a `certification_skill_map.csv` reconciling 122 labels to canonical skill
names. Many are mechanical via the NSQF qualification-pack code already in the name:

| Certification | Resolves to |
|---|---|
| `CNC Operator - Turning - CSC/Q0115` | CNC Machine Operator |
| `Domestic Data Entry Operator - SSC/Q2212` | Data Entry *(Package006 v1.1)* |
| `Trainee Beautician - BWS/Q0108` | Beautician Services *(v1.1)* |
| `Tally Certification` | Accounting *(v1.1)* |
| `Automotive Service Technician - ASC/Q1411` | Automobile Mechanic |

**Note the dependency:** several resolve only to skills that Package006 v1.1 adds. Do E5
**after** Package006 Stage 2, or accept ~18 of 30 now and the rest after.

**Also fixes Defect 1's blast radius.** `RC2` currently falls back to "a certification in
the same category as your gap skill", and 42 of 45 skills share one category. Real
`CERTIFIES` edges replace a fallback that is actively misleading.

**Effort: 0.5 day.**

---

### E6 · `TrainingProvider -TRAINS-> Skill` and `-LOCATED_IN-> District` — ~90 edges

3 `TRAINED_BY` edges across 25 providers. `LR3-PROVIDER` already reports this in its own
`no_signal` text — the rule is honest about being starved.

**Already collected.** `training_centres.csv` has **22 rows with `district_id`,
`district_name` and `skills_or_trades_offered`** — E6's district half, sitting unread by
the builder. `training_providers.csv` has `skills_offered_summary` and
`certification_pathways`.

| Half | Source | Edges |
|---|---|---:|
| `-LOCATED_IN-> District` | `training_centres.csv` `district_id` | ~22 |
| `-TRAINS-> Skill` | `skills_or_trades_offered` + `skills_offered_summary` | ~68 |

**Work:** register `training_centres.csv` in the builder; reconcile the trade labels the
same way as E5.

**Unblocks:** `LR3-PROVIDER`, `RC2-PROVIDER_IN_DISTRICT` (properly, rather than by
category fallback).
**Effort: 0.5 day.**

---

### E7–E10 · the remainder — ~120 edges · 1 day

| | Shape | Orphans cleared | Note |
|---|---|---:|---|
| E7 | `FinancialInstitution -OPERATES_IN-> District` | 13 | SBI, PNB, SIDBI etc. named in prose only |
| E8 | `BusinessOpportunity -SELLS_TO-> Market` | 10 | GeM, ONDC, Amazon apply to most opportunities, not only MSMEs |
| E9 | Repair `Institution -LOCATED_IN-> District` | 8 | 58 of 66 resolve; 8 have an empty or unmatched `district` cell |
| E10 | `Machinery -USED_BY-> Crop` | 8 | Tractor, rotavator, seed drill — clear agronomic links |

---

## 4. Workstream 4 — government schemes

### The four dimensions, measured

| Dimension | Schemes with ≥1 link | of 40 |
|---|---:|---:|
| MSME | 13 | 32.5% |
| BusinessOpportunity | 7 | 17.5% |
| FinancialInstitution | 7 | 17.5% |
| Skill | 5 | 12.5% |
| **Industry** | **0** | **0%** |
| **District** | **0** | **0%** |

Every edge shape touching a scheme:

```
57  MSME                -SUPPORTED_BY_SCHEME-> GovernmentScheme
12  Crop                -SUPPORTED_BY_SCHEME-> GovernmentScheme
12  BusinessOpportunity -SUPPORTED_BY_SCHEME-> GovernmentScheme
12  GovernmentScheme    -FUNDED_BY----------> FinancialInstitution
11  Skill               -SUPPORTED_BY_SCHEME-> GovernmentScheme
```

### The 21 orphans are miscategorised, not unlinked

> Atal Pension Yojana · Ayushman Bharat PM-JAY · Ayushman Bharat HWC · MGNREGS ·
> National Food Security Act (PDS) · National Social Assistance Programme ·
> PM Awas Yojana Gramin · PM Awas Yojana Urban · PM Jan Dhan Yojana ·
> PM Jeevan Jyoti Bima · PM Suraksha Bima · PM-KISAN · PM Matru Vandana ·
> PM Poshan Shakti Nirman · Samagra Shiksha · Soil Health Card ·
> Central Sector Scholarship · National Means-cum-Merit Scholarship ·
> Post-Matric Scholarship (SC) · PM Young Achievers Scholarship ·
> Deendayal Antyodaya NRLM

**Pension, health insurance, food security, housing, maternity benefit, school meals,
scholarships.** They have no `REQUIRES_SKILL` or business relationship because they are
not business schemes.

**Linking MGNREGS to an MSME would invent a relationship that does not exist in the
world.** The platform's governance forbids exactly that. These 21 are not badly
connected — they are the wrong shape for the questions being asked of them.

### Recommendation

**Step 1 — add `scheme_class` to Package007** (a column, not new rows):

| Class | Est. | Edges it should carry |
|---|---:|---|
| `ENTERPRISE` | ~19 | Industry, Skill, MSME, BusinessOpportunity, District |
| `WELFARE` | ~17 | **District only** — plus a demographic eligibility model |
| `EDUCATION` | ~4 | Institution, District |

**Step 2 — E4 for all 40.** For a `WELFARE` scheme the district link is the *only*
meaningful one, which is why E4 serves both classes and comes first.

**Step 3 — connect the 19 `ENTERPRISE` schemes properly:**

| Missing | Est. edges | Source |
|---|---:|---|
| Industry | ~40 | Package007 `sector_focus` |
| Skill | ~35 | `skill_scheme_mapping.csv`, currently 11 edges |
| MSME | ~25 | Extend `scheme_mapping.csv` beyond 13 schemes |
| Business model | ~30 | Enterprise-type eligibility |

**Step 4 — a second surface, v1.2.** Jan Dhan, Ayushman Bharat and a post-matric
scholarship genuinely matter to a student. They belong in *"benefits you may be eligible
for"*, keyed on district and demographics, not mixed into business recommendations.
The classification that enables it is v1.1 data work; the surface is v1.2 product work
and is **not** in this plan.

---

## 5. Effort and impact

| # | Shape | Edges | Days | Research needed |
|---|---|---:|---:|---|
| **E4** | Scheme → District | ~350 | 0.5 | **No** — `jurisdiction` exists |
| **E5** | Certification → Skill | ~30 | 0.5 | **No** — reconciliation |
| **E6** | Provider → Skill/District | ~90 | 0.5 | **No** — `training_centres.csv` |
| **E1** | Business → Skill | ~135 | 1.5 | Partly — 30 rows exist |
| **E2** | Business → District | ~450 | 1.5 | **Yes** |
| **E3** | Industry → District | ~200 | 1.0 | **Yes** |
| E7–E10 | remainder | ~120 | 1.0 | Partly |
| | **Total** | **~1,375** | **6.5** | |

**Wave-1 scope is E1–E6: ~1,255 edges in 5 days.** E7–E10 are cleanup and can follow.

### Do the free ones first

**E4, E5 and E6 need no new research** and together take **1.5 days** for ~470 edges.
They alone:

- bring `RS2-VIA_DISTRICT` from dead to live
- clear **52 orphans** (30 certifications + 22 providers)
- give `courses` its first real evidence base
- replace `RC2`'s misleading category fallback with real edges

**That is the best day-and-a-half available anywhere in the programme**, and it consumes
data that has been sitting in `packages/` since Package006 was assembled.

### Projected

| Metric | Now | After E4–E6 | After E1–E6 |
|---|---:|---:|---:|
| Edges | 865 | ~1,335 | **~2,120** |
| Edges per entity | **1.34** | 2.06 | **3.28** |
| Orphan entities | **142** | ~69 | **~18** |
| Dead rules | **2** | **1** | **0** |
| Businesses with a skill edge | 2 of 45 | 2 | **45 of 45** |
| Schemes with a district link | 0 of 40 | **40 of 40** | 40 |
| Districts scoring ≥50 | 4 | ~6 | **~14** |

---

## 6. Constraints

**No new entity type.** Every edge connects entities that already exist, are already
sourced, and are already validated.

**No inferred edge presented as researched.** E3 is derivable from MSME district
presence, and it is written as a **collection task with a source** for exactly that
reason. An inferred edge that looks researched is worse than a missing one — it carries
provenance it has not earned.

**`PENDING_VERIFICATION` where suitability is genuinely unknown.** E2 will have such
cells; a district guess for a business opportunity is precisely the kind of claim the
sentinel exists for.

**Two builder defects must be fixed before Wave 1 is trustworthy** — both recorded in
`KNOWLEDGE_COLLECTION_QUEUE.md` as prerequisites, neither in scope here:

1. `skill_business_mapping` losses are dropped **silently**. 27 of 30 rows vanished with
   no log entry. The certification path logs all 122 of its failures; this one logs
   none. **The inconsistency is the bug** — a builder that reports some losses and hides
   others is worse than one that reports none, because the failure log looks complete.
2. `training_centres.csv` is not registered in the builder at all, so 22 rows of
   district-linked training data have never been read.
