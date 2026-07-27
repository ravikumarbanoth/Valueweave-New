# Graph Completion Plan

**Phase 2 · Wave 1** · Commit `0d63a0a` · 2026-07-26

**Implementation plan. No package data or graph code was modified.**

---

## 0. Headline

> **410 relationships are recoverable at 100% verification from datasets already in the
> repository, requiring zero research and zero new collection.**
>
> The packages were built with **cross-package foreign keys already in place** —
> `package001_dist_id`, `package004_opportunity_id`, `package006_skill_id`,
> `package007_scheme_id`, `package002_record_id`. **`build_graph.py` reads almost none
> of them.**
>
> **42 of 77 datasets (1,232 rows) are never opened by the builder.** One of them —
> `Package007/district_scheme_mapping.csv` — holds **305 rows mapping 5 schemes across
> all 61 districts, with both foreign keys joining at 100%.** It is the exact edge shape
> that makes `RS2-VIA_DISTRICT` a dead rule.

**Phase 1 estimated E4 as "expand `jurisdiction`, 0.5 days." It is one builder
registration.**

---

## 1. A correction to Phase 1 that changes the sequencing

Phase 1 projected **142 → ~18 orphans after Wave 1**. Measured against what the recovery
actually touches, the honest figure is **142 → 138**.

The projection conflated two different problems:

| | Fixes | Measured effect |
|---|---|---|
| **Relationship recovery** (WS1) | **Reach** — edges between entities that were already connected | 865 → 1,275 edges · orphans **−4** |
| **Entity resolution** (WS3) | **Orphans** — entities nobody references at all | orphans −52, but needs curation |

The 410 recovered edges are enormously valuable — they revive a dead rule and give every
one of 61 districts its first scheme edge — and they barely move the orphan count,
because a recovered edge joins two things that already had edges.

**Orphans are cleared by entity resolution, not by dataset registration**, and E5
(certifications) is **23 of 30 blocked on skills Package006 v1.1 has not collected yet**.
The `<20` orphan target is therefore a Phase 2 + Package006 v1.1 outcome, not a Wave 1
outcome. Stating otherwise would set a gate that cannot be met.

---

## 2. Baseline

| Metric | Value |
|---|---:|
| Entities | 647 |
| Edges | 865 |
| Connected entities | 505 (78.1%) |
| Orphan entities | **142 (21.9%)** |
| Average node degree | 2.64 |
| **Median node degree** | **1** |
| Edges per entity | 1.34 |
| Distinct edge shapes | 27 |
| Connected components | **150** — 1 giant (489, 75.6%), 7 islands, **142 singletons** |
| Districts reaching a scheme in 1 hop | **0 of 61** |
| Businesses with a skill edge | **2 of 45** |
| Schemes with a district edge | **0 of 40** |
| Skills reaching a business in 1 hop | **3 of 45** |

**Structural health is excellent**: 0 duplicate edges, 0 self-loops, 0 dangling
endpoints, 0 unregistered relationship types. The graph is not corrupt — it is sparse
and under-consumed.

---

## 3. The six workstreams

| WS | Finding | Deliverable |
|---|---|---|
| **1** | **410 edges** recoverable at 100% both-endpoint verification | `RELATIONSHIP_RECOVERY_REPORT.md` |
| **2** | **42 of 77 datasets unconsumed**; 23 carry foreign keys | `RELATIONSHIP_RECOVERY_REPORT.md` §2 |
| **3** | Fuzzy matching produces confident garbage; a distinctive-token rule resolves 5 of 25 honestly | `ENTITY_MATCHING_RULES.md` |
| **4** | Structurally clean; 150 components; **4 registered-but-unused edge types** | `GRAPH_VALIDATION_REPORT.md` |
| **5** | Multi-hop **does not** fix the district problem — median 2-hop reach is 1 node once the State hub is excluded | `TRAVERSAL_STRATEGY.md` |
| **6** | Before/after across 12 metrics | `IMPACT_ESTIMATION.md` |

---

## 4. Implementation plan

### Stage A · Builder registrations — 1.5 days · **no package data changes**

Register six datasets and emit their edges. Every join is verified at 100%.

| # | Dataset | Edges | Shape |
|---|---|---:|---|
| **R1** | `P007/district_scheme_mapping.csv` | **305** | `GovernmentScheme -AVAILABLE_IN-> District` |
| **R2** | `P006/training_centres.csv` | 22 | `TrainingCentre -LOCATED_IN-> District` *(+22 entities)* |
| **R3** | `P008/industry_mapping.csv` | 19 | `MSME -RELATED_TO-> BusinessOpportunity` |
| **R4** | `P005/agri_business_mapping.csv` | 17 | `Crop -PROCESSED_BY-> BusinessOpportunity` |
| **R5** | `P005/agri_business_mapping.csv` | 17 | `BusinessOpportunity -REQUIRES_SKILL-> Skill` |
| **R6** | `P005/agri_business_mapping.csv` | 30 | `Crop -REQUIRES_SKILL-> Skill` |

**R1 alone reverses the single worst structural defect in the graph.**

**Prerequisite, and it is not optional.** `build_graph.py` currently discards
unresolvable mapping rows **silently** — 27 of 30 `skill_business_mapping` rows vanish
with no log entry, while the certification path logs all 122 of its failures. Fix the
logging **before** Stage A, or these six registrations will fail the same way and the
failure log will still look complete.

### Stage B · Entity resolution — 1.5 days · mapping files only

Deterministic rules in `governance/vocabulary/`, following the Step 0 pattern.

| | Task | Auto-resolves | Needs curation |
|---|---|---:|---:|
| **M1** | Package006 business names → Package004 opportunities | **5 of 25** | 10 |
| **M2** | Certification labels → skills | **7 of 30** | 0 now, 23 after Package006 v1.1 |

