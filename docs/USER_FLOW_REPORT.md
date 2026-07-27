# User Flow Report — Platform v3.0, Step 3

Whether the knowledge graph feels connected, traced hop by hop.

---

## 0. The brief's loop, walked

```
Dashboard → Business → Skill → Scheme → District → Related businesses
         → Related skills → Related schemes → Back to Dashboard
```

**Every hop exists. Every hop is a link, not a search.**

| # | From | Hop | Mechanism | Status |
|---|---|---|---|---|
| 1 | `/dashboard` | Business rail card | `RecommendationRail` → `hrefFor` | ✅ |
| 2 | `/knowledge/business/…` | Required skill | `RelatedEntities`, `REQUIRES_SKILL` | ✅ |
| 3 | `/knowledge/skill/…` | Supporting scheme | `SUPPORTED_BY_SCHEME` | ✅ |
| 4 | `/knowledge/scheme/…` | District coverage | `AVAILABLE_IN` | ⚠️ **0 edges** |
| 5 | `/knowledge/district/…` | Businesses here | grouped related | ⚠️ thin |
| 6 | any detail | Related businesses | `RelatedEntities` | ✅ |
| 7 | any detail | Related skills | `RelatedEntities` | ✅ |
| 8 | any detail | Related schemes | `RelatedEntities` | ✅ |
| 9 | any detail | Back to dashboard | `AppNavbar` + `NextSteps` | ✅ |

**Hop 4 is the loop's one broken link, and it is a data gap rather than a UI one.** No
`GovernmentScheme → District` edge exists, so `RS2-VIA_DISTRICT` cannot fire. The
section renders and says so. Phase 2 `R1` recovers 305 such edges from
`district_scheme_mapping.csv`, a 305-row dataset already in the repository that the graph
builder never reads.

---

## 1. What makes it feel connected

### Every card links

Before Step 3, five of ten recommendation categories were dead ends —
`HREF_BUILDERS` returned `null` for schemes, MSMEs, industries, markets and courses. The
engine had always emitted the `global_entity_id`; there was simply nowhere to send it.

| Surface | Before | After |
|---|---|---|
| Dashboard rails | 3 of 10 categories linked | **10 of 10** |
| Search results | `<div>` | **`<Link>`** |
| District panel cards | no link | **link** |
| Idea-page enriched entities | no link | **link** |
| Explorer results | — | **link** |

### `NextSteps` — the loop as a control

Every graph detail page ends with up to three concrete next hops, drawn from its own
related entities:

> **Explore a required skill: Welding (MIG/TIG/Arc) →**
> **See a supporting scheme: PMEGP →**
> **Browse all knowledge →**

Not generic navigation — the actual neighbours of the record being read. A dead end is
impossible while the entity has any edge at all.

### Relationship type on every chip

Each related entity shows *why* it is there — `requires skill`, `supported by scheme`,
`located in`. "Why is this here?" is the first question a connected view raises, and
answering it inline is what separates a graph from a list of tags.

---

## 2. Entry points into knowledge

| From | Route | Priority |
|---|---|---|
| Navbar / direct | `/knowledge` | 2 |
| Dashboard rail | `/knowledge/{type}/{slug}` | 1 |
| Dashboard "Latest knowledge" | `/knowledge/{type}/{slug}` | 1 |
| Search result | `/knowledge/{type}/{slug}` | 7 |
| District page card | `/knowledge/{type}/{slug}` | 6 |
| Idea page enrichment | `/knowledge/{type}/{slug}` | 10 |
| `/schemes`, `/skills` (CMS empty) | `/knowledge/scheme|skill/{slug}` | 4, 5 |
| Static knowledge page | `/knowledge` | — |

**Eight entry points, one destination shape.** A user who learns the detail page once
knows every knowledge surface in the product.

---

## 3. Three journeys, as they run today

### A · Student with resolving skills — works

```
/dashboard        6 rails, intelligence summary, latest knowledge
   ↓ business idea card
/knowledge/msme/sheet-metal-fabrication-unit
                  investment, risk, employment; related skills and schemes
   ↓ required skill
/knowledge/skill/welding-mig-tig-arc
                  NSQF level, duration, demand, automation risk
   ↓ supporting scheme
/knowledge/scheme/pmegp
                  ministry, assistance, subsidy, "Apply on the official portal ↗"
   ↓ district coverage
                  ⚠️ EMPTY — no scheme→district edge exists
```

Four of five hops land. The fifth explains itself.

### B · Student whose skills do not resolve — degrades honestly

```
/dashboard        rails render NO_SIGNAL with named reasons, not blank panels
   ↓ Knowledge Explorer
/knowledge        browse by package — no personalisation required
   ↓ Skills (45)
/knowledge?type=skill&page=1
   ↓ any skill
/knowledge/skill/...
```

**The Explorer is the fallback for the 77% of users whose skills do not resolve.** It is
the strongest argument for Priority 2: browsing needs no vocabulary match, so it works
for exactly the users personalisation fails.

### C · Anonymous visitor — works, unauthenticated

`/knowledge` → browse → detail → related → detail. No auth gate; the middleware protects
`/dashboard`, `/profile`, `/connections` and `/admin`, not `/knowledge`.

Correct: this is public reference data with public sources.

---

## 4. Dead ends, and what each says

| Situation | Message |
|---|---|
| Schema not deployed | "The knowledge schema has not been deployed to this environment. Nothing is wrong with your account." |
| Synced but empty | "1,812 researched rows are waiting in Git." |
| No search match | "We searched the researched knowledge base and found nothing. That is a gap in our data, not in your query." |
| Entity has no edges | "Nothing in the knowledge graph links to this record yet. That is a gap in our relationship coverage, not a statement that no connection exists." |
| No mentors / events | `NO_DATA_SOURCE` with the reason from the engine |

**Every dead end names its cause and offers a way onward.** The difference between "we
have not collected this" and "there is nothing here" is the difference between a user
trusting the platform and not.

---

## 5. Provenance on the path

At every hop the user can see where a claim came from:

| Element | Shows |
|---|---|
| `SourceBadge` | `Package007 · Government Schemes` |
| `ConfidenceBadge` | 0–100, banded, tooltip explaining it scores *source strength* |
| `ProvenanceLine` | package · dataset · row id |
| Official source link | The public URL, where the row has one |
| `UnverifiedNotice` | "Not yet reviewed" — computed, so it disappears when it stops being true |

A user can go from a dashboard recommendation to the CSV row behind it in three clicks
without leaving the flow.

---

## 6. Honest assessment

**Does the graph feel connected? Structurally yes; experientially, not yet.**

The navigation is complete — every entity links to its neighbours, every card reaches a
detail page, every dead end explains itself. **What is missing is edges, not links.**

| Measure | Now | After Phase 2 W1 |
|---|---:|---:|
| Recommendation categories that link | **10 / 10** | 10 / 10 |
| Entry points into knowledge | **8** | 8 |
| Loop hops that work | **8 / 9** | 9 / 9 |
| Districts reaching a scheme | **0 / 61** | 61 / 61 |
| Businesses showing required skills | **2 / 45** | 19 / 45 |
| Entities with no neighbours at all | **142 / 647** | ~138 |

**22% of detail pages will be leaf nodes** — a header, attributes, and an honest note
that nothing links to them yet.

The UI cannot fix that, and it should not pretend to. What it does instead is make the
gap **visible and specific**: a user who reaches an orphan entity is told the platform
has not connected it, rather than being left to conclude no connection exists.

That is the correct division of labour between this step and Phase 2 — and Phase 2 W1
recovers ~410 of those edges from datasets already sitting in `packages/`.
