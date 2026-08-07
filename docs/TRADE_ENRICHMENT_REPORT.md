# Trade Enrichment Report — Skilled Trades

What three supplied career datasets — 50 skilled trades across 140 pages —
contributed to the ValueWeave Knowledge Graph, what they could not contribute,
and why the line falls where it does.

| | A · Electrician | B · Construction | C · Manufacturing |
|---|---|---|---|
| pages | 36 | 48 | 56 |
| roles | 20 | 15 | 15 |
| against the graph | 12 merge, 8 new | 15 new, 0 merge | 4 merge, 11 new |
| concepts kept | 3 | 8 | **2 of 9 written** |
| queries corrected | 4 | **9** | 4 |
| queries newly answered | 4 | 7 | 1 |

**Document B gave the most. Document C gave the least — and cost the most to
find that out.** Nine concepts were written for C, measured, and six deleted
again because they made results *worse*. That episode is §11 and is the most
useful thing in this report.

---

## 1. The source, and what it says about itself

| | |
|---|---|
| document | *Electrician and Similar Role Career Decision Dataset* |
| pages | 36 |
| roles covered | 20 |
| origin | DeepSeek-generated, supplied by the maintainer |
| normalised to | `research/sources/electrician_trades_2026.py` |

Three things the document states about itself decide how it is treated:

> *"Contacts replaced with placeholder XXXX; verify from official websites."*

> *"Confidence is moderate for salary and fees, based on typical ranges."*

> *"I will now generate datasets for the remaining 18 roles… Due to length
> constraints, I will now output the remaining 16 datasets in a compact form."*

The third is the author narrating their own token budget. It is a useful
signal: detail falls off sharply after role four, and the last twelve roles are
a paragraph each. Confidence is scored accordingly and nothing exceeds **60**,
the repository's ceiling for a single uncorroborated secondary source.

### A defect in the source that had to be caught

**The Telugu in the PDF is damaged and none of it was used.** Text extraction
dropped the conjunct clusters:

| the document means | what extraction produced |
|---|---|
| ఎలక్ట్రిషియన్ | `ఎలక` |
| టెక్నీషియన్ | `టెక` |
| వ్యక్తి | `వ్యక` |
| లిఫ్ట్ | `లి ్ట` |

Copying any of it into the search index would have created permanent dead
entries — strings no reader will ever type. Every Telugu term used is either
already present and correct in `concepts.js` or verified character by character.
`tests/test_trade_vocabulary.py` asserts the damaged fragments never appear.

---

## 2. Entity enrichment — 12 merge, 8 new

Determined by reading `knowledge_graph/entities/entities.csv`, not by guessing
from names. Two roles that looked new — **Painter** and **Tile & Marble Fixer** —
have a `BusinessOpportunity` but no `Skill`, so they are new *as skills*.

### Merge onto an existing Skill (12)

| document role | existing entity | what it adds |
|---|---|---|
| Electrician | Electrician (Domestic Wiring) | 6 aliases, tools, 3-tier skills, 8-step ladder, 15 related careers |
| EV Technician | EV Technician | 4 aliases, HV safety tools, CAN/BMS skills, 13 related |
| Solar PV Installer | Solar Panel Installation & Maintenance | Suryamitra term, MC4 toolkit, 15 related |
| AC & Refrigeration | HVAC Technician | RAC/fridge terms, gauge manifold set, 14 related |
| Plumber | Plumbing | pipe fitter/steam fitter, threading tools |
| Welder | Welding (MIG/TIG/Arc) | arc/MIG/TIG/coded grades, 9 related |
| Carpenter | Carpentry | joiner, modular kitchen installer |
| Mason | Masonry & Brickwork | bricklayer, plasterer |
| CNC Machine Operator | CNC Machine Operator | VMC/turn-mill, 5-axis progression |
| Industrial Electrician | Industrial Electrician | megger/clamp meter, VFD & switchgear |
| Industrial Automation (PLC) | PLC Programming & Control Systems | SCADA/HMI, integrator path |
| Robotics Technician | Industrial Robotics | cobot, teach pendant, RoboDK |

