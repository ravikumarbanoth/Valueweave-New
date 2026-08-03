# First Deployment Checklist

**Every step: command · expected output · validation · rollback.**

Print it. Tick every box. Record the commit before you start:
`git rev-parse HEAD` → `________________`

Narrative and reasoning: `PRODUCTION_DEPLOYMENT_GUIDE.md`. This file is the sequence.

**Step 6 fails silently.** It is the only step here that a script cannot take for you, and
the only one where a mistake produces no error anywhere.

### The scripted path

`scripts/first_deploy.sh` executes steps 5, 7, 8, 10 and 14 in order, stopping at a manual
gate before step 6. Every script honours `DRY_RUN=1`:

```bash
DRY_RUN=1 scripts/first_deploy.sh     # print every command, touch nothing
scripts/first_deploy.sh               # for real
```

Work through this checklist either way — the scripts print the same step names, and the
boxes below are what you are signing off on regardless of who typed the commands.

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
| **Expected** | `TOTAL 530 0 0 0 PASS` — 14 suites |
| **Validation** | 0 fail, 0 error, 0 skip |
| **Rollback** | n/a — nothing changed |

**A failure here stops the deployment.** Every later step assumes the clone is sound. The
`deployment` suite (50 tests) covers the writer, the scripts and migration 011 — the
machinery this checklist runs.

- [ ] 530 passing

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

## 4 · Understand migration 009 before you run it

| | |
|---|---|
| **Problem** | 009 declares `references public.kg_entity_registry(...)`; **no migration creates that table** |
| **Symptom** | `ERROR: relation "public.kg_entity_registry" does not exist` |
| **Fix** | `frontend/migrations/011_repair_vocabulary_crosswalk.sql`, applied in step 5 |
| **Expected** | **009 fails. That is correct.** 011 then creates the table in `knowledge`, without the FK |
| **Validation** | after step 5: `\dt knowledge.kg_vocabulary_map` exists; 0 foreign keys on it |
| **Rollback** | `drop table knowledge.kg_vocabulary_map;` — the `public` copy, if any, is untouched |

**009 is not edited and never will be.** It stays in history as it shipped; 011 moves
forward from whatever state the database is actually in, and handles all four of them
(009 never applied · 009 applied · 011 already applied · both copies present).

011 also fixes the quieter half of the defect: 009 put the table in `public` while
`lib/knowledge.js` reads it through a `knowledge`-scoped client, so even a *successful* 009
would have produced a table nothing could read.

**Do not create an empty `kg_entity_registry` instead.** That would be a third entity
table in `public`, alongside the CMS `kg_*` tables and the real `knowledge.kg_entities`.

- [ ] 011 read and understood · [ ] 009 left unmodified

---

## 5 · Migrations

| | |
|---|---|
| **Command** | The 15 `psql -f` lines in `PRODUCTION_DEPLOYMENT_GUIDE.md` §5.1, in order — or `scripts/first_deploy.sh` |
| **Expected** | `CREATE TABLE` / `CREATE POLICY` / `ALTER TABLE` · **009 errors, nothing else does** |
| **Validation** | see below |
| **Rollback** | see below |

`first_deploy.sh` expects 009 to fail and continues to 011. **Any other migration failing
stops it**, and should stop you.

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

## 7 · Load the vocabulary crosswalk

| | |
|---|---|
| **Command** | `scripts/load_crosswalk.sh` |
| **Expected** | `district 33` · `sector 22` · `skill 147` · total **202** |
| **Validation** | `select term_kind, count(*) from knowledge.kg_vocabulary_map group by 1;` → 33 / 22 / 147 |
| **Rollback** | `truncate knowledge.kg_vocabulary_map;` then re-run the script |

Each CSV is staged into a temp table and merged with `on conflict … do update`, so a
re-run corrects drift instead of duplicating. The script **fails unless the final count is
exactly 202** — a half-loaded crosswalk resolves some terms and not others, which reads as
missing data rather than as a broken load.

No schema move is needed any more; migration 011 (step 4) created the table in
`knowledge`, which is where the client looks.

**Without this, every district and skill a user types fails to resolve** — silently.

- [ ] 202 rows loaded · [ ] counts match 33 / 22 / 147

---

## 8 · Pre-sync checks — no credentials needed

| | |
|---|---|
| **Command** | `scripts/run_sync.sh --plan-only` |
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
| **Command** | `scripts/run_sync.sh` |
| **Expected** | 1st: `1812 inserted` · 2nd (automatic): **`0 inserted, 0 updated, 1812 skipped`** |
| **Validation** | `select count(*) from knowledge.kg_entities;` → 647 |
| **Rollback** | `scripts/rollback.sh list` → `scripts/rollback.sh sync <run_id>` |

