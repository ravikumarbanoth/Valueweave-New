# Missing Features — Platform v3.0, Step 2, Phase 8

Four features the platform references and does not have. Each verified absent
against every migration in the repository before being written up here.

**Migrations only. No seed data. Nothing fabricated.**
`frontend/migrations/010_missing_application_features.sql` — five tables, **zero
`INSERT` statements**, enforced by a test.

---

## 1. Why empty tables rather than plausible rows

Seeding one mentor would make the intelligence engine's `mentors` category start
returning a row that describes nobody. Seeding one event would do the same for
`events`. The user could not tell the difference between a real recommendation and a
placeholder, and the platform's entire credibility rests on that distinction being
reliable.

So the tables ship empty, the recommendation categories keep returning
`NO_DATA_SOURCE`, and the UI keeps saying *"We don't have this data yet"*. That is
the correct behaviour, and `tests/test_user_intelligence.py` asserts it holds for
every fixture.

**A fabricated mentor is an unsourced claim about a person.** That is worse than an
unsourced claim about a scheme, and this platform refuses those too.

---

## 2. `assessment_results`

**Status:** table created, empty. No assessment feature exists.

**Verified absent:** no `create table` for it in `frontend/supabase_schema.sql`, any
of `frontend/migrations/001`–`009`, or either `supabase/migrations/*`.

**What references it**
- The Step 1.5 brief lists it as an engine input
- The v3.0 brief asks for an "Assessment Profile" on the profile page

**What it blocks**

| Blocked | Consequence |
|---|---|
| Assessment Profile on `/profile` | Not rendered. No score, no placeholder. |
| Assessment-weighted readiness | `startup_readiness` composites seven scores; an eighth would need this. |

**Schema decision.** `dimensions` and `answers` are `jsonb` rather than columns
because *no assessment has been designed*. Pinning the schema to a particular
question set would be guessing at a product, and a migration per dimension is a
worse outcome than a documented jsonb shape. `score` is `0–100` so it composes with
the engine's range without a conversion someone would forget.

**To activate:** design the assessment, apply the migration, populate on completion,
then flip `INPUTS["assessment_results"]` from `MISSING` to `AVAILABLE` — one line,
and the engine's `capabilities()` output updates itself.

---

## 3. `mentor_profiles`

**Status:** table created, empty. `user_intelligence` `mentors` returns
`NO_DATA_SOURCE` for every user.

**Verified absent:** no mentor table, no `Mentor` entity type in the knowledge
graph's 19 registered types, no mentor flag on `profiles`.

**The near-miss that is not one.** `collaborator_profiles.archetype` records
self-declared archetypes. **None of them means "mentor."** Treating the closest
archetype as a mentor would be inventing a role the person never claimed — the exact
inference the engine refused to make.

**What it blocks**

| Blocked | Consequence |
|---|---|
| `mentors` recommendation category | Zero rows, with the reason shown |
| Mentor matching by expertise | Nothing to match against |

**Schema decisions, and why**

| Decision | Reason |
|---|---|
| `primary key (user_id)` — extends `profiles` | A mentor **is** a user who offered to mentor. A parallel people table would drift from `profiles` immediately. |
| `is_active boolean default false` | **Explicit opt-in.** Nobody becomes a mentor by inference from their profile. |
| `expertise_skills text[]`, free text allowed | Should be crosswalked terms where possible, but forcing a controlled vocabulary at a 22.8% resolve rate would reject real expertise. |
| `verified_by_admin default false` | Never set by an automated process, matching the platform's verification discipline. |

**To activate:** build an opt-in flow, then extend the `mentors` recommender —
`CategorySpec.no_data_reason` becomes rules.

---

## 4. `events`

**Status:** table created, empty. `user_intelligence` `events` returns
`NO_DATA_SOURCE`.

**Verified absent:** no events table, no `Event` entity type, no calendar source
anywhere in the eight packages or the application.

