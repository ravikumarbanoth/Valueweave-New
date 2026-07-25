# Methodology — Package007_Government_Schemes v1.0.0

How the 15 datasets were built, sourced, scored and validated.

## 1. Environment constraint, stated first

Direct `WebFetch` to `.gov.in`, `.nic.in` and `.ac.in` domains is blocked by this session's
organizational egress policy — the same constraint that applied to Package004, Package005 and
Package006. It matters more here than in any previous package, because government scheme data is
*exactly* the kind of data that requires a live primary source.

**Consequence:** no row rests on a primary-source page read. Every row is attributed to the scheme's
own portal or its administering ministry in `data_source`, and `confidence_score` is capped at 85
package-wide to record that the attribution was not confirmed by fetching the page.

**What this does not mean:** it does not mean the data is guessed. A scheme's ministry, objective,
beneficiary group, application mode and benefit *type* are stable structural facts. What could not
be confirmed is anything that moves: amounts, rates, ceilings, percentages, timelines, and current
scheme status.

That distinction drove the single biggest design decision in this package.

## 2. The no-fabrication rule, and why this package is full of sentinels

Applied consistently, the rule produced **534 sentinelled cells of 10,401 (5.13%)** — more than
double Package005's rate. The concentration is the finding:

| Cluster | Cells | What is sentinelled |
|---|---|---|
| **District variation** | 305 | `district_specific_variation`, all rows |
| **Monetary quantum** | ~85 | `financial_assistance`, `benefit_quantum` |
| **Timelines** | 43 | `typical_timeline`, all process rows |
| **Cross-package absences** | ~35 | Upstream records that do not exist |
| **Institution-type rows** | ~10 | `official_website` for agency and institution *types* |

### Why no amount is stated anywhere

This is the decision a reader is most likely to question, so it is worth being direct about.

A government scheme's benefit amount is revised by notification and budget cycle. PM-KISAN's
instalment, PMSBY's premium and cover, MUDRA's category ceilings, PMEGP's margin money percentage,
PM-JAY's family cover — every one of these has changed at least once since launch, and several
have changed more than once. Writing a figure into a dataset dated 2026-07-25 with no primary
source read would produce something that *looks* authoritative, is unverifiable, and will be wrong
at an unpredictable future date — in precisely the field an applicant relies on most.

So `government_schemes.financial_assistance` and `scheme_benefits.benefit_quantum` are sentinelled
throughout, and every row carries `official_portal` so a consumer can fetch the live figure.

The same logic applies to eligibility. `eligibility_criteria.criterion_value` says "below the
prescribed ceiling" rather than naming a rupee figure. This makes the package a **candidate-set
narrower, not an eligibility decider** — which is the honest description of what it can do.

### Why timelines are sentinelled

`application_process.typical_timeline` is the sentinel on all 43 rows. Only MGNREGA has a statutory
period, and even that is stated in `notes` rather than asserted as a data value. Every other
scheme's processing time is either unpublished or varies so widely by district and season that a
single figure would mislead.

### Why 305 district rows carry a sentinel in one column

`district_scheme_mapping` maps 5 district-delivered schemes across all 61 Package001 districts. The
`package001_dist_id`, `district_level_agency` and `application_channel` columns are fully
populated and structurally true: every district has a DIC, a Collector, Gram Panchayats. But
`district_specific_variation` — whether the benefit or capacity actually differs in *that* district
— was not confirmable per district. Rather than drop the column or invent variation, it is
sentinelled with the column retained, so v1.1.0 has somewhere to put the answer.

## 3. Source tiers and confidence

| Band | Tier | Sources |
|---|---|---|
| 70–85 | Tier 1 | The scheme's own portal (pmkisan.gov.in, pmjay.gov.in, mudra.org.in, scholarships.gov.in), administering ministries, India.gov.in, MyScheme |
| 62–69 | Tier 2 | Government notifications and gazette references |
| 56–61 | Tier 3 | Official scheme guidelines and operational manuals |
| 45–55 | Tier 4 | Ministry annual reports and derived aggregates |

**Ceiling 85, never reached. Observed range 60–78.**

Each scheme row is attributed to *its own portal* rather than to an aggregator. That is a
deliberate choice: `pmkisan.gov.in` is a stronger attribution for PM-KISAN than MyScheme is, even
though MyScheme is where a citizen would browse. Aggregators appear as `data_source` only on the
cross-cutting datasets (eligibility, benefits, process) where no single scheme portal governs.

**The floor of 60** is confined to `scheme_ai_recommendations`. Every row there scores exactly 60
because `priority_score` is a designed heuristic — a deterministic function of eligibility overlap,
benefit magnitude and sequencing logic — with no uptake, approval-rate or benefit-realisation data
behind it. Scoring those rows higher would imply empirical grounding the package does not have.

## 4. Design decisions worth explaining

### The registry is canonical, and the overlap is declared

Five released packages already carry scheme data: Package002 (25 scholarships), Package003 (9
health insurance), Package004 (18 MSME support), Package005 (12 agriculture), Package006 (15
skill). That is 79 scheme rows already in the knowledge base before Package007 existed.

Package007 could have ignored them, duplicated them, or absorbed them. It does none of those. The
`government_schemes.also_in_package` column names every package that already holds each scheme, and
the corresponding mapping dataset carries a hard foreign key to that package's record.

This makes the overlap **explicit and reconcilable** rather than a hidden fork. It does not
*resolve* the governance question of which package owns scheme truth — that decision is flagged in
`quality_report.md` and `codex_handoff.md` as the highest-priority open item.

