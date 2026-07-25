# Validation Report — Package008_MSME v1.0.0

**Result: PASS** · 0 violations · 18 datasets · 477 records · 7770 cells · 40 businesses

**Normalization check (V13): V13 PASS**

Validated 2026-07-25 by `validate.py` (in-package, re-runnable). Machine-readable output in `validation_summary.json`.

## Checks run

| Check | Enforces | Result |
|---|---|---|
| V1 Structural | Every row matches its header's column count | PASS |
| V2 Primary key | Unique and non-empty in all 18 datasets | PASS |
| V3 Provenance | All six provenance columns on every dataset | PASS |
| V4 Confidence | Integer, 0-100, <= 85 ceiling | PASS |
| V5 Sentinel | Bare-string discipline | PASS |
| V6 Verification | `verification_status` enum | PASS |
| V7 Collection date | Uniform `2026-07-25` | PASS |
| V8 In-package FK | FKs resolve; denormalised names agree | PASS |
| V9 Cross-package FK | Ten FK sets into six upstream packages | PASS |
| V10 Empty cells | No silently blank cells | PASS |
| V11 Coverage | Every business has >=1 scheme, skill and machinery row, and exactly 1 investment row | PASS |
| V12 Enum integrity | Closed domains on 11 classification columns | PASS |
| **V13 Normalization** | **No column restates an upstream-owned attribute** | **PASS** |

## V13 — the normalization rule, enforced mechanically

The brief states Package008 **SHALL NOT** duplicate government schemes, skills, industries, geography, education or agriculture. A rule that is only written down erodes, so V13 enforces it in code: the build fails if any Package008 column name collides with an attribute owned by an upstream entity.

| Upstream owner | Forbidden column fragments |
|---|---|
| Package007 scheme | `scheme_benefit`, `benefit_amount`, `eligibility_criteri`, `application_mode`, `ministry`, `scheme_objective`, `subsidy_component`; plus `official_portal` on any dataset referencing `package007_scheme_id` |
| Package006 skill | `nsqf`, `skill_duration`, `learning_duration`, `training_duration`, `skill_description` |
| Package005 crop | `crop_season`, `crop_yield`, `water_requirement`, `soil_type`, `rainfall`, `scientific_name` |
| Package001 district | `population`, `area_sq_km`, `literacy`, `sex_ratio`, `latitude`, `longitude`, `mandal_count` |
| Package002 institution | `established_year`, `affiliation`, `university_type` |

V13 flagged two apparent violations on its first run: `official_portal` in `license_compliance.csv` and `market_channels.csv`. Both were **false positives** — those are licence portals (FOSCOS, GST, Udyam, DGFT) and sales-channel portals (GeM, ONDC), and Package007 owns neither licences nor channels.

Rather than add blanket exceptions, the rule was **narrowed to be correct**: flag `official_portal` only on datasets that already reference `package007_scheme_id`, which is precisely where restating a scheme portal would be duplication. Narrowing a check beats suppressing it — a suppressed check stops finding anything.

One deliberate exception is declared in code: `financial_support.linked_package007_scheme_short_name` is a navigational pointer, not a scheme attribute. It says which scheme a finance source connects to and nothing about that scheme.

## Per-dataset results

