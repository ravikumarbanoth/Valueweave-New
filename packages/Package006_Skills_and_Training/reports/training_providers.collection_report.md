# Collection Report — Training Providers (Package006_Skills_and_Training)

Collection date: 2026-07-24
Researcher: Claude (web-search-based knowledge engineering)
Output file: `datasets/training_providers.csv` (25 rows)

## Methodology

1. Built a target list of 25 rows spanning every category named in the task brief: ITI
   (Telangana + Andhra Pradesh), Polytechnics (Telangana + Andhra Pradesh + one named
   flagship institution), engineering-college vocational add-on programmes, a national
   NSTI/DGT network row, a real named state skill university, TASK, APSSDC, NSDC (plus a
   named NSDC training partner), PMKK, NPTEL, SWAYAM, two corporate-academy examples
   (Siemens COE, Maruti Suzuki ASEC), two private-institute examples (CADD Centre, NIIT),
   and three online-platform examples (upGrad, FutureSkills Prime, Skill India Digital Hub),
   plus NIELIT's Hyderabad centre, the National Academy of Construction, and DGT itself as a
   national government skill body.
2. `WebFetch` to `.gov.in` / `.ac.in` / `.nic.in` domains was **not used**, per the task's
   confirmed-blocked constraint (repeated HTTP 403s in this environment). All facts
   attributed to government domains (iti.telangana.gov.in, dgt.gov.in, nielit.gov.in,
   sbtet.ap.gov.in, apssdc.in, task.telangana.gov.in, swayam.gov.in, aicte-india.org, pib.gov.in,
   etc.) were sourced via `WebSearch` result snippets/summaries of those pages, or via
   secondary corroboration (Wikipedia, education portals, press coverage), never via a
   directly rendered page. This is flagged explicitly in the `notes` field of every affected
   row and reflected in a lower confidence score than a directly-fetched Tier-1 page would
   receive.
3. For quantitative claims (ITI/polytechnic counts, PMKK counts, training-centre-network
   sizes), multiple independent searches were run per fact. Where sources disagreed
   materially (see "Conflicts" below), the discrepancy is recorded in `notes` rather than
   silently resolved, and `confidence_score` was set toward the lower end of the applicable
   tier band.
4. `provider_id` values were generated as UUIDv4 via Python's `uuid` module (25 pre-generated
   UUIDs, one per row, verified unique).
