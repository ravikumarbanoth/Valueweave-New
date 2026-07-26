# Page Status Report — Platform v3.0, Step 2

Every one of the **79** routes in the application, and what Step 2 did to it.

**5 pages changed. 74 unchanged.** One shared component
(`KnowledgeSearch`) was extended, which reaches every page that renders it.

---

## 1. Summary

| Phase | Route | Status |
|---|---|---|
| 2 | `/dashboard` | ✅ integrated |
| 3 | `/profile` | ✅ integrated |
| 4 | `components/platform/KnowledgeSearch` | ✅ extended (shared component, not a page) |
| 5 | `/district/[slug]` | ✅ integrated |
| 6 | `/ideas/[slug]` | ✅ integrated |
| 7 | `/connections` | ✅ integrated |
| 8 | — | ✅ migration only, no page |

**No new page was created.** The brief forbids duplicate pages, and every phase had
an existing surface to extend.

---

## 2. Phase detail

### Phase 2 — `/dashboard`

**Was:** `profiles` lookup, up to 50 `opportunities` with an owner join, 9 category
chips, text search, and a city-boost that floats nearby rows to the top.

**Now:** all of that, untouched, plus four rails above it and an `Open opportunities`
heading so the feed is still clearly labelled.

| Rail | Category | Resolves at |
|---|---|---|
| Business ideas for you | `business_ideas` | mixed — editorial + researched |
| Schemes you may qualify for | `government_schemes` | via matched businesses |
| District opportunities | `msmes` | district crosswalk, **100%** |
| Skills worth adding | `courses` | skill crosswalk, **22.8%** |

Ordered by how reliably each resolves, so the rails most likely to have content come
first. The feed query, its ranking and `OpportunityCard` are byte-identical.

### Phase 3 — `/profile`

**Was:** `profiles` + owned `opportunities`, rendered by `ProfileView`.

**Now:** `ProfileView` unchanged, with `IntelligencePanel` below it: five score
cards, a three-column skill profile, and the learning roadmap.

The most valuable element is the **third skill column** — claimed skills with no
researched counterpart, each with a reason. Roughly 50 such skills exist. Dropping
them would read as *"you have no skills"*; showing them reads as *"we haven't
collected data on yours"*, which is true and is also the collection backlog.

Owner-only by RLS (`auth.uid() = user_id`, no admin exception), not by an `isMe`
check that could be forgotten.

### Phase 4 — `KnowledgeSearch`

**Extended, not replaced.** The existing client-side search over
`lib/static-knowledge` is untouched: same input, same cards, same behaviour. A
second group appears beneath it for researched entities.

The two groups stay **visually separate** because they are different kinds of thing —
56 hand-written editorial records versus 647 sourced, confidence-scored entities.
Merging them into one ranked list would hide which is which.

Postgres `ilike`, not the Python `SearchEngine`'s four-mode ladder. The UI does not
claim parity; `docs/SEARCH_GUIDE.md` documents the difference.

### Phase 5 — `/district/[slug]`

**Was:** static from `lib/districts-data.js` (14 rich editorial profiles), with full
SEO, JSON-LD and `AiReadableSummary`.

**Now:** the same page, made `async`, with `DistrictIntelligencePanel` **below** the
editorial content.

**The narrative was not migrated.** `districts-data.js` is better writing than
anything the graph generates. The graph contributes sourced facts, labelled
`RESEARCHED KNOWLEDGE`, and the two coexist.

Six sections: Industries, MSMEs, Business opportunities, Government schemes,
Institutions, Markets. Resolution uses the Step 0 district crosswalk, which is at
**100%** — including the curated cases (`Anantapur` → `Ananthapuramu`, `Nellore` →
`Sri Potti Sriramulu Nellore`, `Vijayawada` → `NTR`).

Coverage is uneven and the panel says so: 32 `GENERATES_EMPLOYMENT` edges across 61
districts, so most districts will show institutions and industries but few
businesses.

**`/districts/[slug]` was deliberately not extended.** It is a stub over a 1-record
JSON file that duplicates a better page. Extending both would mean maintaining both.

### Phase 6 — `/ideas/[slug]`

**Was:** static from `lib/idea-library` (122 ideas), fully client-side.

**Now:** plus `BusinessKnowledgeSection`, spanning four packages:

| Package | Contributes | Via |
|---|---|---|
| 004 / 008 | comparable researched businesses | `PART_OF` |
| 007 | schemes supporting them | `SUPPORTED_BY_SCHEME` |
| 006 | skills they require | `REQUIRES_SKILL` |
| 001 | districts they employ in | `GENERATES_EMPLOYMENT` |

**Links, never merges.** An idea is editorial — written to inspire, no source, no
confidence score. A Package004/008 row is researched. Presenting them as one list
would launder the first into the credibility of the second, so each card says which
it is and the section header says it too.

11 of 22 idea sectors resolve. When one does not, the section says so explicitly.

### Phase 7 — `/connections`

**Was:** `connections` both directions with opportunity and profile joins, and a
status update.

**Now:** the join gains `skills` on both profiles, and two additions:

1. **Skill complementarity on accepted connections** — *"brings skills you don't
   have"* versus *"shared"*. Compares the two `profiles.skills` arrays directly; no
   crosswalk needed, because the question never leaves the two profiles. **This works
   today, with no migration.**
2. **Engine-ranked suggestions** — `user_recommendations` where
   `category = 'collaborators'`, replacing static sector matching.

