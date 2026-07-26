# ValueWeave — Pilot Launch Plan

**100 students · 10 faculty · 20 entrepreneurs · 4 weeks**

Grounded in `VERSION1_READINESS_REPORT.md`. The one decision that shapes everything
else is geographic, and it comes from a measurement rather than a preference.

---

## 0. The decision that makes or breaks this pilot

> **Recruit the entire cohort from four districts: Hyderabad, Guntur, Tirupati,
> Visakhapatnam.**

Not because they are the biggest. Because they are the only districts where the
platform has enough knowledge to be useful.

`district_opportunity` scored across all 61 districts, using a skill that resolves:

| Band | Districts | Recommendation rows |
|---|---:|---|
| ≥70 | **1** — Hyderabad (85) | 25 |
| 50–69 | **3** — Guntur (59), Tirupati (51), Visakhapatnam (50) | 25 each |
| 30–49 | 12 | 12–25 |
| **<30** | **45** | **6** |

**Median across all 61 districts: 0.** Mean: 11.9.

A student in one of the bottom 45 districts gets **6 recommendation rows**. A student
in Hyderabad gets **25**. Same product, same effort to sign up.

The institution data agrees independently — Institution→District edges concentrate in
exactly those districts: **Hyderabad 12, Tirupati 7, Guntur 6, Visakhapatnam 3**. So
the districts with the most knowledge are also where the colleges are, which makes
recruitment and coverage the same problem.

### Why not recruit broadly and learn more

Because the lesson would be wrong. Spread 100 students across the state and ~74% land
somewhere scoring under 30. They would see honest, well-built empty states — and read
them as a broken product. You would learn that people dislike empty screens, which
nobody needed a pilot to establish, while burning the goodwill of 74 students and the
faculty who introduced them.

**A narrow pilot measures the product. A broad one measures the knowledge gap you have
already measured.**

---

## 1. Entry gates

Nothing is recruited until these hold. All three are from `PRODUCT_BACKLOG.md`.

### Gate A — deployment (1–2 days)

- [ ] `DEPLOYMENT_CHECKLIST.md` complete through §10
- [ ] Second consecutive sync reports **0 inserted, 0 updated**
- [ ] Smoke test passes with **non-resolving** skills too, and the result reads as
      *incomplete* rather than *broken*

### Gate B — knowledge (6–7 days, runs in parallel)

- [ ] **K5 first** — Package006 completed: `VERSION`, `README`, `CHANGELOG`,
      `package_manifest.json`, `validate.py`, populated `metadata/` and `registry/`;
      duplicate `Package006_Skills/` deleted. **This gates K1** — without a validator
      there is nothing to validate 40 new skills against
- [ ] **K1** — ~40 backlog skills collected **with edges**. Onboarding resolve rate
      moves from **22.8%** toward 60%+
- [ ] **K2** — top 40 entities human-reviewed. From **0 of 2,299** to something
- [ ] **K3** — 21 orphan government schemes connected (currently 47.5% connected,
      median degree 0)

### Gate C — the simulation gate

Re-run the six-profile simulation from `VERSION1_READINESS_REPORT.md` §0.

| Requirement | Today | Required |
|---|---:|---:|
| Every profile fills ≥3 of 10 categories | 1–5 | **≥3** |
| No profile scores 0 on `skill_profile` | **4 of 6 score 0** | **0 of 6** |
| ≥1 non-editorial category fills for every profile | fails for 3 of 6 | **all 6** |

**This is the gate that decides launch.** The first two are logistics; this one is
whether the product works for a real person.

> Do not soften Gate C to hit a date. "Every student sees at least three kinds of
> recommendation, and at least one comes from researched knowledge rather than the
> editorial idea library" is the minimum bar for calling this a knowledge platform.

---

## 2. Cohort

### 100 students

| District | Students | Why |
|---|---:|---|
| Hyderabad | 40 | Score 85, 12 institutions, deepest graph |
| Guntur | 20 | Score 59, 6 institutions |
| Tirupati | 20 | Score 51, 7 institutions |
| Visakhapatnam | 20 | Score 50, 3 institutions |

Recruit **through 4–6 institutions**, not individually. Faculty introduction roughly
doubles completion in a 4-week pilot and gives you a channel for follow-up.

**Deliberate skill mix** — this is where the real learning is:

| Group | n | Skills | Expected today |
|---|---:|---|---|
| **A — resolving** | 30 | Welding, Food Processing, Tailoring, Electrician, Plumbing | 4–5 of 10 categories |
| **B — non-resolving** | 40 | Digital Marketing, Accounting, Data Entry, Teaching, Graphic Design | **1–2 of 10** |
| **C — unconstrained** | 30 | Whatever they actually have | Unknown — the most valuable group |

**Group B is not a control group to be pitied — it is the measurement.** 40 students
typing their real skills produce the ranked collection backlog that v1.1 works from.
Group C is where you find the skills nobody thought to put on a list.

### 10 faculty