5. `confidence_score` was assigned per the task's tier bands: 70-85 where the underlying
   fact traces to an explicitly Tier-1 body (MSDE/NSDC/NCVET/DGT/AICTE/UGC/NIELIT/NPTEL/
   SWAYAM/TASK/official ITI portals) even if accessed via search snippet rather than direct
   fetch; 55-69 where the fact rests on Tier-2/3 sources (industry press releases, a
   provider's own corporate website, aggregated education portals) or where a Tier-1 fact
   carries material cross-source disagreement. No score exceeds 85, per instructions.
6. `collection_date = 2026-07-24` and `verification_status = VST-NEEDS_REVIEW` were applied
   uniformly to all 25 rows.
7. Programmatically validated the final CSV (Python `csv` module round-trip): confirmed
   exactly 14 columns matching the required header/order, exactly 25 data rows, all
   `provider_id` values unique, all `confidence_score` values in [55, 78] (none above 85),
   and — critically, per the recurring project bug this task called out — confirmed **zero**
   cells contain any variant of `PENDING_VERIFICATION` with appended text; in fact this
   dataset required **zero** uses of the placeholder at all (every field was resolved to a
   stated, sourced fact, with uncertainty handled via lower confidence scores and explicit
   `notes` caveats instead).

## Sources consulted (representative)

**Telangana state bodies / portals**
- https://iti.telangana.gov.in/ and its 2025 admissions prospectus PDF (ITI counts)
- https://polycet.sbtet.telangana.gov.in/ (SBTET Telangana polytechnic network)
- https://gptmasb.dte.telangana.gov.in/ and https://en.wikipedia.org/wiki/Government_Polytechnic,_Hyderabad (Govt Polytechnic Masab Tank)
- https://www.task.telangana.gov.in/, https://it.telangana.gov.in/initiatives/task/, Vikaspedia TASK profile
- https://www.yisu.in/ and Telangana State Portal press releases (Young India Skills University)
- https://www.nielit.gov.in/hyderabad/index.php (NIELIT Hyderabad)
- https://en.wikipedia.org/wiki/National_Academy_of_Construction, https://nacbocwb.cgg.gov.in/ (NAC)

**Andhra Pradesh state bodies / portals**
- https://iti.ap.gov.in/, Careers360 news coverage of AP's Rs 100 crore ITI/polytechnic/skill-college modernization
- https://sbtet.ap.gov.in/-adjacent secondary reporting on AP POLYCET 2026 counselling
- https://www.apssdc.in/home/, https://tirupati.ap.gov.in/apssdc/, India.gov.in APSSDC service listing
- Siemens official press release on the APSSDC Centres-of-Excellence agreement

**National bodies**
- https://dgt.gov.in/ and NSTI subdomains (nstiwhyderabad.dgt.gov.in, nstihyderabad2.dgt.gov.in)
- https://nsdcindia.org/ (training-partner network, PMKK)
- https://www.msde.gov.in/ and IMPRI India policy brief (PMKK scheme)
- https://nptel.ac.in/ and https://swayam.gov.in/ (NPTEL, SWAYAM)
- https://www.aicte-india.org/ (SWAYAM bureau, Community College Scheme)
- https://www.futureskillsprime.in/, https://www.digitalindia.gov.in/ (FutureSkills Prime)
- https://www.pib.gov.in/ press release and India.gov.in listing (Skill India Digital Hub)

**Corporate / private providers (own websites, Tier 3)**
- https://www.marutisuzuki.com/corporate/careers/training-academy and .../csr/iti-upgradation-sdd (MSTA, ASEC)
- https://caddcentre.com/ and https://caddcentreglobal.com/network.php (CADD Centre)
- https://www.niit.com/ and https://niitfoundation.org/ (NIIT)
- https://www.upgrad.com/ (upGrad)

## Conflicts found and resolution

1. **Telangana polytechnic total count**: sources cited 92-95 (24 govt + 68 private), 128
   (54 govt + 74 private), and 120 as separate "total polytechnic" figures, with no single
   authoritative SBTET Telangana count directly confirmable given the gov.in fetch
   restriction. Resolved by presenting the range as-is in `sample_locations_or_reach` with
   an explicit `notes` disclaimer, and lowering `confidence_score` to 56 (bottom of the
   Tier-2/3 band) rather than picking one figure and overstating certainty.
2. **Andhra Pradesh polytechnic government-college count**: figures of 29, ~84, and 88
   (from 2026 POLYCET counselling) all appeared across sources, alongside a combined-total
   figure of ~180 (147 private + 29-33 government-ish, itself inconsistent). Resolved the
   same way as (1) — documented the spread, confidence 56.
3. **Andhra Pradesh government-ITI count**: only one usable figure was found (83, from a
   November 2023 news report on a Rs 100 crore modernization programme bundling ITIs,
   polytechnics and skill colleges together); this is a Tier-3/4 secondary-news citation of
   an official announcement rather than a directly-loaded departmental page, so
   `confidence_score` was set to 58 and the likely staleness of the 2023-dated figure is
   flagged in `notes`.
4. **CADD Centre network size**: sources gave both "250+" and "400+ training centres";
   both figures were preserved in the row text with the discrepancy noted, rather than
   silently choosing one.
5. **Maruti Suzuki ASEC location count**: an older CSRBox article cited "15 ITIs" while
   Maruti's own current CSR page cites "31 locations" — treated as programme growth over
   time rather than a contradiction, with both figures/sources referenced in `notes`.

## Notable findings

- **Young India Skills University (YISU)**, Hyderabad, is a genuine, recently-established
  (2024) state skill university created under a dedicated Telangana PPP Act — a strong,
  directly-named fit for the "skill university" category requested in the brief. No
  equivalent standalone "skill university" was found for Andhra Pradesh in this pass.
- **APSSDC's Siemens partnership** (six Centres of Excellence covering Automotive,
  Industrial Machinery, Industrial Automation, Aerospace & Defence, and Shipbuilding) is a
  well-documented, named corporate-academy example anchored specifically in Andhra Pradesh,
  directly satisfying the brief's "Siemens Centers of Excellence in India" example category.