Complementarity is shown **only once accepted**. Before that the pair is not a
working group, and the comparison would be speculation about people who have not
agreed to work together.

---

## 3. Every route

| Route | Status | Phase | Change | Components |
|---|---|---|---|---|
| `/` | unchanged | — | — | — |
| `/about` | unchanged | — | — | — |
| `/admin` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/analytics` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/announcements` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/content-opportunities` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/demand-index` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/devops` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/district-opportunity-index` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/districts` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/districts-cms` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/engagement` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/geo` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/intent` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/knowledge-graph` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/matches` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/notifications` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/opportunity-generator` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/opportunity-mapping` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/opportunity-performance` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/recommendations` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/research` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/research-performance` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/research/[id]` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/research/new` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/resources` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/retention` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/roadmaps` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/schemes` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/search-intelligence` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/seo` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/skills` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/admin/tools` | unchanged | — | Analytics/CMS over Supabase; no knowledge surface | — |
| `/ai` | unchanged | — | — | — |
| `/business-ideas/[district]` | unchanged | — | — | — |
| `/collaborators` | unchanged | — | — | — |
| `/collaborators/[sector]` | unchanged | — | — | — |
| `/connections` | **CHANGED** | Phase 7 | Skill complementarity on accepted connections + engine-ranked suggestions | `RecommendationRail` |
| `/dashboard` | **CHANGED** | Phase 2 | Four recommendation rails + not-deployed/not-computed notice | `RecommendationRail, UnverifiedNotice` |
| `/discover` | unchanged | — | — | — |
| `/district` | unchanged | — | — | — |
| `/district-opportunity-index` | unchanged | — | — | — |
| `/district/[slug]` | **CHANGED** | Phase 5 | Six sections of researched district knowledge below the editorial profile | `DistrictIntelligencePanel` |
| `/districts` | unchanged | — | — | — |
| `/districts/[slug]` | unchanged | — | — | — |
| `/explore` | unchanged | — | — | — |
| `/get-started` | unchanged | — | — | — |
| `/ideas` | unchanged | — | — | — |
| `/ideas/[slug]` | **CHANGED** | Phase 6 | Comparable researched businesses, supporting schemes, unresolved terms | `BusinessKnowledgeSection` |
| `/knowledge/[type]/[slug]` | unchanged | — | — | — |
| `/manufacturing` | unchanged | — | — | — |
| `/network` | unchanged | — | — | — |
| `/network/collaborators` | unchanged | — | — | — |
| `/notifications` | unchanged | — | — | — |
| `/onboarding` | unchanged | — | — | — |
| `/opportunities/[id]` | unchanged | — | — | — |
| `/opportunities/[id]/[district]` | unchanged | — | — | — |
| `/opportunities/new` | unchanged | — | — | — |
| `/opportunity-radar` | unchanged | — | — | — |
| `/opportunity-radar/[segment]` | unchanged | — | — | — |
| `/privacy` | unchanged | — | — | — |
| `/profile` | **CHANGED** | Phase 3 | Five scores, skill profile, learning roadmap | `IntelligencePanel, ScoreCard, SkillGapPanel` |
| `/profile/[id]` | unchanged | — | — | — |
| `/questions` | unchanged | — | — | — |
| `/questions/[id]` | unchanged | — | — | — |
| `/readiness` | unchanged | — | — | — |
| `/research` | unchanged | — | — | — |
| `/research/[slug]` | unchanged | — | — | — |
| `/resources` | unchanged | — | — | — |
| `/resources/[slug]` | unchanged | — | — | — |
| `/roadmaps` | unchanged | — | — | — |
| `/roadmaps/[slug]` | unchanged | — | — | — |
| `/scale` | unchanged | — | — | — |
| `/schemes` | unchanged | — | — | — |
| `/schemes/[slug]` | unchanged | — | — | — |
| `/signin` | unchanged | — | — | — |
| `/skills` | unchanged | — | — | — |
| `/skills/[slug]` | unchanged | — | — | — |
| `/terms` | unchanged | — | — | — |

---

## 4. Routes deliberately not changed

| Group | Count | Why |
|---|---:|---|
| `/admin/*` | 30 | Analytics and CMS over Supabase. `/admin/knowledge-graph` and a stewardship queue are named in `IMPLEMENTATION_ROADMAP.md` for a later step. |
| Marketing, legal, auth | ~10 | Editorial or authentication; auth is explicitly out of scope. |
| Q&A, research, resources, roadmaps | ~10 | User- and admin-authored content with no graph counterpart. |
| Discovery variants | 6 | `/explore`, `/discover`, `/ai`, `/scale`, `/readiness`, `/manufacturing` all offer variations on browsing opportunities. **Adding knowledge to six near-duplicate surfaces would entrench the duplication**; consolidation is a product decision, not an integration one. |
| `/districts/*` | 3 | Duplicates `/district/[slug]` over a 1-record dataset. |

That fourth row is worth restating: the application has more discovery *routes* than
distinct discovery *experiences*. This step integrated the best surface in each
family rather than all of them.

---

## 5. Verification

```
next build          exit 0 · 213/213 static pages · 0 prerender errors
tests               447 passed, 0 failed (39 new)
diff                +361 / −7 across 6 files
dependencies        unchanged
```

Baseline before any change was also exit 0 / 213 pages, so the comparison is
meaningful rather than incidental.
