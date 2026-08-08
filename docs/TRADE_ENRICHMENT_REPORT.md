# Trade Enrichment Report — Skilled Trades

What five supplied career datasets — 80 skilled trades across 205 pages —
contributed to the ValueWeave Knowledge Graph, what they could not contribute,
and why the line falls where it does.

| | A · Electrician | B · Construction | C · Manufacturing | D · Automobile | E · Electronics |
|---|---|---|---|---|---|
| pages | 36 | 48 | 56 | 37 | 28 |
| roles | 20 | 15 | 15 | 15 | 15 |
| against the graph | 12 merge, 8 new | 15 new | 4 merge, 11 new | 5 merge, 10 new | 7 merge, 8 new |
| concepts kept | 3 | 8 | **2 of 9 written** | 3 of 5 written | 3 of 3 written |
| queries corrected | 4 | 9 | 4 | 10 | **22** |
| queries newly answered | 4 | 7 | 1 | 0 | 0 |

**E gave the most by a distance, because it started from the worst place.** All
four of its target Skills already existed and every probe query reached the
wrong one — `mobile repair` returned *Mobile App Development*, `smart home`
returned *Telangana Homestays*. Twenty-two wrong answers, three concepts, no
collisions to work around (§15).

**C gave the least and cost the most to find that out.** Nine concepts were
written for it, measured, and six deleted because they made results *worse* —
§11, the most useful passage in this report.

**Document D is the only one of the five whose stated method survives checking
against its own body** (§13). Document E is the only one that grades its own
confidence, and grades it highest while auditing itself least (§15).

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

---

## 13. Document D — Automobile & Mobility Careers

*37 pages, 15 automotive and EV-service trades. Normalised to
`research/sources/automobile_trades_2026.py`.*

### The only document whose stated method survives checking

It makes the same promise document C made:

> *"Where data gaps exist, 'Research Gap' is noted. **No statistics are
> invented.**"*

The difference is that it keeps it. **`Research Gap` appears 23 times across 37
pages.** Document C's equivalent marker appeared eight times across 56. That is
the one quality signal in this batch that could be checked against the body
rather than taken on trust — and it is the reason to read this document's gaps
as real gaps rather than as omissions.

It still ends with the familiar admission — *"for brevity, later role sections
assumed similar thoroughness"* — and the structure shows it: roles 1 and 2 have
full alias tables, roles 3 onward are condensed bullets. Where aliases are the
trade's rather than the document's, the row says so, and
`test_reconstructed_aliases_are_marked_as_such` holds that line.

Ceiling stays 60. Marking a gap honestly is good practice, not a citation.

### 5 merge, 10 new

Merging onto three existing Skills:

| document role | existing entity |
|---|---|
| Automobile Mechanic, Diesel Mechanic | Automobile Mechanic (Diesel/Petrol) |
| Bike Mechanic | Two-Wheeler Mechanic |
| BMS Technician, Diagnostic Technician | EV Technician |

New: Tractor Mechanic · Heavy Vehicle Technician · Battery Technician · Battery
Refurbishment · **EV Charging Station Technician** · Tyre Technician · Wheel
Alignment · Denting · Automotive Painting · Service Advisor.

**EV Charging Station Technician** is another *business you cannot learn* —
`EV Charging Station Operator` exists as an MSME with no matching skill.

### A disagreement between two documents, recorded rather than resolved

Document A lists **"Battery Technician"** as an *alias* of EV Technician. This
one makes it role 6 — a separate career with its own salary band and its own
PMKVY course.

Both readings are defensible; whether a specialisation is a career depends on
whether anyone hires for it alone. The graph has no Battery Technician entity
to settle it, so:

* **search follows document A** — the term resolves to the EV trade today;
* **the candidate follows document D** — a reviewer gets to decide.

Search should not wait on a taxonomy question, and a taxonomy question should
not be settled by whichever alias list was edited last.

### What it fixed — 10 of 21 queries, all of them wrong answers

| query | before | after |
|---|---|---|
| `car mechanic` | **Carpentry** | Automobile Mechanic |
| `bike mechanic` | Automobile Mechanic *(the car trade)* | Two-Wheeler Mechanic |
| `tractor mechanic` | **Electrical Contracting** | Automobile Mechanic |
| `heavy vehicle technician` | **Field Technician – Computing** | Automobile Mechanic |
| `bms technician` | **Field Technician – Computing** | Electric Vehicles |
| `auto electrician` | Electrician *(domestic wiring)* | Automobile Mechanic |

Zero newly-answered queries and zero regressions: the graph already had three
automotive Skills, so nothing was unreachable — a great deal was reachable and
wrong. `car mechanic` returning a woodworking trade is about as ordinary a
query as this platform will ever receive.

### A substring collision, and a funny one

**"tractor" is inside "con-TRACTOR-ing."** Expanding a tractor query to the
word `tractor` CONTAINS-matched *Electrical Contracting (Licensed Supervisor/
Contractor)* at 300, beating the 220 the actual trade scored. The expansion was
dropped — a tractor mechanic wants the mechanic trade, not the machine.

`test_no_concept_expands_to_the_word_tractor` guards the cause rather than the
symptom, exempting the farming concepts that legitimately mean the machine.

### Two concepts folded rather than added

