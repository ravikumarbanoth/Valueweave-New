# Changelog — Package008_MSME

All notable changes to this package. Released versions are immutable; corrections ship as new
versions. Format follows [Keep a Changelog](https://keepachangelog.com/); this package uses
semantic versioning.

## [1.0.0] — 2026-07-25

First release. Promotes Package008 from an empty placeholder to a Stable 18-dataset Business
Intelligence Layer, and completes the eight-package ValueWeave knowledge base programme.

### Added

**Reference taxonomies (Layer 1, no upstream dependency)**

- `msme_categories.csv` — 24 categories, with `category_group` separating four things the brief's
  flat list conflated: Primary Sector Group, Manufacturing Sub-Sector, Services Sub-Sector and
  Emerging Sector. `nic_section_hint` anchors each to the National Industrial Classification.
- `business_models.csv` — 15 models classified by what each actually depends on (Asset-Based,
  Skill-Based, Working-Capital-Based, IP-Based, Infrastructure, Project-Based), with
  `primary_risk` naming the specific failure mode.
- `license_compliance.csv` — 14 licences and registrations. The brief's twelve plus Shops and
  Establishments registration (which most service and trading businesses need) and EPR
  Authorisation (which creates the recycler market).
- `financial_support.csv` — 12 finance sources with instrument, typical use and collateral
  requirement.
- `market_channels.csv` — 11 channels with buyer type, entry barrier and digital intensity.
- `ai_business_tools.csv` — 12 tool classes (not named products) with MSME relevance separated from
  implementation complexity.
- `startup_ecosystem.csv` — 12 incubators, institutes, district offices and trade bodies with
  target stage.

**Core entity (Layer 2)**

- `msme_businesses.csv` — 40 business opportunities across 26 columns. Every attribute column is a
  closed-domain ordinal, enforced by V12, making the dataset machine-filterable rather than free
  text.

**Requirements and cross-package mappings (Layers 3–6)**

- `machinery_mapping.csv` — 64 rows; 10 reference Package005 `farm_machinery` by id
- `raw_material_mapping.csv` — 33 rows; 12 reference Package005 `crops` by id
- `scheme_mapping.csv` — 57 rows, all resolving to Package007 `scheme_id`
- `skill_mapping.csv` — 53 rows; 46 resolving to Package006 `skill_id`
- `industry_mapping.csv` — 19 rows, all resolving to Package004 opportunity `id`
- `agriculture_business_mapping.csv` — 14 rows against Package005 crops and processing opportunities
- `education_support_mapping.csv` — 13 rows against Package002 universities and Package006 providers
- `district_business_mapping.csv` — 32 rows against Package001 districts

**Market and investment (Layers 8, 11)**

- `export_opportunities.csv` — 12 export-capable businesses, each naming its binding readiness
  barrier rather than just its certificates
- `investment_intelligence.csv` — exactly one profile per business (enforced by V11)

**Release artifacts**

- `schemas/schema_catalog.json`, 18 `metadata/*.metadata.json`, 18
  `reports/*.collection_report.md`, `registry/dataset_registry.csv`, `package_manifest.json`,
  `VERSION`, `validation_report.md`, `validation_summary.json`, `quality_report.md`,
  `VERSION_HISTORY.md`, `RELEASE_NOTES.md`, `codex_handoff.md`
- `docs/METHODOLOGY.md`, `docs/USAGE.md`, `docs/DATA_DICTIONARY.md`, `docs/IMPORT_GUIDE.md`
- `validate.py` — 13-check validation engine
- `gen_core.py`, `gen_mappings.py`, `build_artifacts.py`, `build_docs.py` — generators, retained so
  the package is reproducible from source

### Normalization enforced in code — new in this package

The brief made non-duplication a hard requirement. Every earlier package documented cross-package
relationships in prose and checked only that ids resolved. That is insufficient: a rule about what a
package must *not* contain cannot be enforced by verifying that what it *does* contain resolves.

**Validation check V13** fails the build if any Package008 column name collides with an attribute
owned by an upstream entity — a scheme's benefit or ministry, a skill's NSQF level, a crop's season
or yield, a district's population, an institution's affiliation.

The result:

| Upstream domain | Package008 holds | Package008 does NOT hold |
|---|---|---|
| Government schemes | 57 relationship rows | Any benefit, eligibility, portal, ministry or amount |
| Skills | 53 relationship rows | Any NSQF level, duration or training route |
| Crops | 22 crop references | Any season, yield, soil type or water requirement |
| Districts | 32 suitability rows with a documented basis | Any population, area, literacy or coordinate |
| Industries | 19 typed opportunity references | Any Package004 investment or machinery detail |
| Institutions | 13 talent-flow rows | Any established year, affiliation or type |

**The trade-off, stated plainly:** Package008 is not independently useful. Ask it what a scheme pays
and it cannot tell you — only which scheme to look up. That is the correct trade (one authoritative
copy stays current where six drift) but it means consumers must load the upstream packages.

### Cross-package integration

Ten foreign key sets into six released packages — the widest surface in the knowledge base. All
resolved against upstream CSVs at generation time, all re-checked on every validation run,
**zero unresolved**:

| Upstream | Resolved | Sentinel |
|---|---|---|
| Package007 `government_schemes.scheme_id` | 57 | 0 |
| Package006 `skills.skill_id` | 46 | 7 |
| Package006 `training_providers.provider_id` | 9 | 4 |
| Package005 `crops.crop_id` (raw material) | 12 | 21 |
| Package005 `crops.crop_id` (agri business) | 10 | 4 |
| Package005 `farm_machinery.machinery_id` | 10 | 54 |
| Package005 `agri_processing_opportunities.opportunity_id` | 14 | 0 |
| Package004 opportunity `id` | 19 | 0 |
| Package002 `universities.id` | 4 | 9 |
| Package001 `district.dist_id` | 32 | 0 |

Package003_Healthcare has no foreign key: healthcare is an MSME category here, but Package003 holds
institutions and insurance schemes, not enterprise opportunities.

### Validation

477 records, 7,770 cells, **0 violations** across 13 checks. Three checks are new relative to
Package007's twelve: V11 (business coverage), V12 (enum integrity on 11 columns) and V13
(normalization).

Five defect classes caught before release:

1. **Ten district refs were plausible guesses that do not exist.** `AP-GNT`, `AP-KNL`, `AP-EG`,
   `AP-WG`, `AP-VSP`, `AP-SKL`, `AP-CTR`, `AP-PKM`, `TG-SGR`, `TG-KMM` — the real refs are
   `AP-GUN`, `AP-KUR`, `AP-EAS`, `AP-WES`, `AP-VIS`, `AP-SRI`, `AP-CHI`, `AP-PRA`, `TG-SNG`,
   `TG-KHM`. Every one would have produced a silently broken join. Guessing an id format is not
   reading it.
2. **Three skill names did not match Package006's actual values**, and two matched nothing at all.
   The generator aborted on each rather than writing an unresolvable UUID.
3. **Eleven businesses had no skill or machinery mapping.** Absence could not be distinguished from
   omission, so rows were added — IT and premises infrastructure for the four asset-light
   businesses, a real Package006 match for two skills, explicit sentinel rows for five with no
   upstream counterpart.
4. **V13 false positives, resolved by narrowing the rule rather than suppressing it.**
   `official_portal` on a licence or sales channel is Package008-owned; the check now flags it only
   on datasets that reference `package007_scheme_id`.
5. **A Package004 opportunity that does not exist** — as in Package007, an assumed AI opportunity
   was repointed at the real software startup record.

### Provenance

- Confidence **57–78** against an **85** ceiling (never reached). The ceiling records that WebFetch
  to `.gov.in` / `.nic.in` / `.ac.in` is blocked by this environment's egress policy — the same
  constraint as Package004 through Package007.
- Sentinel rate **3.72%** (289 of 7,770 cells). The largest block (108 cells) is not missing data:
  it records that Package005's `farm_machinery` does not catalogue CNC centres or biochemistry
  analysers, which is correct for an agriculture package.
- All 477 rows are `VST-NEEDS_REVIEW`. **No human data-steward sign-off.**

### Deliberately not asserted

- **No rupee figure anywhere.** `investment_range` is sentinelled on all 40 businesses. A
  per-business project cost depends on throughput, automation, premises and state; the MSMED Act
  thresholds are official but a project cost is not. `udyam_classification` carries the statutory
  Micro/Small/Medium signal instead, and `industry_mapping` points at Package004 for the
  opportunities that do have sourced investment detail.
- **No computed return.** `investment_intelligence` has no percentage, no payback period, no IRR —
  every field is ordinal, because computing any of them would need the figures above.
- **No machinery cost, payment cycle or lead time to revenue.**
- **No blanket district cross-product.** 32 rows, not 2,440; every row names its documented basis.

### Known limitations

- 21 of 24 categories have at least one business; several have none. Semiconductors, robotics and
  creative industries have one each.
- `industry_mapping` covers 19 of 40 businesses; the rest have no Package004 counterpart.
- Seven `skill_mapping` rows sentinel the Package006 id — a real upstream coverage gap for foundry
  casting, handloom weaving, corrugation operation, plastic reprocessing, chemical formulation,
  data entry and training delivery. Documented as a request back to Package006.
- 54 of 64 machinery rows sentinel the Package005 reference, correctly, since Package005 catalogues
  agricultural machinery only.
- No state MSME incentive policies; Package004 holds the Telangana and Andhra Pradesh records.

---

## [Unreleased] — planned for 1.1.0

- **Investment bands from DIC and MSME-DI project profiles.** The largest gap between this package
  and entrepreneur-facing use. MSME-DI publishes project profiles free of charge — the right primary
  source.
- Expand `msme_businesses` beyond 40 toward full category coverage.
- Feed the seven unmatched skill requirements back to Package006 as a coverage request.
- Propose a general industrial machinery reference (or an expanded Package005 `farm_machinery`) so
  the 54 sentinelled machinery references can resolve.
- State MSME incentive mapping, reconciled against the Package004 policy records.
- Human data-steward review to move rows from `VST-NEEDS_REVIEW` to `VST-VERIFIED`.

---

## [0.0.0] — 2026-07-20

- Placeholder `README.md` reserving Package008 for MSME knowledge assets. No data.
