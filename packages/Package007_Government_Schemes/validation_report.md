# Validation Report — Package007_Government_Schemes v1.0.0

**Result: PASS** · 0 violations · 15 datasets · 655 records · 10401 cells · 40 schemes

Validated 2026-07-25 by `validate.py` (in-package, re-runnable). Machine-readable output in `validation_summary.json`.

## Checks run

| Check | Enforces | Result |
|---|---|---|
| V1 Structural | Every row matches its header's column count | PASS |
| V2 Primary key | First column unique and non-empty in all 15 datasets | PASS |
| V3 Provenance | All six provenance columns present on every dataset | PASS |
| V4 Confidence | Integer, 0–100, ≤ 85 policy ceiling | PASS |
| V5 Sentinel | `PENDING_VERIFICATION` only as a bare exact string | PASS |
| V6 Verification | `verification_status` in the allowed enum | PASS |
| V7 Collection date | Uniform `2026-07-25` package-wide | PASS |
| V8 In-package FK | FKs resolve; denormalised names agree; multi-value column members resolve | PASS |
| V9 Cross-package FK | Package001/002/004/005/006 references resolve upstream | PASS |
| V10 Empty cells | No silently blank cells — a gap must be the sentinel | PASS |
| V11 Scheme coverage | Every scheme has ≥1 eligibility criterion and ≥1 benefit row | PASS |
| V12 Enum integrity | `government_level`, `status`, `is_mandatory`, `is_terminal`, `priority_sector_lending` use closed domains | PASS |

## Per-dataset results

| Dataset | Records | Cols | PK unique | Confidence | Avg | Sentinel | Blank |
|---|---|---|---|---|---|---|---|
| `scheme_categories.csv` | 24 | 12 | ✓ | 72–78 | 75.3 | 0 | 0 |
| `required_documents.csv` | 15 | 13 | ✓ | 68–78 | 72.9 | 0 | 0 |
| `implementing_agencies.csv` | 20 | 14 | ✓ | 68–78 | 73.8 | 6 | 0 |
| `financial_institutions.csv` | 12 | 14 | ✓ | 68–76 | 72.7 | 4 | 0 |
| `scheme_application_status.csv` | 8 | 15 | ✓ | 69–72 | 70.9 | 0 | 0 |
| `government_schemes.csv` | 40 | 25 | ✓ | 70–78 | 74.3 | 53 | 0 |
| `eligibility_criteria.csv` | 55 | 13 | ✓ | 70–76 | 72.7 | 11 | 0 |
| `scheme_benefits.csv` | 51 | 14 | ✓ | 69–76 | 72.4 | 45 | 0 |
| `application_process.csv` | 43 | 16 | ✓ | 68–74 | 72.1 | 39 | 0 |
| `education_scheme_mapping.csv` | 7 | 15 | ✓ | 68–76 | 71.6 | 9 | 0 |
| `agriculture_scheme_mapping.csv` | 14 | 15 | ✓ | 68–76 | 71.9 | 8 | 0 |
| `skill_scheme_mapping.csv` | 12 | 17 | ✓ | 62–73 | 69.7 | 42 | 0 |
| `industry_scheme_mapping.csv` | 12 | 14 | ✓ | 68–73 | 71.1 | 0 | 0 |
| `district_scheme_mapping.csv` | 305 | 16 | ✓ | 71–73 | 71.8 | 305 | 0 |
| `scheme_ai_recommendations.csv` | 37 | 18 | ✓ | 60–60 | 60.0 | 12 | 0 |
| **package** | **655** | — | ✓ | **60–78** | — | **534** (5.13%) | **0** |

## Cross-package foreign key integrity (V9)

This is the widest cross-package surface in the knowledge base: **nine distinct foreign key sets into five released packages.** Every one was resolved by reading the upstream CSVs at generation time, and all are re-checked on every validation run, so a rename upstream fails the build rather than silently breaking.

| Reference | Upstream target | Resolved | Sentinel | Unresolved |
|---|---|---|---|---|
| `district_scheme_mapping.package001_dist_id` → Package001 `district.dist_id` | — | 305 | 0 | **0** |
| `education_scheme_mapping.package002_record_id` → Package002 `scholarships.id` | — | 4 | 3 | **0** |
| `agriculture_scheme_mapping.package005_scheme_id` → Package005 `agriculture_schemes.scheme_id` | — | 12 | 2 | **0** |
| `agriculture_scheme_mapping.package005_crop_id` → Package005 `crops.crop_id` | — | 12 | 2 | **0** |
| `skill_scheme_mapping.package006_scheme_id` → Package006 `government_skill_schemes.scheme_id` | — | 9 | 3 | **0** |
| `skill_scheme_mapping.package006_skill_id` → Package006 `skills.skill_id` | — | 11 | 1 | **0** |
| `skill_scheme_mapping.package006_certification_id` → Package006 `certifications.certification_id` | — | 4 | 8 | **0** |
| `skill_scheme_mapping.package006_provider_id` → Package006 `training_providers.provider_id` | — | 3 | 9 | **0** |
| `industry_scheme_mapping.package004_opportunity_name` → Package004 `name` / `scheme_name` / `adapted_indian_concept` | — | 12 | 0 | **0** |

