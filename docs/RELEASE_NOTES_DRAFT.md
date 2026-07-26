# ValueWeave v1.0 — Release Notes (DRAFT)

> **DRAFT — not for publication.** Version 1.0 is assessed **CONDITIONAL GO** for a
> narrow pilot only (`VERSION1_READINESS_REPORT.md`). Publishing these notes as-is
> would announce a general availability that has not been earned. Four conditions
> (§Before this ships) must close first, and several figures below are written to be
> re-measured on the day of release rather than copied.

**Target release:** v1.0.0 · **Assessed at:** commit `6fec48a` · **Scope:** pilot,
Telangana + Andhra Pradesh

---

## What ValueWeave is

A knowledge platform for entrepreneurship in Telangana and Andhra Pradesh. It holds
researched, source-traced information about districts, skills, government schemes,
businesses, crops and MSMEs, and uses it to give a signed-in user reasoned
recommendations — not generated text.

**Every claim traces to a public source.** Every recommendation states why it was made,
which entities support it, and how much the underlying data can be trusted.

---

## Highlights

### A knowledge base, not a content library

| | |
|---|---:|
| Researched rows | **2,299** |
| Datasets | **77** across 8 packages |
| Graph entities | **647** in 19 types |
| Relationships | **865** in 15 types |
| Districts | **61** — all 33 Telangana, 28 Andhra Pradesh |

Every row carries six provenance columns: source, dataset, row id, collection date,
confidence and verification status. Nothing is generated; where a fact could not be
confirmed from a public source, the cell says `PENDING_VERIFICATION` instead of
guessing.

### Recommendations you can audit

Ten categories, driven by **21 rules over the knowledge graph** — no AI, no model, no
randomness. Given the same inputs the engine produces a byte-identical result hash, so
a recommendation a user acted on months ago can still be explained.

Every recommendation carries:

- **A reason** in plain language
- **Supporting entities** — the graph nodes and edges behind it
- **A match score** (fit to you) *and* a **confidence score** (trust in the data),
  kept deliberately separate, because a perfect match on weak data is a real situation
  one number cannot describe
- **A timestamp** and the rules version that produced it

### Eight profile scores

Skill profile, business readiness, learning roadmap, district opportunity,
collaboration, AI readiness, funding readiness, and a composite startup readiness.

**A score can be absent, and that means something specific.** If an input does not
exist, the score is `—`, not `0`. Telling you your district has no opportunity when the
truth is that we have not collected it yet would be the easiest way to mislead you, and
the distinction is enforced in the type system rather than left to a convention.

### Search across researched knowledge

Search reaches the knowledge graph as well as the platform's own content, and results
from research are shown as a **separate group** so you always know which is which.

### Collaborators and connections

Find collaborators by real skill overlap, sector and district. Requests, acceptance and
1:1 connections, with skills visible only after a connection is accepted.

### The "Discover Yourself" assessment

A 7-minute assessment mapping personality, sector interest, budget and district to an
entrepreneur archetype, founder role and suited business ideas.

---

## Honest limitations

Read this section. It is not boilerplate — it is the part of the release that respects
your time.

### None of the knowledge has been reviewed by a human yet

**0 of 2,299 rows.** Every row was collected from a public source and machine-validated
for structure, provenance and internal consistency. **None has been read by a person
who knows the domain.**

Every page showing researched data carries a notice saying so. The notice is computed
from the data, so it will disappear on its own the day it stops being true.

Treat this release as a well-sourced starting point, not a verified answer. **Please
tell us when it is wrong** — there is a report link on every provenance line.

### Coverage is uneven, and heavily concentrated

Knowledge is deepest in **Hyderabad**, then Guntur, Tirupati and Visakhapatnam. It is
thin in most other districts.

| Coverage | Districts |
|---|---:|
| Strong | 1 |
| Moderate | 3 |
| Limited | 12 |
| Minimal | **45** |

If you are outside the first sixteen, expect fewer recommendations. That is a gap in
our research, not a statement about your district.

### Your skills may not resolve yet

The platform knows **45 skills** in depth. If you enter a skill outside that set, it
will say so plainly rather than guessing at a near match — and you will see fewer
recommendations as a result.

Currently **about 1 in 4** skills entered during onboarding matches a researched skill.
Trades (welding, electrical, plumbing, food processing, tailoring) are well covered.
Commercial and digital skills (accounting, digital marketing, data entry, graphic
design, teaching) are **not yet** — collecting them is the top priority for v1.1, and
the skill you enter is recorded as a request.

### Features that do not exist in this release

Stated plainly rather than hidden behind a "coming soon":

| Not in v1.0 | Status |
|---|---|
| **Team workspaces** | Not built. Schema exists; the feature does not |
| **Startup workspace** | Not built |
| **Mentor matching** | No mentor data exists. The category tells you so rather than showing a guess |
| **Event and deadline tracking** | No event data exists. Same |
| **AI advisory** (`/ai`) | Reserved. No AI features are implemented |
| **Manufacturing, Readiness, Scale** modules | Shells for future work |

Where a feature has no data, the platform says *"we don't have this data yet"* and names
the reason. It never fills the gap with something plausible.

### Healthcare data is not yet connected

Package003_Healthcare — 146 rows on government hospitals, medical colleges, regulatory
bodies and health insurance schemes — is researched and released but **not yet wired
into the knowledge graph**, so it does not appear in search or recommendations. Planned
for v1.1.

### Half the government schemes are not yet linked

