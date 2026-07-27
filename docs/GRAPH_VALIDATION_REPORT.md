# Graph Validation Report

**Workstream 4** · Measured against `0d63a0a` · 647 entities · 865 edges

---

## 0. Verdict

**The graph is structurally clean and semantically sparse.**

| Check | Result | |
|---|---|:---:|
| Duplicate edges | **0** | ✅ |
| Self-loops | **0** | ✅ |
| Dangling endpoints | **0** | ✅ |
| Unregistered relationship types | **0** | ✅ |
| Orphan entities | **142 (21.9%)** | ❌ |
| Connected components | **150** | ❌ |
| Median node degree | **1** | ❌ |
| Registered-but-unused edge types | **4** | ⚠️ |

Nothing is corrupt. Every defect is an absence.

**And nothing currently checks any of the four passing rows.** `validate_graph.py` runs
G1–G11 covering provenance, ownership and referential integrity; it does not test for
duplicate edges, self-loops, component structure or orphan census. They pass by
construction rather than by verification, which is a different thing.

---

## 1. Integrity — all clean

### D1 · Duplicate edges — 0

No `(from_entity, relationship_type, to_entity)` triple appears twice across 865 edges.

Worth stating because Wave 1 adds 410 edges from six new sources, and two of them can
legitimately produce the same shape: `agri_business_mapping` yields
`BusinessOpportunity -REQUIRES_SKILL-> Skill` (R5), and so does
`skill_business_mapping` after M1 resolution. **A duplicate is likely the moment
recovery lands**, and nothing would catch it.

### D2 · Self-loops — 0
### D3 · Dangling endpoints — 0

Every `from_entity` and `to_entity` resolves. `unresolved_endpoints.csv` (132 rows) is
the reason: the builder diverts failures rather than emitting broken edges. **Except
where it diverts them nowhere** — §5.

### D4 · Relationship types — 19 registered, 15 used, 0 unregistered

**Four registered types are never emitted:**

| Type | Intended | Status |
|---|---|---|
| **`CERTIFIED_BY`** | `Skill -CERTIFIED_BY-> Certification` | **The schema anticipated E5.** 30 orphan certifications; 122 unresolved rows |
| **`STUDIED_AT`** | `Skill -STUDIED_AT-> Institution` | No producer |
| `PREDECESSOR_OF` / `SUCCESSOR_OF` | Skill or career sequencing | `career_paths.csv` (15 rows) is unconsumed |

**`CERTIFIED_BY` being registered and unused is the strongest single piece of evidence in
this report.** Whoever designed the schema knew certifications should connect to skills.
The type exists, the data exists, the builder attempts it, and the vocabulary mismatch
defeats all 122 attempts.

`PREDECESSOR_OF`/`SUCCESSOR_OF` have a plausible source in the unconsumed
`career_paths.csv` — a Wave 2 candidate, and a modelling decision rather than a recovery.

---

## 2. Orphan census — 142 (21.9%)

| Type | Orphans | of total | Root cause | Cleared by |
|---|---:|---:|---|---|
| **Certification** | **30** | 30 (**100%**) | Free-text `related_skill_names` | M2 — **7 now, ~24 after v1.1** |
| **TrainingProvider** | **22** | 25 (88%) | No `TRAINS` producer | Wave 2 |
| **GovernmentScheme** | **21** | 40 (53%) | Welfare schemes, no business link | **R1 clears 4** |
| Industry | 17 | 78 (22%) | 6 are `AI Tooling:` pseudo-industries | Taxonomy decision |
| FinancialInstitution | 13 | 21 (62%) | Named in prose only | Wave 2 |
| Market | 10 | 11 (91%) | Reachable only via MSME | Wave 2 |
| Institution | 8 | 66 (12%) | Empty/unmatched `district` | Repair |
| Machinery | 8 | 69 (12%) | Agri machinery, no crop link | Wave 2 |
| ExportCountry | 7 | 29 (24%) | Parsed from free text | Accept |
| Skill | 5 | 45 (11%) | Emerging tech, no business | E1 |
| Soil | 1 | 10 (10%) | Saline, no crop | Accept |

**After Wave 1 recovery: 138.** Four orphan schemes — MGNREGS, PMAY-G, PM-KISAN,
AB PM-JAY — gain 61 district edges each from R1.

**The other 406 recovered edges clear no orphans**, because they join entities that
already had edges. Reach and orphan-clearing are different problems, and only entity
resolution addresses the second.

### Six `Industry` orphans that are a modelling defect

