# Recommendation Rules — User Intelligence

The ten categories, the rules behind each, and what every recommendation must carry.

`user_intelligence/recommenders.py` · rules version **1.0.0**

---

## 1. What every recommendation carries

The brief requires four fields. All four are `NOT NULL` in the migration, and a
test checks every emitted row:

| Field | Meaning |
|---|---|
| `reason` | Why, in a sentence a user can read |
| `supporting_entities` | The entities, edges and profile fields behind it |
| `confidence` | Trust in the underlying rows — inherited, never invented |
| `generated_at` | When |

Plus two the engine adds because they make the rest usable:

| Field | Meaning |
|---|---|
| `rule` | Which rule fired, e.g. `RS1-VIA_BUSINESS` |
| `match_score` | How well it fits **this user** — separate from confidence |

A real row, from the `resolving` fixture:

```json
{
  "category": "government_schemes",
  "item_id": "vw:governmentscheme:pm-formalisation-of-micro-food-processing-enterprises",
  "item_label": "PM Formalisation of Micro Food Processing Enterprises",
  "item_type": "GovernmentScheme",
  "match_score": 90.0,
  "confidence": 72,
  "confidence_band": "GOVERNMENT_GRADE",
  "reason": "supports Cold-Pressed Oil Unit, which matches 100.0% of your skills",
  "rule": "RS1-VIA_BUSINESS",
  "rank": 1,
  "supporting_entities": [
    {
      "kind": "entity",
      "ref": "vw:governmentscheme:pm-formalisation-of-micro-food-processing-enterprises",
      "label": "PM Formalisation of Micro Food Processing Enterprises",
      "confidence": 73,
      "source_package": "Package007_Government_Schemes",
      "source_row_id": "sch-019"
    },
    {
      "kind": "entity",
      "ref": "vw:msme:cold-pressed-oil-unit",
      "label": "Cold-Pressed Oil Unit",
      "confidence": 72,
      "source_package": "Package008_MSME",
      "source_row_id": "mb-003"
    },
    {
      "kind": "edge",
      "ref": "vwr:000303",
      "label": "SUPPORTED_BY_SCHEME",
      "detail": "vw:msme:cold-pressed-oil-unit -> vw:governmentscheme:pm-formalisation-of-micro-food-processing-enterprises",
      "confidence": 72,
      "source_package": "Package008_MSME",
      "source_dataset": "scheme_mapping.csv",
      "source_row_id": "smap-006"
    }
  ]
}
```

Every row also carries `unverified_notice`, because all 2,299 knowledge rows are
`VST-NEEDS_REVIEW`:

> Based on knowledge-base rows that no human has reviewed (verification_status = VST-NEEDS_REVIEW). Confidence reflects source strength, not correctness.

---

## 2. Ranking, filtering and capping

```
score  →  drop below MIN_MATCH_SCORE (20)
       →  sort by (-match_score, -confidence, item_id)
       →  cap at MAX_PER_CATEGORY (20)
```

`item_id` is the final tiebreak so ordering is **total** — without it, two equally
scored items could swap places between runs and break `result_hash`.

The floor of 20 comes from the data rather than from taste: with 86
`REQUIRES_SKILL` edges and a 22.8% skill resolve rate, anything lower produces long
lists where a single weak signal carried the whole match.

---

## 3. Results on the `resolving` fixture

| Category | Recommendations | Status |
|---|---:|---|
| `business_ideas` | 20 | `OK` |
| `collaborators` | 2 | `OK` |
| `courses` | 0 | `NO_MATCHES` |
| `events` | 0 | `NO_DATA_SOURCE` |
| `government_schemes` | 8 | `OK` |
| `industries` | 1 | `OK` |
| `markets` | 1 | `OK` |
| `mentors` | 0 | `NO_DATA_SOURCE` |
| `msmes` | 8 | `OK` |
| `research` | 1 | `OK` |

---

## `business_ideas` — Business Ideas

| | |
|---|---|
| Sources | `idea_library`, `BusinessOpportunity`, `MSME` |
| Requires | `profiles`, `vocabulary_crosswalk`, `knowledge_graph`, `idea_library` |
| Rules | 3 |
| On the `resolving` fixture | **20** recommendations, status `OK` |

- **`RB1-SKILL_MATCH`**
- **`RB2-DISTRICT_FIT`**
- **`RB3-SECTOR_INTEREST`**

## `government_schemes` — Government Schemes

| | |
|---|---|
| Sources | `GovernmentScheme` |
| Requires | `profiles`, `vocabulary_crosswalk`, `knowledge_graph` |
| Rules | 3 |
| On the `resolving` fixture | **8** recommendations, status `OK` |