**What it blocks:** the `events` category, and any deadline reminder.

**Schema decisions**

| Decision | Reason |
|---|---|
| `related_entity_id text`, nullable | A scheme application deadline **is** an event a user needs. This lets one point at a knowledge entity without forcing every event to. |
| `data_source`, `source_url` | Same discipline as every package: an event with no source is one nobody should act on. |
| `event_type` constrained, includes `deadline` | The most useful event type here is a scheme closing date, not a meetup. |

**Note.** `events` is the one gap where an external source plausibly exists — scheme
portals publish deadlines. That makes it a **collection** task for the Knowledge
Engine rather than a user-generated feature, and the `data_source` column exists so
the provenance survives the trip.

---

## 5. `teams` and `team_members`

**Status:** tables created, empty. Team features fall back to accepted connections.

**Verified absent:** no `teams` table, no `team_members`, no `/teams` route. This
gap was first reported in `FRONTEND_INTEGRATION_PLAN.md` §9 during v3.0 planning and
is unchanged.

**Why `connections` cannot serve this**

| `connections` | A team needs |
|---|---|
| Opportunity-scoped | Can exist independently |
| Strictly 1:1 | N members |
| `pending`/`accepted`/`rejected` | Roles: owner, admin, member, advisor |
| No expected contribution | Who covers which skill |

Step 1.5 used accepted connections as the closest real working group and said so in
its reason text. That remains the honest approximation until these tables carry data.

**What it blocks**

| Blocked | Current fallback |
|---|---|
| Team page | None; no route exists |
| Team-level skill gap | `SkillGapPanel` over accepted connections on `/connections` |
| Team-aware recommendations | Individual only |

**Schema decisions**

| Decision | Reason |
|---|---|
| Deliberately minimal | A workspace needs invitations, roles, permissions and a lifecycle. Designing all of it with no feature to check against produces a schema the eventual product fights. |
| `covers_skills text[]` on the member | Enables a **real** team skill gap rather than the connection-level approximation. |
| `opportunity_id` nullable | Teams usually form around an existing opportunity, but not always. |
| Membership-driven RLS | A team is readable by its members; the owner manages it. Richer permissions belong with the feature. |

---

## 6. What each gap actually costs

| Feature | Tables | Rows | Blocks | Severity |
|---|---:|---:|---|---|
| `assessment_results` | 1 | 0 | Assessment Profile | Low — nothing else depends on it |
| `mentor_profiles` | 1 | 0 | 1 of 10 recommendation categories | Medium |
| `events` | 1 | 0 | 1 of 10 categories | Medium |
| `teams` + `team_members` | 2 | 0 | Team page, team skill gap | **High** — the largest single feature gap |

**Teams is the one to prioritise**, and it is a product decision rather than an
integration task: it needs invitations, roles and a lifecycle, which is more work
than everything in Step 2 combined.

---

## 7. The gap that is not in this list

**Zero of 2,299 knowledge rows have been reviewed by a human.**

No migration fixes that. It is not a missing table — it is missing *work*, and it is
the largest credibility gap in the platform. Every knowledge surface added in Step 2
carries `UnverifiedNotice` for exactly this reason, and the notice is computed so it
disappears on its own the day it stops being true.

`audit/reports/DATA_STEWARDSHIP.md` has the plan: the 40 highest-leverage entities
cover 37.2% of all edge endpoints, so a first pass is roughly two days of reading.

---

## 8. Applying the migration

```bash
psql "$DATABASE_URL" -f frontend/migrations/010_missing_application_features.sql
```

Additive and safe: five `create table if not exists`, no `alter` on an existing
table, no `drop`, no `insert`. A test asserts all four properties.

**Applying it changes nothing a user sees.** The categories stay
`NO_DATA_SOURCE` until a real feature populates them — and the engine's `INPUTS`
registry deliberately still reports `assessment_results` and `teams` as `MISSING`,
because a written migration is not a deployed, populated table. A test enforces that
too.
