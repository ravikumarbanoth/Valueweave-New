# Operational Runbook

**For whoever is on the other end of it.** Five procedures: update packages, rebuild the
graph, run the sync, deploy, roll back.

First principle, and everything below follows from it:

> **Git is the source of truth. Supabase is a cache.**
> Never edit package data in Supabase — the next sync reverts it, and the fix is lost
> from Git. Every projected table has **no write policy at all**, so this should be
> impossible rather than merely discouraged.

---

## 1. Update a package

**Trigger:** a correction, a new dataset, or a package release.

```bash
git checkout -b fix/scheme-benefit-figure
# edit packages/Package007_Government_Schemes/datasets/government_schemes.csv
python3 packages/Package007_Government_Schemes/validate.py      # where present
python3 tests/run_all.py --quiet                                # 478 PASS
git commit -am "fix(P007): correct PMEGP subsidy ceiling" && git push -u origin HEAD
```

Merge, then §2 and §3.

### Adding a **new dataset** — read this

```
FAIL: dataset(s) present in packages/ but absent from the compiler registry
```

`tests/test_graph_compiler.py` fails the moment a CSV appears that the builder does not
know about. That is the guard working. Either wire it into `build_graph.py` and add it to
`CONSUMED`, or add it to `IGNORED` with an entry in `BUILDER_REGISTRY.md` saying why.

**Do not delete the test to get green.** It exists because 38 datasets were silently
skipped, and that is how the repository reached 39 of 77 consumed.

### Checks

- [ ] Package validator clean · [ ] 478 tests · [ ] provenance columns on every new row
- [ ] No sentinel in a provenance column · [ ] `PENDING_VERIFICATION` where unconfirmed

---

## 2. Rebuild the graph

**Trigger:** package data changed, or the builder changed.

```bash
python3 knowledge_graph/build_graph.py
python3 knowledge_graph/validate_graph.py
```

**Expected:**

```
  entities ................. 647          ← moves only if entities changed
  connectivity ............. 505/647 (78.05%)
WARNINGS (1):
  [G10-ORPHANS] 142 entities have no relationships …
PASS — graph is structurally sound, provenance-complete and ownership-clean.
```

| Signal | Means |
|---|---|
| `PASS` + 1 orphan warning | Normal |
| Entity count moved unexpectedly | A name changed → **new id, old id orphaned** |
| A second warning | Read it. Do not sync. |
| `FAIL` | Fix the package. Do not sync. |
| `unresolved endpoints` rose | A mapping stopped joining — inspect `unresolved_endpoints.csv` |

> **The rebuild always dirties `git status`** — `created_at`/`updated_at` are stamped
> with today's date. Confirm the diff is date-only before committing:
> ```bash
> git diff knowledge_graph/ | grep '^[+-]' | grep -v '^[+-][+-]' \
>   | sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/<D>/g' | sort | uniq -c | sort -rn | head
> ```
> Additions and deletions should cancel exactly. **On a deployment host, do not rebuild
> at all** — use the committed artifacts.

- [ ] `PASS` · [ ] counts explained · [ ] diff is date-only or intended

---

## 3. Run the sync

### Always plan first

```bash
python3 -m knowledge_sync plan
```

**Steady state is all-skip.** Anything else must trace to a commit.

| Output | Action |
|---|---|
| `0 error(s), 4 warning(s)` | Expected — ADR-005 overlaps |
| `insert` on an established table | New rows — expected after a release |
| `update` | Content changed |
| **Large `delete`** | **Stop.** Usually a renamed dataset or a changed key, not retired facts |
| `ERROR` | Nothing was written. Fix the package. |

### Apply

```bash
python3 -m knowledge_sync sync --target supabase
python3 -m knowledge_sync sync --target supabase     # must report 0 inserted, 0 updated
python3 -m knowledge_sync history --limit 5
```

### Recovery

| Situation | Action |
|---|---|
| Apply failed partway | **Re-run.** The manifest advances last, so the run replays |
| Wrong data synced | `rollback <run_id> --dry-run`, then without |
| Manifest lost | Next run is a full insert. Harmless — upserts are idempotent |
| Manifest stale vs target | `sync --full` |
| Someone hand-edited a row | Next sync overwrites it. Expected |
| Second run reports updates | **Diagnose before scheduling.** A value round-trips differently through Postgres than through the content hash |

### Never

- **Never edit `knowledge.*` by hand.** No write policy exists; if one is added, it will
  be reverted on the next sync and the change lost from Git.