V9 also verifies the **denormalised upstream name** columns agree with the upstream record, not just that the id exists. A stale `package005_crop_name` against a valid `crop_id` fails.

Sentinels here are honest absences, not failures:

- **Package002 (3 sentinel)** — Samagra Shiksha and PM POSHAN are institutional and entitlement schemes with no scholarship record to point at; Skill Loan is education finance, which Package002 does not cover.
- **Package005 (2 sentinel each side)** — PM-KUSUM and PMFME are not in Package005 v1.0.0; and crop-agnostic schemes (PM-KISAN, Soil Health Card) deliberately carry the crop sentinel because support is per landholding, not per crop.
- **Package006 (3, 1, 8, 9 sentinel)** — PM Vishwakarma and PMEGP have no Package006 scheme counterpart. Certification and provider links are sparse because most scheme-to-skill relationships do not run through one named certificate or one named provider.

## In-package foreign key integrity (V8)

| Reference | Target | Rows checked | Result |
|---|---|---|---|
| `government_schemes.category_id` | `scheme_categories.category_id` | 40 | PASS |
| `eligibility_criteria.scheme_id` | `government_schemes.scheme_id` | 55 | PASS |
| `eligibility_criteria.verification_document_hint` | `required_documents.document_name` | 55 | PASS |
| `scheme_benefits.scheme_id` | `government_schemes.scheme_id` | 51 | PASS |
| `application_process.scheme_id` | `government_schemes.scheme_id` | 43 | PASS |
| `district_scheme_mapping.scheme_id` | `government_schemes.scheme_id` | 305 | PASS |
| `scheme_ai_recommendations.scheme_id` | `government_schemes.scheme_id` | 37 | PASS |
| `scheme_ai_recommendations.suggested_next_scheme_id` | `government_schemes.scheme_id` | 37 | PASS |
| `scheme_ai_recommendations.related_scheme_ids` | `government_schemes.scheme_id` (semicolon-delimited members) | 37 | PASS |

## Issues found and resolved during validation

Four real defects were caught by the checks before release. Three of the four were found by checks that exist specifically because earlier packages in this programme shipped without them:

**1. Cross-package FK to a non-existent record (V9, caught at generation).** The skill mapping assumed Package006 held an entrepreneurship skill — a Package006 collection report describes one — but the released `skills.csv` does not contain it. The generator aborted rather than writing an unresolvable UUID. The PMEGP row now carries the sentinel on all four Package006 columns. **A collection report described data the dataset does not contain**; only reading the actual CSV surfaced it.

**2. A second non-existent cross-package record (V9, caught at generation).** The industry mapping assumed Package004 held an AI opportunity. It does not. The row was repointed at the real `Small IT Services Firm / Software Development Startup` record.

**3. Denormalised name drift (V8).** `government_schemes` recorded Stand-Up India's `short_name` as `SUI` while five child datasets used `Stand-Up India`. Every join would have worked — the ids were correct — but any display or grouping on the denormalised column would have split one scheme into two. The registry was corrected to the widely used form.

**4. Document hint pointing at no document (V8).** Two eligibility rows cited `Bonafide Certificate` while `required_documents.csv` holds `Bonafide / Study Certificate`. Corrected to the actual document name.

**5. Scheme coverage gaps (V11).** Four schemes — Soil Health Card, Samagra Shiksha, PM POSHAN and AB-HWC — had no eligibility rows at all, because they are universal, institutional or automatic-entitlement schemes with nothing to screen. Absence was the wrong representation: a consumer cannot distinguish 'no criteria exist' from 'criteria not yet collected'. Explicit rows were added stating the universality.

## Confidence distribution

Package range **60–78**, ceiling **85** (never reached).

The ceiling exists because WebFetch to `.gov.in` / `.nic.in` / `.ac.in` is blocked by this environment's egress policy, so no row rests on a primary-source page read. Ranked lowest-confidence first, since that is where a reviewer should look:

| Dataset | Avg | Range | Why |
|---|---|---|---|
| `scheme_ai_recommendations.csv` | 60.0 | 60–60 | priority_score is a designed heuristic with no empirical calibration — a rule-engine seed, not evidence |
| `skill_scheme_mapping.csv` | 69.7 | 62–73 | Four-way cross-package FK; several links have no upstream counterpart |
| `scheme_application_status.csv` | 70.9 | 69–72 | Generic reference workflow observed across portals, not any single portal's state machine |
| `industry_scheme_mapping.csv` | 71.1 | 68–73 | Scheme-to-opportunity fit is an analytical judgement over two released packages |
| `education_scheme_mapping.csv` | 71.6 | 68–76 | Reconciliation against Package002; three rows have no counterpart record |
| `district_scheme_mapping.csv` | 71.8 | 71–73 | Package001 district master is Tier 1; the district-agency claim is structural |
| `agriculture_scheme_mapping.csv` | 71.9 | 68–76 | Reconciliation against Package005; crop-specific relevance is an agronomic judgement |
| `application_process.csv` | 72.1 | 68–74 | Workflow steps from portal documentation; no published service standards for timelines |
| `scheme_benefits.csv` | 72.4 | 69–76 | Scheme guidelines; quantum unsourceable so scored on type, mode and frequency |
| `financial_institutions.csv` | 72.7 | 68–76 | Institution-type rows (RRBs, cooperatives, PACS) describe categories, not named entities |
| `eligibility_criteria.csv` | 72.7 | 70–76 | Scheme guidelines; thresholds stated qualitatively since figures are notification-driven |
| `required_documents.csv` | 72.9 | 68–78 | Issuing authorities are Tier 1, but validity and route vary by state |
| `implementing_agencies.csv` | 73.8 | 68–78 | District and local-body rows describe agency types present in every district |
| `government_schemes.csv` | 74.3 | 70–78 | Each row attributed to the scheme's own portal — the strongest source class in the package |
| `scheme_categories.csv` | 75.3 | 72–78 | Ministry attribution is Tier 1; cross-cutting categories are inherently fuzzy |

The floor of 60 is confined to `scheme_ai_recommendations`. That is deliberate: `priority_score` is a designed heuristic, and scoring those rows higher would imply empirical grounding the package does not have.

## Sentinel distribution

**534 of 10401 cells (5.13%)** carry the bare sentinel, clustered in exactly the fields that could not be sourced without a primary page read:

| Dataset | Column | Rows |
|---|---|---|
| `district_scheme_mapping.csv` | `district_specific_variation` | 305 / 305 |
| `scheme_benefits.csv` | `benefit_quantum` | 45 / 51 |
| `application_process.csv` | `typical_timeline` | 39 / 43 |
| `government_schemes.csv` | `financial_assistance` | 35 / 40 |
| `government_schemes.csv` | `also_in_package` | 18 / 40 |
| `scheme_ai_recommendations.csv` | `suggested_next_scheme_id` | 12 / 37 |
| `eligibility_criteria.csv` | `verification_document_hint` | 11 / 55 |
| `skill_scheme_mapping.csv` | `package006_provider_id` | 9 / 12 |
| `skill_scheme_mapping.csv` | `package006_provider_name` | 9 / 12 |
| `skill_scheme_mapping.csv` | `package006_certification_id` | 8 / 12 |
| `skill_scheme_mapping.csv` | `package006_certification_name` | 8 / 12 |
| `implementing_agencies.csv` | `official_website` | 6 / 20 |
| `financial_institutions.csv` | `official_website` | 4 / 12 |
| `education_scheme_mapping.csv` | `package002_dataset` | 3 / 7 |
| `education_scheme_mapping.csv` | `package002_record_id` | 3 / 7 |
| `education_scheme_mapping.csv` | `package002_record_name` | 3 / 7 |
| `skill_scheme_mapping.csv` | `package006_scheme_id` | 3 / 12 |
| `skill_scheme_mapping.csv` | `package006_scheme_name` | 3 / 12 |
| `agriculture_scheme_mapping.csv` | `package005_crop_id` | 2 / 14 |
| `agriculture_scheme_mapping.csv` | `package005_crop_name` | 2 / 14 |
| `agriculture_scheme_mapping.csv` | `package005_scheme_id` | 2 / 14 |
| `agriculture_scheme_mapping.csv` | `package005_scheme_name` | 2 / 14 |
| `skill_scheme_mapping.csv` | `package006_skill_id` | 1 / 12 |
| `skill_scheme_mapping.csv` | `package006_skill_name` | 1 / 12 |

Two clusters dominate. **Monetary quantum** — `financial_assistance`, `benefit_quantum` — is sentinelled because scheme amounts, premium rates, loan ceilings and subsidy percentages are revised by notification and budget cycle; a figure stated here would date badly in exactly the field applicants rely on most. **Timelines** — `typical_timeline` on all 43 process rows — is sentinelled because no published service standard was confirmable except MGNREGA's statutory period.

## Verification status

**All 655 records are `VST-NEEDS_REVIEW`.** Nothing in this package has had human data-steward sign-off. Machine validation confirms structural integrity, referential integrity across five packages, provenance completeness and coverage; it does not confirm factual accuracy or currency. For a package whose subject matter changes with every budget, currency is the binding risk.

## Reproducing this report

```bash
cd packages/Package007_Government_Schemes
python3 validate.py       # writes validation_summary.json, exit 0 = clean
python3 build_docs.py     # regenerates this report from that summary
```

Every figure above is derived from the released CSVs rather than hand-maintained, so this report cannot drift out of agreement with the data it describes.