**No existing entity was overwritten.** The enrichment that shipped is
vocabulary only; the field-level content above is attached to review candidates
where it needs a person.

### New — queued for review (8)

`lift-technician` · `tile-marble-fixer` · `fabricator` · `painter` ·
`steel-fixer` · `scaffolding-technician` · `machine-maintenance-technician` ·
`mechatronics-technician`

These are in `collection/state/review_queue.jsonl` as `NEEDS_REVIEW`, each
carrying the full extracted role as its raw record. They are **not** in any
package and no reader can see them.

---

## 3. What shipped, and what it actually fixed

The **vocabulary** shipped. That an employer says "RAC mechanic" and a student
says "fridge mechanic" and both mean the HVAC trade is not a claim needing a
citation — it is how the words are used, and it is checkable by asking the
search engine.

**63 English aliases** across 11 concepts, plus **3 new concepts**
(`cnc`, `industrial-electrician`, `plc-automation`) — each added only because
its entity already exists, which is the concept table's own rule.

### Measured against the real 647-entity graph, before and after

Coverage barely moved — 4 of 22 probe queries went from nothing to something
(`suryamitra`, `joiner`, `scaffolder`, `bricklayer`). The ranker's fuzzy and
related rungs already reached most terms.

**The gain was in being right.** Four queries had a confident wrong answer:

| query | before | after |
|---|---|---|
| `rac mechanic` | **Automobile Mechanic** (RELATED 127) | HVAC Technician (EXACT 1033) |
| `fridge mechanic` | **Automobile Mechanic** (RELATED 127) | HVAC Technician (EXACT 1033) |
| `factory electrician` | **Manufacturing** (EXACT 928) | Industrial Electrician (EXACT 1039) |
| `pipe fitter` | **Filter Press** (RELATED 121) | Plumbing (RELATED 170) |

A search that returns nothing tells a student to try other words. A search that
confidently returns *Filter Press* for "pipe fitter" tells them the platform
knows nothing useful, and they leave.

Two further promotions: `vmc operator` and `tile setter` moved from RELATED to
PREFIX; `cobot` from FUZZY to EXACT. **No regressions** across 22 queries.

### Two defects found while doing this

**Phonetic collisions.** Putting "factory electrician", "maintenance
electrician" and "electrical fitter" on *both* `electrician` and
`industrial-electrician` made those phrases ambiguous. `test_multilingual_search`
refused the build. They belong on the specific concept.

**The silent b in "plumber".** `plumer` and `plummer` returned **nothing**. The
phonetic key is a consonant skeleton, so it fixes vowel errors for free
(`solor`, `masson`, `tiels`, `electrition` all resolve) but cannot bridge a
*missing consonant*: `plmr` never meets `plmbr`. Isolated by testing `plumbr`
(b kept, e dropped), which resolves fine.

"Plumber" has a silent b. Dropping it is not a typo — it is a phonetically
correct spelling by somebody who has heard the word and not read it, which is
exactly this platform's reader. This is the one documented exception to the
concept table's "do not enumerate spellings" rule, licensed by that rule's own
rationale failing here.

---

## 4. Connected Knowledge

The document's per-role **"Related Careers"** lists are its richest structural
content: **119 distinct career mentions** across 20 roles, hand-written as
trade adjacency rather than derived from a co-occurrence statistic.

**19 already match an entity in the graph** and are proposable edges today.
The rest name trades ValueWeave does not hold (Cable Jointer, Boilermaker,
Energy Auditor, Metro Rail Technician…) and are **research backlog**, not edges.

Relationship type for all of them: `RELATED_SKILL` — the document asserts
adjacency, not prerequisite. Reading "Electrician → Solar PV Installer" as
`REQUIRES` would invent a dependency the source never claimed.

