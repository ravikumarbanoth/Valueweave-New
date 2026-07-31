# Placeholder Removal Report

**ValueWeave Platform v3.0 · Step 4 — Frontend Knowledge Activation**

Every placeholder found, what happened to it, and why. Counts are of **rendered
elements** — what a user meets — not of string literals in source. A `"Coming
Soon"` chip inside a `.map()` is one literal and however many cards the array
holds, and the second number is the one that matters.

---

## Summary

| | |
|---|---|
| Placeholder elements found | **99** |
| Removed and replaced with live knowledge | **93** |
| Relabelled `NOT_AVAILABLE_YET` / `NO_DATA_SOURCE` with a named dependency | **6** |
| Remaining `"Coming Soon"` / `"Planned"` in rendered output | **0** |
| Mock knowledge datasets still surfaced to users | **0** |
| Files changed | 26 · 1 deleted |

The 6 that were relabelled rather than removed are the homepage roadmap modules.
None has a data source in any package, and the brief's instruction for that case
is explicit: change the message and include the actual dependency.

---

## 1 · Discovery

Searched `frontend/app` and `frontend/components` (excluding `admin/`, which is
operator tooling) for the brief's ten patterns.

| Pattern | Instances | Files |
|---|---:|---|
| `Coming Soon` / `coming soon` | 7 literals → **32 rendered** | 5 |
| `Planned` chip | 1 literal → **6 rendered** | 1 |
| `comingSoon` boolean prop | 2 | 2 |
| Placeholder module dashboards | **65 rendered** | 1 route |
| Static JSON knowledge datasets | 7 files, 56 records | `frontend/data/` |
| Mock arrays surfaced as knowledge | 2 modules | `static-knowledge.js`, `radar-data.js` |
| Hardcoded statistics | 2 fields × 40 rows | `radar-data.js` |
| `Future` / `TODO` / `FIXME` | 0 | — |
| `Knowledge Base Coming Soon` | 0 | — |
| `No Data` | 0 (already handled by `KnowledgeCardGrid`) | — |

**Nothing matched `TODO` or `FIXME`.** That is unusual and worth recording: the
placeholders in this codebase were deliberate product decisions with chips
attached, not forgotten work.

---

## 2 · The inventory, item by item

### 2.1 Module dashboards — 25 elements

`components/platform/ModuleDashboard.jsx` rendered a `"Coming Soon"` chip on
every expansion card and a fixed amber panel reading *"This dashboard is
intentionally prepared for future workflows without adding database tables, APIs,
AI logic, or business rules yet."*

Five pages used it: `/readiness`, `/manufacturing`, `/scale`, `/ai`, `/network`.
**20 cards + 5 panels.**

That sentence was true when written and false by the time this step ran. Of the
20 cards, **11 described capabilities the knowledge graph already held**.

| Module | Card | Before | After | Records |
|---|---|---|---|---:|
| readiness | Skill Assessment | Coming Soon | **LIVE** → `/knowledge?type=skill` | 45 |
| readiness | Training | Coming Soon | **LIVE** → `/knowledge?type=certification` | 30 |
| readiness | Learning Paths | Coming Soon | **LIVE** → `/knowledge?type=provider` | 25 |
| readiness | Mentors | Coming Soon | `NO_DATA_SOURCE` | 0 |
| manufacturing | Product Discovery | Coming Soon | **LIVE** → `/knowledge?type=business` | 45 |
| manufacturing | Machinery | Coming Soon | **LIVE** → `/knowledge?type=machinery` | 69 |
| manufacturing | Production | Coming Soon | **LIVE** (raw materials) → `?type=material` | 21 |
| manufacturing | Factory Planning | Coming Soon | `NO_DATA_SOURCE` | 0 |
| scale | Export | Coming Soon | **LIVE** → `/knowledge?type=export` | 29 |
| scale | Quality | Coming Soon | **LIVE** (markets) → `?type=market` | 11 |
| scale | Automation | Coming Soon | **LIVE** (capital) → `?type=bank` | 21 |
| scale | Robotics | Coming Soon | `NO_DATA_SOURCE` | 0 |
| network | Co-founders | Coming Soon | **LIVE** → `/collaborators` | live table |
| network | Institutions | Coming Soon | **LIVE** → `/knowledge?type=institution` | 66 |
| network | Experts | Coming Soon | `NO_DATA_SOURCE` | 0 |
| network | Investors | Coming Soon | `NO_DATA_SOURCE` | 0 |
| ai | Knowledge Graph | Coming Soon | **LIVE** → `/knowledge` | 647 |
| ai | Recommendations | Coming Soon | **LIVE** → `/dashboard` | rule engine |
| ai | AI District Advisor | Coming Soon | `NOT_AVAILABLE_YET` | 0 |
| ai | AI Manufacturing Advisor | Coming Soon | `NOT_AVAILABLE_YET` | 0 |

The five amber panels became per-module dependency statements naming what each
module is actually waiting on.

> **The `/scale` finding is the one worth reading twice.** Package001_Geography
> holds **29 ExportCountry entities** — the destinations researched businesses
> already sell to. They were not merely unwired: `ExportCountry` was missing from
> `TYPE_BY_URL` in `lib/knowledge.js`, so `hrefFor()` returned a search URL for
> every one of them. The data was synced, the page said "Coming Soon", and no
> route existed to prove otherwise.

