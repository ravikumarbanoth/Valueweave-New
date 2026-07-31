# Supabase Schema Report

**ValueWeave v1.0 · every table declared by a migration**

Enumerated by parsing every `.sql` file in the repository. **51 tables across 3
schemas, from 15 migration files in 4 directories.**

Row counts are **"rows waiting in Git"**, not rows in production. No credential
in this environment reaches a database — `frontend/.env.local` holds
placeholders — so no live count could be taken. Where a count is unknown it says
so rather than guessing.

---

## Schema `knowledge` — the projection (10 tables)

Declared by `knowledge_sync/migrations/001_knowledge_schema.sql` and
`frontend/migrations/011_repair_vocabulary_crosswalk.sql`.
**Every one of these is empty in production: the import has never run.**

| Table | Purpose | Rows in Git | Frontend | Search | District | Opportunity | Cards |
|---|---|---:|:-:|:-:|:-:|:-:|:-:|
| `kg_entities` | every node: id, type, name, source, confidence | 647 | ✓ | **✓** | ✓ | ✓ | **✓** |
| `kg_relationships` | typed edges with provenance | 865 | ✓ | — | **✓** | ✓ | — |
| `kg_districts` | population, area, literacy, HQ | 61 | ✓ | — | **✓** | — | — |
| `kg_skills` | NSQF level, duration, demand | 45 | ✓ | — | ✓ | ✓ | **✓** |
| `kg_schemes` | ministry, subsidy, portal | 40 | ✓ | — | ✓ | ✓ | ✓ |
| `kg_businesses` | investment, employment, risk | 85 | ✓ | — | ✓ | **✓** | **✓** |
| `kg_industries` | capital and skill intensity | 24 | ✓ | — | ✓ | ✓ | ✓ |
| `kg_agriculture` | season, yield, water need | 45 | ✓ | — | ✓ | — | ✓ |
| `kg_vocabulary_map` | free text → entity id | 202 | ✓ | — | **✓** | — | — |
| `sync_runs` | import audit trail | 0 | — | — | — | — | — |

`kg_vocabulary_map` is the single bridge from a typed skill or district name to a
graph entity. Without it every district page and every skill match fails
silently — see `DISTRICT_PIPELINE_REPORT.md`.

---

## Schema `user_intelligence` — per-user computation (5 tables)

Declared by `user_intelligence/migrations/001_user_intelligence.sql`. Populated
by `user_intelligence/writer.py`, which has also never run against a database.

| Table | Purpose | Frontend |
|---|---|:-:|
| `user_skill_profile` | resolved skills and gaps | `/profile` |
| `user_business_profile` | readiness scores | `/profile`, `/dashboard` |
| `user_learning_profile` | suggested learning order | `/profile` |
| `user_activity_summary` | the row the dashboard checks first | `/dashboard` |
| `user_recommendations` | the six dashboard rails | `/dashboard` |

RLS scopes every row to `auth.uid() = user_id`, with no admin exception and no
write policy.

---

## Schema `public` — the application (36 tables)

These are live and populated. Nothing here is package data.

| Group | Tables | Used by |
|---|---|---|
| Identity & social | `profiles`, `connections`, `collaborator_profiles` | sign-in, `/collaborators`, `/network` |
| Marketplace | `opportunities`, `opportunity_interests`, `opportunity_views` | `/explore`, `/opportunities/*`, `/dashboard` |
| Content | `research_articles` | `/research` |
| Q&A and comms | `questions`, `answers`, `notifications`, `announcements`, `subscriptions`, `weekly_digests` | `/questions`, `/notifications` |
| Teams | `teams`, `team_members`, `events`, `mentor_profiles`, `assessment_results` | `/discover`, workspace |
| Analytics | `page_views`, `search_events`, `visitor_sessions`, `user_feedback`, `user_requests`, `founder_matches`, `admin_notifications` | `/admin/*`, homepage stats |
| Settings | `platform_settings` | navigation toggles |
| **CMS knowledge** | `kg_district_profiles`, `kg_skills`, `kg_schemes`, `kg_resources`, `kg_roadmaps`, `kg_roadmap_steps`, `kg_relationships`, `kg_industry_sectors`, `kg_collaborator_types` | `/skills`, `/schemes`, `/resources`, `/roadmaps` |
| Superseded | `kg_vocabulary_map` (migration 009) | none — replaced by the `knowledge` copy |

### The name collision, stated plainly

`public.kg_skills`, `public.kg_schemes` and `public.kg_relationships` are
**different tables** from `knowledge.kg_skills`, `knowledge.kg_schemes` and
`knowledge.kg_relationships`.

The `public` set is an admin CMS: hand-authored, `status = 'published'`, and
nothing populates it. The `knowledge` set is the researched projection. Two
knowledge systems with colliding names, recorded as backlog A1 and mitigated in
Step 3 by `lib/kg-fallback.js`, which serves the researched rows when the CMS is
empty — which it is.

---

## Migration inventory

| File | Tables | Note |
|---|---:|---|
| `frontend/supabase_schema.sql` | 3 | base |
| `frontend/migrations/001`–`007` | 17 | application build-out |
| — 008 — | 0 | planned, superseded by the `knowledge` schema |
| `frontend/migrations/009_vocabulary_crosswalk.sql` | 1 | **fails**: FK to a table no migration creates |
| `frontend/migrations/010_missing_application_features.sql` | 5 | |
| `frontend/migrations/011_repair_vocabulary_crosswalk.sql` | 1 | forward repair for 009 |
| `supabase/migrations/2026062000*` | 10 | CMS knowledge + settings |
| `knowledge_sync/migrations/001_knowledge_schema.sql` | 9 | the projection |
| `user_intelligence/migrations/001_user_intelligence.sql` | 5 | per-user tables |

Applying them in order **fails at 009 and is expected to** — 011 repairs it
forward without editing history. `scripts/first_deploy.sh` encodes that.

---

**Companions:** `KNOWLEDGE_ARCHITECTURE_AUDIT.md` · `PACKAGE_TO_DATABASE_MAPPING.md`
