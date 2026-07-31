# Remaining Dependencies

**ValueWeave Platform v3.0 · Step 4 — Frontend Knowledge Activation**

Everything the frontend still cannot show, why, and what would have to change.
Ordered by how cheap the fix is.

Every `NOT_AVAILABLE_YET` and `NO_DATA_SOURCE` state in the application names one
of these. That is the point of the exercise: a chip saying "not yet" without a
reason is the "Coming Soon" this step removed, wearing a different word.

---

## 0 · The one that blocks everything

**The `knowledge` and `user_intelligence` schemas are not deployed to any
environment.**

Until they are, **every** knowledge surface renders `NOT_DEPLOYED` — the homepage
featured cards, search, the explorer, all five module dashboards, both district
routes, every detail page, and every dashboard rail. The pages are correct; the
database is absent.

The blockers that used to prevent this were closed in the Operational Completion
Sprint (migration 011, `load_crosswalk.sh`, `writer.py`). What remains is running
them:

```bash
scripts/first_deploy.sh          # migrations, crosswalk, sync, verification
# manual gate: expose `knowledge` and `user_intelligence` in the Supabase dashboard
scripts/run_user_intelligence.sh --from-db --apply
scripts/verify_deployment.sh
```

**Effort:** hours, not days. **Blocks:** 14 of 49 public routes.

---

## 1 · Researched in Git, not projected to Supabase

The research exists. `knowledge_sync` projects **8 tables**, and these are not
among them. Each needs a `TableSpec` in `knowledge_sync/config.py`, a column set
in the migration generator, and a frontend binding.

| Dataset | Rows | Blocks | Effort |
|---|---:|---|---|
| `Package007/eligibility_criteria.csv` | 55 | **Scheme eligibility** — asked for by name in Phase 8 | S |
| `Package007/application_process.csv` | 43 | Application steps on scheme pages | S |
| `Package007/required_documents.csv` | 15 | Document checklist on scheme pages | S |
| `Package006/training_centres.csv` | 22 | Named training centres — Phases 6, 7, 9 ask for these; the 25 `TrainingProvider` entities are *organisations*, not centres | S |
| `Package006/career_paths.csv` | 15 | Learning roadmap ordering — Phase 7 | M |
| `Package006/ai_skill_mapping.csv` | 45 | AI-augmentation detail beyond the single column already projected | S |

**Scheme eligibility is the most visible of these.** A user reading a scheme page
wants to know whether they qualify, the answer is researched, and 55 rows sit in
Git that no frontend query can reach. `/knowledge/scheme/<slug>` says exactly
that, naming the file.

> This is backend scope, not frontend. Step 4's brief is explicit — *"DO NOT
> modify package data. DO NOT modify the Knowledge Graph"* — and extending the
> sync projection is neither a frontend change nor a small one: it needs a spec,
> a migration, idempotency proof, and tests. Naming it precisely is the correct
> output of a frontend step.

---

## 2 · Packages with no graph contribution

| Package | Entities in graph | Consequence |
|---|---:|---|
| Package003_Healthcare | **0** | No hospital, medical college or health scheme is reachable anywhere in the application. `/discover`'s healthcare assessment path has no researched knowledge behind it. |

Found in the v1.0 readiness assessment and unchanged since. The package has
datasets; `knowledge_graph/build_graph.py` has no builder that reads them. Until
one exists, no frontend work can surface a single healthcare record.

**Effort:** M — a builder plus entity/relationship emission.

---

## 3 · Capabilities with no data source anywhere

No package covers these. They are not sync gaps or deployment gaps — the research
does not exist. Each is rendered as `NO_DATA_SOURCE` at the surface that would
have shown it.