Two or three per institution. They need something different from students: a view of
their cohort, and a way to say "this recommendation is wrong."

**There is no faculty view in the product.** Accept that for the pilot — faculty use a
normal account plus a weekly 30-minute call. Do not build a faculty dashboard for 10
people; find out what they ask for first.

### 20 entrepreneurs

Recruited from the same four districts, ideally already operating in one of the 24
Industry sectors in the graph. They are the group most likely to catch a factual error
in the researched data, which makes them the best reviewers you have — and the
verification gap (0 of 2,299 rows reviewed) is the platform's largest.

**Ask each to review 5 entities in their sector.** Twenty entrepreneurs × 5 = 100
entities reviewed by domain practitioners. That is a better first review pass than any
amount of internal reading, and it converts a credibility gap into a feature of the
pilot.

---

## 3. Four weeks

### Week 0 — pre-flight

| | |
|---|---|
| Mon–Tue | Gates A and C verified; rollback rehearsed once |
| Wed | Faculty briefed. **Say plainly what is missing** — Teams and Startup Workspace do not exist; ~3 in 4 skills may not resolve yet |
| Thu | 10 faculty onboard themselves; fix what they trip over |
| Fri | Entrepreneur cohort onboards; assign 5 review entities each |

Faculty onboarding first is not politeness. They will find the confusing parts before
100 students do, and their trust is the recruitment channel.

### Week 1 — students onboard

Target: **80 of 100 complete onboarding**, 60 complete the assessment.

Watch daily:

- Drop-off point in onboarding (which field?)
- **Every skill string typed** — this is the primary research output
- Recommendation counts by group A/B/C
- Any page that errors rather than empties

> ⚠️ `/discover` persists only via an opt-in button inside a secondary "network" tab
> and requires sign-in, and the route is not auth-gated (backlog A3). **Expect
> assessment results to be lost.** Instrument this in week 1 rather than discovering
> it in the week-4 numbers.

### Week 2 — depth

Target: 50 students return at least once.

- Recommendation-outcome capture live (§5) — **launch requirement, not analytics**
- Entrepreneur reviews land; first corrections flow back into packages
- First skill-collection sprint from week 1's typed strings
- Faculty call #1

### Week 3 — connections

Target: 30 connection requests, 15 accepted.

Connections and the collaborator marketplace are the most complete part of the product
and they need a critical mass that a 130-person cohort can just about reach. Watch
whether `skillOverlap` produces overlaps people find meaningful — it is real data, so
this is a genuine test of the matching idea.

### Week 4 — close

- Exit survey: all 130
- 20-minute interviews: 15 students, all 10 faculty, 8 entrepreneurs
- Ranked skill backlog published
- Go/No-Go for general launch

---

## 4. Success metrics

Thresholds are set against **measured current behaviour**, not aspiration.

### Tier 1 — does it work at all

| # | Metric | Target | Baseline |
|---|---|---:|---|
| 1 | Onboarding completion | **≥70%** | Unmeasured |
| 2 | Users with ≥3 filled categories | **≥80%** | 33% (2 of 6 profiles) |
| 3 | Users with `skill_profile` > 0 | **≥75%** | 33% (2 of 6) |
| 4 | Sessions with a runtime error | **<2%** | 0 prerender errors at build |
| 5 | Skill terms resolving | **≥60%** | **22.8%** |

Metric 5 is the one to put on the wall. Every other number moves with it.

### Tier 2 — is it useful

| # | Metric | Target |
|---|---|---:|
| 6 | Return within 7 days | ≥40% |
| 7 | Recommendations marked "useful" | ≥50% of rated |
| 8 | Users rating ≥1 recommendation | ≥60% |
| 9 | Connection requests sent | ≥30 |
| 10 | Acceptance rate | ≥50% |
| 11 | Median session (returning) | ≥4 min |

### Tier 3 — is it trusted

| # | Metric | Target | Why |
|---|---|---:|---|
| 12 | Users who open a provenance line | ≥20% | Does anyone check the sources? |
| 13 | Factual corrections reported | **≥15** | High is **good** — it means people are reading closely |
| 14 | Entities reviewed by entrepreneurs | **≥100** | From 0 of 2,299 |
| 15 | "I trust this data" agreement | ≥60% | Against a visible `UnverifiedNotice` |

**Metric 13 is deliberately inverted.** A pilot with zero corrections reported on
2,299 unreviewed rows means nobody looked hard enough to be useful.

### Tier 4 — what to build next

| # | Metric | Purpose |
|---|---|---|
| 16 | Ranked list of unresolved skill terms | Direct input to v1.1 collection |
| 17 | Districts requested but under-covered | Which of the other 57 to deepen |
| 18 | Feature requests, ranked | Does anyone actually ask for Teams? |
| 19 | Where users expected data and found none | Finds gaps not on any list |

**Metric 18 is worth stating.** The stated journey has Teams and Startup Workspace as
stages 8 and 9 — 14 days of product work. Nobody has confirmed users want them.
**If the pilot does not ask for them, that is 14 days saved and better spent on
skills.**

