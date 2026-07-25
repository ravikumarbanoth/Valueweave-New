# Methodology — Package008_MSME v1.0.0

How the 18 datasets were built, sourced, scored and validated.

## 1. Environment constraint, stated first

Direct `WebFetch` to `.gov.in`, `.nic.in` and `.ac.in` domains is blocked by this session's
organizational egress policy — the same constraint that applied to Package004 through Package007.

**Consequence:** no row rests on a primary-source page read. Every row is attributed to the
ministry, authority or association that governs the fact, and `confidence_score` is capped at 85
package-wide to record that the attribution was not confirmed by fetching the page.

**What this does not mean:** the structural facts here are stable published knowledge — which
ministry runs a scheme, what a licence is called and who issues it, which machine a rice mill
needs, what NIC division a category maps to. What could not be confirmed is anything that moves,
and in this package that is dominated by one thing: money.

## 2. Why no rupee figure appears anywhere

This is the decision most likely to be questioned, so it is worth being direct.

`msme_businesses.investment_range` is the bare sentinel on **all 40 rows**. So is every machinery
cost, every payment cycle, and every lead time to revenue. `investment_intelligence` contains no
percentage, no payback period and no IRR.

The reason is not that investment figures are unknowable. It is that **a per-business project cost
is not a single number**. A rice mill's capital requirement depends on throughput, degree of
automation, whether the building is owned or rented, whether a boiler is included, and which state
you are in. MSME-DI project profiles do exist and do carry costed configurations — but they are
specific to a stated configuration, and this environment could not fetch them. Writing a plausible
"₹15–25 lakh" into a dataset dated 2026-07-25 with no source would look authoritative, be
unverifiable, and be wrong for most readers.

What the package carries instead:

- **`udyam_classification`** — Micro, Small or Medium. These are the **statutory** categories under
  the MSMED Act, and placing a business in one is a defensible classification rather than an
  invented figure.
- **`capex_intensity`** and **`working_capital_intensity`** in `investment_intelligence` — ordinal
  bands (Very Low to Very High). `capex_intensity` is derived deterministically from the business
  model rather than assigned per business, so it cannot drift from `business_models.csv`.
- **`investment_category`** in `machinery_mapping` — Core Plant, Ancillary, Tooling, IT
  Infrastructure or Premises. This tells you what kind of spend a machine represents without
  pretending to know how much.

Where costs genuinely matter, **Package004_Industries already carries sourced
`investment_range_summary` and `machinery_equipment_summary` for the overlapping food-processing
and trade-service opportunities.** `industry_mapping` points at those records. That is the correct
source, and Package008 deliberately does not approximate it.

Sentinel total: **289 of 7,770 cells (3.72%)**, concentrated as follows.

| Cluster | Cells | What is sentinelled |
|---|---|---|
| Upstream absence in `machinery_mapping` | 108 | `package005_machinery_id` + name for non-agricultural machines |
| Upstream absence in `raw_material_mapping` | 42 | `package005_crop_id` + name for non-crop inputs |
| Monetary and duration | ~66 | `investment_range`, lead time, payment cycle |
| Upstream absence elsewhere | ~40 | Package002 institution, Package006 skill, Package005 crop |
| Institution-type rows | ~10 | `official_website` / `official_portal` for entity *types* |

Note that the **largest sentinel block is not missing data at all** — it is 108 cells recording
that Package005's `farm_machinery` does not catalogue CNC machining centres or biochemistry
analysers, which is correct, because Package005 is an agriculture package.

## 3. The normalization rule, and why it is enforced in code

The brief states: Package008 SHALL NOT duplicate Government Schemes, Skills, Industries, Geography,
Education or Agriculture. Reference upstream IDs wherever possible.

Every previous package in this programme documented its cross-package relationships in prose and
enforced only that the ids resolved. That is not enough. A rule about what a package must *not*
contain cannot be enforced by checking what it *does* contain resolves correctly — you have to
check for the presence of columns that should not exist.

So **V13** exists. It fails the build if any Package008 column name collides with an attribute
owned by an upstream entity:

| Upstream owner | Forbidden fragments |
|---|---|
| Package007 scheme | `scheme_benefit`, `benefit_amount`, `eligibility_criteri`, `application_mode`, `ministry`, `scheme_objective`, `subsidy_component` |
| Package006 skill | `nsqf`, `skill_duration`, `learning_duration`, `training_duration`, `skill_description` |
| Package005 crop | `crop_season`, `crop_yield`, `water_requirement`, `soil_type`, `rainfall`, `scientific_name` |
| Package001 district | `population`, `area_sq_km`, `literacy`, `sex_ratio`, `latitude`, `longitude`, `mandal_count` |
| Package002 institution | `established_year`, `affiliation`, `university_type` |

The check found two apparent violations immediately: `official_portal` in `license_compliance.csv`
and `market_channels.csv`. Both were false positives — those are licence portals (FOSCOS, GST,
Udyam, DGFT) and channel portals (GeM, ONDC), and Package007 owns neither licences nor channels.

The fix was to **narrow the rule to be correct**, not to add exceptions: `official_portal` is
flagged only on datasets that already reference `package007_scheme_id`, which is exactly where
restating a scheme portal would be duplication. A suppressed check stops finding anything; a
narrowed check keeps working.

One exception is declared explicitly in code:
`financial_support.linked_package007_scheme_short_name` is a navigational pointer — it says which
scheme a finance source connects to, and nothing about that scheme.

### What normalization looks like in practice

`machinery_mapping` is the clearest illustration. It holds 64 rows. Ten of them name a machine that
Package005 already catalogues — rice mill, dal mill, oil expeller, cold storage, solar dryer,
packaging machine, cold chain, agricultural drone — and those rows carry
`package005_machinery_id` instead of restating the machine's power rating, automation level or
subsidy scheme. The other 54 name machines Package005 does not hold, and sentinel the reference.

The same pattern runs through `raw_material_mapping` (crop inputs referenced, steel and chemicals
not), `scheme_mapping` (57 scheme ids, zero scheme attributes) and `skill_mapping` (46 skill ids,
zero NSQF levels).

## 4. Source tiers and confidence

| Band | Tier | Sources |
|---|---|---|
| 70–85 | Tier 1 | Ministry of MSME, Udyam portal, SIDBI, NABARD, NSIC, KVIC, DPIIT, Startup India, GeM, MSME-DIs, state industries departments, sector ministries |
| 62–69 | Tier 2 | Government reports and programme literature |
| 56–61 | Tier 3 | Industry associations — CII, FICCI, ASSOCHAM, NASSCOM |
| 45–55 | Tier 4 | Official sector reports |

**Ceiling 85, never reached. Observed range 57–78.**

The floor of **57** is worth explaining because it is not a quality failure. It appears on seven
`skill_mapping` rows where Package006 v1.0.0 has **no matching skill record** — foundry casting,
handloom weaving, corrugation machine operation, plastic reprocessing, chemical formulation, data
entry and training delivery. Each row states the requirement in `skill_role` and sentinels the id.
Scoring those at 70 would imply the link was verified; 57 says "this is a placeholder for missing
upstream data".

That is a concrete, actionable output: **Package008 has produced a documented coverage request back
to Package006.**

## 5. Design decisions worth explaining

**Categories separate four things the brief's list conflated.** The 24 categories include
Manufacturing (a primary sector group), Food Processing (a manufacturing sub-sector), IT (a service
sub-sector) and AI (an emerging sector). Treating those as one flat level would be misleading, so
`category_group` distinguishes them. `nic_section_hint` anchors each to the National Industrial
Classification so consumers can bridge to official statistics.

**Business models are classified by what they depend on.** Asset-Based, Skill-Based,
Working-Capital-Based, IP-Based, Infrastructure, Project-Based. That classification tells an
entrepreneur what the binding constraint will be, which is more useful than the model's name.
`primary_risk` names the specific failure mode.

**Every business has a machinery row, even the asset-light ones.** V11 enforces this. SaaS,
digital marketing, rural BPO and homestay initially had none, which was wrong: a consumer cannot
distinguish "needs no machinery" from "not yet mapped". They now carry IT infrastructure or
premises rows.

