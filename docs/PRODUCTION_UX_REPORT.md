# Production UX Report

**ValueWeave v1.0 · Production UX Polish Sprint**

What a student, an entrepreneur or a job seeker now meets, and what they used to.

---

## The change in one paragraph

ValueWeave was built in five engineering sprints, and each one left its
vocabulary on the screen. The platform did not describe opportunities to a
student; it described its own architecture to them. A first-year student looking
for a welding course in Warangal could be shown a sentence naming a shell script,
a migration and a checklist filename. Under every card sat
`Package008_MSME · businesses.csv · B-014`. The most useful block on six page
types was titled "AI-readable summary" — which told the reader it was not for
them. Meanwhile the first link on the landing page 404'd.

**65 occurrences of internal vocabulary across 21 files are gone, and the 404 is
fixed.** The technology is unchanged and now invisible.

---

## Before and after

| Where | Before | Now |
|---|---|---|
| Landing · featured opportunity | 404 | Opens the opportunity |
| Landing · video | "Video coming soon" | "Video coming shortly" + link to the YouTube channel |
| Landing · roadmap | "No package covers patents, TRLs or tech transfer" | "We have not started gathering this yet" |
| Landing · explore | "647 researched records across Packages 001–008" | "647 things to explore" |
| Search · heading | "Search the Knowledge Base" | "What are you looking for?" |
| Search · description | "Searches 647 sourced entities across Packages 001–008. Rule-based substring matching — no AI" | "Find a district, a skill worth learning, a business you could start or a government scheme you may qualify for" |
| Explorer · heading | "Everything we have researched" | "What would you like to explore?" |
| Explorer · search box | "Search researched knowledge…" | "Try a district, a skill, or a business idea…" |
| Any card · source | `Package008_MSME · businesses.csv · B-014` | "From our small business research" |
| Any card · badge | "Package006 · Skills & Training" | "Skills & training research" |
| Empty state · not deployed | "The knowledge schema has not been deployed to this environment. **Depends on:** …`scripts/run_sync.sh`… `docs/FIRST_DEPLOYMENT_CHECKLIST.md` steps 5–10" | "This information is being prepared. Nothing is wrong with your account, and nothing you did caused this." |
| Empty state · no research | "Nothing in Packages 001–008 covers this" | "Our team gathers information from official public sources, and we have not covered this area yet" |
| Dashboard · no matches | "Personalised recommendations are not switched on yet" | Block hidden, or "Tell us a little more and we'll suggest what fits you" + **Complete your profile →** |
| District · unmatched | "has no entry in the district vocabulary crosswalk" | "We have not linked our research to Medak yet. The profile above is still accurate." |
| District · panel | "What the knowledge base records for Medak" | "Opportunities in Medak" |
| Profile | "Knowledge graph profile · rule-based · no AI" | "Your readiness profile · based on your skills and district" |
| Opportunity page | "AI-readable opportunity summary" | "Opportunity Snapshot" |
| Verification notice | "Confidence scores describe source strength, not correctness" | "If you are about to apply for a scheme or invest money, confirm the details on the official website first" |

---

## Student-first: does each screen answer a question?

The brief's five questions: *What opportunity can I explore? What skill should I
learn? What business can I start? What government support is available? Who can I
collaborate with?*

| Page | Answers | How |
|---|---|---|
| Landing | all five | Six live entities across districts, industries, businesses, skills, schemes and crops, each with a count and a way in |
| Explorer | all five | Seven domains, 19 categories, each showing how many there are to explore |
| Search | all five | Ten filters, examples in the placeholder, one honest result set |
| Dashboard | opportunity, skill, business, support | Six personal rails, each showing why it was suggested |
| District detail | opportunity, business, support | Everything linked to that district, grouped |
| Business detail | business, skill, support | Investment, skills, schemes, markets, districts, training |
| Skill detail | skill | Where to train, what it unlocks, which schemes help |
| Scheme detail | support | What you get, how to apply, who it helps |
| Readiness | skill | 45 skills, 30 certifications, 25 training providers |
| Manufacturing | business | 45 opportunities, 69 pieces of equipment, 21 materials |
| Scale | business | 29 export destinations, 11 market channels, 21 funder types |
| Network | collaborate | Marketplace plus 66 institutions |
| Opportunity radar | opportunity | 40 ranked ideas, now labelled as editorial judgement |