`battery-technician` and `ev-charging` were written, collided with the existing
`electric-vehicle` concept, and were **merged into it** instead of competing.
That is also how the document-A disagreement above got its search-side answer:
the graph holds one EV trade, so the vocabulary holds one EV concept.

### Five trades left with no vocabulary

`tyre technician`, `wheel alignment`, `denting technician`, `service advisor`
and `puncture shop` still return nonsense — *Field Technician – Computing*,
*Instagram Shopping*. No entity exists to send a reader to, and pointing at a
sector is what made document C worse. They are fixed by approving the
candidates.

**Service Advisor is worth approving first.** It is the only non-manual role in
any of the four documents — the one automotive career reachable by somebody who
cannot do heavy physical work, and the graph has nothing like it.

---

## 14. Combined position — four documents

| | |
|---|---|
| documents processed | 4 |
| pages read | 177 |
| trades read | 65 |
| review candidates | **44** (8 + 15 + 11 + 10), all `NEEDS_REVIEW` |
| concepts | 16 kept, 9 written-and-deleted, 2 folded |
| aliases added | 71 |
| queries corrected from a wrong answer | **27** |
| queries newly answered | 12 |
| regressions | 0 |
| entities overwritten | 0 |
| packages modified | 0 |

### What four documents taught that one could not

1. **The copy-paste defect is systemic** — B and C each carry a role whose
   alternative titles belong to its neighbour. Check the tool tables against
   each other; that is what makes it visible. *(Overtaken by document E, which
   has fifteen clean alias lists: common, not universal — see §16.)*
2. **The deduper only sees titles.** Two documents can queue the same trade
   under different names and nothing notices (§11).
3. **A concept needs a thing, not a sector.** Reaching for a broad anchor when
   a trade has none makes search worse than leaving it alone (§11).
4. **Substrings bite.** `tractor` ⊂ `contractor`, `crane` ≈ `corn`,
   `granite` ≈ `grant`, `turning` ≈ `training`, `digger` ≈ `degree`. Five
   collisions across four documents — measure every expansion before keeping it.
5. **Documents disagree with each other, and that is information.** Battery
   Technician is an alias in A and a career in D. Record the disagreement;
   do not let the last edit win.
6. **A self-declared caveat can be checked.** C and D make the same promise;
   only D keeps it. Count the markers.

```bash
python3 -m research.sources.emit_candidates --doc automobile   # dry
python3 -m research.sources.emit_candidates --write            # all four
python3 -m collection.cli queue --state NEEDS_REVIEW --limit 60
```

Primary sources to review against: **DGT trade list** (A), **CSDCI role list**
(B), **Capital Goods Skill Council** packs (C), and for D the **Automotive
Skills Development Council (ASDC)** qualification packs — Automotive Battery
Technician, Tyre Service Technician and Service Advisor are all named ASDC job
roles with published NSQF levels, which the document itself cites and which
makes both the existence claim and the level checkable in one place.

---

## 15. Document E — Electrical & Electronics Careers

*28 pages, 15 electronics-service and low-voltage trades. Normalised to
`research/sources/electronics_trades_2026.py`.*

### The boldest claim paired with the thinnest self-audit

This is the only one of the five that grades itself:

> *"Confidence Level: **High**. Salary ranges reflect 2025-2026 Indian market
> realities for tier-1/tier-2 cities in TS/AP."*
> *"Research Gaps: Exact district-wise hiring numbers for private local
> integrators are not centrally tracked."*
> *"Graph Optimization: Headings and sub-bullets are standardized for
> automated JSON/Knowledge Graph extraction."*

The third line is the interesting one — the author wrote this expecting a
pipeline like ours to read it, and the structure is genuinely the cleanest of
the five: every role carries the same headings in the same order, which is why
extraction needed no per-role special cases.

The first two are the problem. **High confidence, and exactly ONE flagged
research gap across 15 roles.** Document D made a weaker claim and marked 23
gaps in 37 pages. A document that audits itself *less* is not more reliable.

Well-structured is not well-sourced. A document that is easy to parse invites
you to trust it, which is exactly when to check. **Ceiling stays 60**, and
`test_being_easy_to_parse_did_not_raise_the_ceiling` says so in the suite.

### The first document with no copy-paste defect

B and C each carried a role whose alternative titles belonged to its
neighbour. After two occurrences the defect looked systemic. This one does not
have it: all fifteen roles carry distinct, appropriate alias lists, and
`test_this_is_the_first_document_with_no_copy_paste_defect` checks it by
collision rather than asserting it in prose. **Common, then, but not
universal** — worth correcting the earlier conclusion.

One real overlap remains: **"Security System Installer" is an alt title of role
1 (CCTV Technician) and is also role 4**, with its own distinct aliases
("Physical Security Technician, Access Control Tech"). Reading both, role 1 is
surveillance and role 4 is access control — adjacent in the field, and
distinguishable. Recorded in role 4's `notes` rather than resolved: how a
Telangana integrator actually splits that work is a question for somebody who
has hired one, and the two candidates should be decided together.

### 7 merge, 8 new

| document role | existing entity |
|---|---|
| Mobile Phone Repair, Laptop Repair, LED TV Repair, Electronics Service | Electronics Repair & Maintenance |
| PCB Repair Technician | PCB Assembly & Soldering |
| Home Automation Technician | IoT Systems Development |
| Solar Inverter Technician | Solar Panel Installation & Maintenance |

