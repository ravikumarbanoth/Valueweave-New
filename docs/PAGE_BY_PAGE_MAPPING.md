# Page-by-Page Knowledge Mapping — ValueWeave v3.0

**Phase 2 deliverable.** For every route: what it does today, what knowledge is injected,
what is required to inject it, and which component renders it.

**Reading rule.** *Existing* is what the code does now, verified by reading it. *Inject* is
additive — a new section below existing content, never a replacement. *Reuse* names an
existing component; **bold** names a genuinely new one.

**79 routes analysed.** 21 receive knowledge in v3.0. 58 are unchanged and are listed in
§9 so the reader can see they were considered, not missed.

---

## 0. The component budget

Nine new components serve all 21 pages. Everything else is reuse.

| Component | Used by | Purpose |
|---|---|---|
| **`KnowledgeCard`** | 12 pages | One entity: name, type, confidence badge, provenance line, link |
| **`KnowledgeCardGrid`** | 9 pages | Responsive grid of `KnowledgeCard` + empty/`NO_COUNTERPART` state |
| **`ProvenanceLine`** | inside every card | "Package007 · government_schemes.csv · sch-005 · confidence 78" |
| **`ConfidenceBadge`** | inside every card | 0–100 → colour band + tooltip |
| **`UnverifiedNotice`** | 8 pages | The `VST-NEEDS_REVIEW` disclosure (R2) |
| **`RelatedEntities`** | 7 pages | Graph neighbours, grouped by relationship type |
| **`SkillGapPanel`** | 3 pages | Have / need / no-data-for, from the crosswalk |
| **`DistrictIntelligencePanel`** | 3 pages | Industries, MSMEs, schemes, institutions for one district |
| **`RecommendationRail`** | 2 pages | Horizontal rail with a "why this?" affordance |

Every one uses existing Tailwind tokens (`card-base`, `chip`, `bg-cream`, `text-ink`,
`text-muted`) and `lucide-react` icons. No new colour, font, or dependency.

---

## 1. Dashboard — `/dashboard`

**Existing.** Client component. Loads `profiles` for the signed-in user, redirects to
`/onboarding` if `profile_complete` is false. Loads up to 50 `opportunities` with owner
join, filters by 9 hard-coded categories and a text search, then re-ranks so rows whose
`location` contains the user's city float to the top. Renders `OpportunityCard` +
`FeedSkeleton`. Shows a profile-completion percentage from 6 checks.

**Inject** — four rails, below the existing feed, in this order:

| Rail | Source | Join | Component |
|---|---|---|---|
| District Opportunities | `profiles.city` → `District` → `LOCATED_IN` / `GENERATES_EMPLOYMENT` | district crosswalk, **86% today** | **`DistrictIntelligencePanel`** |
| Recommended Schemes | `District` + `Industry` → `SUPPORTED_BY_SCHEME` (92 edges) | district crosswalk | **`RecommendationRail`** |
| Recommended Businesses | `profiles.skills` → `Skill` ← `REQUIRES_SKILL` (86 edges) | **skill crosswalk — 12% today** | **`RecommendationRail`** |
| Recommended Skills | adjacent skills of matched `BusinessOpportunity` | skill crosswalk | **`KnowledgeCardGrid`** |

**Recommended Collaborators** is deliberately *not* graph-driven. `founder_matches` and
`collaborator_profiles` already exist and already do this. The knowledge contribution is
one line of *explanation* on the existing card — "also needs Welding, which you have" —
which requires the skill crosswalk and nothing else.

> **Blocking dependency.** Rails 3 and 4 must not ship before the skill crosswalk. With a
> 12% resolve rate they would be blank for ~9 users in 10. Rails 1 and 2 can ship at 86%
> with an honest empty state for the other 14%.

**Reuse:** `AppNavbar`, `OpportunityCard`, `FeedSkeleton`, existing city-boost logic.
**Do not touch:** the feed query, the category chips, the completion calculation.

---

## 2. Idea Library — `/ideas`, `/ideas/[slug]`