### Pilot-level Go/No-Go for general launch

| Outcome | Meaning |
|---|---|
| **Strong GO** | Metrics 1–5 met, ≥8 of 11 in Tier 2, ≥15 corrections |
| **Conditional** | Tier 1 met, Tier 2 mixed → fix the specific gaps, extend 4 weeks |
| **NO-GO** | Metric 3 or 5 missed → the knowledge base is the product and it is not ready. More districts will not fix it |

---

## 5. Feedback collection

### In-product — must exist at launch

**One thumbs up/down plus an optional reason on every recommendation card.**

Not an analytics nicety. `RULE_ENGINE.md` §4 states the 23 scoring weights are
*reasoned, not calibrated*, and that nothing in the platform records whether a
recommendation was useful — which is why the v2.1 audit named calibration as blocked.

**This pilot is the first chance to create that signal.** Capture:

```
user_id · rules_version · category · item_id · match_score
        · confidence · useful(bool) · reason(text) · timestamp
```

`rules_version` matters: recommendations are keyed `(user_id, rules_version)` so a
rating stays attributable after the rules change.

Also needed:

- **"Report an error"** on every provenance line → resolves to a package/dataset/row,
  so a correction lands where the data lives rather than in an inbox
- **"I expected something here"** on every empty state — the highest-value signal in
  the pilot, because it finds gaps that are on no list

### Weekly — faculty

30 minutes, same three questions each week:

1. What did your students ask you that the platform should have answered?
2. What did you see that was wrong?
3. What did they stop using after week 1?

### Structured — exit survey (all 130)

12 questions max, mixed scale and free text. Non-negotiable items:

- Did the recommendations reflect your skills? *(tests metric 3 subjectively)*
- Did you trust the data? Why?
- What did you look for and not find?
- Would you use this next semester?
- One sentence: what is this platform for?

The last question is a positioning test. If 130 people cannot describe it
consistently, the problem is not the knowledge base.

### Interviews — 33 people

15 students (5 from each skill group), 10 faculty, 8 entrepreneurs. 20 minutes.
**Weight Group B heaviest** — the students whose skills did not resolve are the ones
whose experience v1.1 has to fix.

---

## 6. What to tell the cohort

Say this in the briefing, in writing, before anyone signs up:

> ValueWeave is a research platform in pilot. It holds **2,299 researched rows** about
> Telangana and Andhra Pradesh — districts, skills, government schemes, businesses,
> crops, MSMEs — every one traceable to a public source.
>
> **None of it has been reviewed by a human yet.** You will see a notice saying so on
> every page that shows it. Treat it as a well-sourced starting point, not a verified
> answer, and please tell us when it is wrong.
>
> Some things do not exist yet: **team workspaces**, **mentor matching**, and **event
> deadlines**. The platform will tell you which of those it cannot do rather than
> showing you a guess.
>
> If you enter a skill we have not researched, you will see fewer recommendations.
> That is a gap in our data, not a judgement about your skill — and telling us which
> skill it was is the most useful thing you can do in this pilot.

**Say it plainly and up front.** The platform's entire architecture is built to
distinguish "we measured and found nothing" from "we cannot measure this." Briefing
the cohort in the same register is consistent — and it converts the biggest weakness
into a reason to participate.

---

## 7. Risks

| Risk | L | Impact | Mitigation |
|---|---|---|---|
| Group B reads empty as broken | **High** | Bad word of mouth through faculty | Brief explicitly (§6); frame them as researchers |
| Assessment results lost | **High** | Journey stage 3 silently fails | Instrument week 1; fix A3 if it bites |
| Teams asked for immediately | Medium | Journey looks incomplete | Say up front it does not exist; **let demand decide** |
| Exposed-schemas step missed | Medium | Total silent emptiness | `DEPLOYMENT_CHECKLIST.md` §4; boxed off for this reason |
| A factual error embarrasses a faculty member | Medium | Institutional trust | K2 review first; make correction one click |
| Nobody rates a recommendation | Medium | No calibration signal, again | Single tap, on the card, no modal |
| `/skills` says skills don't exist while dashboard recommends them | Medium | Reads as a bug | Backlog A1 before the pilot if it fits; otherwise brief faculty |
| 500 synthetic opportunities taken as real | **High** | Undermines the provenance story | `DEPLOYMENT_CHECKLIST.md` §3 — label or remove. **Decide before launch** |

---

## 8. After the pilot

The pilot's real deliverable is not a usage report. It is **three ranked lists**:

1. **Skills to collect**, ranked by how many students typed them
2. **Districts to deepen**, ranked by where students actually are
3. **Features to build**, ranked by what people asked for unprompted

List 3 decides whether Teams and Startup Workspace — 14 days of the Medium backlog —
are v1.1 or never. Right now that is a guess dressed as a roadmap, and 130 users can
settle it.

Lists 1 and 2 are the ones that move metrics 3 and 5, which are the ones that matter.