```
AI Tooling: AI Credit Scoring and Cash Flow Forecasting
AI Tooling: AI Quality Inspection
AI Tooling: Computer Vision Sorting and Grading
AI Tooling: Customer Service Chatbot
AI Tooling: Predictive Maintenance
AI Tooling: Workflow and Robotic Process Automation
```

These are **capabilities, not industries.** They were derived from
`ai_business_tools.csv` and typed as `Industry` because that was the nearest available
type. They inflate the Industry count from 72 to 78 and can never be located in a
district or required by a skill.

**Recommendation: retype or retire.** Six orphans removed by a decision rather than by
collection — the cheapest item in the census.

---

## 3. Component structure — 150 components

| Size | Count | Share |
|---:|---:|---:|
| **489** | 1 | **75.6%** |
| 4 | 1 | 0.6% |
| 2 | 6 | 1.9% |
| **1** | **142** | **21.9%** |

**One giant component holds 75.6% of entities.** The rest is 142 isolated nodes and 7
tiny islands.

### The seven islands

| Size | Contents |
|---:|---|
| 4 | WhatsApp Group Buying · Instagram Live Selling · Instagram Shopping · Retail & Local Commerce |
| 2 | Bridal Wear & Traditional Textiles · Local Entrepreneurship |
| 2 | Local Entrepreneurship · Common Service Centres |
| 2 | Agriculture & Allied Livelihoods · Farmer Producer Organisations |
| 2 | Instagram/YouTube Creator · Retail & Local Commerce |

Every island is a **Package004 opportunity attached only to its own Industry**, where
that Industry is itself attached to nothing else. `BusinessOpportunity -PART_OF->
Industry` fires, and no other shape does.

**R3 and R5 dissolve most of these** by giving those opportunities MSME and Skill edges.
It is the clearest illustration of the Phase 1 finding: the opportunity half of the graph
is a scatter of islands, and MSME is the only bridge.

---

## 4. Proposed checks — G12 to G15

`validate_graph.py` has 11 checks. Four more, all passing today, so they lock in the
current state before Wave 1 disturbs it.

| # | Check | Level | Rationale |
|---|---|---|---|
| **G12** | No duplicate `(from, type, to)` triple | **ERROR** | Two Wave 1 sources can emit the same shape (§1) |
| **G13** | No self-loops | ERROR | Cheap; would indicate a resolution bug |
| **G14** | Component census reported; largest ≥70% | **WARN** | A drop means a new source landed disconnected |
| **G15** | Orphan census by type; **fail on regression** | **WARN → ERROR** | Adding entities without edges is the failure Wave 1 exists to reverse |

**G15 is the one worth arguing for.** It is not a threshold on the absolute count — 142 is
too high to gate on today. It fails when a *rebuild increases* orphans. Registering a
dataset that adds nodes and no edges is precisely how the graph reached 21.9%, and G15
makes that visible in CI instead of in a later audit.

### One check that must be fixed, not added

**Unresolved endpoints must be logged consistently.** Today:

| Path | Failures | Logged |
|---|---:|:---:|
| `certifications.csv` | 122 | ✅ all |
| `skill_business_mapping.csv` | 27 | ❌ **none** |
| `export_opportunities.csv` | 3 | ✅ |
| `skill_mapping.csv` | 7 | ✅ |

`unresolved_endpoints.csv` holds 132 rows and **looks complete**. It is missing 27 — 17%
of the real failures — and there is no way to tell from the file.

**A partial failure log is worse than no failure log**, because it invites trust it has
not earned. Every mapping site must route through the same reporting helper before Wave 1
registers six more.

---

## 5. Post-Wave-1 expectations

| Check | Now | After | Note |
|---|---:|---:|---|
| Duplicate edges | 0 | **0** | **G12 must be live first** |
| Self-loops | 0 | 0 | |
| Dangling | 0 | 0 | |
| Unregistered types | 0 | 0 | R1–R6 need `AVAILABLE_IN`, `PROCESSED_BY` registered |
| Orphans | 142 | **138** | −4 schemes |
| Components | 150 | **~142** | Islands dissolve; singletons persist |
| Largest component | 489 (75.6%) | **~525 (78%)** | |
| Median degree | **1** | **2** | |
| Unused registered types | 4 | **4** | `CERTIFIED_BY` waits on M2 |

**Two new relationship types must be registered before Stage A**: `AVAILABLE_IN` (R1) and
`PROCESSED_BY` (R4). Emitting an unregistered type would break D4, which is currently
clean — and D4 being clean is why the builder can be trusted at all.