**Existing.** Fully static from `lib/idea-library/`. **122 ideas** with `sector`, `bucket`,
`district_fit`, `skills_needed`, `investment_min/med/adv`, `team_roles`, `tags`. `/ideas`
does client-side filtering across 7 dimensions and 5 sorts. No Supabase, no network.

**Inject on `/ideas/[slug]`** — four sections after the existing detail:

| Section | Source | Edge / join | Note |
|---|---|---|---|
| Comparable researched businesses | Package004 `BusinessOpportunity` (45), Package008 `MSME` (40) | sector crosswalk → `Industry` → `PART_OF` | **Link, never merge.** An idea is editorial; a Package004 row is sourced. Label the distinction. |
| Schemes that support this | `SUPPORTED_BY_SCHEME` (92 edges) | via matched business | Package007, 40 schemes |
| Skills mapped to real training | `REQUIRES_SKILL` (86) → `TRAINED_BY` (**3 edges**) | skill crosswalk | `TRAINED_BY` is nearly empty — say so, don't render a stub |
| Where this is viable | `district_fit` → `District` (16/19 resolve) | district crosswalk | Links to the district page |

**Inject on `/ideas`:** one filter chip — "Has researched data" — driven by whether the
idea's sector resolves. Cheap, honest, and immediately useful.

**Reuse:** the entire existing filter/sort UI. **Do not touch** `ideas.json`; the crosswalk
lives outside it so the dataset stays hand-editable.

---

## 3. Profile — `/profile`, `/profile/[id]`

**Existing.** `/profile` loads `profiles` + owned `opportunities`, renders `ProfileView`
with `isMe`. `/profile/[id]` is the public view. `profiles.skills` is `text[]`, free text,
populated from 57 non-binding suggestions in onboarding.

**Inject** — three sections in `ProfileView`, gated on `isMe` where noted:

| Section | Content | Join |
|---|---|---|
| Knowledge Graph Profile | Resolved skills as `KnowledgeCard`s with NSQF level, difficulty, automation risk (Package006-owned attributes) | skill crosswalk |
| Skill Profile | Adjacent skills, certifications (30 `Certification`), providers (25 `TrainingProvider`) | `REQUIRES_SKILL`, `TRAINED_BY` |
| Recommendation Profile *(isMe only)* | Which businesses/schemes the profile unlocks, and **which claimed skills have no researched counterpart** | skill crosswalk |

> That last item is the most valuable thing on the page and the easiest to get wrong. With
> 39 of 57 suggested skills having **no Package006 counterpart**, the honest message is
> *"We don't have researched data for AC Repair yet"* — not silence, and not a fabricated
> card. It doubles as the collection backlog.

**Assessment Profile** (from the brief) has no data behind it — no assessment table, no
assessment package. Listed as a gap in `IMPLEMENTATION_ROADMAP.md` §Phase 5, not built.

**Reuse:** `ProfileView`. **Do not touch:** the `profiles` schema, the onboarding form.

---

## 4. District pages — `/district/[slug]`, `/districts/[slug]`, `/districts`, `/district`

**Existing — and duplicated.** Two route families:

- `/district/[slug]` — server component, static from `lib/districts-data.js` (**14
  districts**, rich editorial: `keyIndustries`, `emergingSectors`, `topOpportunities` with
  `fitScore`, `skillsDemand`). Full SEO: `buildDistrictMetadata`, `localBusinessJsonLd`,
  `breadcrumbJsonLd`, `AiReadableSummary`. Renders `DistrictProfile`.
- `/districts/[slug]` — a "planned workspace" shell over `DISTRICTS` +
  `data/districts.json` (**1 record**), rendering `DistrictModuleCards`.

**Inject into `/district/[slug]`** (the real one) — six sections, matching the brief:

| Section | Source | Volume | Edge |
|---|---|---:|---|
| Industries | Package004 | 78 `Industry` | `LOCATED_IN`, `PART_OF` |
| Businesses | Package004/008 | 45 + 40 | `GENERATES_EMPLOYMENT` (32) |
| Schemes | Package007 | 40 | `SUPPORTED_BY_SCHEME` (92) |
| Institutions | Package002 | 66 `Institution` | `LOCATED_IN` (121) |
| Markets | Package008 | 11 `Market` | `SELLS_TO` (**12 edges — thin**) |
| MSMEs | Package008 | 40 `MSME` | `LOCATED_IN` |

**Do not migrate the editorial content.** `districts-data.js` narrative is better writing
than anything the graph can generate. Graph data goes *below* it, clearly labelled as
researched data with provenance. The two coexist: A owns narrative, C owns facts.

**`/districts/[slug]` recommendation:** do not extend it. It is a stub over a 1-record
dataset that duplicates a better page. Redirect it to `/district/[slug]` in a separate
cleanup PR, or leave it. Extending both means maintaining both.

**Coverage caveat.** The graph has **61 districts**; the app has 14 with editorial. The 47
graph-only districts have no page. Generating thin pages for them is an SEO decision, not
an integration one — flagged, not assumed.

---

## 5. Public knowledge pages — `/skills`, `/schemes`, `/resources`, `/roadmaps`

**Existing.** Server components, `revalidate = 300`, `getKgEntities(type)` →
`kg_*` table filtered to `status = 'published'`, rendered by `PublicEntityList`.
Detail pages use `PublicEntityDetail`.

**The state today.** These tables were created with *"No seed data: content is added
gradually through the admin dashboard."* So these pages render:

> *"Schemes will appear here after admins publish them from the Government Scheme CMS."*

**Inject: nothing. Backfill instead.**

| Page | Backfill from | Rows |
|---|---|---:|
| `/schemes` | Package007 `government_schemes.csv` | **40** |
| `/skills` | Package006 `skills.csv` | **45** |
| `/resources` | Package006 `training_providers` + Package002 institutions | 25 + 66 |
| `/roadmaps` | — no package counterpart | stays admin-authored |

**This is the highest-value change in v3.0 and it touches no UI code.** The page, the
component, the styling, the SEO and the revalidation all already work. The tables are
simply empty. Add `ProvenanceLine` + `ConfidenceBadge` to `PublicEntityDetail` and the
integration is complete.

**Reuse:** `PublicEntityList`, `PublicEntityDetail`, `getKgEntities`, `kgStructuredData`.

---

## 6. Connections & network — `/connections`, `/network`, `/collaborators`, `/collaborators/[sector]`

**Existing.** `/connections` loads `connections` both directions with opportunity and
profile joins, and updates `status`. `/collaborators` reads `collaborator_profiles`
(archetype, `top_sectors`, `district`, `ep_score`).

**Inject:**

| Page | Addition | Join |
|---|---|---|
| `/connections` | On an accepted connection: shared vs complementary skills | skill crosswalk over both `profiles.skills` |
| `/collaborators/[sector]` | Which researched industries and businesses the sector maps to | sector crosswalk (**41%**) |

**This is where "Team Intelligence" actually lands.** See `FRONTEND_INTEGRATION_PLAN.md`
§9: there is no Teams feature. The accepted connections on an opportunity *are* the
working group, and `SkillGapPanel` over that set is the deliverable — real, small, and
built on tables that exist.

---

## 7. Opportunities — `/opportunities/[id]`, `/opportunities/[id]/[district]`, `/opportunities/new`

**Existing.** `opportunities` rows with `category`, `skills_needed text[]`, `location`,
`collaboration_type`, `commitment`. Public detail pages (shareable, no auth).

**Inject on `/opportunities/[id]`:**

- **`SkillGapPanel`** — `skills_needed` vs the accepted collaborators' skills
- Schemes supporting this category in this location — `SUPPORTED_BY_SCHEME`
- Researched comparables from Package004/008 — sector crosswalk

**Inject on `/opportunities/new`:** as the user types `skills_needed`, suggest crosswalked
skills. **This is the leverage point for the whole vocabulary problem** — it is where new
free text enters the system. Suggesting resolvable skills at the point of entry raises the
join rate for every future feature at near-zero cost.

