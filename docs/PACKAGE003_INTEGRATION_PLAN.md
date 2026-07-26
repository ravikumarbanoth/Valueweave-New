# Package003 Healthcare — Integration Plan

**Workstream 3** · 146 rows · Stable v1.0.0 · **0 entities · 0 edges**

---

## 0. Why it is disconnected

Not neglect, and not a broken pipeline. `knowledge_graph/build_graph.py` maps 19 entity
types to source packages and **none of them names Package003**:

```python
"Institution":       "Package002_Education",
"Skill":             "Package006_Skills_and_Training",
"GovernmentScheme":  "Package007_Government_Schemes",
"Crop":              "Package005_Agriculture",
...   # no Package003 anywhere
```

**The reason it was skipped is the interesting part.** Three of its four datasets
describe things another package already owns:

| Dataset | Rows | Natural type | Already owned by |
|---|---:|---|---|
| `government_hospitals_telangana_andhra_pradesh` | 55 | **no type exists** | — |
| `medical_colleges_telangana_andhra_pradesh` | 58 | `Institution` | **Package002** |
| `government_health_insurance_schemes` | 9 | `GovernmentScheme` | **Package007** |
| `medical_regulatory_bodies_and_health_missions` | 24 | ambiguous | — |

Registering Package003 naively would have created a second `Institution` producer and a
second `GovernmentScheme` producer — the exact collision ADR-003 was written to prevent.
**Skipping it was the correct conservative choice.** Leaving it skipped without a
decision record is the defect.

### One of the two hard questions is already answered

`knowledge_graph/ownership/known_overlaps.csv` **already governs the scheme overlap**:

> `GovernmentScheme` · canonical owner `Package007_Government_Schemes` · also held by
> `Package002_Education; Package003_Healthcare; Package004_Industries;
> Package005_Agriculture; Package006_Skills_and_Training` · **status RESOLVED · ADR-003**

Package003's 9 health-insurance schemes are among the 79 domain rows that already carry
`package007_scheme_id` and `scheme_ownership`. Confirmed by inspection: *Ayushman Bharat
PM-JAY* exists in both packages, and Package007 holds the canonical row.

**So the scheme question needs no new governance — only the builder honouring the
crosswalk that exists.**

---

## 1. Entity model

### One new type, one reused, one deferred, one narrow

| Dataset | Decision | Entity type | Count |
|---|---|---|---:|
| Government hospitals | **New type** | `Hospital` | **55** |
| Medical colleges | **Reuse `Institution`** under Package002's ownership | `Institution` | +58 |
| Health insurance schemes | **Defer to ADR-003** | *(none new)* | 0 |
| Regulatory bodies | **New type**, narrowly scoped | `RegulatoryBody` | **24** |

**≈137 new entities**, of which 58 extend an existing type.

### Why `Hospital` is a new type and not an `Institution`

A hospital and a university answer different questions and carry different attributes:

| | `Institution` | `Hospital` |
|---|---|---|
| Question it answers | Where can I study? | Where is care delivered? |
| Key attributes | `naac_grade`, `affiliation`, seats | `bed_capacity`, `specialties`, `teaching_status` |
| Relationship role | Trains people | Employs people; anchors demand |

Forcing 55 hospitals into `Institution` would put `bed_capacity` alongside `naac_grade`
and produce a type meaning "any organisation" — which means nothing. The platform already
has 19 types precisely because that distinction is worth keeping.

### Why medical colleges *are* `Institution`

Osmania Medical College is a college. It has an affiliating university, an establishment
year, and `mbbs_seats` — structurally identical to Package002's 66 universities, three of
which are **already health universities** (Dr. NTR UHS, Kaloji Narayana Rao UHS, SVIMS).
A parallel `MedicalCollege` type would immediately drift from `Institution`, and the
overlap is real rather than accidental.

**Governance: Package002 stays the canonical owner of `Institution`.** Package003's 58
rows carry `also_in_package: Package002_Education` and an `institution_ownership` column,
following the ADR-003 pattern exactly. Add a `known_overlaps.csv` row:

```
Institution,Package002_Education,Package003_Healthcare,
"58 medical colleges in Package003 are Institutions; 3 health universities already
 exist in Package002",PARTIALLY_RESOLVED,ADR-006,...
```

### Why `RegulatoryBody` is narrow and deliberately so

24 rows: National Medical Commission, state health missions, nursing councils. They are
neither institutions nor hospitals. **They are also almost certainly orphans-in-waiting**
— a regulatory body relates to a *profession*, which the graph does not model.

**Recommendation: create the type, and accept ~8 of 24 will have no edge.** Better than
forcing them into `Institution` where they would pollute a well-defined type. Recorded
against the <20 orphan target in `GRAPH_CONNECTIVITY_PLAN.md`, which has ~2 orphans of
headroom — so **this workstream must not exceed it**, and §3 sizes the edges accordingly.

---

## 2. Relationships

≈240 new edges, all derivable from columns that already exist.

| # | Shape | Edges | Source column | Derivable? |
|---|---|---:|---|---|
| H1 | `Hospital -LOCATED_IN-> District` | **55** | `district` | **Yes** |
| H2 | `Institution -LOCATED_IN-> District` | **58** | `district` | **Yes** |
| H3 | `Institution -AFFILIATED_WITH-> Institution` | ~50 | `affiliation` | **Yes** |
| H4 | `Institution -ATTACHED_TO-> Hospital` | ~40 | `attached_teaching_hospital` | **Yes** |
| H5 | `Hospital -REQUIRES_SKILL-> Skill` | ~15 | `specialties_summary` → Healthcare Support | Partly |
| H6 | `Hospital -SUPPORTED_BY_SCHEME-> GovernmentScheme` | ~20 | `empanelled_hospitals_summary` | Partly |
| H7 | `RegulatoryBody -REGULATES-> Institution/Hospital` | ~16 | `mandate_summary` | Partly |
| H8 | `Industry(Healthcare) -LOCATED_IN-> District` | ~25 | derived from H1 | **Collect, don't infer** |

**H1 and H2 are the valuable ones.** 113 edges into districts, from a `district` column
that is already populated and already provenance-carried.

### What this does for district coverage

Today `District` has three edge shapes and 34 of 61 districts have degree 1.

| District | Degree now | After H1+H2 |
|---|---:|---:|
| Hyderabad | 18 | ~30 |
| Guntur | 9 | ~14 |
| Visakhapatnam | ~5 | ~10 |
| Krishna | 5 | ~9 |
| *typical degree-1 district* | **1** | **~3** |

**Healthcare becomes the fourth industry with real district coverage**, after education,
MSME and agriculture. That feeds `DO2-DENSITY` and `DO3-DIVERSITY` directly, which is
why this workstream shows up in `PILOT_DISTRICT_SELECTION.md` as a tier-2 unlock.

### H5 and H8 need care

**H5** would connect hospitals to `Nursing Assistant / MPHW` — the one healthcare skill
Package006 has. Real, but thin: one skill for 55 hospitals. Package006 v1.1 adds
Healthcare Support skills (Lab Operations, GDA), so **do H5 after Package006 Stage 3.**

**H8 must be collected, not inferred.** "Healthcare is present in district X because a
hospital is there" is a defensible inference and it is still an inference. Presented as a
researched edge it would carry provenance it has not earned. Either collect a district
health-infrastructure profile with a source, or leave H8 out. **Leaving it out is the
recommendation** — H1 already gives the district its healthcare signal.

---

## 3. Queries this unlocks

| Question | Today | After |
|---|---|---|
| What healthcare infrastructure is in my district? | **Nothing** | 55 hospitals, 58 colleges by district |
| Where can I study medicine near me? | Nothing | `Institution` + `mbbs_seats` by district |
| Which hospitals accept Ayushman Bharat? | Nothing | H6, 20 edges |
| Is healthcare a viable sector in my district? | Nothing | H1 density |
| What skills do hospitals need? | Nothing | H5 *(after Package006 v1.1)* |

### Recommendations it improves

