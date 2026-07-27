# Entity Matching Rules

**Workstream 3** · Deterministic cross-package resolution

---

## 0. The rule that governs all the others

> **A matcher that resolves more is not a better matcher.**

On the 25 unmatched Package006 business names, a conventional similarity ladder returns:

| Source | Matched to | Score | Correct? |
|---|---|---:|:---:|
| Apparel Manufacturing Unit | Masala Powder Manufacturing Unit (Small Scale) | **0.76** | **No** |
| Aerial Surveying Service | Plumbing Services | 0.63 | **No** |
| Construction Service | Painting Services | 0.65 | **No** |
| Solar Energy Installation | POP Works / False Ceiling Installation | 0.62 | **No** |
| Two-Wheeler Service Center | Rural IT-Enabled Service Center / BPO-KPO | 0.54 | **No** |
| Factory Automation Service | Data Analytics Services | 0.61 | **No** |

Six confident, wrong answers — and *Apparel → Masala Powder* scores **higher** than the
threshold most crosswalks would use.

**The failure is structural, not tunable.** These names are `<modifier> <generic head
noun>`. The head nouns — *Manufacturing, Unit, Service, Installation, Center* — are
shared across the entire domain and carry no discriminating information. String
similarity weights them equally with the modifier, which is the only part that means
anything.

Raising the threshold does not fix it: *Apparel → Masala Powder* at 0.76 survives almost
any threshold that still resolves *Plumbing Service → Plumbing Services* at 0.97.

---

## 1. Rule set M1 — Package006 business names → Package004 opportunities

### The ladder

```
1  EXACT_NAME          identical after case/punctuation normalisation
2  DISTINCTIVE_TOKEN   Jaccard >= 0.34 over distinctive tokens only,
                       AND exactly one candidate clears it
3  MULTI               more than one candidate clears -> stays unresolved,
                       candidates recorded
4  CURATED             human decision, written reason, reviewable
5  NO_COUNTERPART      no counterpart exists -> stays unresolved, reason recorded
```

**Step 2 is the new part.** Before comparing, remove generic head nouns:

```
GENERIC = {unit, service, services, business, centre, center, company, agency,
           shop, store, manufacturing, production, works, platform, network,
           hub, venture, consulting, small, scale, operator, and, or, the, of, for}
```

`"Apparel Manufacturing Unit"` → `{apparel}`
`"Masala Powder Manufacturing Unit (Small Scale)"` → `{masala, powder}`
Intersection **empty** → no match. The false positive is eliminated by construction, not
by a threshold.

### Measured result

| Outcome | Count | Names |
|---|---:|---|
| `EXACT_NAME` | **2** | Cybersecurity Consulting · Digital Marketing Agency |
| `DISTINCTIVE_TOKEN` | **3** | Plumbing Service → Plumbing Services (1.00) · Metal Fabrication Service → Welding & Metal Fabrication (0.67) · Cloud Infrastructure Company → Cloud Services Consulting (0.50) |
| `NO_COUNTERPART` | **20** | see below |
| **Auto-resolved** | **5 of 25** | |

**All six false positives are rejected.** The rule that resolves 5 is the rule that
gets 5 right.

### The 20, triaged

**CURATED — 10, genuinely resolvable by a person**

| Source | Target | Reason to record |
|---|---|---|
| Electrical Installation Service | Electrical Services (Domestic Wiring & Wireman Work) | Same trade; the target names its sub-specialities |
| Bakery Business | Bakery & Confectionery Unit | Same activity, different head noun |
| Furniture Manufacturing | Carpentry & Furniture Workshop | Same activity |
| Automobile Service Center | Two-Wheeler & Auto Repair Workshop | Target is narrower; note the narrowing |
| Two-Wheeler Service Center | Two-Wheeler & Auto Repair Workshop | Same target as above — **many-to-one, and legitimate** |
| Restaurant or Cloud Kitchen | Cloud Kitchen / Tiffin Service | Target covers the cloud-kitchen half only |
| Construction Service | *(select from the construction set)* | Needs a human to pick |
| Hotel/Hospitality Business | *(select)* | |
| Warehousing Logistics Hub | *(select)* | |
| Precision Tool Manufacturing | *(select)* | |