- **`RS1-VIA_BUSINESS`**
- **`RS2-VIA_DISTRICT`**
- **`RS3-VIA_SKILL`**

## `courses` — Courses

| | |
|---|---|
| Sources | `Certification`, `TrainingProvider` |
| Requires | `profiles`, `vocabulary_crosswalk`, `knowledge_graph` |
| Rules | 2 |
| On the `resolving` fixture | **0** recommendations, status `NO_MATCHES` |

- **`RC1-FOR_GAP_SKILL`**
- **`RC2-PROVIDER_IN_DISTRICT`**

> **Sparse:** TRAINED_BY has 3 edges in the whole graph, so most gap skills resolve to no provider. Certifications are matched by category instead, which is weaker.

## `research` — Research

| | |
|---|---|
| Sources | `research_articles` |
| Requires | `profiles`, `research_articles` |
| Rules | 2 |
| On the `resolving` fixture | **1** recommendations, status `OK` |

- **`RR1-DISTRICT_TAG`**
- **`RR2-SECTOR_TAG`**

## `mentors` — Mentors

**Status: `NO_DATA_SOURCE`. Zero recommendations, for every user, always.**

> No mentor data exists anywhere in the platform: no Mentor entity type, no mentors table, no mentor flag on profiles. `collaborator_profiles.archetype` records self-declared archetypes, none of which means 'mentor'. Recommending mentors would require inventing them.

There is no rule to document because there is nothing to rule over. The category is
still emitted, with the reason attached, so a UI can explain the gap rather than
render a blank panel — and so the day data arrives, the category is already wired.

`test_no_data_categories_never_emit_a_recommendation` asserts this across all four
fixtures.

## `collaborators` — Collaborators

| | |
|---|---|
| Sources | `profiles`, `collaborator_profiles` |
| Requires | `profiles`, `connections`, `collaborator_profiles` |
| Rules | 3 |
| On the `resolving` fixture | **2** recommendations, status `OK` |

- **`RL1-COMPLEMENTARY_SKILL`**
- **`RL2-SAME_DISTRICT`**
- **`RL3-SHARED_SECTOR`**

## `events` — Events

**Status: `NO_DATA_SOURCE`. Zero recommendations, for every user, always.**

> No event data exists: no Event entity type, no events table, no calendar source. Nothing in the knowledge base or the application records an event.

There is no rule to document because there is nothing to rule over. The category is
still emitted, with the reason attached, so a UI can explain the gap rather than
render a blank panel — and so the day data arrives, the category is already wired.

`test_no_data_categories_never_emit_a_recommendation` asserts this across all four
fixtures.

## `markets` — Markets

| | |
|---|---|
| Sources | `Market` |
| Requires | `profiles`, `vocabulary_crosswalk`, `knowledge_graph` |
| Rules | 2 |
| On the `resolving` fixture | **1** recommendations, status `OK` |

- **`RM1-VIA_BUSINESS`**
- **`RM2-BY_DIGITAL_INTENSITY`**

> **Sparse:** 11 Market entities and 12 SELLS_TO edges. Ranking is possible but shallow.

## `msmes` — MSMEs

| | |
|---|---|
| Sources | `MSME` |
| Requires | `profiles`, `vocabulary_crosswalk`, `knowledge_graph` |
| Rules | 3 |
| On the `resolving` fixture | **8** recommendations, status `OK` |

- **`RN1-SKILL_MATCH`**
- **`RN2-DISTRICT`**
- **`RN3-RISK_FIT`**

## `industries` — Industries

| | |
|---|---|
| Sources | `Industry` |
| Requires | `profiles`, `vocabulary_crosswalk`, `knowledge_graph` |
| Rules | 3 |
| On the `resolving` fixture | **1** recommendations, status `OK` |

- **`RI1-VIA_SKILL`**
- **`RI2-VIA_INTEREST`**
- **`RI3-VIA_DISTRICT`**

---

## 4. Deduplication

Categories that can reach the same item by several paths (`government_schemes`,
`markets`, `industries`) keep the **highest-scoring** path and discard the rest.
The surviving `reason` is therefore the strongest available explanation, not the
first one found — which matters because "supports a business matching 100% of your
skills" is a better sentence than "available in your district", and a user should
see the better one.

`test_no_duplicate_item_within_a_category` enforces uniqueness.

---

## 5. Two things no rule will do

**Recommend an item with no reason.** Every constructor requires one, the column is
`NOT NULL`, and a test walks every emitted row.

**Invent an item because a category looked empty.** `mentors` and `events` return
zero for every user. The temptation to fill them with something plausible — the
nearest collaborator relabelled as a mentor, a training programme relabelled as an
event — is exactly what this platform is built to refuse.