---

## Where honesty was kept rather than smoothed away

Making the product friendlier is easy to overdo. Four places where the
uncomfortable version stayed:

**The verification notice.** It could have been dropped — it tells users our data
has not been checked line by line. It stayed and got blunter, because the
consequence is concrete: *"If you are about to apply for a scheme or invest
money, confirm the details on the official website first."*

**Scheme eligibility.** The obvious way to fill that section is to compose
something from `coverage` and `ideal_target_audience`. It would look complete. It
would be a fabricated eligibility rule for a government scheme, which is the one
error on this platform that could cost a user money. The section says we have not
published it and why.

**The opportunity radar's scores.** `fitScore: 91` is a hand-assigned editorial
judgement rendered as a `/100` badge with a progress bar — indistinguishable from
a computed rating. Both radar pages now say so.

**`/ai`.** The platform has a recommendation engine and it is rule-based on
purpose. Calling it an AI advisor would have been the single most misleading
change available in this sprint. The page says what it is: *"we compare your
skills and district against what we have researched, and always show you why."*

---

## What is preserved for operators

Nothing diagnostic was deleted. It moved out of the reading path:

| Signal | Where it lives now |
|---|---|
| Which of five empty states fired | `data-reason` on the element |
| Why (the runbook sentence) | `data-operator-note` |
| Source research area | `data-source-package` |
| Source dataset and row | `data-source-dataset`, `data-source-row`, plus the `title` on hover |
| Confidence value | still rendered, with a plainer tooltip |

Support can read all of it from an element inspector. A student meets none of it.

---

## Tests

`tests/test_production_ux.py` — **21 tests**, 6 classes, registered as
`production_ux`. Total **584 across 16 suites**, up from 563.

`DeveloperLanguageTest` is the one that matters. It greps every non-admin page
and component for fifteen banned patterns on every run. Three terms — `sync`,
`migration`, `deployment` — are deliberately *not* banned as bare words: they are
ordinary English, and a rule that produces false positives gets silenced rather
than obeyed. The phrases that actually leaked are banned instead.

It found three leaks I had missed by hand: "Knowledge graph" as a card title on
`/ai`, "Packages 007 and 008" on `/scale`, and "Packages 005 and 008" on
`/manufacturing`.

Two of my own assertions were wrong on the first run and were fixed rather than
loosened:

* the label test matched the `PACKAGE_LABELS` **keys**, which must stay — only
  the values are read by a person;
* the AI-readable test matched `data-ai-readable`, the machine attribute the
  rename deliberately preserved.

One earlier test was updated: `test_the_deployment_states_name_their_dependency`
became `test_the_deployment_states_keep_an_operator_note`, asserting the
diagnosis **moved** to `data-operator-note` rather than being deleted. Losing the
distinction between "not deployed" and "empty" would make the two states
genuinely indistinguishable, which is the failure Step 4 existed to prevent.

---

## Verification

```
Tests   584 passing, 16 suites, 0 failures, 0 errors
Build   ✓ Compiled successfully · ✓ 214/214 static pages · exit 0 · 0 warnings
Routes  49 public routes fetched from `next start` — 0 unexpected 404s
Log     0 errors, 0 warnings, 0 hydration mismatches
HTML    15 key pages fetched and grepped — no internal vocabulary rendered
```

`npx next lint` is **not** run: this project has no ESLint configuration and the
command prompts to create one. Setting one up would flag hundreds of pre-existing
issues unrelated to this sprint. The build's own type and syntax checking passes
clean, and that is the checking this repository actually has.

---

**Companions:** `CURRENT_REPOSITORY_STATE.md` · `CODEX_RECOVERY_REPORT.md` ·
`BUG_FIX_REPORT.md` · `DEPLOYMENT_REPORT.md`