| Dataset | Records | Cols | PK unique | Confidence | Avg | Sentinel | Blank |
|---|---|---|---|---|---|---|---|
| `msme_categories.csv` | 24 | 14 | ok | 58-78 | 70.6 | 0 | 0 |
| `business_models.csv` | 15 | 14 | ok | 64-76 | 70.7 | 15 | 0 |
| `license_compliance.csv` | 14 | 16 | ok | 66-78 | 71.4 | 6 | 0 |
| `financial_support.csv` | 12 | 15 | ok | 62-76 | 71.2 | 8 | 0 |
| `market_channels.csv` | 11 | 15 | ok | 62-74 | 68.5 | 19 | 0 |
| `ai_business_tools.csv` | 12 | 15 | ok | 57-72 | 63.1 | 0 | 0 |
| `startup_ecosystem.csv` | 12 | 15 | ok | 66-76 | 70.2 | 3 | 0 |
| `msme_businesses.csv` | 40 | 26 | ok | 63-74 | 69.0 | 40 | 0 |
| `machinery_mapping.csv` | 64 | 16 | ok | 61-72 | 66.8 | 108 | 0 |
| `raw_material_mapping.csv` | 33 | 17 | ok | 60-72 | 66.5 | 42 | 0 |
| `scheme_mapping.csv` | 57 | 14 | ok | 61-73 | 67.8 | 0 | 0 |
| `skill_mapping.csv` | 53 | 14 | ok | 57-72 | 66.4 | 14 | 0 |
| `industry_mapping.csv` | 19 | 13 | ok | 60-74 | 68.6 | 0 | 0 |
| `agriculture_business_mapping.csv` | 14 | 14 | ok | 58-74 | 70.0 | 8 | 0 |
| `education_support_mapping.csv` | 13 | 15 | ok | 64-70 | 67.4 | 26 | 0 |
| `district_business_mapping.csv` | 32 | 16 | ok | 62-74 | 67.9 | 0 | 0 |
| `export_opportunities.csv` | 12 | 15 | ok | 60-72 | 66.2 | 0 | 0 |
| `investment_intelligence.csv` | 40 | 20 | ok | 61-72 | 67.0 | 0 | 0 |
| **package** | **477** | — | ok | **57-78** | — | **289** (3.72%) | **0** |

## Cross-package foreign key integrity (V9)

**Ten foreign key sets into six released packages — 213 resolved, 99 sentinel, 0 unresolved.** Every id was resolved against the upstream CSV at generation time; the generator aborts rather than write an unresolvable reference, and V9 re-checks on every run.

| Reference | Resolved | Sentinel | Unresolved |
|---|---|---|---|
| `district_business_mapping.package001_dist_id` -> Package001 `district.dist_id` | 32 | 0 | **0** |
| `education_support_mapping.package002_institution_id` -> Package002 `universities.id` | 4 | 9 | **0** |
| `raw_material_mapping.package005_crop_id` -> Package005 `crops.crop_id` | 12 | 21 | **0** |
| `agriculture_business_mapping.package005_crop_id` -> Package005 `crops.crop_id` | 10 | 4 | **0** |
| `machinery_mapping.package005_machinery_id` -> Package005 `farm_machinery.machinery_id` | 10 | 54 | **0** |
| `agriculture_business_mapping.package005_processing_opportunity_id` -> Package005 `agri_processing_opportunities.opportunity_id` | 14 | 0 | **0** |
| `skill_mapping.package006_skill_id` -> Package006 `skills.skill_id` | 46 | 7 | **0** |
| `education_support_mapping.package006_provider_id` -> Package006 `training_providers.provider_id` | 9 | 4 | **0** |
| `scheme_mapping.package007_scheme_id` -> Package007 `government_schemes.scheme_id` | 57 | 0 | **0** |
| `industry_mapping.package004_opportunity_id` -> Package004 `id` (4 datasets) | 19 | 0 | **0** |

V9 also verifies the **denormalised upstream name** agrees with the upstream record, not just that the id exists — a stale `package006_skill_name` against a valid `skill_id` fails.

### What the sentinels mean

- **Package005 machinery (54 of 64 sentinel)** — the largest block, and a scope statement not a gap. Package005's `farm_machinery` catalogues *agricultural* machinery; a CNC machining centre, a module laminator or a biochemistry analyser is correctly absent. The 10 that resolve — rice mill, dal mill, oil expeller, cold storage, solar dryer, packaging machine, cold chain, agricultural drone — are referenced rather than restated. That is the normalization rule working at row level.
- **Package005 crop (21 of 33 raw materials sentinel)** — non-agricultural inputs. Steel, switchgear, surfactants and solar cells are not crops.
- **Package006 skill (7 of 53 sentinel)** — a **real upstream coverage gap**. Package006 v1.0.0 has no skill record for foundry casting, handloom weaving, corrugation machine operation, plastic reprocessing, chemical formulation, data entry or training delivery. Each is an explicit sentinel row with the requirement stated in `skill_role`, not pointed at an approximate skill. This is a concrete, actionable request back to Package006.
- **Package002 institution (9 of 13 sentinel)** — most `education_support_mapping` rows legitimately belong to Package006 (ITI, polytechnic, skill mission) rather than Package002 (degree-granting universities). One side or the other is populated, not both.