| Capability | Where it appears | Nearest thing that does exist |
|---|---|---|
| Mentors | `/readiness`, `/network` | 66 institutions; a marketplace of real people. Neither is a mentor record. |
| Events | `/network` | — |
| Experts | `/network` | The marketplace has people but models no expertise or seniority. |
| Individual investors | `/network` | 21 financial institutions as *categories* — angel networks, NBFCs — with no ticket size or mandate. |
| Communities | `/network` | — |
| Suppliers | `/manufacturing` | 21 raw materials; the firms supplying them are not recorded. |
| Factory layout / production planning | `/manufacturing` | Investment range and working capital per opportunity; no plan. |
| Compliance / licences | `/manufacturing` | 30 certifications, which are skill credentials, not business licences. |
| Automation and robotics vendors | `/scale` | `automation_level` and `ai_readiness` describe a *business*, not the equipment that would change it. |
| ERP, logistics, energy, quality systems | `/scale` | — |
| Resources, roadmaps | `/resources`, `/roadmaps` | CMS-only. No entity type exists, so `kg-fallback.js` correctly does not cover them. |
| AI advisors | `/ai` | A rule engine — explainable, traceable to a CSV row, and deliberately not a model. |

**Effort:** L each. These are research programmes, not tickets.

---

## 4 · Graph coverage that limits what populated pages show

The schemas could be deployed tomorrow and these pages would still look thin.
They are the honest ceiling on Step 4's work.

| Edge type | Edges | Consequence |
|---|---:|---|
| `TRAINED_BY` | **3** | The "courses" rail and training-provider sections are near-empty for almost everyone. |
| `SELLS_TO` | **12** | "Where you could sell" resolves for a handful of businesses. |
| `GENERATES_EMPLOYMENT` | **32** across 61 districts | Most district pages show institutions and industries but few businesses. `DistrictIntelligencePanel` says this in its empty state rather than letting a blank read as "this district has no economy". |
| scheme → district | **0** | `RS2-VIA_DISTRICT` and `RI3-VIA_DISTRICT` are structurally dead. `verify_deployment.sh` reports this as `KNOWN GAP`, not a failure. |

Skill resolution through the vocabulary crosswalk is **22.8%**, so roughly three
in four users see empty skill-driven rails on a fully working deployment. That is
data coverage, and `PILOT_PLAN.md` covers what to do about it before inviting a
general cohort.

Tracked in `GRAPH_CONNECTIVITY_PLAN.md` and `KNOWLEDGE_COMPLETION_MASTER_PLAN.md`.

---

## 5 · Deliberately not done in this step

| Item | Why |
|---|---|
| Delete `lib/static-knowledge.js` and `frontend/data/*.json` | 56 indexed URLs resolve through them. Nothing links there any more and each page now opens with a "superseded" notice. Deleting them breaks live URLs to make a point about data quality — a worse trade. |
| Rebuild `/opportunity-radar` on graph data | 40 editorially curated opportunities with real links into the Idea Library. The brief protects editorial content. Both pages now disclose that fit and demand are hand-assigned, not measured. |
| Merge `/district/<slug>` and `/districts/<slug>` | Two routes, both now live, sharing one component. Merging them means deleting a route and breaking URLs, which this brief forbids. |
| Browser-based page tests | No harness exists; adding one is a larger change than this step. `npx next build` proves every page renders; `POST_DEPLOYMENT_VALIDATION.md` covers what a person must check. |

---

## Priority

1. **Deploy the schemas.** Hours. Unblocks 14 routes and everything below.
2. **Project scheme eligibility** (55 rows). Small. The most visible single gap.
3. **Project training centres** (22 rows). Small. Named in three phases.
4. **Build a Package003 graph builder.** Medium. An entire package is dark.
5. **Recover `TRAINED_BY` and `GENERATES_EMPLOYMENT` edges.** Medium; `RELATIONSHIP_RECOVERY_REPORT.md` identified 410 edges recoverable at 100% verification with zero new research.

---

**Companions:** `PLACEHOLDER_REMOVAL_REPORT.md` · `KNOWLEDGE_BINDING_REPORT.md` ·
`LIVE_PAGE_REPORT.md` · `USER_EXPERIENCE_COMPLETION.md`