New: CCTV Technician · Fire Alarm Technician · Security System Installer ·
Inverter Technician · UPS Technician · Networking Technician · Fiber Optic
Technician · Telecom Tower Technician.

**Four roles are one skill.** Mobile, laptop, LED TV and general electronics
service are the same bench, the same meter, the same rework station. The same
over-splitting document C showed with the lathe trades — the document sells
specialisations as careers and the graph is right to hold one. Named in
`COLLAPSES_ONTO_ELECTRONICS_REPAIR` so a later reader does not promote four.

### What it fixed — 22 of 32 queries, every one of them a wrong answer

The worst baseline of the five. Nine probe queries landed on *Field Technician
– Computing & Peripherals*, and the ones that missed that magnet were worse:

| query | before | after |
|---|---|---|
| `mobile repair` | **Mobile App Development** | Electronics Repair & Maintenance |
| `phone repair` | Automotive Repair & Services | Electronics Repair & Maintenance |
| `laptop repair` | Automotive Repair & Services | Electronics Repair & Maintenance |
| `tv repair` | Automotive Repair & Services | Electronics Repair & Maintenance |
| `appliance repair` | Automotive Repair & Services | Electronics Repair & Maintenance |
| `electronics service technician` | Freelance Software/IT Consultant | Electronics Repair & Maintenance |
| `smt technician` | **Field Technician – Computing** | PCB Assembly & Soldering |
| `chip level repair` | **NIELIT 'A' Level** | PCB Assembly & Soldering |
| `board repair` | Automotive Repair & Services | PCB Assembly & Soldering |
| `smart home` | **Telangana Homestays** | IoT Systems Development |
| `home automation` | **Robotics** *(EXACT match)* | IoT Systems Development |
| `building automation` | **Construction** | IoT Systems Development |

**22 corrected, 0 newly answered, 0 regressions.** Nothing was unreachable —
the graph already held all four target Skills. Everything was reachable and
wrong.

`mobile repair` → *Mobile App Development* is the single most damaging answer
in the batch. Phone repair is the lowest-capital electronics shop there is,
and the platform was sending that reader to a software career. The two share
one word and share nothing else: entry qualification, capital, tools,
customers.

`smart home` → *Telangana Homestays* is the funniest and the same failure: the
word "home" won.

### Three concepts, no collisions

`electronics-repair` (12 aliases), `pcb-repair` (5), `home-automation` (5).
Measured before and after against the real graph, as every document has been.
This is the first of the five where nothing had to be dropped for a substring
collision — the vocabulary of electronics service happens not to overlap
anything the graph already names.

Two aliases were added beyond the document's own tables — `phone repair` and
`smartphone repair` — because both returned *Automotive Repair & Services* and
both are what a person actually types. Neither is a claim about the world.

### Eight trades left with no vocabulary, on purpose

`cctv technician`, `fire alarm technician`, `inverter technician`, `ups
technician`, `networking technician`, `fiber optic technician` and `telecom
tower technician` **all still return *Field Technician – Computing &
Peripherals***. No Skill entity exists to send a reader to, and pointing them
at an approximately-related entity is the confidently-wrong failure this whole
exercise is against — the mistake §11 records making. They are fixed by
approving the candidates, not by writing aliases.

`test_the_queued_trades_are_honestly_still_unreachable` pins the gap so it is
read as a decision rather than an oversight, and tells whoever promotes one of
these to retire it.

### One alias refused

The document lists **"Network Engineer"** as an alternative title for
Networking Technician. It is not carried across. An engineer designs the
network and a technician installs it; the first is a degree-entry job. Treating
them as the same word would send a 10th-pass reader somewhere they cannot go —
which is the exact harm the ITI-to-engineer confusion does in the field.

---

## 16. Combined position — five documents

> **The figures in this section were wrong and have been corrected.** An
> earlier version of this table read *93 aliases, 49 corrected, 12 newly
> answered, 0 regressions*. Every one of those numbers was too low, and the
> last one was not merely low but false.
>
> **Why they were wrong.** Each document was measured against its own curated
> probe set — the twenty to thirty queries that document's table reports. That
> is a sound way to check one document and a bad way to total five: the probes
> overlapped unevenly, additions to pre-existing concepts were counted for some
> documents and not others, and no document's probe set contained another
> document's terms. The revised figures come from a single measurement over the
> **complete alias set** — all 206 terms added or changed by the five commits —
> run against the pre-enrichment baseline `fcc2364^` on the real 647-entity
> graph.
>
> **What the wider measurement found that the narrow ones could not:** five
> live regressions, all from one concept in document A, invisible to every
> per-document probe set because they came from a document written before the
> rule that catches them existed. They are described in §17 and are fixed.
>
> The corrected figures are below. They are larger, not smaller — the narrow
> measurement had been understating the gain as well as hiding the harm.