**Each entry needs a written reason.** *"Automobile Service Center → Two-Wheeler & Auto
Repair Workshop"* narrows the scope, and a later reader must be able to see that was a
decision rather than a match.

**MULTI — 4, one-to-many; must stay unresolved**

`Agro-Processing Unit` · `Distribution Network` · `E-commerce Store` ·
`Smart Farm IoT Platform`

Each spans several researched opportunities. Forcing one would assert something the
source did not say. Recorded with a `MULTI:` note listing candidates, exactly as Step 0
handles ambiguous skill terms.

**NO_COUNTERPART — 6, genuinely absent**

`Any MSME Venture` (not a business opportunity at all) · `AI-Based SaaS Product` ·
`Cloud Infrastructure Company` · `Aerial Surveying Service` · `Factory Automation
Service` · `Solar Energy Installation`

The last is worth noting: solar work exists as a **Skill** (Solar Panel Installation &
Maintenance) but not as a BusinessOpportunity. `NO_COUNTERPART` with a note pointing at
the collection gap is the correct answer — this is a Package004 backlog item, not a
matching problem.

### Final disposition

| | Count |
|---|---:|
| Auto-resolved | 5 |
| Curated | 10 |
| Multi | 4 |
| No counterpart | 6 |
| **Resolvable** | **15 of 25 (60%)** |

---

## 2. Rule set M2 — certification labels → skills

### The problem the builder already documented

```python
# build_graph.py:669
"Package006 certifications use descriptive skill labels rather than the
 canonical skill_name vocabulary in its own skills.csv"
```

**122 of the 132 rows in `unresolved_endpoints.csv` are these certifications.** All 30
have `related_skill_names` populated; the labels are *"Vocational Training"*,
*"Employability Skills"*, *"Sector-Specific Training"* — categories, not skills.

### The ladder

```
1  EXACT_NAME          label matches a canonical skill name
2  NSQF_QP_CODE        extract [A-Z]{3}/Q\d{4} -> resolve via the QP registry
3  DISTINCTIVE_TOKEN   as M1, with a certification-specific stopword list
4  CURATED
5  NO_COUNTERPART
```

Step 2 is deterministic and authoritative: an NSQF qualification pack code is a
government identifier with exactly one occupational meaning.

```
CERT_GENERIC = {certified, certification, certificate, course, training, program,
                programme, level, india, national, professional, fundamentals,
                associate, user, operator, technician, prior, learning, short, term}
```

### Measured result

| Outcome | Count |
|---|---:|
| `DISTINCTIVE_TOKEN` | **1** — AWS Certified Cloud Practitioner → AWS/Azure Cloud Administration |
| `NSQF_QP_CODE` | **6** |
| `NO_COUNTERPART` **today** | **23** |

**The six NSQF codes**

| Certification | QP code | Resolves to |
|---|---|---|
| CNC Operator - Turning | `CSC/Q0115` | CNC Machine Operator ✓ *(exists)* |
| Automotive Service Technician | `ASC/Q1411` | Automobile Mechanic ✓ *(exists)* |
| Field Technician - Computing | `ELE/Q4601` | Electronics Repair ✓ *(exists)* |
| Domestic Data Entry Operator | `SSC/Q2212` | Data Entry — **Package006 v1.1** |
| General Duty Assistant | `HSS/Q5101` | Healthcare Support — **v1.1** |
| Trainee Beautician | `BWS/Q0108` | Beautician Services — **v1.1** |

### The 23 are blocked, not unmatchable