40 schemes are in the knowledge base; **19** are connected to districts, businesses or
skills. Recommendations traverse those links, so the other 21 are searchable but will
not be recommended until they are connected. Planned for v1.1.

### Example opportunities are labelled

Some opportunities in the feed are **illustrative examples** to show the format, not
verified openings. They are labelled. Everything drawn from the knowledge base carries
a source line; anything without one is not a research finding.

*(Release blocker H1 — confirm labelling is applied before publishing this section.)*

---

## For administrators

- 33 admin routes: research CMS, analytics, engagement, retention, opportunity
  management, knowledge-graph inspection
- Admin access is `profiles.is_admin`, with an `ADMIN_EMAILS` bootstrap allowlist
- **RLS is the security boundary**, not the UI. All 50 tables have row-level security;
  85 policies
- Neither projected schema (`knowledge`, `user_intelligence`) has **any** write policy.
  Projected data cannot be edited in the console — it is derived from Git, and the next
  sync would revert an edit anyway
- No admin can read a user's computed intelligence. `user_intelligence` is gated on
  `auth.uid() = user_id` with **no admin exception**

---

## For operators

### Architecture

```
packages/ + knowledge_graph/     Git — the single source of truth
        │  knowledge_sync
        ▼
Supabase `knowledge` schema      8 tables, 1,812 rows, read-only
        │  user_intelligence engine
        ▼
Supabase `user_intelligence`     5 tables, per-user, RLS-isolated
        │  supabase.from(...)
        ▼
Next.js 14 App Router            no separate backend service
```

**Git is canonical.** Supabase is a read-optimised projection. Never edit package data
in Supabase — fix it in the CSV, commit, and let the sync propagate it.

### Deployment

`DEPLOYMENT_CHECKLIST.md`, in order, all of it. Two steps fail silently and are called
out for that reason:

1. **`knowledge` and `user_intelligence` must be added to Supabase's exposed schemas.**
   Skip it and every knowledge read returns empty with no error anywhere.
2. **`kg_vocabulary_map`'s schema mismatch must be resolved** or vocabulary resolution
   silently returns nothing.

### Operations

| | |
|---|---|
| Sync | `python3 -m knowledge_sync plan` then `sync` — incremental, idempotent |
| Rollback | Per-run, snapshot-based, always reversible |
| Steady state | `plan` reporting all-skip |
| Full reset | `drop schema knowledge cascade` — safe; it holds only a projection |

`OPERATIONS_GUIDE.md` is written for whoever is on the other end of a failed sync at an
inconvenient hour.

---

## Quality

| | |
|---|---:|
| Automated tests | **447** — 0 failures, 0 errors, 0 skips |
| Build | exit 0, **213/213** static pages, 0 prerender errors |
| Tables with RLS | **50 of 50** |
| Fabricated knowledge rows | **0** — enforced by test |
| Runtime dependencies added by the knowledge integration | **0** |

Tests cover the knowledge engine, graph integrity, ownership governance, search, data
stewardship, the sync framework, the intelligence engine, the vocabulary crosswalk, the
API and frontend integration. Several assert absences rather than behaviours — no
randomness in the engine, no AI dependency, no database access from the rule layer, no
write path into a user table.

---

## Known issues

| # | Issue | Workaround |
|---|---|---|
| 1 | `/skills`, `/schemes`, `/resources`, `/roadmaps` read the admin CMS and appear empty even though researched skills and schemes exist | Use search or the dashboard rails. Fix in v1.1 |
| 2 | District detail pages exist for 14 of 61 districts | Others appear in search and recommendations |
| 3 | Assessment results may not persist unless explicitly saved while signed in | Sign in first, then use *Join the collaborator marketplace* |
| 4 | Dashboard and profile refetch on every visit | None; noticeable on slow connections |
| 5 | Search is a substring scan without a trigram index | None needed at current data volume |
| 6 | `next@14.2.15` carries a published advisory | Framework upgrade planned |

---

## What v1.1 will address, in priority order

1. **~40 commercial and digital skills** — the single change that most improves
   recommendations for most users
2. **Human review** of the highest-leverage entities
3. **Connect the 21 unlinked government schemes**
4. **Healthcare data into the graph** — 146 researched rows currently invisible
5. **One knowledge system**, not two — resolve `/skills` and `/schemes` reading an
   empty CMS while the graph holds the answer
6. **District pages for all 61**
7. **Team workspaces** — if the pilot asks for them

Items 1–3 come straight from measurement. Item 7 does not, deliberately: it is 8 days
of work and nobody has yet confirmed users want it. The pilot decides.

---

## Before this ships

Four conditions from `VERSION1_READINESS_REPORT.md` §10 — **7.5 to 9.5 days**:

| # | Condition | Status |
|---|---|---|
| 1 | Deploy: migrations, exposed schemas, full sync, engine run, OAuth, admin, vocabulary fix | ☐ |
| 2 | Human-review the top 40 entities | ☐ |
| 3 | Complete Package006, then collect ~40 backlog skills with edges | ☐ |
| 4 | Label or remove the 500 illustrative opportunities | ☐ |

And re-measure before publishing: skill resolve rate, reviewed-row count, district
coverage bands, test count, build result. **Do not copy this draft's figures into a
published release** — the whole point of the platform is that numbers are measured
rather than asserted, and a release note is no exception.

---

## Thanks

To the pilot cohort — 100 students, 10 faculty, 20 entrepreneurs — who are using
something incomplete and telling us where it falls short. **The skill you typed that we
did not recognise is the most useful thing you gave us.**