| | |
|---|---|
| documents processed | 5 |
| pages read | 205 |
| trades read | 80 |
| review candidates | **52** (8 + 15 + 11 + 10 + 8), all `NEEDS_REVIEW` |
| concepts | 19 new + 11 pre-existing extended · 9 written-and-deleted · 2 folded |
| aliases added | **187** *(was reported as 93)* |
| probe terms measured | 206 |
| queries corrected from a wrong answer | **116** *(was reported as 49)* |
| queries newly answered | **33** *(was reported as 12)* |
| queries that lost an answer | 0 |
| queries unchanged | 57 |
| regressions found by the consolidated measurement | **5** *(was reported as 0)* |
| regressions after the §17 fix | **0** |
| entities overwritten | 0 |
| entities created | 0 |
| candidates promoted | 0 |
| packages modified | 0 |
| schema / migration changes | 0 |

### What five documents taught that four could not

1. **The copy-paste defect is common, not systemic.** §14 called it systemic on
   two occurrences out of three. Document E has fifteen clean alias lists.
   Two out of five is a pattern to check for, not a law — and the correction
   is worth more than the original claim.
2. **Clean structure is a reason to trust the extraction, never the content.**
   Document E was written for a machine to read and says so. It parsed
   perfectly and audits itself least of the five. Those facts are unrelated,
   and the first one makes the second easier to miss.
3. **A self-graded confidence level is not evidence.** Only one document grades
   itself, and it gives itself "High". Count the research gaps instead: D
   claimed less and marked 23; E claimed more and marked one.
4. **The worst answers are in the most ordinary queries.** `car mechanic` →
   Carpentry (D). `mobile repair` → Mobile App Development (E). Not obscure
   trades — the two things a school-leaver in Telangana is most likely to
   type. Both were fixed by one alias line each.
5. **Refusing to write an alias is a deliverable.** Eight electronics trades
   and five automotive ones were left returning nonsense because no entity
   exists to send a reader to. The tests record the gaps so nobody quietly
   "fixes" them with a sector expansion.
6. **Per-document measurement cannot find cross-document harm.** Five
   regressions sat in the branch through four rounds of careful before-and-
   after work, because each round asked "did MY probes get better" and none
   asked "did anything get worse". The only measurement that finds this is the
   whole alias set against the original baseline, and it costs one script run.
   Do it before every merge, not after every document.

```bash
python3 -m research.sources.emit_candidates --doc electronics   # dry
python3 -m research.sources.emit_candidates --write             # all five
python3 -m collection.cli queue --state NEEDS_REVIEW --limit 70
```

Primary sources to review against: **DGT trade list** (A), **CSDCI role list**
(B), **Capital Goods Skill Council** packs (C), **ASDC** packs (D), and for E
the **Electronics Sector Skills Council of India (ESSCI)** and **Telecom Sector
Skill Council (TSSC)** qualification packs — CCTV/Field Technician, Fibre
Splicer and Tower Technician are all named QPs with published NSQF levels, so
the existence claim and the level are checkable in one place. Fire-alarm work
additionally sits under state fire-services licensing, which is a second
authority and worth checking separately.

---

## 17. The blocker the consolidated review found

### One string, five wrong answers

`plc-automation` shipped from document A with:

```json
"expands_to": ["plc programming", "industrial automation", "automation"]
```

The bare word **`automation`** CONTAINS-matches a real BusinessOpportunity, and
five queries landed on it:

| query | before the documents | on the branch | after the fix |
|---|---|---|---|
| `plc automation` | Robotics | **WhatsApp Business Automation** | PLC Programming & Control Systems |
| `plc programmer` | Freelance Software/IT Consultant | **WhatsApp Business Automation** | PLC Programming & Control Systems |
| `automation technician` | Robotics | **WhatsApp Business Automation** | PLC Programming & Control Systems |
| `industrial automation technician` | Robotics | **WhatsApp Business Automation** | PLC Programming & Control Systems |
| `scada` | *(nothing)* | **WhatsApp Business Automation** | PLC Programming & Control Systems |

This is worse than the Masala Powder incident §11 records. There, six concepts
reached for a sector because their trades had no anchor at all. Here **the
graph holds the right answer** — `PLC Programming & Control Systems`, a Skill —
and the expansion dragged five queries off it. `scada` is the sharpest case: it
was counted in the "newly answered" column as a gain, and it was a new harm.

### Why four rounds of measurement missed it

Each document was probed against its own curated query set. `plc-automation`
came from document **A**, written before document **C** established the rule
that catches it, and no later document's probe set contained the words `plc`,
`scada` or `automation technician`. Every round asked *did my probes improve*;
none asked *did anything get worse*.

The fix is not a better rule — the rule was already written. It is a better
measurement, and it is one script: the complete alias set against the
pre-enrichment baseline, before merge.

### What changed

One string deleted. **No alias was touched** — `plc`, `plc programmer`, `scada`,
`automation technician`, `hmi`, `control systems` and `industrial automation
technician` are the vocabulary this document paid for and all seven remain.
Only the expansion was wrong.

Re-measured across all 206 probe terms afterwards: **116 corrected, 33 newly
answered, 0 lost, 0 landing on a business with "Automation" in its name.**

### Guarded so it cannot come back

`AutomationExpansionRegressionTest` pins the five queries to the PLC Skill and
asserts the seven aliases survive. `SectorExpansionGuardTest` generalises it:
no concept may expand to a bare sector word unless it is in
`SECTOR_EXPANSION_EXEMPT` **with a written reason**, and `plc-automation` is
explicitly barred from that list — adding the offender to the exemption is the
cheapest way to make a guard test pass, so the guard refuses it.