### 2.2 District detail — 65 elements

`/districts/[slug]` served one slug (`medak`) from `data/districts.json` and
**thirteen** from a `ModuleDashboard` promising a district overview, industries,
resources and schemes. **13 × (4 cards + 1 panel) = 65 placeholder elements**,
against a graph holding **61 researched districts** with population, area,
literacy, headquarters, and everything linked to each one.

Replaced with `DistrictIntelligencePanel` — the component `/district/[slug]`
already used. No second component was written. `app/districts/components/
DistrictModuleCards.jsx` was deleted.

### 2.3 Homepage — 8 elements

| Element | Before | After |
|---|---|---|
| "Explore Knowledge" grid | 6 hard-coded slugs over 56 static JSON records, under the banner **"STATIC KNOWLEDGE LAYER · Early static knowledge previews"** | `featuredByType()` — one live entity per type with its confidence, source package and category count |
| "Future Infrastructure Roadmap" | 6 modules with a `Planned` chip | 6 `NO_DATA_SOURCE` cards, each naming the package that would have to exist |
| AI Intelligence Layer card | `comingSoon: true` | `status="NOT_AVAILABLE_YET"` |
| Open Opportunities stat | empty label `"Coming soon"` | `"None open yet"` — the feature is live; zero is a fact about the marketplace |
| Explainer video | `"Video coming soon"` | `"Not available yet"` + where to set one |

### 2.4 Search — the whole result set

`KnowledgeSearch` searched two things and put the weaker one first. The primary
grid — filled before you typed anything, sitting at the top — came from
`lib/static-knowledge.js`: **56 hand-written records with no source, no
confidence, no provenance**. The **647 sourced entities** appeared underneath, as
a secondary group, and only after two characters.

All seven static types have researched counterparts. The static group is gone;
the projection is the search. Type filters went 8 → 10.

### 2.5 Mock knowledge datasets

| Module | Records | Verdict |
|---|---:|---|
| `lib/static-knowledge.js` | 56 | **Demoted.** No longer displayed anywhere. Retained only as a URL shim for 56 indexed detail pages, which now open with a "superseded" notice. `featuredKnowledge` and `futureInfrastructureModules` deleted. |
| `frontend/data/*.json` | 56 | Read only by the shim above. |
| `lib/radar-data.js` | 40 | **Kept, labelled.** Editorial curation with real links into the Idea Library. Its `fitScore: 91` / `demandScore: 93` are hand-assigned and rendered as `/100` badges with progress bars — visually identical to computed confidence. Both radar pages now say so and link to sourced figures. |
| `lib/districts-data.js` | 14 | **Kept.** Editorial narrative, better writing than the graph generates. Now leads `/districts` with 47 researched districts listed below it. |
| `lib/idea-library/` | — | **Kept and enriched.** Phase 10 says do not remove editorial content. |
| `lib/opportunity-templates.js` | — | **Kept.** Admin generator tooling, not user-facing knowledge. |

---

## 3 · What was NOT removed, and why

The brief lists four capabilities to relabel rather than delete. All four survive:

| Capability | Where | Status | Dependency named |
|---|---|---|---|
| Mentors | `/readiness`, `/network` | `NO_DATA_SOURCE` | No package holds mentors. Package002 has 66 institutions and the marketplace has real people; neither is a mentor record. |
| Events | `/network` | `NO_DATA_SOURCE` | No package holds events. |
| Startup / team workspace | `/network` | `NOT_AVAILABLE_YET` | Communities and workspace not built. |
| AI advisors | `/ai` | `NOT_AVAILABLE_YET` | No model, inference or prompt layer exists in the repository. |

**`/ai` deserves a note.** It would have been easy to make this page look
activated: the platform does have a recommendation engine. It is rule-based on
purpose — `user_intelligence` fires deterministic rules and every recommendation
carries the rule that produced it. Presenting that as an "AI advisor" would have
been the single most misleading change available in this step. The page now names
it as what it is and keeps all four advisors unavailable.

---

## 4 · Regression protection

`tests/test_frontend_activation.py` — **33 tests**, registered as the
`frontend_activation` suite.

`PlaceholderRemovalTest` scans every non-admin `.js`/`.jsx` under `app/` and
`components/` for `Coming Soon`, a bare `Planned` chip, and `Knowledge Base
Coming`. It runs against **comment-stripped source**, so a file may still explain
the placeholder it removed — several do, and that history is worth keeping — but
may not render one.

Getting that helper right took two attempts. The first stripped only `//` line
comments and immediately flagged `HomeVideoEmbed.jsx`, whose `{/* … */}` JSX
comment documents the phrase it had just deleted. The fix was to strip block
comments too, rather than reword the comment: a future developer writing a
legitimate JSX note would have hit the same false positive.

---

**Companions:** `KNOWLEDGE_BINDING_REPORT.md` · `LIVE_PAGE_REPORT.md` ·
`REMAINING_DEPENDENCIES.md` · `USER_EXPERIENCE_COMPLETION.md`
