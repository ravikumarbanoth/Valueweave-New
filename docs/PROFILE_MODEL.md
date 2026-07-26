# Profile Model — User Intelligence

The eight scored profiles, the five output tables, and what each field means.

`user_intelligence/profiles.py` · `user_intelligence/engine.py`

---

## 1. Two numbers per score, never one

| | Range | Means | Source |
|---|---|---|---|
| `score` | 0–100 or `None` | how well the user matches | computed by rules |
| `confidence` | 0–100 | how much the rows can be trusted | minimum across evidence |
| `status` | enum | whether it could be computed at all | see below |

`score = None` is a real value and means *we could not compute this*. It is not
zero, and a UI must not render it as one.

---

## 2. The eight scores

### `skill_profile` — User Skill Profile

Which claimed skills resolve to the knowledge graph, at what NSQF level, and which have no researched counterpart.

**Requires:** `profiles`, `vocabulary_crosswalk`, `knowledge_graph`


On the `resolving` fixture: **75.2**, status `APPLIED`, confidence 65

| Rule | Status | Value | Weight | Reason |
|---|---|---:|---:|---|
| `SK1-RESOLVED` | `APPLIED` | 100.0 | 2.0 | 5 of 5 skills resolve to the knowledge graph |
| `SK2-DEPTH` | `APPLIED` | 30.0 | 1.0 | highest NSQF level among resolved skills is 3 |
| `SK3-BREADTH` | `APPLIED` | 50.0 | 1.0 | skills span 2 category(ies): Food Processing, Soft Skills & Communication |
| `SK4-DEMAND` | `APPLIED` | 96.0 | 1.0 | 12 researched businesses require these skills |

### `business_readiness` — Business Readiness

Whether the user's resolved skills and district cover what a researched business actually requires.

**Requires:** `profiles`, `vocabulary_crosswalk`, `knowledge_graph`
**Low score means:** Skills do not yet cover any researched business's requirements.

On the `resolving` fixture: **69.5**, status `APPLIED`, confidence 56

| Rule | Status | Value | Weight | Reason |
|---|---|---:|---:|---|
| `BR1-SKILL_COVERAGE` | `APPLIED` | 100.0 | 2.0 | covers 1 of 1 skills required by Bio-Fertiliser and Vermicompost Unit |
| `BR2-DISTRICT` | `APPLIED` | 10.0 | 1.0 | 1 researched entities are linked to Medak |
| `BR3-CATEGORY_FIT` | `APPLIED` | 68.0 | 1.0 | 2 declared sector(s) map to researched industries |

### `learning_roadmap` — Learning Roadmap

Ordered skill gaps between what the user has and what their best matched businesses need.

**Requires:** `profiles`, `vocabulary_crosswalk`, `knowledge_graph`


On the `resolving` fixture: **100.0**, status `APPLIED`, confidence 69

| Rule | Status | Value | Weight | Reason |
|---|---|---:|---:|---|
| `LR1-GAP` | `APPLIED` | 100.0 | 2.0 | already covers every skill required by 8 matched business(es) |
| `LR2-SEQUENCE` | `UNAVAILABLE` | — | 1.0 | no skill gap to sequence — the user already covers every skill their matched businesses  |
| `LR3-PROVIDER` | `UNAVAILABLE` | — | 1.0 | no roadmap steps, so no provider to find |

### `district_opportunity` — District Opportunity Score

How much researched opportunity exists in the user's district.

**Requires:** `profiles`, `vocabulary_crosswalk`, `knowledge_graph`
**Low score means:** Little researched data for this district yet — a coverage gap, not an absence of opportunity.

On the `resolving` fixture: **33.0**, status `APPLIED`, confidence 65

