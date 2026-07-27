# First Deployment Checklist

**Every step: command · expected output · validation · rollback.**

Print it. Tick every box. Record the commit before you start:
`git rev-parse HEAD` → `________________`

Narrative and reasoning: `PRODUCTION_DEPLOYMENT_GUIDE.md`. This file is the sequence.

**Three steps fail in ways that are not obvious — 4, 6 and 7. Two of them fail silently.**

---

## 1 · Clone and install

| | |
|---|---|
| **Command** | `git clone <repo> && cd Valueweave-New && cd frontend && npm ci && cd ..` |
| **Expected** | `added N packages` · no `ERESOLVE` |
| **Validation** | `node --version` ≥ 18 · `python3 --version` ≥ 3.11 |
| **Rollback** | `rm -rf Valueweave-New` |

- [ ] Clone complete · commit recorded

---

## 2 · Baseline test run

| | |
|---|---|
| **Command** | `python3 tests/run_all.py --quiet` |
| **Expected** | `TOTAL 478 0 0 0 PASS` — 13 suites |
| **Validation** | 0 fail, 0 error, 0 skip |
| **Rollback** | n/a — nothing changed |

**A failure here stops the deployment.** Every later step assumes the clone is sound.

- [ ] 478 passing

---

## 3 · Environment

| | |
|---|---|
| **Command** | `set -a; . ./.env.deploy; set +a` |
| **Expected** | no output |
| **Validation** | `echo "${SUPABASE_URL:?}${DATABASE_URL:?}" >/dev/null && echo ok` |
| **Rollback** | `unset SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY DATABASE_URL` |

- [ ] `.env.deploy` gitignored
- [ ] `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_BASE_URL`, `ADMIN_EMAILS` set in Vercel (Production **and** Preview)
- [ ] `SUPABASE_SERVICE_ROLE_KEY` **not** in Vercel

> The service role key bypasses RLS. Operator shell and CI secret only.

---

## 4 · ⚠️ Patch migration 009 — it cannot apply as committed

| | |
|---|---|
| **Problem** | 009 declares `references public.kg_entity_registry(...)`; **no migration creates that table** |
| **Symptom** | `ERROR: relation "public.kg_entity_registry" does not exist` |
| **Command** | `sed 's| references public\.kg_entity_registry(global_entity_id) on delete restrict||' frontend/migrations/009_vocabulary_crosswalk.sql > /tmp/009_patched.sql` |
| **Expected** | file written, one line shorter in content |
| **Validation** | `grep -c kg_entity_registry /tmp/009_patched.sql` → **0** |
| **Rollback** | `rm /tmp/009_patched.sql` — the committed file is untouched |

Integrity is preserved by 009's own `kg_vocab_resolution_is_coherent` CHECK.

**Do not create an empty `kg_entity_registry` instead.** That would be a third entity
table in `public`, alongside the CMS `kg_*` tables and the real `knowledge.kg_entities`.

- [ ] Patched file produced · `grep` returns 0

---

## 5 · Migrations

| | |
|---|---|
| **Command** | The 14 `psql -f` lines in `PRODUCTION_DEPLOYMENT_GUIDE.md` §5.1, **substituting `/tmp/009_patched.sql` for 009** |
| **Expected** | `CREATE TABLE` / `CREATE POLICY` / `ALTER TABLE` · **no `ERROR`** |
| **Validation** | see below |
| **Rollback** | see below |

```sql
select count(*) from pg_tables
 where schemaname in ('public','knowledge','user_intelligence');          -- 50
select tablename from pg_tables
 where schemaname in ('public','knowledge','user_intelligence')
   and rowsecurity = false;                                               -- 0 rows
```

```sql
-- rollback: the two derived schemas are safe to drop; they hold only projections
drop schema knowledge cascade;
drop schema user_intelligence cascade;
-- public is NOT safe to drop once real users exist. Restore from a Supabase backup.
```

- [ ] 50 tables · [ ] 9 in `knowledge` · [ ] 5 in `user_intelligence` · [ ] RLS on all

---

## 5b · Decide about the 500 seeded opportunities

| | |
|---|---|
| **Command** | label them, **or** skip `003_seed_opportunities.sql` |
| **Expected** | either recorded |
| **Validation** | `select count(*) from public.opportunities where created_by='system_seed';` |
| **Rollback** | `delete from public.opportunities where created_by='system_seed';` |

Synthetic, no provenance, and the main content of `/dashboard`.

- [ ] ☐ labelled ☐ omitted — decided by: ____________

---

## 6 · ⚠️ Expose the schemas — silent if skipped

| | |
|---|---|
| **Command** | Dashboard → Settings → API → **Exposed schemas** → add `knowledge, user_intelligence` → Save |
| **Expected** | both listed after save |
| **Validation** | §12 diagnostic — SQL returns rows **and** the app shows them |
| **Rollback** | remove them; the app returns to empty states |

**No error is produced when this is missed.** Every query fails, `safe()` returns `[]`,
and the application looks exactly as it did before deployment.

- [ ] `knowledge` exposed · [ ] `user_intelligence` exposed · [ ] saved

---

## 7 · ⚠️ Load the vocabulary crosswalk — no loader exists

| | |
|---|---|
| **Command** | the three `\copy` statements in `PRODUCTION_DEPLOYMENT_GUIDE.md` §7 |
| **Expected** | `COPY 33` · `COPY 22` · `COPY 147` |
| **Validation** | `select term_kind, count(*) from public.kg_vocabulary_map group by 1;` → 33 / 22 / 147 |
| **Rollback** | `truncate public.kg_vocabulary_map;` |

Then resolve the schema mismatch — the table is in `public`, the client queries
`knowledge`:

```sql
alter table public.kg_vocabulary_map set schema knowledge;   -- re-grant 009's policies after
```

**Without both, every district and skill a user types fails to resolve.**

- [ ] 202 rows loaded · [ ] table moved **or** code fix scheduled

---

## 8 · Pre-sync checks — no credentials needed

| | |
|---|---|
| **Command** | `python3 knowledge_sync/generate_migration.py --check && python3 -m knowledge_sync plan` |
| **Expected** | `001_knowledge_schema.sql: matches the specs` · `1812` rows · `0 error(s), 4 warning(s)` |
| **Validation** | exactly 4 warnings, all `V6-OWNERSHIP … governed by ADR-005` |
| **Rollback** | n/a — writes nothing |

**Any error, or a fifth warning, stops the deployment.**

- [ ] DDL matches · [ ] 1,812 rows · [ ] 4 governed warnings

---

## 9 · Sync one table

| | |
|---|---|
| **Command** | `python3 -m knowledge_sync sync --table kg_schemes --target supabase` |
| **Expected** | `40 inserted` |
| **Validation** | `select count(*) from knowledge.kg_schemes;` → **40**; `verification_status` = `VST-NEEDS_REVIEW` |
| **Rollback** | `python3 -m knowledge_sync rollback <run_id>` |

- [ ] 40 rows · [ ] provenance columns populated

---

## 10 · Sync everything, twice

| | |
|---|---|
| **Command** | `python3 -m knowledge_sync sync --target supabase` — **then run it again** |
| **Expected** | 1st: `1812 inserted` · 2nd: **`0 inserted, 0 updated, 1812 skipped`** |
| **Validation** | `select count(*) from knowledge.kg_entities;` → 647 |
| **Rollback** | `python3 -m knowledge_sync snapshots` → `rollback <run_id> --dry-run` → `rollback <run_id>` |

**The second run is the step that matters.** Updates on an unchanged repository mean a
value round-trips differently through Postgres than through the content hash. Diagnose
before scheduling the sync.

- [ ] 1,812 rows · [ ] **second run 0/0** · [ ] `run_id` recorded: ____________

---

## 11 · ⚠️ Per-user intelligence — no writer exists

| | |
|---|---|
| **Command** | `python3 -m user_intelligence capabilities` |
| **Expected** | 8 scores, 10 categories, `mentors`/`events` = `NO DATA` |
| **Validation** | `python3 -m user_intelligence run --fixture resolving --explain` produces a rule trace |
| **Rollback** | `truncate` the five `user_intelligence` tables |

**There is no `--target supabase`.** The five tables stay empty until a pipeline is
built (`PRODUCTION_DEPLOYMENT_GUIDE.md` §9). `/dashboard` shows `NOT_COMPUTED` and says
so — correct behaviour, not a failure.

- [ ] Engine runs · [ ] `NOT_COMPUTED` accepted for launch, **or** pipeline built

---

## 12 · Authentication and admin

| | |
|---|---|
| **Command** | `update public.profiles set is_admin=true where email='<you>';` |
| **Expected** | `UPDATE 1` |
| **Validation** | `/admin` loads for you, redirects for a signed-out browser |
| **Rollback** | `update public.profiles set is_admin=false where email='<you>';` |

- [ ] Google sign-in → `/onboarding` → `/dashboard`
- [ ] Second sign-in goes straight to `/dashboard`
- [ ] `NODE_ENV=production` confirmed *(dev opens all 33 admin routes)*

---

## 13 · Build and deploy

| | |
|---|---|
| **Command** | `cd frontend && npm ci && npm run build` |
| **Expected** | `exit 0` · `✓ Generating static pages (214/214)` · **0 prerender errors** |
| **Validation** | build succeeds **without** database access |
| **Rollback** | Vercel → Deployments → previous → Promote |

- [ ] 214/214 · [ ] 0 prerender errors · [ ] deployed · [ ] previous deployment id recorded

---

## 14 · Verify

| | |
|---|---|
| **Command** | `POST_DEPLOYMENT_VALIDATION.md` |
| **Expected** | 9 surfaces render; each empty state names its cause |
| **Validation** | both smoke profiles — resolving **and** non-resolving skills |
| **Rollback** | §15 |

- [ ] Validation complete · [ ] result recorded

---

## 15 · Rollback ladder

Least to most destructive. **Stop at the first that works.**

| # | Situation | Action | Loses |
|---|---|---|---|
| 1 | Frontend bug | Vercel → promote previous | nothing |
| 2 | Bad sync | `knowledge_sync rollback <run_id>` | that run |
| 3 | Projection wrong | `drop schema knowledge cascade` → re-migrate → `sync --full` | nothing — it is derived from Git |
| 4 | Intelligence wrong | `drop schema user_intelligence cascade` → re-migrate | computed rows, recomputable |
| 5 | Schema mistake in `public` | **Supabase point-in-time restore** | everything after the restore point |

> **Levels 1–4 lose nothing that is not derived from Git.** Level 5 is the only one that
> touches user data, and it is the only one that needs a decision rather than a command.

**Rehearse level 2 once** on the `kg_schemes` sync from step 9, before real users exist.

- [ ] Level 2 rehearsed

---

## Sign-off

| | |
|---|---|
| Deployed by | |
| Date | |
| Commit | |
| 009 patched | ☐ |
| Schemas exposed | ☐ |
| Crosswalk loaded (202) | ☐ |
| Second sync reported 0/0 | ☐ |
| Intelligence pipeline | ☐ built ☐ deferred |
| Seeded opportunities | ☐ labelled ☐ omitted |
| Rollback rehearsed | ☐ |
| **Go / No-Go** | |