**Do not touch:** the form schema, RLS, or the `unique(opportunity_id, from_user_id)`
constraint.

---

## 8. Admin — `/admin/*` (30 routes)

Two receive knowledge; the rest are analytics and unchanged.

| Route | Injection |
|---|---|
| `/admin/knowledge-graph` | Real graph stats replacing `getKnowledgeGraphStats()`'s `kg_*` counts: 647 entities, 865 relationships, 19 types, 78.05% connectivity, 142 orphans. **This page is the natural first consumer of the Python API** (`GET /graph`) — it is admin-only, low-traffic, and a failure degrades an internal dashboard rather than a user page. |
| `/admin/schemes`, `/admin/skills` | Mark projected rows read-only, with a "sourced from Package007 · sch-005" badge. Prevents R6 (admin and sync fighting over a row). |
| **New:** `/admin/stewardship` | The v2.2 review queue — 40 highest-leverage entities covering 37.2% of edge endpoints. Turns `stewardship/cli.py` into a UI and is the only path off 0% verified. |

`/admin/search-intelligence` already reads `search_events`; once unified search ships it
gains knowledge-result data for free.

---

## 9. Routes with no knowledge injection

Considered and deliberately excluded.

| Group | Routes | Why |
|---|---|---|
| Marketing & legal | `/`, `/about`, `/privacy`, `/terms`, `/get-started` | Editorial. `/` may later show live graph counts; not required. |
| Auth & onboarding | `/signin`, `/onboarding` | Auth is out of scope. The *one* exception is the skill suggestion list — see §7 and Roadmap Step 0. |
| Q&A and content | `/questions`, `/questions/[id]`, `/research/*`, `/resources/[slug]`, `/roadmaps/[slug]` | User- and admin-authored content, no graph counterpart. |
| Analytics admin | 27 of 30 `/admin/*` | Operational dashboards over Supabase analytics tables. |
| Exploratory shells | `/explore`, `/discover`, `/ai`, `/scale`, `/readiness`, `/manufacturing`, `/opportunity-radar/*`, `/business-ideas/[district]`, `/district-opportunity-index` | Overlap heavily with `/ideas` and `/district/[slug]`. **Recommend consolidation before extension** — injecting knowledge into all of them multiplies the surface to maintain. |
| Notifications | `/notifications` | Event stream. |

That last row is worth stating plainly: **the app has more route families for
"discovery" than it has distinct discovery experiences.** `/explore`, `/discover`,
`/opportunity-radar`, `/business-ideas/[district]`, `/district-opportunity-index` and
`/manufacturing` all offer variations on browsing opportunities. Consolidation is a
separate product decision, but adding knowledge to six near-duplicate surfaces would
entrench the duplication.

---

## 10. Injection summary

| Page | Sections added | New components | Blocked by | Step |
|---|---:|---|---|---|
| `/skills`, `/schemes`, `/resources` | 0 (backfill) | provenance only | — | 1 |
| `/ideas/[slug]` | 4 | 2 | sector + skill crosswalk | 6 |
| `/ideas` | 1 filter | 0 | sector crosswalk | 6 |
| `/district/[slug]` | 6 | 2 | district crosswalk (86%) | 4 |
| `/dashboard` | 4 rails | 3 | **skill crosswalk (12%)** | 5 |
| `/profile`, `/profile/[id]` | 3 | 2 | skill crosswalk | 5 |
| `/opportunities/[id]` | 3 | 1 | skill + sector crosswalk | 5 |
| `/opportunities/new` | 1 | 0 | skill crosswalk | 0 |
| `/connections` | 1 | 1 | skill crosswalk | 7 |
| `/collaborators/[sector]` | 1 | 1 | sector crosswalk | 7 |
| `/admin/knowledge-graph` | replace stats | 0 | Python API deploy | 4 |
| **New** `/admin/stewardship` | new page | 1 | — | 2 |

Every row past Step 1 depends on Step 0. That is the plan's single critical path.
