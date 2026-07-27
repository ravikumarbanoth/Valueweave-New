# Traversal Strategy

**Workstream 5** · All 44 rules reviewed · one-hop vs multi-hop vs precomputed

---

## 0. Recommendation

> **Keep every rule at one hop. Add exactly one typed two-hop path. Do not precompute
> anything.**

Multi-hop traversal looks like the fix for the district problem and is not. Measured:

| From a District | Median reach | Mean |
|---|---:|---:|
| 1 hop | **1** | 2.5 |
| 2 hops | 34 | 38.6 |
| **2 hops, State/Country excluded** | **1** | **8.2** |

**The State node supplies 30 of the 39 average two-hop nodes, and every one of them is a
sibling district.** `Telangana` has degree 34, `Andhra Pradesh` has 29. A blanket
depth-2 rule would make every district recommend all 60 others, with a confident reason
string.

Strip that artefact and two-hop reach collapses to a median of **1 node**.

**The graph is sparse, not deep.** Traversal cannot reach what does not exist. This is
the strongest available confirmation that Phase 1 sequenced correctly: fix the edges,
then revisit depth.

---

## 1. Measured fan-out

| Seed | Hops | Median | Mean | p95 | Max |
|---|---:|---:|---:|---:|---:|
| District | 1 | 1 | 2.5 | 6 | 18 |
| District | 2 | 34 | 38.6 | 57 | 82 |
| District | 3 | 76 | 95.6 | 151 | 172 |
| Skill | 1 | 2 | 2.2 | 5 | 8 |
| Skill | 2 | 9 | 10.6 | 26 | 70 |
| Skill | 3 | 50 | 45.0 | 91 | 178 |

### Hub nodes drive everything

| Degree | Type | Entity |
|---:|---|---|
| **39** | FinancialInstitution | Scheduled Commercial Banks |
| **34** | **State** | **Telangana** |
| **29** | **State** | **Andhra Pradesh** |
| 27 | Soil | Loamy |
| 22 | MSME | Spice Grinding and Packing Unit |
| 21 | Soil | Red Soil |
| 20 | ClimateZone | Semi-arid |
| 20 | GovernmentScheme | Pradhan Mantri MUDRA Yojana |

**Any multi-hop rule must exclude `State`, `Country`, and `Scheduled Commercial Banks`**,
or it will return the hub's entire neighbourhood as a recommendation. "Loamy" soil is the
same trap in the agriculture half — two hops from a crop reaches every other crop that
grows in loam.

### What two hops actually adds from a district

| Type gained at 2 hops but not 1 | Districts |
|---|---:|
| Country, District | 61/61 — **hub artefact** |
| Machinery | 21/61 |
| **GovernmentScheme** | **21/61** |
| FinancialInstitution | 20/61 |
| **Skill** | **20/61** |
| Market · ExportCountry | 17/61 |
| Crop | 13/61 |
| **Industry** | **2/61** |
| **BusinessOpportunity** | **0/61** |

**BusinessOpportunity is unreachable from a district even at two hops.** It sits three
hops away for 22 districts and five for the other 39. No traversal setting fixes that;
only E1/E2 do.

---

## 2. Rule-by-rule review

### The two dead rules — traversal is not the cause

| Rule | Traversal | Edges | Verdict |
|---|---|---:|---|
| `RS2-VIA_DISTRICT` | `neighbours(district, SUPPORTED_BY_SCHEME, in)` | **0** | **Stays one-hop.** R1 supplies 305 edges and revives it |
| `RI3-VIA_DISTRICT` | `neighbours(district, LOCATED_IN, in, Industry)` | **0** | **Stays one-hop.** Needs E3 collection |

**Neither is a traversal problem.** Both look for exactly one edge shape and no edge of
that shape exists. Making them two-hop would substitute a longer wrong path for a short
missing one.

`RS2` is the proof: after R1 it fires at one hop for **61 of 61 districts**. No depth
change required.

### All 44 rules

| Rules | Traversal | Verdict |
|---|---|---|
| `SK1–SK4` skill profile | crosswalk + `REQUIRES_SKILL` | **One-hop.** Depth adds nothing |
| `BR1–BR3` business readiness | skill → business | **One-hop.** Blocked by E1, not depth |
| `LR1–LR3` learning roadmap | gap skill → provider | **One-hop.** `LR3` needs E6, and says so itself |
| `DO1–DO3` district opportunity | district degree/diversity | **One-hop — and must stay.** Counting two-hop neighbours would count sibling districts as opportunity |
| `CO1–CO3` collaboration | Supabase rows | Not graph traversal |
| `AI1–AI3` ai readiness | `USES_AI` | **One-hop** |
| `FR1–FR3` funding | scheme/bank reach | **One-hop.** `FR1` improves with R1 |
| `RB1–RB3` business ideas | skill/district/sector → idea | **One-hop.** Editorial JSON, not graph |
| `RS1` schemes via business | business → scheme | **One-hop** |
| **`RS2`** schemes via district | district → scheme | **One-hop after R1** ✅ |
| `RS3` schemes via skill | skill → scheme | **One-hop** |
| `RC1–RC2` courses | gap skill → cert/provider | **One-hop.** Needs E5/E6 |
| `RL1–RL3` collaborators | Supabase | Not traversal |
| `RM1–RM2` markets | business → market | **One-hop** |
| `RN1–RN3` msmes | skill/district → MSME | **One-hop** |
| `RI1–RI2` industries | skill/interest → industry | **One-hop** |
| **`RI3`** industries via district | district → industry | **One-hop; blocked on E3** |