### Eligibility is decomposed, not prose

`eligibility_criteria.csv` holds one row per condition, typed against a closed vocabulary (Age,
Gender, Income, Category, Occupation, Education, Land Holding, Business Size, Citizenship, Banking,
Other, Exclusion) matching the axes in the specification.

Holding eligibility as prose in a scheme row would have been faster and would have read fine. It
would also have been useless for machine matching, which is the stated purpose of the package. One
row per condition, with `is_mandatory` distinguishing hard gates from quantum-affecting factors, is
what makes rule-based screening possible.

`is_mandatory = No` is doing real work: SMAM's category criterion affects the *subsidy percentage*,
not whether you qualify. Collapsing that into a single eligibility flag would produce false
exclusions.

### Benefits are itemised, not summarised

PM Vishwakarma delivers training with a stipend, a toolkit incentive, and credit in tranches. Those
are three rows in `scheme_benefits.csv`, not one. A recommender that needs to answer "which schemes
give equipment support" cannot do it against a collapsed summary field.

### QUERY_RAISED was added to the status workflow

The specification listed Draft, Submitted, Under Review, Approved, Rejected, Disbursed, Closed.
`scheme_application_status.csv` adds an eighth: `QUERY_RAISED`. It is the single most common cause
of silent application failure — an application sent back for clarification that the applicant never
responds to, which eventually becomes a rejection they do not understand. A status model without it
cannot represent the most common failure mode.

### District mapping covers 5 schemes, not 40

Mapping all 40 schemes across 61 districts would produce 2,440 rows and assert a district dimension
that does not exist for 35 of them. Central schemes are nationally uniform in *coverage*; what
varies by district is *which office you approach*, and that only applies where the application is
district-mediated. Five schemes qualify. The other 35 are excluded deliberately.

## 5. Cross-package foreign keys resolved at generation time

`gen_mappings.py` reads the upstream CSVs and resolves every foreign key against them **while
generating**, aborting on any unresolvable reference. Nine FK sets into five packages, zero
unresolved.

This caught two real defects that would otherwise have shipped:

**Package006 has no entrepreneurship skill.** The PMEGP skill mapping assumed one existed — a
Package006 *collection report* describes "MSME Entrepreneurship & Startup Launch" — but the
released `skills.csv` does not contain it. The generator aborted. The row now sentinels all four
Package006 columns.

The lesson generalises: **a collection report described data the dataset does not contain.**
Trusting documentation over the artifact would have produced a broken foreign key. Only reading the
actual CSV surfaced it.

**Package004 has no AI opportunity.** The SISFS industry mapping assumed one. It does not exist;
the row was repointed at the real `Small IT Services Firm / Software Development Startup` record.

## 6. Validation

Twelve checks in `validate.py`. Three are new relative to Package005's ten:

- **V11 (scheme coverage)** — every scheme must have at least one eligibility row and one benefit
  row. This caught four schemes with no eligibility rows at all: Soil Health Card, Samagra Shiksha,
  PM POSHAN and AB-HWC, all universal, institutional or automatic-entitlement schemes with nothing
  to screen. Absence was the wrong representation — a consumer cannot distinguish "no criteria
  exist" from "criteria not yet collected". Explicit rows were added stating the universality.
- **V12 (enum integrity)** — closed domains on `government_level`, `status`, `is_mandatory`,
  `is_terminal`, `priority_sector_lending`.
- **V8 extended** — beyond id resolution, it validates the semicolon-delimited
  `related_scheme_ids` multi-value column member by member, and checks
  `eligibility_criteria.verification_document_hint` against actual `required_documents` names.

V8's denormalised-name check caught a subtler defect: `government_schemes` recorded Stand-Up
India's `short_name` as `SUI` while five child datasets used `Stand-Up India`. Every *join* would
have worked — the ids were correct — but any display or `GROUP BY` on the denormalised column would
have split one scheme into two.

**Final state: 655 records, 10,401 cells, 0 violations.**

## 7. Reproducibility

| Script | Produces |
|---|---|
| `gen_core.py` | 7 scheme-intrinsic datasets |
| `gen_mappings.py` | 8 relational and workflow datasets, resolving upstream FKs live |
| `validate.py` | `validation_summary.json`, exit status |
| `build_artifacts.py` | schema catalog, 15 metadata files, registry, manifest, 15 collection reports |
| `build_docs.py` | data dictionary, import guide, validation report, quality report, version history, release notes |

```bash
python3 gen_core.py && python3 gen_mappings.py \
  && python3 validate.py && python3 build_artifacts.py && python3 build_docs.py
```

Order matters: both builders read `validation_summary.json`, so validation runs first. Every count
in every artifact is derived from the CSVs rather than hand-maintained, which is why they cannot
drift out of agreement with the data.

## 8. What would raise confidence

In priority order:

1. **Unblock government-domain fetching.** This alone would lift the ceiling above 85 and let
   amounts, rates, ceilings and current scheme status be confirmed rather than attributed. It is
   the single largest constraint on this package.
2. **Human data-steward review of the 40 registry rows.** Highest value per hour, because
   everything else hangs off the registry.
3. **Resolve the duplication governance question.** Every release that passes without deciding
   makes the eventual reconciliation larger.
4. **Scheme currency monitoring.** Schemes are renamed, merged and subsumed. `status` has enum
   values for Closed, Subsumed and Revised, but nothing currently detects when one applies.
5. **State scheme registry**, reconciled against the state slices already in Package002,
   Package003 and Package004.