**Not written.** Edges belong to the graph builder, and proposing 119 of them
from one secondary source would swamp the review queue with material whose
correct disposition is mostly "yes, obviously" — which trains reviewers to
approve without reading. They are recorded here and in the candidates' raw
records for a person to work through deliberately.

---

## 5. RSS readiness

The document's **17 official references** are the genuinely verifiable content
in it — well-known government domains, checkable in a browser:

`nsdcindia.org` · `skillindia.gov.in` · `pmkvyofficial.org` · `msde.gov.in` ·
`dgt.gov.in` · `ititelangana.gov.in` · `itiap.gov.in` ·
`apprenticeshipindia.gov.in` · `tssouthernpower.com` · `apeasternpower.com` ·
`asdc.org.in` · `task.telangana.gov.in` · `apssdc.in` · `mnre.gov.in` ·
`nise.res.in` · `tsredco.telangana.gov.in` · `nredcap.in`

They are in `OFFICIAL_REFERENCES` and are good seeds for
`collection/registry/monitored_sources.csv`.

**Not registered as sources yet, deliberately.** Every one needs
`collection.cli verify` run against it from a network that can reach it, and
this sandbox's proxy 403s all government hosts. Registering ten unverified
sources would put ten rows in the registry that have never been fetched. The
runbook's rule stands: one source per pull request, verified first.

Tracking keywords for when they are: *ITI admission, apprenticeship
notification, PMKVY batch, Suryamitra training, electrical contractor licence,
skill development tender, RAC trade, lift mechanic curriculum, EV technician
certification, ASDC.*

---

## 6. What was deliberately NOT taken

| content | why not |
|---|---|
| Salary bands (all 20 roles) | self-declared estimates; a student planning on a wrong number is worse served than one told nothing |
| Course fees | same |
| Institute phone numbers | literal `XXXX` placeholders in the source |
| Institute websites, placement claims | unverified against the institutions |
| Named hiring companies | recruitment claims change monthly and this is a static document |
| Telugu strings | extraction-damaged (§1) |
| 70 tools as `Machinery` entities | tools are attributes of a trade, not entities; `Machinery` in this graph means industrial plant |

`UNVERIFIED_FIELDS` in the source module names the first four so the promoter
blanks them mechanically rather than relying on anyone to remember.

---

## 7. Files changed

| file | change |
|---|---|
| `research/sources/electrician_trades_2026.py` | **new** — normalised 20 roles with provenance and per-role confidence |
| `research/sources/emit_candidates.py` | **new** — the 8 new roles into the review queue |
| `frontend/lib/search/vocabulary/concepts.js` | 63 aliases across 11 concepts, 3 new concepts |
| `tests/test_trade_vocabulary.py` | **new** — 12 tests |
| `collection/state/review_queue.jsonl` | +8 candidates, `NEEDS_REVIEW` |

Architecture unchanged. No package modified, no entity overwritten, no
relationship written, no schema touched.

---

## 8. What a person should do next

```bash
# read the eight proposed trades
python3 -m collection.cli queue --state NEEDS_REVIEW

# for one you want, check it against DGT's trade list, then
python3 -m collection.cli review  doc-electrician-trades-2026:lift-technician \
    --actor YOUR.NAME --evidence https://dgt.gov.in/...
python3 -m collection.cli approve doc-electrician-trades-2026:lift-technician \
    --actor YOUR.NAME

# see the package row it becomes, then write it
python3 -m collection.cli promote
python3 -m collection.cli promote --write
```

The DGT trade list is the right primary source for all eight: every one is or
maps to a recognised ITI trade, which makes the existence claim verifiable in a
single place. Salary and fee figures need a second source and should stay
`PENDING_VERIFICATION` until they have one.

See `docs/COLLECTION_RUNBOOK.md`.

---

## 9. Document B — Construction & Infrastructure

*48 pages, 15 trades, TG/AP focus. Normalised to
`research/sources/construction_trades_2026.py`.*

