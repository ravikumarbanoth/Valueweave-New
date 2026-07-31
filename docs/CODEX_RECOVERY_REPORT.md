# Codex Recovery Report

**ValueWeave v1.0 · Production UX Polish Sprint**

The brief instructed: *"Recover every unfinished Codex change. If files are
partially edited, finish them. If changes were lost, reimplement them. Never
duplicate work."*

---

## Recovery outcome

| | |
|---|---|
| Codex commits found for this sprint | **0** |
| Partially edited files | **0** |
| Work recovered | **0** — there was none to recover |
| Work reimplemented from scratch | **10 of 10 items** |
| Work duplicated | **0** |

`CURRENT_REPOSITORY_STATE.md` carries the full evidence. In short: clean working
tree, no stash, no untracked files, `HEAD` identical to `origin/main`, and the
newest commit anywhere in the repository is the previous session's Step 4 merge.
Five dangling commits exist and every one traces to a `git stash` of my own.

Three `codex/*` branches exist on the remote. One was merged on 16 July; the
other two are from **30 May**, sit 210 and 209 commits behind `main`, and cover
footer links, profile routing and onboarding suggestions — none of the ten items
below. They are stale history, not unfinished work.

**So "continue, do not restart" resolved to: build all ten for the first time on
top of the current `main`, changing nothing that already worked.** No file was
rewritten that did not need changing, and nothing that Steps 1–4 established was
undone.

---

## The ten items

| # | Item | Before | Now | Where |
|---|---|---|---|---|
| 1 | Legacy `/explore/{id}` redirect | **404 on every landing-page card** | Card points at `/opportunities/<id>`; `/explore/:id+` → 308 | `HomeFeaturedOpportunities.jsx`, `next.config.js` |
| 2 | Opportunity Snapshot rename | "AI-readable opportunity summary" | "Opportunity Snapshot" | `SnapshotPanel.jsx` + 6 call sites |
| 3 | Remove AI Readable Summary | Component named and titled for machines | Renamed `SnapshotPanel`; machine attributes kept | `components/geo/` |
| 4 | Hide package terminology | "Package006 · Skills & Training" on every card | "Skills & training research" | `PACKAGE_LABELS`, `SourceBadge`, `ProvenanceLine` |
| 5 | Hide research-database terminology | "The knowledge schema has not been deployed…" | "This information is being prepared" | `KnowledgeEmptyState`, `KnowledgeCardGrid` |
| 6 | Improve search wording | "Searches 647 sourced entities across Packages 001–008" | "What are you looking for?" + real examples | `KnowledgeSearch.jsx` |
| 7 | Improve district wording | "has no entry in the district vocabulary crosswalk" | "We have not linked our research to Medak yet" | both district routes |
| 8 | Improve recommendation wording | "Personalised recommendations are not switched on yet" | Block hidden; profile prompt when the user can act | `dashboard/page.js`, `lib/intelligence.js` |
| 9 | YouTube on landing page | Video embedded; no route to the channel | "More videos on YouTube" link under the player | `HomeVideoEmbed.jsx` |
| 10 | Improve research source labels | `Package008_MSME · businesses.csv · B-014` in monospace | "From our small business research" | `ProvenanceLine.jsx` |

---

## Items that needed a decision, not just a rewrite

### 3 · The AI-readable block was renamed, not removed

The brief lists "Remove AI Readable Summary". Taken literally that would have
deleted the most useful block on six page types — investment range, district, who
it suits, what to do next — and with it the `data-ai-readable` and `data-ai-faq`
markup that answer engines read.

What was wrong was the **title**: "AI-readable summary" describes who the block
is *for*, and told the human reading it that this part of the page was not meant
for them. The component is now `SnapshotPanel`, titled per page ("Opportunity
Snapshot", "District Snapshot", "Research Snapshot"). The machine-readable
attributes are untouched and a test asserts they survive.

### 8 · Recommendations: hidden in one case, actionable in the other

The brief offers two options — *"Show friendly empty state or hide section"*.
Both were right, for different states:

* **We cannot serve it** (our matching service is not connected): the whole block
  is **hidden**. The user did nothing and can do nothing; an empty panel
  explaining our infrastructure would occupy the most valuable space on the
  dashboard to say "not our best day". The opportunity feed moves up instead.
* **We have not worked out their matches yet** (no skills or district on the
  profile): a **friendly card** with the one button that changes it.

`lib/intelligence.js` still distinguishes the two internally — that distinction
drives which behaviour fires — it just no longer drives what anyone reads.

### 4, 5, 10 · Diagnosis kept, moved out of sight

Step 4 gave every empty state a named cause and a dependency so an operator could
tell a deployment gap from a research gap. That was genuinely useful and aimed at
entirely the wrong audience.

Nothing was deleted. `reason` still carries the five names, `data-reason` still
exposes them in the DOM, and the runbook sentence lives on as
`data-operator-note`. Support can read it from an inspector; a student never
meets it. Same for provenance: `data-source-package`, `data-source-dataset` and
`data-source-row` are all still on the element, and the full string is the
`title` for anyone who hovers.

---

## What was not touched

| | Why |
|---|---|
| `codex/unify-footer-routing` (8 commits) | Its six files all exist in `main` already. Cherry-picking would duplicate work the brief forbids duplicating. |
| `codex/phase-2a-idea-discovery` (4 commits) | `lib/idea-library/index.js` has 26 exports there vs 17 in `main`. The extras are from May, and the idea library has been reworked twice since; importing 209-commit-old helpers would import stale assumptions with them. Recorded rather than silently skipped. |
| `conflict_240526_0104` (1,045 files) | Contains a `user_intelligence/writer.py` that predates and conflicts with the one shipped in the Operational Completion Sprint. Merging it would regress. |
| Steps 1–4 architecture | Nothing needed undoing. The bindings, routing, empty-state model and capability model are sound — only their vocabulary was wrong. |

---

## A bug found while verifying the fix

The first version of the legacy redirect was:

```js
{ source: "/explore/:id*", destination: "/opportunities/:id*", permanent: true }
```

`:id*` matches **zero** or more segments, so it also matched `/explore` itself and
redirected the working marketplace page to `/opportunities`. The config looked
correct in review and in diff; it only showed up when the route was curled
against a running production server:

```
/explore          308 -> /opportunities     ← broken
```

Fixed to `:id+` (one or more) and re-verified:

```
/explore                200
/explore/abc123         308 -> /opportunities/abc123
/explore/abc123/medak   308 -> /opportunities/abc123/medak
```

`test_the_legacy_url_still_redirects` now asserts the exact modifier and
explicitly rejects the star form, because both spellings look right in a diff and
only one of them works.

---

**Companions:** `CURRENT_REPOSITORY_STATE.md` · `PRODUCTION_UX_REPORT.md` ·
`BUG_FIX_REPORT.md` · `DEPLOYMENT_REPORT.md`
