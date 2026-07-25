# Quality Report — Package007_Government_Schemes v1.0.0

An assessment of what this package is fit for and where it is not. Read it before building on the data.

## Headline

| Dimension | Assessment |
|---|---|
| **Structural integrity** | Strong. 12 checks, 0 violations, 15/15 datasets clean. |
| **Referential integrity** | Strong. 9 cross-package FK sets into 5 released packages, 0 unresolved. |
| **Provenance completeness** | Strong. 6 mandatory columns on all 655 rows; every row attributed to a named authority. |
| **Coverage breadth** | Adequate. 40 schemes across 24 categories, all Central. |
| **Coverage depth** | Mixed. Eligibility and benefits complete for all 40 schemes; process workflows for only 8. |
| **Numeric completeness** | Weak by design. No monetary amount asserted anywhere. |
| **Currency** | Unverified. Subject matter changes with every budget; no row re-checked against a live portal. |
| **Human review** | None. All rows `VST-NEEDS_REVIEW`. |

## What this package is fit for

- **Eligibility screening logic.** `eligibility_criteria.csv` decomposes conditions into 55 typed rows across a closed vocabulary, which is what makes rule-based matching possible. Every scheme has at least one criterion row (V11).
- **Scheme discovery and navigation.** Category, ministry, beneficiary group and application mode are populated throughout.
- **Cross-domain recommendation.** The five mapping datasets connect schemes to crops, skills, business opportunities, education records and districts using real upstream ids.
- **Document checklist generation.** `required_documents.csv` joined through `eligibility_criteria.verification_document_hint` produces a per-scheme document list.
- **Process expectation setting.** `application_process.csv` names the actor and output of each step for 8 schemes — enough to tell an applicant what happens next, though not when.

## What this package is NOT fit for

- **Quoting benefit amounts to a citizen.** No amount is asserted. Every monetary field is the sentinel. Read the `official_portal` instead.
- **Promising processing times.** `typical_timeline` is the sentinel on all 43 process rows.
- **Determining actual eligibility.** Thresholds are stated qualitatively ('below the prescribed ceiling'), not numerically. This package narrows a candidate set; it cannot decide a case.
- **State scheme discovery.** All 40 registry rows are Central. State schemes for Telangana and Andhra Pradesh live in Package002, Package003 and Package004.
- **Ranking schemes by expected value.** `priority_score` is a designed heuristic with no outcome calibration.

## Registry composition

**40 schemes** across **19 of 24 categories**. Categories with no scheme in v1.0.0 hold classification value for future additions but currently have no rows pointing at them.

| Category | Schemes |
|---|---|
| Agriculture | 8 |
| MSME | 3 |
| Skill Development | 3 |
| Education | 2 |
| Employment | 2 |
| Entrepreneurship | 2 |
| Healthcare | 2 |
| Housing | 2 |
| Insurance | 2 |
| Renewable Energy | 2 |
| Scheduled Castes | 2 |
| Scholarships | 2 |
| Social Welfare | 2 |
| Backward Classes | 1 |
| Financial Inclusion | 1 |
| Innovation | 1 |
| Livelihood | 1 |
| Senior Citizens | 1 |
| Women | 1 |

**Overlap with domain packages:** 22 of 40 schemes are also released in a domain package, declared in `also_in_package`. That column exists so the duplication is explicit and reconcilable. The remaining 18 are Package007-only.

This overlap is the single most important governance question for the package. Five packages now hold scheme data. Either Package007 becomes the single source of truth and the domain packages reference it, or the two drift. `also_in_package` records the current state; it does not resolve it. See `codex_handoff.md`.

## Eligibility criterion coverage

55 criterion rows across 12 criterion types:

| Criterion type | Rows |
|---|---|
| Age | 9 |
| Income | 9 |
| Other | 9 |
| Education | 8 |
| Business Size | 5 |
| Occupation | 5 |
| Category | 4 |
| Land Holding | 2 |
| Banking | 1 |
| Citizenship | 1 |
| Exclusion | 1 |
| Gender | 1 |

## Benefit type coverage

51 benefit rows across 10 benefit types. Multi-component schemes carry multiple rows — PM Vishwakarma has three (training, equipment, loan), which is the structure a recommender needs:

| Benefit type | Rows |
|---|---|
| Grant | 11 |
| Loan | 9 |
| Subsidy | 6 |
| Insurance | 5 |
| Scholarship | 5 |
| Interest Subvention | 4 |
| Training | 4 |
| Infrastructure | 3 |
| Equipment Support | 2 |
| Pension | 2 |

## Risk register

| Risk | Severity | Mitigation in place | Residual |
|---|---|---|---|
| Scheme amounts change by budget cycle | High | No amount asserted; `official_portal` on every row | Consumers must fetch live figures |
| Scheme renamed, merged or subsumed | High | `status` enum includes Subsumed and Revised; `notes` records known renames | No automated currency check |
| Domain-package duplication drifts | High | `also_in_package` declares overlap; V9 verifies linked records exist | Governance decision unresolved |
| Upstream id renamed | Medium | V9 fails the build on any unresolved id | Requires `validate.py` to actually be run |
| Eligibility thresholds misread as current | Medium | Thresholds stated qualitatively, never numerically | Consumer may still over-read |
| `priority_score` mistaken for evidence | Medium | Confidence 60 on every row; caveat in notes, metadata, schema catalog and here | Depends on consumers reading docs |
| No human review | Medium | Every row `VST-NEEDS_REVIEW`; stated in 6 places | Unresolved until a data steward signs off |

## Recommended next actions, in priority order

1. **Resolve the duplication governance question.** Decide whether Package007 is the single source of truth for schemes. Every release that passes without deciding makes the eventual reconciliation larger.
2. **Human data-steward review of the 40 registry rows.** Highest value per hour spent, because the registry is what everything else hangs off.
3. **Primary-source access for amounts and timelines.** Would clear the two dominant sentinel clusters and is the main thing standing between this package and citizen-facing use.
4. **`health_scheme_mapping.csv`** to give Package003 a hard FK — the one released package with no structural link.
5. **State scheme registry**, reconciled against the state slices already in Package002, Package003 and Package004.

## Reproducing this report

```bash
python3 validate.py && python3 build_docs.py
```

Every count is computed from the released CSVs at generation time.