| Certification | Would resolve to | Status |
|---|---|---|
| Tally Certification | Accounting | **v1.1** |
| Google Digital Garage — Digital Marketing | Digital Marketing | **v1.1** |
| Microsoft Office Specialist | Data Entry / Office Productivity | **v1.1** |
| NIELIT 'O' / 'A' Level, CCC | Computer Literacy | **v1.1** |
| Skill India / PMKVY / RPL Certificate | *(cross-sector wrappers)* | `NO_COUNTERPART` — correct |

**The mismatch is not a vocabulary problem. It is the same finding as Package006's
category defect**: the certifications were collected across the full 24-category
taxonomy, and `skills.csv` only covers the technical corner. The certifications are
pointing at skills that were never researched.

### Disposition

| | Now | After Package006 v1.1 |
|---|---:|---:|
| Auto-resolved | **7 of 30** | **~24 of 30** |
| Blocked on v1.1 skills | 17 | 0 |
| Genuinely `NO_COUNTERPART` | 6 | 6 |

**E5 is 23 of 30 blocked on Package006 v1.1.** The `<20` orphan target cannot be met
in Wave 1, and `GRAPH_COMPLETION_PLAN.md` §1 states so rather than carrying the Phase 1
projection forward.

---

## 3. Where the rules live

```
governance/vocabulary/
  business_crosswalk.csv          M1 output, same 10-column shape as Step 0
  certification_crosswalk.csv     M2 output
  curated_overrides.json          + business/certification sections
  crosswalk_summary.json          + M1/M2 resolve rates
```

Same header, same match-method vocabulary, same `_multi_candidate` mechanism, same
requirement that every curated entry carries a reason. **A fourth crosswalk in an
established pattern, not a new subsystem.**

### Determinism

| Property | How |
|---|---|
| Stable across runs | No RNG; sorted iteration; ties → `MULTI`, never arbitrary choice |
| Stable across machines | Pure stdlib string ops; no locale-dependent collation |
| Reviewable | Every non-exact row records method, score and reason |
| Testable | `tests/test_vocabulary.py` extends to M1/M2 unchanged in shape |
| Reversible | Delete a crosswalk row → the edge disappears on the next rebuild |

---

## 4. Combined effect

| | M1 | M2 |
|---|---:|---:|
| Source terms | 25 | 30 |
| Auto-resolved | **5** | **7** |
| Curated | 10 | 0 |
| Resolvable now | **15** | **7** |
| Blocked on Package006 v1.1 | 0 | **17** |
| Genuinely absent | 6 (+4 multi) | 6 |

**Edges unlocked:** M1 ≈ 25 `BusinessOpportunity -REQUIRES_SKILL-> Skill` (the
`skill_business_mapping` rows whose business name now resolves); M2 ≈ 7 now, ~24 after
v1.1.

**Orphans cleared:** M2 clears **7 of 30** orphan certifications now, ~24 after v1.1.
M1 clears none — the business names are not entities, they are labels pointing at
entities that were never isolated.

---

## 5. What these rules will not do

**They will not force the 4 MULTI terms.** *"Agro-Processing Unit"* legitimately spans
several opportunities. A `MULTI:` note listing candidates is a better answer than a
confident wrong one, and Step 0 established the mechanism.

**They will not lower the distinctive-token threshold to lift the resolve rate.** The
threshold is not what rejects *Apparel → Masala Powder*; removing the generic head nouns
is. Lowering it would readmit the false positives without recovering any true one.

**They will not parse `related_businesses_summary`.** It is prose in four Package004
datasets and reads like a relationship. Extracting edges from it is inference, and the
mission forbids speculative relationships. The fix is a structured column in Package004.

**They will not resolve the 17 certifications blocked on v1.1.** Mapping *Tally
Certification* onto the nearest existing skill would put an accounting credential under a
manufacturing trade. `NO_COUNTERPART` with a note naming the missing skill is the honest
answer, and it doubles as the collection brief.