The neighbouring `robotics` concept also carries a bare `automation` expansion.
It predates all five documents and the brief was one string, so it is exempted
rather than changed — but exempting it without measuring it would be taking the
same risk twice, so its five aliases are pinned to `Robotics` by test.

---

## 18. The 52 candidates — classification and research gaps

Recorded in `research/sources/candidate_classification.py`, checked against the
queue and the graph by `CandidateClassificationTest` and `ResearchGapTest`.
**Nothing is approved. Nothing is promoted. No entity was created.** All 52 rows
are still `NEEDS_REVIEW` and a test fails if any of them stops being so.

### Five classes

| class | meaning | count |
|---|---|---|
| **A** | likely merge into an existing entity after a primary-source check | 7 |
| **B** | likely requires a new Skill entity | 22 |
| **C** | duplicate — decide with its group | 17 |
| **D** | disputed — requires a human decision | 5 |
| **E** | reject | 1 |

*(B and D shifted by one after §19: Fire Alarm Technician was reclassified when
verification failed to find a national qualification for it.)*

"Likely" is load-bearing. A and B are predictions about what a reviewer will
conclude *after* checking a primary source, not permission to skip the check.

**Class A (7)** — each names a target that exists in the graph today, and a
test verifies it: Tile & Marble Fixer → *Tiles Fixing* · Fabricator → *Welding
(MIG/TIG/Arc)* · Steel Fixer → *Masonry & Brickwork* · Modular Kitchen
Installer → *Carpentry* · Granite Cutter → *Tiles Fixing* · Milling Machine
Operator → *Lathe Operation* · Heavy Vehicle Technician → *Automobile Mechanic
(Diesel/Petrol)*.

**Class D (4)** — the ones no source settles:

* `battery-technician` — document A calls it an alias of EV Technician,
  document D makes it a career. Search follows A, the candidate follows D, on
  purpose: a taxonomy question should not be decided by whichever alias list
  was edited last.
* `security-system-installer` — document E lists it as both an alias of CCTV
  Technician and a role in its own right.
* `auto-painting-technician` — must stay distinct from the building Painter;
  search currently returns *Painting Services* for both, contradicting the
  source module.
* `interior-finishing-technician` — reads as an umbrella over four trades
  document B also queues separately. Trade or category is a judgement.

**Class E (1)** — `production-operator`. Sector-shaped rather than a defined
trade; search returns *Manufacturing*, which is the honest answer. Creating it
would repeat §11's mistake at the entity layer. A test pins it rejected,
because the reason is a definition and definitions do not change when somebody
wants a shorter queue.

### Eight duplicate groups — 52 decisions become about 38

`maintenance-fitter` · `false-ceiling` · `fenestration` · `plant-operator` ·
`fluid-power` · `battery` · `tyre-and-alignment` · `physical-security`.

Each carries its members, its reason and the primary source that settles the
group. Tests hold that no candidate sits in two groups and that every grouped
candidate is class C or D — never a straightforward merge or a straightforward
new entity, because deciding it alone is exactly what the group prevents.

**Two pairs must stay distinct**, recorded because the pressure runs the other
way — a long queue makes merging feel like progress:

* **Painter** ≠ **Auto Painting Technician** — different materials, booth,
  certification, customer.
* **Fabricator** ≠ **Aluminium Fabricator** — different metals, joining
  methods and sites.

### Research gap 1 — the Field Technician magnet

**Eighteen of the 52** — more than a third — return the same top result:

> `Field Technician - Computing & Peripherals - ELE/Q4601` *(Certification)*

**This must not be fixed with aliases.** Every one of these is a trade with no
Skill entity to point at; an alias would only move the wrong answer somewhere
else, which is the confidently-wrong failure §11 records and §17 repeats. It is
a **knowledge-coverage** problem: the graph has nothing to return and one broad
certification wins by default because it contains the word "Technician".

It resolves as the queue resolves — each promoted Skill takes its queries off
the list, and the test says so. Whatever remains afterwards is a ranking
question about occupational suffixes and belongs in the search backlog.

### Research gap 2 — promotion is two edits, not one

For **18 candidates** the vocabulary already resolves the trade's words to an
approximate existing entity, usually a BusinessOpportunity or an Industry
rather than a learnable Skill. That is the "business you cannot learn" gap and
it is the strongest case for promoting them.

It also carries an obligation nothing in the pipeline tracks: **promote the
Skill without re-pointing the concept and the new entity is unreachable by the
very words that were added for it.** `REPOINT_ON_PROMOTION` names each
candidate with its concept and the entity that currently answers, and a test
verifies all three still exist.

### Nothing factual may be promoted from these documents

Salaries, course fees, institute contacts, placement claims, employer names and
demand estimates. Five LLM-generated secondary documents, zero citations. The
role names and aliases are observable facts about how words are used and were
verifiable here; the numbers are claims about the world and are not. They live
in the queue's raw records and nowhere else.

---

## 19. Primary-source verification — the top ten candidates

Recorded in `research/sources/verified_candidates.py`, held by
`VerifiedCandidateTest` and `FieldTechnicianFamilyTest`. **Nothing promoted, no
entity created, no alias written.**

### What "verified" means here, and what it does not