- **Never commit `knowledge_sync/state/manifest.json`.** It describes one deployment.
  It is gitignored for that reason.

---

## 4. Deploy

### Frontend

```bash
cd frontend && npm ci && npm run build      # exit 0 · 214/214 · 0 prerender errors
```

Vercel deploys on merge to `main`. **Record the previous deployment id** — it is the
fastest rollback available.

The build must succeed **without database access**. If it starts failing on a Supabase
call, a page has begun fetching at build time and needs `revalidate` or dynamic
rendering.

### A new migration

1. Write it as the next number in `frontend/migrations/`
2. Apply to a staging project first
3. Apply to production **before** deploying the frontend that needs it
4. Additive only — `create table if not exists`, `add column`. No `drop` on a live table

### Deploy order when both change

```
migration  →  sync (if package data changed)  →  frontend
```

Frontend last, always. A page that reads a column that does not exist yet renders an
empty state; a column that exists before the page does costs nothing.

---

## 5. Roll back

Least to most destructive. **Stop at the first that works.**

### Level 1 — frontend · seconds · loses nothing

Vercel → Deployments → previous → **Promote to Production**.

### Level 2 — one sync run · minutes · loses that run

```bash
python3 -m knowledge_sync snapshots
python3 -m knowledge_sync rollback <run_id> --dry-run
python3 -m knowledge_sync rollback <run_id>
```

Undoes inserts (soft delete), restores updated rows from pre-images, un-deletes
soft-deleted rows, restores the previous manifest.

**Roll back only the most recent run.** Reversing an older one while newer ones stand
produces a state matching no version of Git.

**Cannot** restore a row edited by hand in the console — that edit is in no snapshot.

### Level 3 — the whole projection · ~10 min · loses nothing

```sql
drop schema knowledge cascade;
```
Then re-apply `knowledge_sync/migrations/001` and `sync --full`.

**Safe by construction: the schema holds nothing but a projection of Git.**

### Level 4 — intelligence · loses recomputable rows

```sql
drop schema user_intelligence cascade;
```

### Level 5 — `public` · loses user data

**Supabase point-in-time restore.** The only level that touches real user data, and the
only one needing a decision rather than a command. Everything after the restore point is
gone: profiles, connections, opportunities.

> Levels 1–4 lose nothing that is not derived from Git. **Level 5 is a different kind of
> action** — treat the boundary as real.

---

## 6. Routine schedule

| When | Do | Alert if |
|---|---|---|
| Every PR touching `packages/**` | `plan` + tests in CI | errors, or a 5th warning |
| Merge to `main` touching `packages/**` | rebuild graph → `plan` → `sync` | any error |
| Nightly | `plan` | it reports changes — a sync was missed |
| Weekly | `history --limit 20` | any non-`SUCCESS` outcome |
| Monthly | rehearse level 2 rollback on staging | it does not work |
| After a DB restore | `sync --full` | — |

**There is no CI yet** (`.github/workflows/` does not exist). Until there is, the nightly
`plan` is manual and is the only thing that catches a missed sync.

---

## 7. Symptom → cause

| Symptom | First check |
|---|---|
| Every knowledge surface empty | **Schemas exposed?** The failure with no error |
| Some surfaces empty | Normal — `POST_DEPLOYMENT_VALIDATION.md` §11 |
| Districts/skills never resolve | `kg_vocabulary_map` — loaded? right schema? |
| All rails `NOT_COMPUTED` | Intelligence pipeline not built — Guide §9 |
| Sync aborts on transform | Fix the package, not the sync. Every bad cell is listed |
| Sync aborts on validation | V4 → rebuild the graph first |
| Second sync reports updates | Round-trip mismatch. Do not schedule until understood |
| Build fails on a Supabase call | A page began fetching at build time |
| Admin routes open to everyone | `NODE_ENV` is not `production` |
| Test suite fails on a new CSV | The compiler registry guard. §1 |

---

## 8. Escalation

| Severity | Example | Action |
|---|---|---|
| **P1** | User data at risk; auth broken | Level 5 decision; page the owner |
| **P2** | Site down; build broken | Level 1 rollback, then diagnose |
| **P3** | Knowledge surfaces empty | Check exposure; level 3 if needed |
| **P4** | One surface thin | Probably a known data gap. Check §11 of the validation doc first |

**P4 is the common case and the one most likely to be misdiagnosed.** 142 orphan
entities, 2 dead rules and a 22.8% skill resolve rate mean a thin surface is usually the
data being honest, not the platform being broken.
