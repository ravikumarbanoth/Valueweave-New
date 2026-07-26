# User Intelligence Engine — Platform v3.0, Step 1.5

**`user_intelligence/` — rule-based intelligence connecting a user profile to the
knowledge graph.** No AI, no model, no randomness.

```
profiles.skills (free text)
    │  vocabulary crosswalk (Step 0)
    ▼
knowledge graph: 647 entities, 865 edges
    │  23 scoring rules · 21 recommendation rules
    ▼
8 scored profiles + 10 recommendation categories
    │  each carrying reason · evidence · confidence · timestamp
    ▼
5 output tables
```

```bash
python3 -m user_intelligence capabilities
python3 -m user_intelligence run --fixture resolving --explain
python3 -m user_intelligence rules
```

---

## 1. Three of the six named inputs do not exist

The brief lists `profiles`, `assessment_results`, `connections`, `teams`,
`idea_library` and the knowledge schema. Verified against every migration in the
repository:

| Input | Status | Detail |
|---|---|---|
| `assessment_results` | ❌ MISSING | No such table in any migration. No assessment feature exists. Rules that would use it return UNAVAILABLE. |
| `collaborator_profiles` | ✅ AVAILABLE | Supabase. archetype, district, top_sectors[], budget, ep_score. |
| `connections` | ✅ AVAILABLE | Supabase. Opportunity-scoped, 1:1, pending/accepted/rejected. |
| `idea_library` | 📄 STATIC_FILE | NOT a Supabase table. 122 ideas in frontend/lib/idea-library/ideas.json. Read from disk; a future migration would not change any rule. |
| `knowledge_graph` | ✅ AVAILABLE | Git artifacts: 647 entities, 865 edges. Read directly, so the engine runs offline and Git stays the source of truth. |
| `knowledge_projection` | ⏳ PENDING_MIGRATION | Supabase `knowledge` schema. Migration written in Step 1, not yet applied. The engine reads Git instead, which is equivalent by design. |
| `opportunities` | ✅ AVAILABLE | Supabase. category, skills_needed[], location, collaboration_type. |
| `profiles` | ✅ AVAILABLE | Supabase. id, name, city, bio, skills[], interests[], looking_for. |
| `research_articles` | ✅ AVAILABLE | Supabase. Powers the Research category. |
| `teams` | ❌ MISSING | No such table and no /teams route. `connections` with status=accepted is the closest real working group, and is what the collaboration rules use. |
| `vocabulary_crosswalk` | ✅ AVAILABLE | governance/vocabulary/*.csv from Step 0. The only bridge from free-text profile skills to graph entities. |

**This is configuration, not an error.** `INPUTS` declares each one's status, every
rule declares what it needs, and a rule whose input is missing returns
`UNAVAILABLE` **with the reason** — never a zero.

The difference matters more than it looks. A score of 0 is a claim about the user.
`UNAVAILABLE` is a claim about our data. Only one of them is true when there is no
`assessment_results` table, and only one lets a UI write a useful sentence.

`teams` is handled by substitution rather than omission: `connections` with
`status = 'accepted'` is the real working group in this application, so the
collaboration rules use it and say so in their reason text.

---

## 2. The eight scores

| Key | Label | Rules | Rule ids |
|---|---|---:|---|
| `skill_profile` | User Skill Profile | 4 | `SK1-RESOLVED`, `SK2-DEPTH`, `SK3-BREADTH`, `SK4-DEMAND` |
| `business_readiness` | Business Readiness | 3 | `BR1-SKILL_COVERAGE`, `BR2-DISTRICT`, `BR3-CATEGORY_FIT` |
| `learning_roadmap` | Learning Roadmap | 3 | `LR1-GAP`, `LR2-SEQUENCE`, `LR3-PROVIDER` |
| `district_opportunity` | District Opportunity Score | 3 | `DO1-RESOLVE`, `DO2-DENSITY`, `DO3-DIVERSITY` |
| `collaboration_score` | Collaboration Score | 3 | `CO1-PROFILE`, `CO2-ACCEPTED`, `CO3-COMPLEMENTARITY` |
| `ai_readiness` | AI Readiness | 3 | `AI1-SKILL_AUGMENTATION`, `AI2-BUSINESS_READINESS`, `AI3-TOOLING` |
| `funding_readiness` | Funding Readiness | 3 | `FR1-SCHEME_REACH`, `FR2-BANK_REACH`, `FR3-PROFILE_COMPLETENESS` |
| `startup_readiness` | Startup Readiness | 1 | `ST1-COMPOSITE` |

`startup_readiness` is a weighted composite of the other seven:

| Component | Weight |
|---|---:|
| `skill_profile` | 0.25 |
| `business_readiness` | 0.25 |
| `funding_readiness` | 0.15 |
| `district_opportunity` | 0.15 |
| `collaboration_score` | 0.10 |
| `learning_roadmap` | 0.05 |
| `ai_readiness` | 0.05 |

Weights sum to 1.00, asserted by a test — a composite whose weights drift produces
a number nobody can reproduce.

**Unavailable components are dropped from the denominator, not scored zero**, and
the result records which ones (`excluded_unavailable`) and how much weight was
actually available. A composite that treats "we have no data" as "the user scores
zero" is the easiest way to produce a number that misleads.

---

## 3. The ten recommendation categories

| Key | Label | Data | Rules | Sources |
|---|---|---|---:|---|
| `business_ideas` | Business Ideas | ok | 3 | idea_library, BusinessOpportunity, MSME |
| `government_schemes` | Government Schemes | ok | 3 | GovernmentScheme |
| `courses` | Courses | sparse | 2 | Certification, TrainingProvider |
| `research` | Research | ok | 2 | research_articles |
| `mentors` | Mentors | **NO DATA** | 0 | _caller-supplied_ |
| `collaborators` | Collaborators | ok | 3 | profiles, collaborator_profiles |
| `events` | Events | **NO DATA** | 0 | _caller-supplied_ |
| `markets` | Markets | sparse | 2 | Market |
| `msmes` | MSMEs | ok | 3 | MSME |
| `industries` | Industries | ok | 3 | Industry |

### Two have no data, and say so

`mentors` and `events` are in the brief and have **no backing anywhere** — no entity
type, no table, no column, no flag. They return `NO_DATA_SOURCE` with the reason and
emit **zero** recommendations. A test asserts this holds for every fixture.

`collaborator_profiles.archetype` records self-declared archetypes, none of which
means "mentor". Recommending mentors would require inventing them.

### Two are sparse, and say so

`courses` depends on `TRAINED_BY`, which has **3 edges in the entire graph**.
`markets` depends on `SELLS_TO`, which has **12**. Both work; both carry a
`sparse_note` explaining why results are thin, and `courses` falls back to
same-category certifications with `match_basis` recorded as *"category name, not a
TRAINED_BY edge"* so the weaker signal is visible.

---

## 4. Score and confidence are different numbers

The single most important distinction in the engine.

| | Means | Source |
|---|---|---|
| `match_score` | how well this fits **this user** | computed by the rules |
| `confidence` | how much the underlying rows can be **trusted** | inherited from the graph, as the **minimum** across supporting evidence |

A perfect match resting on a confidence-50 row is a strong claim about weak data.
One number cannot say that, so there are two.

The minimum rather than the mean, because a chain is as trustworthy as its weakest
link and averaging lets one good row mask a poor one.

**Editorial content reports confidence 0.** An idea-library entry has no confidence
score in its source. Its evidence may include a graph entity — the resolved
district at confidence 73 — but that is confidence in the *district*, not in the
idea. Borrowing it would dress an unsourced idea in a researched row's credibility.
A test enforces this.

---

## 5. Three statuses, three different sentences

| Status | Means | What a UI should say |
|---|---|---|
| `APPLIED` | computed, with signal | the result |
| `NO_SIGNAL` | computed; the answer is nothing | *"No researched business requires your skills yet"* |
| `UNAVAILABLE` | could not compute — input missing | *"We don't have your assessment yet"* |

All three render as an empty panel in a naive UI, and they mean different things.
Collapsing them is how an integration disappoints users: a blank reads as broken
when the honest answer is a coverage gap.

---

## 6. Reproducibility is the contract

`result_hash` covers the engine version, rules version, knowledge snapshot hash,
the full user context, every score fingerprint and every recommendation. It
**excludes `generated_at`** — the one field that must differ between two identical
runs.

```
7233cf3cbbced8c1   fixture `resolving`
47cb6298ed6a3396   fixture `unresolvable`
```

Guaranteed by construction, not convention:

- no `random`, no `uuid4`, no clock inside any computation — a test greps for all three
- every collection ordered before iteration; `UserContext` normalises lists to sorted tuples, because a `set` would be stable within one process and not across two
- rules are pure functions of a frozen context and a frozen snapshot
- the engine holds no database client at all

A recommendation a user acted on must be explainable months later, and an
explanation you cannot reproduce is a story.

---

## 7. Measured on the four fixtures

| Fixture | Recs | Unavailable scores | Scores |
|---|---:|---:|---|
| `resolving` | 41 | 0 | ai 25 · busine 70 · collab 54 · distri 33 · fundin 67 · learni 100 · skill 75 · startu 63 |
| `unresolvable` | 22 | 0 | ai 0 · busine 45 · collab 33 · distri 85 · fundin 27 · learni 0 · skill 0 · startu 31 |
| `empty` | 0 | 1 | ai 0 · busine 0 · collab 0 · distri n/a · fundin 0 · learni 0 · skill 0 · startu 0 |
| `district_only` | 20 | 0 | ai 0 · busine 27 · collab 25 · distri 59 · fundin 27 · learni 0 · skill 0 · startu 22 |

The fixtures are chosen to cover the range the engine must survive, not to look
good: `resolving` has skills that Step 0 resolves, `unresolvable` has five real
skills that Package006 does not cover **at all** (the common case, given the 22.8%
onboarding resolve rate), `empty` has nothing but an id, and `district_only`
isolates the geography rules.

`empty` produces **0 recommendations and 1 unavailable score** without raising —
which is the whole test of whether the degradation paths are real.

---

## 8. The engine holds no database client

Callers pass rows in: a profile, its connections, its peers, candidate
collaborators, research articles. Three consequences, all deliberate:

- it is testable without credentials, so its 72 tests are real tests
- it cannot leak a profile the caller's own visibility rules would have hidden
- it reads the **Git** knowledge artifacts, not the Supabase projection, so Git
  stays the source of truth (ADR-001) and the engine runs before Step 1's
  migration is applied

`research` and `collaborators` return an honestly empty category when the caller
supplies nothing, with a note saying so — not a missing category.

---

## 9. Files

```
user_intelligence/
  config.py        input availability, 8 ScoreSpecs, 10 CategorySpecs, thresholds
  rules.py         Outcome / Evidence / combine() — the UNAVAILABLE semantics
  knowledge.py     KnowledgeSnapshot: graph + Step 0 crosswalks, frozen and hashed
  context.py       UserContext, built from caller-supplied rows
  profiles.py      the 8 scorers
  recommenders.py  the 10 categories
  engine.py        orchestration -> 5 output tables, result_hash, explain()
  fixtures.py      four synthetic users, no real data
  cli.py           capabilities | rules | run
  generate_migration.py + migrations/001_user_intelligence.sql
```

Adding a score is a `ScoreSpec` plus a function in `SCORERS`. Adding a category is
a `CategorySpec` plus a function in `RECOMMENDERS`. Nothing else changes.

---

## 10. Honest limits

| Limit | Detail |
|---|---|
| **22.8% of onboarding skills resolve** | Step 0's ceiling. Most users will see `NO_SIGNAL` on skill-driven scores, and that is the data's fault, not the engine's. Fixing it means collecting ~30 skills into Package006. |
| Never run against live Supabase | No credentials in this environment. Profiles arrive as dicts, so the engine is fully exercised — but on synthetic users. |
| Migration not applied | `001_user_intelligence.sql` is generated and tested, not executed. |
| `TRAINED_BY` has 3 edges | The learning roadmap can order gaps but rarely name a provider. |
| No outcome data | Nothing records whether a recommendation was useful, so weights are reasoned, not calibrated. The v2.1 audit flagged this as the blocker for a real recommendation engine and it still is. |
| Scores are not comparable between users | A user in a well-researched district scores higher than one in a thin district for reasons that are about our coverage, not about them. |

**Companion documents:** `RULE_ENGINE.md`, `RECOMMENDATION_RULES.md`,
`PROFILE_MODEL.md`.