**District suitability is sparse by design.** 32 rows across 61 districts and 40 businesses. A full
cross-product would be 2,440 rows of mostly unfounded assertion. Every row that exists names the
documented characteristic that justifies it in `suitability_basis` — Nizamabad's turmeric market
yard, Guntur's chilli yard, Anantapur's groundnut area, Hyderabad's IT concentration. Most of those
characteristics come from Package005's `major_districts` field, which is itself sourced.

**Export rows name the binding barrier, not just the certificates.** For garments the blocker is
social compliance audit readiness, not product quality. For spices it is residue testing capability.
For software there is no physical certification at all — the barrier is data-protection compliance.
`export_readiness_barrier` carries that, and it is the most actionable field in the dataset.

## 6. Cross-package foreign keys resolved at generation time

`gen_mappings.py` reads the upstream CSVs and resolves every foreign key **while generating**,
aborting on any unresolvable reference. Ten FK sets into six packages, zero unresolved.

This caught two classes of defect that would otherwise have shipped:

**Ten district refs were plausible guesses and did not exist.** `AP-GNT`, `AP-KNL`, `AP-EG`,
`AP-WG`, `AP-VSP`, `AP-SKL`, `AP-CTR`, `AP-PKM`, `TG-SGR`, `TG-KMM`. The real ones are `AP-GUN`,
`AP-KUR`, `AP-EAS`, `AP-WES`, `AP-VIS`, `AP-SRI`, `AP-CHI`, `AP-PRA`, `TG-SNG`, `TG-KHM`. Every one
would have produced a silently broken join. **Guessing an id format is not reading it.**

**Three skill names did not match Package006's actual values.** `PLC Programming & SCADA` (actually
`PLC Programming & Control Systems`), `Domestic Electrician` (actually
`Electrician (Domestic Wiring)`), `Nursing Assistant / Health Worker` (actually
`Nursing Assistant / Multipurpose Health Worker`). Two further needles matched nothing at all.

The lesson is the same one Package007 recorded: **trust the dataset, not its documentation, and not
memory.**

## 7. Validation

Thirteen checks in `validate.py`. Three are new relative to Package007's twelve:

- **V11 (business coverage)** — every business must have at least one scheme, skill and machinery
  mapping, and exactly one `investment_intelligence` row. Caught eleven gaps.
- **V12 (enum integrity)** — closed domains on eleven classification columns, which is what makes
  the dataset machine-filterable rather than free text.
- **V13 (normalization)** — described in §3.

**Final state: 477 records, 7,770 cells, 0 violations.**

## 8. Reproducibility

| Script | Produces |
|---|---|
| `gen_core.py` | 9 datasets with no upstream dependency |
| `gen_mappings.py` | 9 datasets, resolving upstream FKs live |
| `validate.py` | `validation_summary.json`, exit status |
| `build_artifacts.py` | schema catalog, 18 metadata files, registry, manifest, 18 collection reports |
| `build_docs.py` | data dictionary, import guide, validation report, quality report, version history, release notes |

```bash
python3 gen_core.py && python3 gen_mappings.py \
  && python3 validate.py && python3 build_artifacts.py && python3 build_docs.py
```

Order matters: both builders read `validation_summary.json`, so validation runs first. Every count
in every artifact is derived from the CSVs rather than hand-maintained.

## 9. What would raise confidence

In priority order:

1. **DIC and MSME-DI project profiles** for investment bands. This is the single largest gap between
   this package and entrepreneur-facing use. MSME-DI publishes project profiles free of charge —
   they are the right primary source, and `startup_ecosystem.csv` records that they are the most
   under-used MSME resource.
2. **Unblock government-domain fetching**, which would let the above happen and lift the ceiling
   above 85.
3. **Human data-steward review of the 40 business rows.** Everything else hangs off them.
4. **Feed the seven unmatched skill requirements back to Package006.** Already documented as
   sentinel rows with the requirement stated.
5. **A general industrial machinery reference**, or an expanded Package005 `farm_machinery`, so the
   54 sentinelled machinery references can resolve.
6. **Expand beyond 40 businesses** toward full category coverage — semiconductors, robotics and
   creative industries have one business each.