**Auto-resolution is deliberately low.** §5 explains why a higher number here would be a
failure, not a success.

### Stage C · Validation — 0.5 day

Extend `validate_graph.py` with G12–G15: duplicate edges, self-loops, component census,
orphan census by type. All four pass today; the point is that nothing currently *checks*.

### Stage D · Traversal — 0.5 day · **one typed path, not blanket depth**

Add exactly one 2-hop typed path: `District -> MSME -> GovernmentScheme`. Do **not**
raise the global traversal depth. §6.

**Total: 4 days.**

---

## 5. Why automatic entity matching resolves so little, and why that is right

A naive similarity ladder on the 25 unmatched business names produces:

```
Apparel Manufacturing Unit   ->  Masala Powder Manufacturing Unit   (ratio 0.76)
Aerial Surveying Service     ->  Plumbing Services                  (ratio 0.63)
Solar Energy Installation    ->  POP Works / False Ceiling Install. (ratio 0.62)
```

Every one is wrong, and every one is **confident**. The shared tokens are the generic
head nouns — *Manufacturing*, *Unit*, *Service*, *Installation* — which carry no
discriminating information. The modifier is the meaning, and similarity scoring drowns
it.

**The rule that works strips generic head nouns and matches only on distinctive
tokens.** It resolves 5 of 25 and correctly rejects all three examples above.

The other 20 are not a matching failure. Package006 named generic business **categories**
and Package004 researched specific **opportunities**:

- *"Any MSME Venture"* is not a business opportunity at all
- *"Agro-Processing Unit"* spans several researched opportunities — a 1:many mapping
- *"Bakery Business"* has a genuine counterpart and needs a human to say so

**A matching rule that resolved 20 of 25 would be inventing 15 relationships.** The
platform's own conservative ladder — `EXACT → ALIAS → PREFIX → FUZZY only if exactly one
candidate clears → CURATED → NO_COUNTERPART` — exists for exactly this, and Phase 2
reuses it rather than reinventing a looser one.

---

## 6. Why multi-hop traversal is not the answer

Measured fan-out from a District node:

| Hops | Median reach | Mean |
|---:|---:|---:|
| 1 | **1** | 2.5 |
| 2 | 34 | 38.6 |
| 3 | 76 | 95.6 |

2-hop looks like a fix until the composition is examined. **The `Telangana` node has
degree 34 and `Andhra Pradesh` has 29.** Two hops from any district passes through its
State and reaches every sibling district.

**With State and Country excluded, 2-hop median reach falls from 34 to 1.**

The State hub contributes 30 of the 39 average 2-hop nodes, and all of them are sibling
districts. A blanket depth-2 rule would make every district recommend all 60 others.

**The graph is sparse, not deep.** Multi-hop cannot reach what does not exist — which is
why Stage A comes before Stage D, and why only one typed path is proposed.

**Performance is not the constraint.** A 2-hop expansion measures **4 microseconds**.
Precomputed paths would be premature optimisation against a cost that is already
negligible at 647 nodes.

---

## 7. Rules honoured

**No speculative relationships.** Every one of the 410 recovered edges has both endpoints
resolving to an existing entity by an existing foreign key or exact name, at 100%. The
13 `agri_business_mapping` rows whose opportunity is `PENDING_VERIFICATION` produce **no
edge** — the sentinel is respected rather than guessed past.

**Every edge traceable to package evidence.** Each carries `provenance_package`,
`provenance_dataset` and `provenance_row_id`, exactly as the existing 865 do.

**Explainable and deterministic.** No fuzzy threshold is introduced. Stage B's rules are
exact-match plus a documented token filter plus a curated file with a written reason per
entry — reproducible across runs and reviewable by a person.

**No new collection.** Stage A adds 22 `TrainingCentre` entities, and those come from a
dataset already in the repository. Nothing is researched in Wave 1.

---

## 8. Sequencing

```
P0  Fix silent-drop logging      ▌                    2 h   ← blocks everything
A   Builder registrations        ████                 1.5 d
B   Entity resolution                ████             1.5 d
C   Validation checks                    ██           0.5 d
D   One typed 2-hop path                   ██         0.5 d
                                                     ──────
                                                       4 d
```

**P0 is a prerequisite, not a nicety.** Registering six datasets into a builder that
hides its failures means the next mapping error is as invisible as the last one — and
the failure log will still look complete, which is worse than having none.

---

## 9. Gate

| # | Check | Baseline | Required |
|---|---|---:|---:|
| G1 | Edges | 865 | **≥1,275** |
| G2 | Districts reaching a scheme in 1 hop | **0 of 61** | **61 of 61** |
| G3 | Businesses with a skill edge | 2 of 45 | **≥19 of 45** |
| G4 | Structurally dead rules | **2** | **1** ‡ |
| G5 | Duplicate edges / self-loops / dangling | 0 / 0 / 0 | **0 / 0 / 0** |
| G6 | Unresolved mapping rows **logged** | partial | **100%** |
| G7 | `validate_graph.py` clean incl. G12–G15 | — | pass |
| G8 | Rebuild is idempotent | pass | pass |

‡ `RI3-VIA_DISTRICT` stays dead after Wave 1. No dataset in the repository carries
`Industry → District`, so reviving it needs collection — Phase 1's E3 — and Phase 2 does
not claim it.

**G6 is the one that protects everything else.** A builder that reports some losses and
hides others is worse than one that reports none.

---

**Companion documents:** `RELATIONSHIP_RECOVERY_REPORT.md` · `ENTITY_MATCHING_RULES.md` ·
`GRAPH_VALIDATION_REPORT.md` · `TRAVERSAL_STRATEGY.md` · `IMPACT_ESTIMATION.md`