| Rule | Status | Value | Weight | Reason |
|---|---|---:|---:|---|
| `DO1-RESOLVE` | `APPLIED` | 100.0 | 1.0 | 'Medak' resolves to Medak (EXACT_NAME) |
| `DO2-DENSITY` | `APPLIED` | 6.0 | 2.0 | 1 researched entities link to this district |
| `DO3-DIVERSITY` | `APPLIED` | 20.0 | 1.0 | spanning 1 entity type(s): MSME 1 |

### `collaboration_score` — Collaboration Score

Readiness and demonstrated activity as a collaborator.

**Requires:** `profiles`, `connections`


On the `resolving` fixture: **54.2**, status `APPLIED`, confidence 65

| Rule | Status | Value | Weight | Reason |
|---|---|---:|---:|---|
| `CO1-PROFILE` | `APPLIED` | 100.0 | 1.0 | 6 of 6 collaboration-relevant profile fields present |
| `CO2-ACCEPTED` | `APPLIED` | 50.0 | 2.0 | 2 accepted connection(s) (using connections; no teams table exists) |
| `CO3-COMPLEMENTARITY` | `APPLIED` | 16.7 | 1.0 | peers bring 1 skill(s) the user does not have |

### `ai_readiness` — AI Readiness

Exposure to AI-augmentable skills and AI-ready businesses.

**Requires:** `profiles`, `vocabulary_crosswalk`, `knowledge_graph`


On the `resolving` fixture: **24.8**, status `APPLIED`, confidence 65

| Rule | Status | Value | Weight | Reason |
|---|---|---:|---:|---|
| `AI1-SKILL_AUGMENTATION` | `APPLIED` | 30.0 | 2.0 | 2 resolved skill(s) carry a Package006 AI-augmentation level |
| `AI2-BUSINESS_READINESS` | `APPLIED` | 39.4 | 1.0 | 8 matched business(es) carry an AI-readiness rating |
| `AI3-TOOLING` | `NO_SIGNAL` | 0.0 | 1.0 | no AI tooling linked to matched businesses — USES_AI holds 16 edges across the whole gra |

### `funding_readiness` — Funding Readiness

Reachable schemes and financial institutions given the user's matched businesses and district.

**Requires:** `profiles`, `vocabulary_crosswalk`, `knowledge_graph`


On the `resolving` fixture: **67.2**, status `APPLIED`, confidence 67

| Rule | Status | Value | Weight | Reason |
|---|---|---:|---:|---|
| `FR1-SCHEME_REACH` | `APPLIED` | 72.0 | 2.0 | 6 government scheme(s) reachable through matched businesses |
| `FR2-BANK_REACH` | `APPLIED` | 25.0 | 1.0 | 1 financial institution(s) linked to matched businesses |
| `FR3-PROFILE_COMPLETENESS` | `APPLIED` | 100.0 | 1.0 | 5 of 5 application-relevant fields present: budget, city, district, name, skills |

### `startup_readiness` — Startup Readiness

Composite of the seven above, weighted.

**Requires:** `profiles`, `vocabulary_crosswalk`, `knowledge_graph`


On the `resolving` fixture: **62.9**, status `APPLIED`, confidence 56

| Rule | Status | Value | Weight | Reason |
|---|---|---:|---:|---|
| `ST1-COMPOSITE` | `APPLIED` | 62.9 | 1.0 | weighted composite of 7 component score(s) (1.00 of 1.00 weight available) |

---

## 3. `startup_readiness` — the composite

| Component | Weight |
|---|---:|
| `skill_profile` | 0.25 |
| `business_readiness` | 0.25 |
| `funding_readiness` | 0.15 |
| `district_opportunity` | 0.15 |
| `collaboration_score` | 0.10 |
| `learning_roadmap` | 0.05 |
| `ai_readiness` | 0.05 |

Weights sum to **1.00** (asserted by a test). On the `resolving` fixture:
**62.9** from
1.0 of 1.00 weight available.

Unavailable components are excluded from the denominator and listed in
`excluded_unavailable`. On the `empty` fixture that list contains
`district_opportunity`, because a user with no city cannot have a district score —
and scoring them 0 for it would be a claim about them rather than about our inputs.