### It is the better-made document, and that cuts both ways

| | document A | document B |
|---|---|---|
| `XXXX` placeholder contacts | 5 institutes | **none** |
| institute web addresses | invented | real (`itimallepally.telangana.gov.in`, `iti.ap.gov.in`) |
| self-declared confidence caveat | yes | **none** |

The last row is not a point in its favour. Document A told the reader where it
was weak; B does not, which makes it *less* self-aware rather than more
reliable. Its salary tables are uncited all the same. Confidence ceiling stays
**60**, and the reviewer note on every candidate says so explicitly:
*"absence of a caveat is not evidence of accuracy."*

### The finding that matters: a business you cannot learn

All fifteen trades are absent from the graph as Skills. **Five already exist as
businesses:**

| trade (no Skill) | business the graph already offers |
|---|---|
| False Ceiling Installer | POP Works / False Ceiling Installation |
| POP Gypsum Technician | POP Works / False Ceiling Installation |
| Aluminium Fabricator | Aluminium Fabrication |
| Borewell Technician | Borewell Drilling Services |
| Pump Technician | Submersible Pump Installation & Repair |

So today a reader can find *"you could start a borewell drilling business"* and
nothing at all about learning to do the work. That asymmetry is the single most
useful thing this document exposes, and it is what the candidates point at —
each one's `classified_reason` names the orphaned business.

### A copy-paste defect in the source, caught and not propagated

**ROLE 3 (Aluminium Fabricator) lists ROLE 4's alternative job titles verbatim**
— *"uPVC Window Technician, Fenestration Installer, uPVC Fitting Specialist"*.
Aluminium fabrication and uPVC fitting are different trades with different
materials, and the document's own tool tables for the two roles disagree, which
is what makes the copy-paste visible.

The wrong aliases are not carried across. That role's confidence is dropped to
**45** and its `notes` field records the defect.

### What it fixed — 16 of 22 queries, 9 of them wrong answers

| query | before | after |
|---|---|---|
| `crane operator` | **Maize** (EXACT) | Construction & Skilled Trades |
| `tower crane` | **Maize** (EXACT) | Construction & Skilled Trades |
| `road roller` | **Microcontroller Programming** | Construction & Skilled Trades |
| `jcb driver` | **PLC, Drives, Sensors and Cabling** | Construction & Skilled Trades |
| `pump technician` | **Field Technician – Computing & Peripherals** | Submersible Pump Installation & Repair |
| `borewell technician` | **Field Technician – Computing & Peripherals** | Borewell Drilling Services |
| `modular kitchen` | **Cloud Kitchen** | Carpentry |
| `aluminium fabricator` | **Welding (MIG/TIG/Arc)** | Aluminium Fabrication (EXACT) |
| `pop plasterer` | **Masonry & Brickwork** | POP Works / False Ceiling Installation |

Newly answered (returned nothing before): `gypsum`, `drywall`, `glazier`,
`upvc window`, `jcb`, `roofing`, `earthmover`. **No regressions.**

Eight new concepts: `false-ceiling`, `aluminium-fabrication`, `borewell`,
`pump-technician`, `heavy-equipment-operator`, `waterproofing`,
`modular-kitchen`, `roofing`.

### A real search bug this exposed: crane → Maize

`crane` and `corn` reduce to the same consonant skeleton, **`krn`**. The
phonetic layer therefore resolved "crane operator" to the `maize` concept —
whose English alias is "corn" — and returned **Maize** on an EXACT match, at
the top, for a trade that builds the Hyderabad metro.

The multi-word forms are fixed by explicit aliases, which resolve through the
ALIAS layer and never let the phonetic layer fire.

**The bare word `crane` is NOT fixed, deliberately.** Adding it was tried and
rejected by `test_no_two_concepts_share_a_phonetic_key`: two concepts may not
claim one key, because a collision silently disables one of their Tanglish
paths. So "corn" and "crane" cannot both be aliases — and "corn" is the English
name of a crop grown across both states. A farmer looking up maize outranks the
one-word form of a query that works in every other phrasing.