| Category | Rule | Effect |
|---|---|---|
| `industries` | `RI3-VIA_DISTRICT` | Healthcare becomes recommendable — **once E3 exists** |
| `government_schemes` | `RS2-VIA_DISTRICT` | 9 health schemes reachable — **once E4 exists** |
| `courses` | `RC1-FOR_GAP_SKILL` | Medical colleges as a real training destination |
| `msmes` | `RN2-DISTRICT` | Hospital-adjacent enterprise in district context |
| `business_ideas` | `RB2-DISTRICT_FIT` | Diagnostics, pharmacy, medical supply become locatable |

> **Sequencing consequence.** Two of the five depend on `E3` and `E4` from
> `GRAPH_CONNECTIVITY_PLAN.md`. **Healthcare integration is worth less on its own than it
> is after Wave 1** — which is why it is W4 in the collection queue and not W1. Doing it
> first would add 137 entities and 240 edges and move no recommendation a user sees.

---

## 4. Plan — 4 days

### Stage 1 — governance · 0.5 day

- [ ] ADR-006: `Institution` shared ownership, Package002 canonical
- [ ] `known_overlaps.csv` row for `Institution`
- [ ] Confirm all 9 health schemes carry `package007_scheme_id` and
      `scheme_ownership` per ADR-003 — **verify, do not assume**
- [ ] Register `Hospital` and `RegulatoryBody` in `entity_types.csv`
- [ ] Register `AFFILIATED_WITH`, `ATTACHED_TO`, `REGULATES` in `relationship_types.csv`

### Stage 2 — package changes · 1 day

- [ ] `also_in_package` + `institution_ownership` on the 58 medical colleges
- [ ] `dist_ref` foreign keys on hospitals and colleges — **the `district` column is
      free text today** and must resolve to Package001's 61 districts, with
      `NO_COUNTERPART` where it does not
- [ ] Bump Package003 to `1.1.0`; update `CHANGELOG.md`
- [ ] Re-run Package003's validator

### Stage 3 — builder · 1.5 days

- [ ] `Hospital` → Package003, `RegulatoryBody` → Package003
- [ ] `Institution` reads Package002 **and** Package003, deduplicating on the
      3 health universities that already exist
- [ ] Derive H1–H4 (~203 edges)
- [ ] Derive H6, H7 (~36 edges)
- [ ] **Log every unresolved endpoint** — do not repeat the silent drop that lost 27 of
      30 rows in `skill_business_mapping`

### Stage 4 — verify · 1 day

- [ ] `validate_graph.py` clean, including G11 ownership
- [ ] Expect **647 → ~784 entities**, **865 → ~1,105 edges**
- [ ] Orphan count rises by **≤8** (the regulatory bodies) — check against the <20 target
- [ ] Re-run the six-profile simulation
- [ ] `knowledge_sync plan` → expect **1,812 → ~2,090 rows**; add `kg_hospitals` to
      `TableSpec` and regenerate the migration with `--check`

---

## 5. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| `Institution` dedup misses the 3 existing health universities → duplicates | **High** | Match on name **and** district before insert; `validate_graph.py` G11 |
| Free-text `district` fails to resolve | **High** | Reuse the Step 0 ladder; `NO_COUNTERPART` rather than a guess |
| 24 regulatory bodies become 24 orphans | Medium | Cap at ~8 via H7; the <20 target has ~2 of headroom, so **this is the binding constraint** |
| Scheme double-count if ADR-003 is not honoured | Medium | Stage 1 verifies rather than assumes |
| `Hospital` type judged unnecessary later | Low | Reversible: 55 entities, one builder block |

---

## 6. Recommendation

**Do it, in Wave 4, after Wave 1.**

146 researched rows — 6.4% of everything the programme has collected — are invisible, and
137 entities plus ~203 high-quality district edges is good value for 4 days. **Two of its
five recommendation benefits depend on `E3` and `E4` landing first**, so doing it earlier
buys entities and no user-visible improvement.

**Do not do H8.** Inferring "healthcare is present here" from a hospital's address is
reasonable and it is still an inference. H1 already gives the district its healthcare
signal with real provenance, and an inferred edge wearing a researched edge's provenance
is the one failure mode this platform is built to avoid.