**43 of 44 stay one-hop.** One candidate for two-hop, below.

---

## 3. The one typed two-hop path worth adding

### `District -> MSME -> GovernmentScheme`

| | |
|---|---|
| Path | `District <-GENERATES_EMPLOYMENT- MSME -SUPPORTED_BY_SCHEME-> GovernmentScheme` |
| Edges available | 32 + 57 |
| Districts served | **21 of 61** |
| Schemes reachable | **48** |
| Semantics | *"a scheme supporting an enterprise that employs people in your district"* |

This is a genuine, explainable, typed path — not depth for its own sake. It complements
R1 rather than duplicating it: R1 gives *availability* (jurisdiction), this gives
*local evidence of use*.

**Add it as a named path with its own rule id (`RS4-VIA_LOCAL_MSME`) and its own reason
string**, not by raising the traversal depth. The reason a user reads must name the
intermediate MSME, or the recommendation cannot be explained — and an unexplainable
recommendation is one the platform should not make.

### Two paths considered and rejected

| Path | Why not |
|---|---|
| `District -> Institution -> ?` | 58 edges in, nothing out. Institutions are leaves |
| `Skill -> Industry -> BusinessOpportunity` | Real (37 + 45 edges) but **every business in an industry would match every skill in it** — 45 opportunities across 24 industries makes this a category match wearing a skill match's clothing. E1 gives the direct edge; use that |

The second is the more tempting one, and the more damaging. It would fill
`business_ideas` immediately with plausible, unfalsifiable matches.

---

## 4. Performance

**2-hop expansion: 4 microseconds.** Measured over 2,000 traversals on the live graph
(647 nodes, 865 edges, adjacency in memory).

| Depth | Median nodes | Est. per-user cost |
|---:|---:|---:|
| 1 | 1–2 | <1 µs |
| 2 | 34 | **4 µs** |
| 3 | 76 | ~12 µs |

A full engine run touches ~40 traversals: **≈0.2 ms of traversal** against a run
dominated by snapshot loading.

### Precomputed paths — not recommended

| Approach | Cost | Verdict |
|---|---|---|
| **On-demand 1-hop** *(today)* | <1 µs | **Keep** |
| On-demand typed 2-hop | 4 µs | **Adopt for `RS4`** |
| Precomputed reachability table | 647² = 418k cells | **No** |
| Materialised path index | Rebuild per graph change | **No** |

Precomputation buys nothing at this scale and costs the property that matters most:
**a live traversal is explainable and a cached one is a claim about a graph that may
have changed.** Every recommendation must cite the edges behind it, and those edges are
cheaper to walk than to look up.

**Revisit at ~10,000 entities or ~50,000 edges.** At the projected post-Wave-1 size —
669 entities, 1,275 edges — this is not close.

---

## 5. Guard rails, if depth is ever raised

1. **Exclude hub types by default.** `State`, `Country`, and any node with degree >25.
   Without this, two hops means "everything in your state."
2. **Type the path, never the depth.** `District -> MSME -> Scheme` is a rule.
   "Two hops from the district" is a bug that has not happened yet.
3. **Name every intermediate in the reason.** *"supports Spice Grinding Unit, which
   employs people in Nizamabad"* is a recommendation. *"related to your district"* is not.
4. **Confidence must decay per hop.** Inherit the **minimum** across the path, as
   `Outcome.confidence` already does. A two-hop conclusion is at most as trustworthy as
   its weakest edge.
5. **Cap results per path.** A single hub can dominate an entire category.

---

## 6. Summary

| Question | Answer |
|---|---|
| Should rules become multi-hop? | **No — 43 of 44 stay one-hop** |
| Any exception? | **One**: `RS4-VIA_LOCAL_MSME`, typed, 21 districts, 48 schemes |
| Should paths be precomputed? | **No.** 4 µs, and caching costs explainability |
| Does traversal explain the district failure? | **No.** Two-hop median reach is 1 node once the State hub is removed |
| What does? | Missing edges. R1 revives `RS2` at one hop for all 61 districts |

**The most useful result in this workstream is a negative one.** Multi-hop traversal was
the obvious lever, it is cheap, and it would not have worked — the reach it appears to
add is 30 sibling districts arriving through a hub. Measuring that before building it is
the whole point of doing Workstream 5 before Workstream 1's code.