Each record names a government qualification — a DGT/NCVT craftsman trade or an
NSQC-approved Sector Skill Council qualification pack — with its code, its NSQF
level and the URL of the official document. That is a real step up from the
five datasets, which asserted role names with no citation at all: a QP code and
a gov.in URL can be checked by one person in one click.

**It is not a direct read of those documents.** This environment's egress proxy
blocks `dgt.gov.in`, `nqr.gov.in`, `essc-india.org`, `asdc.org.in` and
`nsdcindia.org`; every WebFetch was attempted and refused. The codes and levels
below are quoted from a search index's extract of the official document,
corroborated by a second independent search pass. The repository already has
precedent for exactly this — the UGC row in `entities.csv` carries the note
*"Website content could not be directly re-fetched due to proxy access
restriction on gov.in domains"* — and the same discipline applies:

> **Confidence ceiling 75.** Above the 60 given to an uncited secondary
> document; below the 88 the repository gives a fact it fetched itself.

### Nine of ten confirmed

| candidate | authority | code | NSQF | decision |
|---|---|---|---|---|
| Service Advisor | ASDC | **ASC/Q1426** v2.0 | 4.5 | **B** new Skill |
| Fitter | DGT/NCVT CTS 2.0 | Fitter (2 yr) | 4 | **C** settles its group |
| Tool & Die Maker | DGT/NCVT CTS 2.0 | TDM (Dies & Moulds); TDM (Press Tools, Jigs & Fixtures) | 4 / 5 | **B** new Skill |
| Painter | DGT/NCVT CTS 2.0 | Painter (General); Domestic Painter; Industrial Painter | 4 / 3 / 3 | **B** new Skill |
| Mechatronics Technician | DGT/NCVT CTS 2.0 | Technician Mechatronics (2 yr) | 4 | **B** new Skill |
| Lift Technician | DGT/NCVT CTS 2.0 | Lift & Escalator Mechanic | 4 | **B** new Skill |
| CCTV Technician | ESSCI | **ELE/Q4605** v4.0 | 3.5 | **C** settles its group |
| Networking Technician | ESSCI | **ELE/Q4606** v3.0 | 4 | **B** new Skill |
| EV Charging Station Technician | **PSSC**, not ASDC | NQR, 14th NSQC | not established | **B** new Skill |
| Fire Alarm Technician | **not found** | — | — | **D** reclassified |

### The three results worth reading

**Painter settles a KEEP_DISTINCT pair with a primary source.** DGT runs
building painting and automotive refinishing as *separate craftsman trades* —
Painter (General) / Domestic Painter / Industrial Painter on one side, Mechanic
Auto Body Painting (NSQF 3.5) on the other. The source modules said keep them
apart on judgement; the national trade structure agrees. Search currently
returns *Painting Services* for both, and promoting these must fix that.

**CCTV narrows its group.** ESSCI holds **one** qualification covering
surveillance installation, so document E's split into "CCTV Technician" and
"Security System Installer" is not reflected in the national structure. The
pair should resolve to one entity unless a reviewer finds a separate
access-control QP.

**Fire Alarm Technician did not verify, and that is the honest result.**
Searching ESSCI and the National Qualification Register returns Firefighter,
Fire Safety Officer and Fire Safety Technician (Oil & Gas) — all about
*responding* to fire, none about installing detection. The only fire-alarm
credential found is a commercial certificate from a private training company,
which is not a national qualification and must not be recorded as one. The
occupation plainly exists; its credential could not be located from here.
Reclassified **B → D**.

### Three corrections verification forced, two of them mine

| candidate | was | is | whose error |
|---|---|---|---|
| EV Charging Station Technician | ASDC | **PSSC** (Ministry of Power / MNRE) | mine — I assigned the authority from the document the role arrived in, not from the work |
| Lift Technician | "no sector qualification; state licensing only" | **DGT CTS Lift & Escalator Mechanic, NSQF 4** | mine — I assumed no craftsman trade existed because no sector council covers lifts |
| Fire Alarm Technician | class B, "ESSCI QP list" | class D, authority not established | new information |
| Tool & Die Maker | one role | **two DGT trades at two NSQF levels** | new information |

### The Field Technician magnet, diagnosed

§18 recorded it as a knowledge-coverage problem. Verification says what the
coverage problem *is*, and it is sharper than "some skills are missing".

ESSCI publishes a family of **After Sales Support** qualifications sharing the
`ELE/Q46xx` prefix:

| QP | title | NSQF | in the graph |
|---|---|---|---|
| **ELE/Q4601** | Field Technician — Computing & Peripherals | 4 | yes — as a **Certification** |
| ELE/Q4605 | CCTV Installation Technician | 3.5 | no — queued |
| ELE/Q4606 | Field Technician — Networking & Storage | 4 | no — queued |

The graph holds **exactly one** member of the family, as a Certification, and
holds **no Skill for any trade in it**. So a query ending in "technician" with
no Skill to reach finds the one row that contains the word. That is not a
ranking bug; it is an import asymmetry — *qualification packs were imported as
Certification entities without the corresponding trades as Skills.*

The same asymmetry produced a **second magnet**: `Automotive Service Technician
(Two and Three Wheelers) - ASC/Q1411` is also a Certification with no matching
Skill of its own name, and it too surfaced as a wrong top hit during the
five-document work. It is half fixed — the graph does hold *Two-Wheeler
Mechanic*, and document D's vocabulary now routes the bike queries there.