---

## 4. The five output tables

| Table | Grain | Key |
|---|---|---|
| `user_skill_profile` | one row per user | `(user_id, rules_version)` |
| `user_business_profile` | one row per user, five scores as jsonb | `(user_id, rules_version)` |
| `user_learning_profile` | one row per user | `(user_id, rules_version)` |
| `user_recommendations` | **one row per recommendation** | `(user_id, rules_version, category, item_id)` |
| `user_activity_summary` | one row per user | `(user_id, rules_version)` |

### Why `rules_version` is in every key

A recommendation a user acted on must stay explainable after the rules change.
Keying on `user_id` alone would overwrite the row that explains past behaviour the
moment a rule moved. Keying on both keeps the old row until someone deliberately
prunes it.

### `user_skill_profile` — the honest half

```
claimed_skill_count    5
resolved_skill_count   5
resolve_rate_pct       100.0
```

`unresolved_skills` is the field that matters most. On the `unresolvable` fixture:

```json
[
  {
    "term": "Beautician Services",
    "reason": "'Beautician Services' is a recognised skill with no researched counterpart in the knowledge base yet"
  },
  {
    "term": "Data Entry",
    "reason": "'Data Entry' is a recognised skill with no researched counterpart in the knowledge base yet"
  },
  {
    "term": "Digital Marketing",
    "reason": "'Digital Marketing' is a recognised skill with no researched counterpart in the knowledge base yet"
  }
]
```

Every entry carries a reason. These are **real skills the user has** that the
knowledge base has no researched counterpart for — 50 such skills exist today
(Step 0's `collection_backlog`). Showing an empty panel would read as "you have no
skills". Showing this reads as "we haven't collected data on yours yet", which is
the truth and is also the collection backlog.

### `user_activity_summary` — the meta row

Carries what is *missing* as first-class data:

| Field | On the `resolving` fixture |
|---|---|
| `scores_unavailable` | `[]` |
| `categories_without_data` | `['events', 'mentors']` |
| `inputs_unavailable` | `['assessment_results', 'teams']` |
| `knowledge_snapshot_hash` | `0eebdc8acd75aa9d` |
| `result_hash` | `7233cf3cbbced8c1` |

The last two make a run auditable: the snapshot hash says which graph it saw, the
result hash proves what it concluded.

---

## 5. `UserContext` — the input model

Assembled by `from_supabase_rows()` from rows the **caller** fetched. The engine
holds no database client.

| Field | From |
|---|---|
| `skills`, `interests`, `city`, `bio`, `looking_for`, `name` | `profiles` |
| `archetype`, `district`, `top_sectors`, `budget`, `ep_score` | `collaborator_profiles` |
| `accepted_connection_ids`, `pending_connection_ids` | `connections`, split by status |
| `collaborator_skills` | skills of accepted-connection peers |
| `owned_opportunity_skills` | `opportunities.skills_needed` |
| `unavailable_inputs` | computed from `INPUTS` — `assessment_results`, `teams` |

Every list is normalised to a **sorted tuple**. A `set` would iterate in an order
stable within one process and not across two, which would silently break
`result_hash` — the worst kind of bug, because it only appears in production.

`location_term` prefers `district` over `city` and takes the part before the first
comma, so `"Medak, Telangana"` resolves.

---

## 6. Reading a score in the UI

Three statuses, three different sentences. This is the whole point of the model:

| Status | Sentence |
|---|---|
| `APPLIED` | show the score and its `reason` |
| `NO_SIGNAL` | *"No researched business requires your skills yet"* — use `reason` |
| `UNAVAILABLE` | *"We don't have your assessment yet"* — never show a number |

And on the skill profile specifically: **always render `unresolved_skills`.** It is
the difference between a product that seems to have nothing to say about a user and
one that admits what it does not yet know.