- **Maruti Suzuki's Automobile Skill Enhancement Centres (ASEC)** — embedded inside
  government ITIs nationwide — was used in place of the brief's suggested "Maruti Suzuki
  Institute of Automotive Skills (MSIAS)," which could not be verified as a real, currently
  named Maruti Suzuki programme; ASEC and the separate Maruti Suzuki Training Academy (MSTA,
  an actual NSDC training partner) are the real, verifiable Maruti Suzuki-branded skilling
  vehicles that were found instead.
- **Coursera-specific India skilling tie-ups** could not be verified in this research pass
  (searches surfaced FutureSkills Prime — a MeitY-NASSCOM platform with Microsoft/AWS/Cisco
  as named partners — but no confirmed Coursera-branded Government-of-India skilling
  partnership). FutureSkills Prime was used as the substitute real, verifiable example for
  the "national digital-skilling platform with government backing" slot instead of
  fabricating a Coursera tie-up.
- **National Academy of Construction (NAC)** is a useful edge case: founded in 1998 under
  combined (pre-bifurcation) Andhra Pradesh, its Hyderabad campus is now geographically in
  Telangana following the 2014 state split. It was classified under Telangana jurisdiction
  with the historical AP origin explicitly noted in `notes`, since jurisdiction reflects
  current-day location rather than founding-era state boundaries.

## Categories considered but adjusted from the brief's suggested examples

- **AICTE Community College Scheme**: included as a genuine, currently-existing national
  scheme, but no Telangana- or Andhra-Pradesh-specific adopting institution could be
  confirmed; the best-documented example found nationally (Assam Engineering Institute) was
  used illustratively, with this gap disclosed in `notes` rather than inventing a TG/AP
  instance.
- **NSDC training partner example**: Maruti Suzuki Training Academy (MSTA) was used as the
  real, verifiable named partner (per NSDC's own partner materials), even though its core
  campus is in Gurgaon rather than Telangana/Andhra Pradesh — flagged explicitly in `notes`.

## Known gaps / items flagged for follow-up review

- Exact, single-source-confirmed polytechnic counts for both Telangana and Andhra Pradesh
  (rows 3 and 4) remain unresolved to a single figure; a follow-up pass with direct SBTET
  portal access (not blocked) would allow tightening these to a precise, high-confidence
  count.
- PMKK counts specific to Telangana/Andhra Pradesh (as opposed to the national 812-allocated/
  738-established figures) were not found in a single authoritative MSDE state-wise table;
  the district-level concentration noted (Hyderabad/Warangal/Karimnagar/Nalgonda) rests on a
  secondary aggregator (YouthPower India) rather than an official source.
- Siemens COE and Maruti ASEC city-level locations within Telangana/Andhra Pradesh
  specifically were not individually confirmed by name.
- No row in this dataset required the `PENDING_VERIFICATION` placeholder; all 25 rows across
  all 14 columns were resolved to a stated, sourced fact. Confidence scores range from 55 to
  78 (never above 85, per instructions), reflecting a mix of well-corroborated Tier-1
  government facts (accessed via search snippet due to gov.in fetch restrictions) and
  lower-confidence Tier-2/3 facts from corporate sites, press releases, and aggregated
  education portals with some cross-source disagreement.