**The fix is coverage.** Two of the three family members are already queued;
promoting them removes their queries from the magnet and gives the vocabulary
somewhere true to point. No alias can do this.

### Vocabulary prepared, deliberately not shipped

None of the ten is a class-A merge, so not one of them has an existing Skill to
point at. Writing these aliases today would send readers to an
approximately-related entity — the exact failure the magnet gap forbids — and
`test_the_magnet_is_not_being_papered_over_with_aliases` would fail, correctly.

`PROPOSED_VOCABULARY` therefore holds English, Telugu and Tanglish terms for
the nine verified roles and **nothing at all** for the unverified one, so that
promotion is one step rather than a rediscovery. Fire Alarm Technician's entry
is empty on purpose: an unverified role with ready-made aliases is an
invitation to ship it.

**The Telugu is PROPOSED and needs a Telugu-speaking reviewer.** The terms are
transliterated loanwords — లిఫ్ట్ మెకానిక్, సీసీటీవీ, నెట్‌వర్కింగ్ — which is
the register a Hyderabad technician actually uses rather than a Sanskritic
coinage. That is a checkable claim about usage, but not checkable by me and not
by a search engine. Nothing is indexed until a person confirms it. The
`<trade> pani` Tanglish forms follow the convention already in the table
(`current pani`, `tiles pani`, `ac repair pani`).

One entry carries `repoint_existing_concept`: the `painter` concept already
claims "painter" and "house painting" and points at the Painting Services
business. When the Skill lands that concept must be **re-pointed, not
duplicated** — two concepts claiming one alias fails the integrity test.

---

## 20. Document F — Entrepreneurship Decision Datasets

*49 pages, 20 employment-generating businesses. Normalised to
`research/sources/entrepreneurship_businesses_2026.py`.*

### A different shape from the first five

Those described **trades** — things a person learns. This describes
**businesses** — things a person starts. That changes what may be extracted:

* business names, alternative names and sectors are vocabulary, checkable here;
* investment ranges, revenue scenarios, margins, break-even periods, licence
  fees, subsidy percentages and employment counts are the *bulk of the
  document* and are all uncited estimates.

It is the first source whose subject matter **is money**. Every one of the
twenty entries leads with an investment range and a profit scenario — exactly
the material a reader is most likely to act on, and exactly the material with
least behind it. `UNVERIFIED_FIELDS` is therefore longer here (18 entries) than
in any trade module, and a test asserts no rupee figure, salary range or
percentage margin reached the module at all.

It also carries **140 star ratings** — seven per business, for demand,
investment, skill, profit, employment, competition and risk. Not one is a
measurement. `STAR_RATINGS_ARE_NOT_DATA` names them and a test asserts the `★`
character appears nowhere in the module.

### What it says about itself — better than average

> *"All data is based on publicly available information, Indian regulatory
> frameworks, and industry estimates. Research Gaps have been clearly marked
> where verified sources are unavailable."*

`Research Gap` appears **10 times across 49 pages**, plus one explicit "Not
publicly verified" and seven "verify" instructions. Thinner than document D's
23 markers in 37 pages, but honest in kind — and unlike document E it makes no
claim of high confidence. **Ceiling stays 60.**

### The highest overlap of the six — 11 of 20 already exist

This is why a 49-page document queues only 12 rows. Every merge target was
checked against `entities.csv`, and a test holds each one:

| document business | existing entity | type |
|---|---|---|
| Solar Installation Business | Solar Rooftop EPC Contractor | MSME |
| Electrical Contractor | Electrical Contracting (Licensed Supervisor/Contractor) | BusinessOpportunity |
| Plumbing Contractor | Plumbing Services | BusinessOpportunity |
| Computer Service Center | IT Hardware and Network Services | MSME |
| CNC Job Work Unit | CNC Machining Job Shop | MSME |
| Fabrication Workshop · Welding Shop | Welding & Metal Fabrication | BusinessOpportunity |
| Granite & Tiles Contracting | Tiles Fixing (Tile Mason) | BusinessOpportunity |
| Borewell Services | Borewell Drilling Services | BusinessOpportunity |
| Cold Storage Business | Cold Storage Facility | MSME |
| EV Garage | EV Two-Wheeler Service Centre | MSME *(partial — see below)* |

**EV Garage is a partial overlap, not a clean duplicate.** The graph's entity
is two-wheeler specific; the document covers 2/3/4-wheelers and e-buses.
Whether to broaden the existing MSME or hold a second wider entity is a
curation decision — recorded, not taken.

**Fabrication Workshop and Welding Shop are the same entity as each other** —
the document splits into two businesses what the graph rightly holds as one.
The same over-splitting the trade documents showed.

### 12 queued — and the first candidates that are not Skills

| type | n | candidates |
|---|---|---|
| BusinessOpportunity | 7 | Lift Installation · AC Service · Civil Contractor · Interior Contractor · CCTV Installation · Mobile Repair Shop · Water Purification (RO) |
| MSME | 2 | Battery Recycling Unit · Dairy Processing Unit |
| GovernmentScheme | 3 | CLCSS · NABARD DEDS · MIDH |