Fixing it properly means changing when the phonetic layer may fire, which is a
search-engine change and out of scope. `test_the_bare_word_crane_is_a_known_and_recorded_limitation`
pins it: **if that test ever fails, the bug has been fixed and this section is
stale.**

### Three concepts considered and rejected

| concept | why not |
|---|---|
| `granite` | "granite" and "grant" both key to `grnt`. A reader looking for a government grant is a query this platform exists to answer; "granite cutter" already reaches Tiles Fixing on a PREFIX match with no concept at all. |
| `digger` (in heavy equipment) | keys to `dgr`, same as "degree" under `education`. "excavator", "jcb" and "backhoe" reach the same place. |
| `waterproofing` → itself | no entity is named waterproofing, so the expansion cost a query and returned silence. Repointed at `painting` + `construction`. |

### Machinery was not created as entities

The document prices thirteen machines from ₹22 lakh (soil compactor) to ₹90
lakh (asphalt paver). These are **capital plant, not a toolkit**, and the
distinction matters: telling a student a trade needs "₹90 lakh of tools" when
the employer owns the machine would misrepresent the entry cost of the job.
Recorded in each role's `tools` as employer-owned and flagged in `notes`.

---

## 10. Combined position

| | |
|---|---|
| documents processed | 2 |
| trades read | 35 |
| review candidates | **23** (8 + 15), all `NEEDS_REVIEW` |
| concepts added | 11 |
| aliases added | 63 |
| queries corrected from a wrong answer | **13** |
| queries newly answered | 11 |
| regressions | 0 |
| entities overwritten | 0 |
| packages modified | 0 |

```bash
python3 -m research.sources.emit_candidates --doc construction   # dry
python3 -m research.sources.emit_candidates --write              # both
python3 -m collection.cli queue --state NEEDS_REVIEW
```

The DGT trade list remains the right primary source for the electrician set.
For the construction set the better anchors are the **NSQF/NCVT qualification
packs** for construction trades and the **CSDCI** (Construction Skill
Development Council of India) role list — several of these trades (False
Ceiling Installer, Glazier, Bar Bender) are CSDCI-recognised job roles, which
makes the existence claim checkable in one place.

---

## 11. Document C — Manufacturing & Factory Careers

*56 pages, 15 machine-shop and factory-floor trades. Normalised to
`research/sources/manufacturing_trades_2026.py`.*

### It makes the strongest self-claim of the three

Its first page:

> *"Where exact data is unavailable, a confidence note is added.
> **No statistics are invented.**"*

and it closes with the most candid provenance note of the three documents —
naming Naukri and Indeed as salary sources, dating them to 2025, and saying
institute contacts should still be confirmed.

That is genuinely better than either of the others. It is still not a citation:
*"based on market surveys"* names no survey and links to nothing, and
*"verified"* is the author's assertion about their own process. The claim is
also only sparsely honoured — the string "Confidence" appears **eight times
across 56 pages and fifteen roles**. Ceiling stays 60.

### Three roles are one trade

The document presents **Lathe Machine Operator (1)**, **Turner (11)** and
**Machinist (12)** as separate careers — while role 1 lists *"Turner"* among
its own alternative job titles. The graph is right: `Lathe Operation` is one
Skill. All three are recorded as merges onto it.

Role 11 also carries **role 12's alternative titles verbatim** ("All-round
Machinist, Machine Shop Machinist, General Machinist"). That is the third
copy-paste defect across three documents — after document B's ROLE 3 — which
makes it a property of how these files are generated rather than a one-off.
Not propagated; confidence dropped to 45.

### A cross-document collision the deduper cannot see

Role 10 **Fitter** shares *"Mechanical Fitter"* and *"Maintenance Fitter"* with
`machine-maintenance-technician`, already queued from document A. They are
close to the same trade.