## In-package foreign key integrity (V8)

| Reference | Target | Rows | Result |
|---|---|---|---|
| `msme_businesses.category_id` | `msme_categories.category_id` | 40 | PASS |
| `msme_businesses.business_model_id` | `business_models.business_model_id` | 40 | PASS |
| `machinery_mapping.business_id` | `msme_businesses.business_id` | 64 | PASS |
| `raw_material_mapping.business_id` | `msme_businesses.business_id` | 33 | PASS |
| `scheme_mapping.business_id` | `msme_businesses.business_id` | 57 | PASS |
| `skill_mapping.business_id` | `msme_businesses.business_id` | 53 | PASS |
| `industry_mapping.business_id` | `msme_businesses.business_id` | 19 | PASS |
| `agriculture_business_mapping.business_id` | `msme_businesses.business_id` | 14 | PASS |
| `district_business_mapping.business_id` | `msme_businesses.business_id` | 32 | PASS |
| `export_opportunities.business_id` | `msme_businesses.business_id` | 12 | PASS |
| `investment_intelligence.business_id` | `msme_businesses.business_id` | 40 | PASS |

## Issues found and resolved during validation

Five defect classes, all caught by the checks. Two generalise beyond this package:

**1. Cross-package FK to skills that do not exist (V9, at generation).** Three skill needles did not match Package006's actual `skill_name` values: `PLC Programming & SCADA` (actually `PLC Programming & Control Systems`), `Domestic Electrician` (actually `Electrician (Domestic Wiring)`), `Nursing Assistant / Health Worker` (actually `Nursing Assistant / Multipurpose Health Worker`). The generator aborted on each. Two further needles matched nothing at all — Package006 has no data-entry or communication skill — and became explicit sentinel rows.

**2. Ten wrong district refs (V9, at generation).** `AP-GNT`, `AP-KNL`, `AP-EG`, `AP-WG`, `AP-VSP`, `AP-SKL`, `AP-CTR`, `AP-PKM`, `TG-SGR`, `TG-KMM` were plausible-looking and do not exist in Package001's district master. The real refs are `AP-GUN`, `AP-KUR`, `AP-EAS`, `AP-WES`, `AP-VIS`, `AP-SRI`, `AP-CHI`, `AP-PRA`, `TG-SNG`, `TG-KHM`. Every one would have produced a broken join. **Guessing an id format is not reading it.**

**3. Eleven businesses with no skill or machinery mapping (V11).** Four asset-light businesses (SaaS, digital marketing, rural BPO, homestay) had no machinery row and seven had no skill row. Absence was the wrong representation: a consumer cannot distinguish 'needs no machinery' from 'not yet mapped'. Rows were added — IT and premises infrastructure for the asset-light four, a real Package006 match for two skills, explicit sentinel rows for the five with no upstream counterpart.

**4. V13 false positives, resolved by narrowing rather than suppressing.** See above.

**5. A Package004 opportunity that does not exist.** As in Package007, an assumed AI opportunity had to be repointed at the real `Small IT Services Firm / Software Development Startup` record. Recorded because it recurs.

## Confidence distribution

Package range **57-78**, ceiling **85** (never reached). Lowest first, since that is where a reviewer should look:

| Dataset | Avg | Range | Why |
|---|---|---|---|
| `ai_business_tools.csv` | 63.1 | 57-72 | Adoption maturity is an industry-reporting judgement, not measured penetration |
| `export_opportunities.csv` | 66.2 | 60-72 | DGFT, APEDA and council attribution; barriers are analytical |
| `skill_mapping.csv` | 66.4 | 57-72 | Seven rows record a genuine Package006 absence and score 57 to say so |
| `raw_material_mapping.csv` | 66.5 | 60-72 | Input lists are Tier 1-2; volatility ratings are qualitative |
| `machinery_mapping.csv` | 66.8 | 61-72 | MSME-DI project profile framing; configurations are indicative |
| `investment_intelligence.csv` | 67.0 | 61-72 | Every field is ordinal; no computed return exists to validate against |
| `education_support_mapping.csv` | 67.4 | 64-70 | Institution-to-category talent flow is an analytical judgement |
| `scheme_mapping.csv` | 67.8 | 61-73 | Package007 reconciliation; all 57 rows resolve |
| `district_business_mapping.csv` | 67.9 | 62-74 | Package001 master plus Package005 district attribution |
| `market_channels.csv` | 68.5 | 62-74 | Channel structure documented; payment terms are per-buyer and unsourceable |
| `industry_mapping.csv` | 68.6 | 60-74 | Relationship strength between two packages is an analytical judgement |
| `msme_businesses.csv` | 69.0 | 63-74 | MSME-DI project profiles and sector ministries; attributes are ordinal |
| `agriculture_business_mapping.csv` | 70.0 | 58-74 | Package005 reconciliation; one deliberately weak link at 58 |
| `startup_ecosystem.csv` | 70.2 | 66-76 | Entity roles are Tier 1; network rows describe types not named offices |
| `msme_categories.csv` | 70.6 | 58-78 | Ministry attribution is Tier 1; intensity ratings are ordinal |
| `business_models.csv` | 70.7 | 64-76 | Model attributes are structural judgements; lead time unsourceable |
| `financial_support.csv` | 71.2 | 62-76 | Institutions and instruments Tier 1; institution-type rows categorical |
| `license_compliance.csv` | 71.4 | 66-78 | Issuing authorities are Tier 1; state routes and thresholds vary |

The floor of 57 is not a quality failure. It appears on rows recording a genuine upstream absence — a business needs a skill Package006 does not catalogue — where the low score is the signal that the row is a placeholder for missing upstream data rather than an assertion.

## Sentinel distribution

**289 of 7770 cells (3.72%)**:

| Dataset | Column | Rows |
|---|---|---|
| `machinery_mapping.csv` | `package005_machinery_id` | 54 / 64 |
| `machinery_mapping.csv` | `package005_machinery_name` | 54 / 64 |
| `msme_businesses.csv` | `investment_range` | 40 / 40 |
| `raw_material_mapping.csv` | `package005_crop_id` | 21 / 33 |
| `raw_material_mapping.csv` | `package005_crop_name` | 21 / 33 |
| `business_models.csv` | `typical_lead_time_to_revenue` | 15 / 15 |
| `market_channels.csv` | `typical_payment_cycle` | 11 / 11 |
| `education_support_mapping.csv` | `package002_institution_id` | 9 / 13 |
| `education_support_mapping.csv` | `package002_institution_name` | 9 / 13 |
| `market_channels.csv` | `official_portal` | 8 / 11 |
| `skill_mapping.csv` | `package006_skill_id` | 7 / 53 |
| `skill_mapping.csv` | `package006_skill_name` | 7 / 53 |
| `license_compliance.csv` | `official_portal` | 6 / 14 |
| `financial_support.csv` | `official_website` | 4 / 12 |
| `financial_support.csv` | `linked_package007_scheme_short_name` | 4 / 12 |
| `agriculture_business_mapping.csv` | `package005_crop_id` | 4 / 14 |
| `agriculture_business_mapping.csv` | `package005_crop_name` | 4 / 14 |
| `education_support_mapping.csv` | `package006_provider_id` | 4 / 13 |
| `education_support_mapping.csv` | `package006_provider_name` | 4 / 13 |
| `startup_ecosystem.csv` | `official_website` | 3 / 12 |

## Verification status

**All 477 records are `VST-NEEDS_REVIEW`.** Nothing has had human data-steward sign-off. Machine validation confirms structure, referential integrity across six packages, provenance completeness, business coverage and the normalization rule. It does not confirm that a business is viable, that an investment band is right, or that a district suitability claim holds.

## Reproducing this report

```bash
cd packages/Package008_MSME
python3 validate.py && python3 build_docs.py
```

Every figure is derived from the released CSVs rather than hand-maintained.
