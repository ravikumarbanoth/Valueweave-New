# Deployment Report

**ValueWeave v1.0 · Production UX Polish Sprint**

---

## Deployment status

> **Code has been merged, but Vercel deployment could not be executed or verified
> from this environment.**

The brief's instruction is explicit: *"Do NOT claim deployment success unless it
has been verified on the live production deployment."* It has not been, so it is
not claimed.

### What was checked

| Check | Result |
|---|---|
| `frontend/vercel.json` | absent |
| `.vercel/` project link | absent |
| `vercel` CLI | not installed |
| `VERCEL_*` environment variables | none (0) |
| `https://api.vercel.com/v2/user` | **HTTP 000** — unreachable |
| `https://vercel.com` | **HTTP 000** — unreachable |
| `https://valueweave.in` | **HTTP 000** — unreachable |

There is no deployment hook, no token, no project link, and no network path to
Vercel or to the production domain. Nothing in this environment can trigger a
deployment or observe one.

### What this report therefore cannot contain

* Production deployment URL
* Deployment status or build duration on Vercel
* Any statement about how the live site behaves after this merge

Those fields are left empty deliberately. Filling them from the local build would
be reporting a different thing under the same name.

> The background section of the brief lists "✅ Production Deployment" as already
> complete. This environment cannot confirm or deny that — `valueweave.in`
> returns HTTP 000 here, which is a network restriction on this sandbox and not
> evidence about the live site. The same limitation was recorded in the
> Operational Completion Sprint's report, for the same reasons.

---

## What WAS verified, locally

Everything below was executed. No result is inferred.

### Tests

```
suite                     tests  fail  err  skip   secs  status
------------------------------------------------------------------------
api                          29     0    0     0   1.09  PASS
deployment                   50     0    0     0   0.52  PASS
frontend_activation          33     0    0     0   0.07  PASS
frontend_integration         59     0    0     0   0.16  PASS
graph                        15     0    0     0   0.30  PASS
graph_compiler               11     0    0     0   0.00  PASS
knowledge_engine              9     0    0     0   0.29  PASS
knowledge_engine_unit       117     0    0     0   0.03  PASS
knowledge_sync               64     0    0     0   0.91  PASS
ownership                    11     0    0     0   0.02  PASS
production_ux                21     0    0     0   0.21  PASS
regression                    9     0    0     0   0.32  PASS
search                       27     0    0     0   0.55  PASS
stewardship                  31     0    0     0   0.08  PASS
user_intelligence            74     0    0     0   0.40  PASS
vocabulary                   24     0    0     0   0.42  PASS
------------------------------------------------------------------------
TOTAL                       584     0    0     0   5.47  PASS
```

### Production build

```
✓ Compiled successfully
  Linting and checking validity of types ...
✓ Generating static pages (214/214)
exit 0 · 0 warnings · 0 prerender errors
```

**Lint:** `npx next lint` was not run. This project has no ESLint configuration
and the command prompts interactively to create one; adding a config would flag
hundreds of pre-existing issues unrelated to this sprint. The build's own type
and syntax checking passes clean, and that is the checking this repository has.

### Live server verification

`npx next start` on the production build, then every public route fetched.

**Legacy redirect — the fix and the fix's own bug:**

```
/explore                  200                                    ← restored
/explore/abc123           308 -> /opportunities/abc123
/explore/abc123/medak     308 -> /opportunities/abc123/medak
```

**Routes:** 49 public routes fetched. **0 unexpected 404s.** Eight routes 404'd
on invented slugs (`/skills/medak`, `/research/medak`); all return 200 with real
slugs, which is correct behaviour for a record that does not exist.

**Pages the brief names, all fetched and confirmed 200:**

| Page | Status |
|---|---|
| Landing `/` | 200 |
| Knowledge search `/knowledge`, `/knowledge?type=skill` | 200 |
| Opportunity detail `/opportunities/<id>` | 200 |
| District detail `/district/medak`, `/districts/medak` | 200 |
| Business / skill / scheme detail `/knowledge/<type>/<slug>` | 200 |
| Collaborator marketplace `/collaborators` | 200 |
| Readiness, manufacturing, scale, network, ai | 200 |
| Idea detail, research article, opportunity radar | 200 |

**Server log:** 0 errors, 0 warnings, 0 hydration mismatches.

**Rendered HTML:** 15 key pages fetched and grepped for internal vocabulary —
knowledge graph, knowledge schema, package identifiers, crosswalk, script paths,
checklist filenames, "not switched on", `.csv`. **Clean on every page.**

### Not verified

* **No page was opened in a real browser.** Client-side console output,
  interaction behaviour and visual layout are unchecked. The evidence above is
  server logs, HTTP status codes and rendered HTML.
* **No page was rendered against a live database.** The research database is not
  deployed to any environment reachable from here, so every knowledge surface
  currently renders its "information is being prepared" state. The build proves
  each page renders; it does not prove each page renders populated.

---

## Git report

| | |
|---|---|
| Current branch | `main` |
| Feature branch | `claude/production-ux-polish` |
| Commit hash | `cc349b1` |
| Merge commit | `1ded036` (`--no-ff`) |
| Previous `main` | `2de8102` |
| Files changed | 44 · 1 renamed · 5 added |
| Insertions / deletions | +1,471 / −288 |
| Pushed | feature branch and `main`, first attempt each, no retries |
| Tests passed | **584 / 584**, 16 suites |
| Build status | **exit 0**, 214/214 static pages, 0 warnings |
| Git status | clean |
| Working tree | clean, `main == origin/main` |

Graph artifacts churned during the test run (`built_at` rewritten to today);
verified date-normalised-identical and reverted, so no artifact noise is in the
diff.

---

## To deploy this

From an environment with Vercel access:

```bash
git checkout main && git pull
cd frontend && npm ci && npm run build     # expect exit 0, 214/214
vercel --prod                              # or let the GitHub integration fire
```

Then verify, in a browser:

1. Landing page — click a featured opportunity. It must open, not 404.
2. Visit `/explore` — it must load the marketplace, not redirect.
3. Visit any old `/explore/<id>` link — it must land on `/opportunities/<id>`.
4. `/knowledge?type=skill` — search, filter and paginate.
5. An opportunity page — the block must read **Opportunity Snapshot**.
6. `/districts/medak` — no mention of crosswalks or schemas.
7. Dashboard signed in — either personal suggestions, or an invitation to
   complete the profile. Never "not switched on".

`scripts/health_check.sh` covers the database side and exits `0` healthy,
`1` degraded, `2` failed.

---

**Companions:** `CURRENT_REPOSITORY_STATE.md` · `CODEX_RECOVERY_REPORT.md` ·
`PRODUCTION_UX_REPORT.md` · `BUG_FIX_REPORT.md`