Five documents proposed only Skills, so `Skill` was the emitter's hardcoded
classification. **One field changed** — `entity_type`, defaulting to `Skill` —
so the reviewer is asked *"should ValueWeave hold this as a business"* rather
than the wrong question. A test asserts the five trade documents still classify
as `Skill` with a word-for-word identical reason sentence. No new pipeline, no
schema, no migration.

**DEDS carries the lowest confidence in the module (35) and says why:** it has
been reported discontinued or restructured in some years, and a scheme entity
that no longer accepts applications is worse than no entity — a reader would
waste a trip to a bank.

### Two pairs that must be decided together

`lift-installation-business` pairs with the queued **Lift Technician** Skill;
`cctv-installation-business` pairs with the queued and ESSCI-verified **CCTV
Technician**. Approving one without the other recreates the "business you
cannot learn" gap in reverse — a business nobody is trained for.

### The inverse of the recurring pattern

Five documents kept finding businesses the graph holds with no Skill teaching
them. **AC Service Business is the mirror image:** the graph holds *HVAC
Technician* as a Skill and has no business a trained person could start.

### It also settles an open class-D question

The construction document queued *Interior Finishing Technician* and §18 marked
it **DISPUTED** because "interior finishing" read as an umbrella over false
ceiling, painting, tiling and joinery rather than one trade. This document
independently treats interior work as a **business that coordinates those
trades** — evidence for the umbrella reading. Two documents, two framings, and
they agree once the trade question is separated from the business question.

### What it fixed — 17 corrections, 5 newly answered, 0 regressions

| query | before | after |
|---|---|---|
| `ac service` | Freelance Software/IT Consultant | HVAC Technician |
| `ac service business` | **Instagram Shopping / WhatsApp Business** | HVAC Technician |
| `computer repair` | **Course on Computer Concepts (CCC)** | Electronics Repair & Maintenance |
| `desktop repair` | Automotive Repair & Services | Electronics Repair & Maintenance |
| `mobile repair shop` | **Instagram Shopping** | Electronics Repair & Maintenance |
| `fabrication workshop` | **Masala Powder Manufacturing Unit** | Welding (MIG/TIG/Arc) |
| `gate and grill fabrication` | **Masala Powder Manufacturing Unit** | Welding (MIG/TIG/Arc) |
| `plumbing contractor` | Construction *(sector)* | Plumbing |
| `granite contractor` | Construction *(sector)* | Tiles Fixing (Tile Mason) |
| `cold storage business` | **Instagram Shopping** | Cold Storage Facility |
| `ఏసీ సర్వీస్` | *(nothing)* | HVAC Technician |
| `కంప్యూటర్ రిపేర్` | *(nothing)* | Electronics Repair & Maintenance |
| `కోల్డ్ స్టోరేజ్` | *(nothing)* | Cold Storage Facility |

`computer repair` → *Course on Computer Concepts* is the sharpest of these: a
certification about **using** a computer, offered to somebody who wants to
**fix** one.

**One new concept only** — `cold-storage`, with two aliases. `cold storage
unit` was deliberately left out of it: the graph holds *Cold Storage Unit* as
**Machinery** and *Cold Storage Facility* as an **MSME**, two different things
one word apart, and a test pins the machinery query so the new concept cannot
swallow it.

**Three Telugu terms, and one rejected.** ఏసీ సర్వీస్, కంప్యూటర్ రిపేర్ and
కోల్డ్ స్టోరేజ్ each took a query from nothing to the right entity. మొబైల్
రిపేర్ was written and **removed**: it already resolves through
transliteration, so it would have been a row that does no work — which is the
rule the concept table's own header states.

### What was refused

* **Nine businesses got no alias at all.** `ro plant` returns *Tractor (35-45
  HP)* and `dairy processing` returns *Cattle Dung and Farm Waste*. Both are
  embarrassing and both were left alone — no entity exists to point at, and a
  sector expansion is what §11 forbids and §17 proved still bites. Approving
  the candidates is the fix. A test pins the gap.
* **Four localities refused as districts.** Ranigunj, Secunderabad, Balanagar
  and Mallepally are neighbourhoods inside Hyderabad, not districts. The
  graph's 61-district hierarchy would be corrupted by adding them.
* **Seven named institutes and six named companies not carried across.** ATI
  Hyderabad, TASK, ITI Mallepally, APSSDC, NDRI, IIFPT, Sri Venkateswara
  Polytechnic; Bosch, Ather, Ola, Hikvision, CP Plus, Tata Power. The
  institutions are checkable and some may deserve TrainingProvider entities —
  what may never be promoted is the *course claim* attached to them, which the
  document itself marks "Not publicly verified".
* **Every figure.** Investment, revenue, margin, break-even, subsidy
  percentage, employment count, rental rate, licence fee.

### Combined position — six documents

| | |
|---|---|
| documents processed | 6 |
| pages read | 254 |
| trades and businesses read | 100 |
| review candidates | **64** (52 trades + 12 businesses/schemes), all `NEEDS_REVIEW` |
| concepts | 20 new + 11 pre-existing extended |
| aliases added | 209 |
| probe terms measured | 229 |
| queries corrected | **133** |
| queries newly answered | **38** |
| queries that lost an answer | 0 |
| regressions | 0 |
| entities created / overwritten | 0 / 0 |
| packages, schema, migrations changed | 0 |
| tests | 1157 pass |