**The second run is the step that matters, and the script does it for you** — it fails if
the repeat run is not `0 inserted, 0 updated`. Updates on an unchanged repository mean a
value round-trips differently through Postgres than through the content hash. Diagnose
before scheduling the sync.

The script also refuses to proceed if the plan shows anything other than the 4 governed
warnings, and asks for confirmation before more than 50 deletes.

- [ ] 1,812 rows · [ ] **second run 0/0** · [ ] `run_id` recorded: ____________

---

## 11 · Per-user intelligence

| | |
|---|---|
| **Command** | `scripts/run_user_intelligence.sh` (dry) → `scripts/run_user_intelligence.sh --from-db --apply` |
| **Expected** | dry: 8 scores, 10 categories, `mentors`/`events` = `NO DATA` · apply: one write pass per user |
| **Validation** | `select count(*) from user_intelligence.user_activity_summary;` → one row per processed user |
| **Rollback** | `scripts/rollback.sh intelligence` — drops and recreates the schema |

Without `--apply` the script computes against an in-memory target and writes nothing, and
needs no credentials. `--apply` is the only path that reads
`SUPABASE_SERVICE_ROLE_KEY`.

The writer is idempotent by result hash, so re-running over every user costs one read per
unchanged user. `user_activity_summary` is written **last**, so a partial failure leaves
the user reading `NOT_COMPUTED` and replays cleanly rather than showing half a profile.
Per-run detail lands in `user_intelligence/state/writer_log.jsonl` (gitignored).

`NOT_COMPUTED` remains correct for any user not yet processed, and `/dashboard` says so.

- [ ] Dry run clean · [ ] `--apply` completed · [ ] row counts match user count

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
| **Command** | `scripts/verify_deployment.sh` then `scripts/health_check.sh` |
| **Expected** | every assertion passes; 0 scheme→district edges is reported as `KNOWN GAP` |
| **Validation** | `health_check.sh` exits **0**; both smoke profiles — resolving **and** non-resolving skills |
| **Rollback** | §15 |

`verify_deployment.sh` is the scripted form of `POST_DEPLOYMENT_VALIDATION.md`: schemas
and table counts, **anon-key schema exposure** (the step 6 failure, which nothing else
surfaces), crosswalk counts by kind, 1,812 synced rows, sync idempotency, intelligence
population, search results, recommendations.

`health_check.sh` emits JSON and uses the **anon key**, deliberately: the service-role
key can read a schema that is not exposed and would report healthy while every page
renders empty.

Exit codes: `2` on any critical finding, `0` otherwise — warnings are printed and
counted but do not fail the run. Pass `--strict` (or set `VW_HEALTH_STRICT=1`) to make
warnings exit `1` as well; that is the right mode for a monitor and the wrong one for a
deployment gate, which is why the gate does not use it. The JSON keeps reporting
`"status": "degraded"` on warnings regardless, alongside `"strict"` and `"exit_code"`.

Read `POST_DEPLOYMENT_VALIDATION.md` for the human judgements the scripts cannot make —
whether an empty state reads as *incomplete* or as *broken*.

- [ ] `verify_deployment.sh` clean · [ ] `health_check.sh` exit 0 (no critical) · [ ] result recorded

---

## 15 · Rollback ladder

Least to most destructive. **Stop at the first that works.** `scripts/rollback.sh --help`
prints this table; `scripts/rollback.sh list` shows the available rollback points.

| # | Situation | Action | Loses |
|---|---|---|---|
| 1 | Frontend bug | Vercel → promote previous *(not scripted)* | nothing |
| 2 | Bad sync | `scripts/rollback.sh sync <run_id>` | that run |
| 3 | Projection wrong | `scripts/rollback.sh knowledge` | nothing — it is derived from Git |
| 4 | Intelligence wrong | `scripts/rollback.sh intelligence` | computed rows, recomputable |
| 5 | Schema mistake in `public` | **Supabase point-in-time restore** *(not scripted)* | everything after the restore point |

> **Levels 1–4 lose nothing that is not derived from Git.** Level 5 is the only one that
> touches user data, and it is deliberately **not scripted** — it needs a decision rather
> than a command.

**Rehearse level 2 once** on the `kg_schemes` sync from step 9, before real users exist.

- [ ] Level 2 rehearsed

---

## Sign-off

| | |
|---|---|
| Deployed by | |
| Date | |
| Commit | |
| Migration 011 applied | ☐ |
| Schemas exposed | ☐ |
| Crosswalk loaded (202) | ☐ |
| Second sync reported 0/0 | ☐ |
| Intelligence written | ☐ all users ☐ deferred |
| `verify_deployment.sh` clean | ☐ |
| `health_check.sh` exit 0 | ☐ |
| Seeded opportunities | ☐ labelled ☐ omitted |
| Rollback rehearsed | ☐ |
| **Go / No-Go** | |