**`collection/dedupe.py` scores the two titles at 0.00 against its 0.80
threshold.** It compares *titles*, and these are two different words for one
job. Nothing automatic will catch it — a real limit of the deduper, visible
only once there were three documents instead of one. Surfaced by hand in the
candidate's raw record so the reviewer decides them together.

### The mistake this document caught me making

Eleven of its fifteen trades have no entity to point a concept at. I reached
for `expands_to: ["manufacturing"]` as a catch-all on six concepts.

That term matches every entity with the word in its name, and
**"Masala Powder Manufacturing Unit" became the top hit for eleven separate
queries** — tool and die maker, quality inspector, hydraulic technician,
assembly line, bench fitter, die maker and more. *Worse* than the wrong answers
it replaced.

All six were deleted, plus `milling`, which moved "milling machine operator"
from *Tractor* to *Dal Milling Unit* — differently wrong, not better.

**The rule, now tested:** an expansion must name a THING the graph holds, not
the sector it sits in. Document A stated it; this is the measurement that gave
it teeth. `test_a_concept_must_name_a_thing_not_a_sector` enforces it, and
`test_masala_powder_is_not_the_answer_to_a_machine_shop_question` guards the
specific regression.

### What survived — two concepts

| query | before | after |
|---|---|---|
| `turner` | **— nothing —** | Lathe Operation |
| `machinist` | **CNC Machining Job Shop** (a business) | Lathe Operation |
| `lathe operator` | CNC Machine Operator | Lathe Operation |
| `press operator` | **Cold-Pressed Groundnut/Sesame Oil Unit** | Sheet Metal Fabrication Unit |

Both senses of "press" are real; only one is a factory job.

### Eleven trades left with no vocabulary, on purpose

`tool and die maker` still returns *Telangana Homestays*. `assembly line` still
returns *Alkaline*. `bench fitter` still returns *Bank of Baroda*. These are
bad results and they are **not fixable by vocabulary** — there is no entity in
the graph for a reader to be sent to. Inventing one would be fabrication;
pointing at a sector made it worse.

They are fixed by **approving the candidates**, which creates the entities the
words can then point at. That is the queue's job, and it is the clearest
demonstration in this whole exercise of why the split exists.

---

## 12. Combined position — three documents

| | |
|---|---|
| documents processed | 3 |
| pages read | 140 |
| trades read | 50 |
| review candidates | **34** (8 + 15 + 11), all `NEEDS_REVIEW` |
| concepts added | 13 kept, 7 written-and-deleted |
| aliases added | 63 |
| queries corrected from a wrong answer | **17** |
| queries newly answered | 12 |
| regressions | 0 |
| entities overwritten | 0 |
| packages modified | 0 |

### What three documents taught that one could not

1. **The copy-paste defect is systemic.** Documents B and C each carry a role
   whose alternative titles belong to its neighbour. Expect it in the next one
   and check the tool tables against each other — that is what makes it visible.
2. **The deduper only sees titles.** Two documents can queue the same trade
   under different names and nothing will notice.
3. **A concept needs a thing, not a sector.** Reaching for a broad anchor when
   a trade has none makes search worse than leaving it alone.
4. **Self-declared caveats vary and must be quoted, not summarised.** An early
   version of the reviewer note hard-coded document A's `XXXX` caveat for every
   document that declared anything, so document C's candidates claimed
   placeholder contacts it does not have. Fixed; `ReviewerNoteTest` pins it.

```bash
python3 -m research.sources.emit_candidates --doc manufacturing   # dry
python3 -m research.sources.emit_candidates --write               # all three
python3 -m collection.cli queue --state NEEDS_REVIEW
```

Primary sources to review against: **DGT trade list** (document A), **CSDCI
role list** (document B), and for document C the **Capital Goods Skill Council**
qualification packs — Lathe Operator, Fitter, Tool & Die Maker and Quality
Inspector are all CGSC-recognised job roles with published NSQF levels, which
makes both the existence claim and the level checkable in one place.
