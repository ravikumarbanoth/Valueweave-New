# Bug Fix Report

**ValueWeave v1.0 · Production UX Polish Sprint**

Defects found and fixed, each with how it was found and how it is now prevented.

---

## Summary

| | |
|---|---|
| Defects fixed | **3** |
| Found by inspection | 1 |
| Found by executing against a running server | 2 |
| Routes returning 404 that should not | **0** |
| Server errors or hydration warnings | **0** |

---

## BUG-1 · Every featured opportunity on the landing page 404'd

**Severity: high.** The first thing a visitor clicked was the first thing that
broke.

`components/HomeFeaturedOpportunities.jsx:42`

```jsx
href={`/explore/${opp.id}`}
```

`app/explore/` contains only `page.js`. There is no `[id]` route and there never
has been. Every featured-opportunity card on the landing page led to a 404.

**Found:** during the mandatory repository inspection, by listing the files under
`app/explore/` after grepping for links into it. Nothing in the build, the tests
or the type checker had ever flagged it — a template literal in an `href` is just
a string.

**Fixed:**
* the card points at `/opportunities/${opp.id}`, which exists;
* `next.config.js` permanently redirects `/explore/:id+` → `/opportunities/:id+`,
  because the wrong link was live long enough to have been shared and indexed.

**Verified** against a running production server:

```
/explore/abc123          308 -> /opportunities/abc123
/opportunities/abc123    200
```

**Prevented:** `LegacyRouteTest` fails if any public page links to `/explore/<…>`
again, and separately asserts the redirect and its destination route exist.

---

## BUG-2 · The fix for BUG-1 broke the marketplace page

**Severity: high, and entirely self-inflicted.**

The first redirect was written as:

```js
{ source: "/explore/:id*", destination: "/opportunities/:id*", permanent: true }
```

In Next.js path syntax `*` means **zero or more** segments. `/explore` — the
working opportunity marketplace, a real page with real content — matched it and
308'd to `/opportunities`.

**Found:** only by curling the route against `next start` after the build. It was
invisible in review: the config reads correctly, the build passes, and the
difference between `*` and `+` is one character in a string that looks like a
glob to anyone who has not read the routing docs closely.

```
before:  /explore   308 -> /opportunities      ← the page was gone
after:   /explore   200
```

**Fixed:** `:id+` (one or more segments), which is what "a legacy detail URL"
actually means, and which still catches the district variant
`/explore/<id>/<district>`.

**Prevented:** the test asserts the exact modifier and explicitly rejects the
star form:

```python
self.assertIn("/explore/:id+", src)
self.assertNotIn("/explore/:id*", src,
                 "the star modifier also captures /explore itself")
```

> The lesson is narrower than "test your redirects": a config change that looks
> obviously correct is exactly the kind that never gets executed before merge.
> This one took ten seconds to verify and would have taken a production incident
> to discover.

---

## BUG-3 · Deployment instructions rendered to end users

**Severity: medium.** Nothing broke; the product read as broken.

Twenty-one public files rendered internal vocabulary, **65 occurrences**. A
first-year student looking for a welding course could be shown:

> "The knowledge schema has not been deployed to this environment.
> **Depends on:** Run the migrations, expose the `knowledge` schema, then
> `scripts/run_sync.sh`. See docs/FIRST_DEPLOYMENT_CHECKLIST.md steps 5–10."

Every word true. None of it theirs. Elsewhere: `Package008_MSME ·
businesses.csv · B-014` under every card, "Personalised recommendations are not
switched on yet" on the dashboard, and "has no entry in the district vocabulary
crosswalk" on district pages.

**Origin:** most of it was introduced by the previous session's Step 4, which
optimised for operator honesty and never asked who was reading. This is recorded
plainly because the cause matters: the sentences were added deliberately and for
a good reason, and were still wrong.

**Fixed:** all 65 occurrences rewritten. The diagnosis is preserved where it is
useful — `data-reason`, `data-operator-note`, `data-source-package`,
`data-source-dataset`, `data-source-row` — so support and tests keep it and users
never see it.

**Verified** by fetching every key page from a running server and grepping the
rendered HTML:

```
/ /knowledge /knowledge?type=skill /districts /districts/medak /district/medak
/readiness /manufacturing /scale /network /ai /dashboard /ideas/<slug>
/knowledge/district/medak /opportunity-radar
  → CLEAN, no internal vocabulary in any rendered page
```

**Prevented:** `DeveloperLanguageTest` greps every non-admin page and component
for fifteen banned patterns on every test run. It runs against comment-stripped
source, so a file may explain which term it stopped showing — several do — but
may not render one.

---

## Verified, not a defect

Eight routes returned 404 during the sweep. All eight were **invented slugs**
(`/skills/medak`, `/research/medak`, `/questions/abc123`). Re-run with real
slugs, every one returns 200:

| Route | Status |
|---|---|
| `/district/medak` · `/districts/medak` | 200 |
| `/ideas/soil-testing-micro-lab` | 200 |
| `/research/battery-recycling-business-india` | 200 |
| `/knowledge/district/medak` · `/knowledge/districts/medak` | 200 |
| `/opportunity-radar/telangana` · `/collaborators` | 200 |

A 404 for a record that does not exist is the correct answer.

---

## Console, hydration and runtime

`next start`, all 49 public routes fetched:

```
errors:              0
warnings:            0
hydration mismatches: 0
```

Nothing was fetched in a real browser with devtools open — this is the server log
and the response codes. Client-only console output is covered in
`DEPLOYMENT_REPORT.md` under what could not be verified.

---

**Companions:** `CURRENT_REPOSITORY_STATE.md` · `CODEX_RECOVERY_REPORT.md` ·
`PRODUCTION_UX_REPORT.md` · `DEPLOYMENT_REPORT.md`
