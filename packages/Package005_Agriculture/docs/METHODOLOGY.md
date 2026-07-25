# Methodology — Package005_Agriculture v1.0.0

How the 16 datasets in this package were built, sourced, scored and validated.

## 1. Environment constraint, stated first

Direct `WebFetch` to `.gov.in`, `.nic.in` and `.ac.in` domains is blocked by this session's
organizational egress policy. This is the same constraint that applied to Package004_Industries
and Package006_Skills_and_Training, and it is the single most important thing to understand
about this package's provenance.

**Consequence:** no row in this package rests on a primary-source page read. Every row is
attributed to the authoritative body that governs the fact — ICAR and its crop-specific
institutes, the Ministry of Agriculture & Farmers Welfare, statutory commodity boards, named
scheme portals — and `confidence_score` is capped at 85 across the package to record that the
attribution was not confirmed by fetching the page.

**What this does not mean:** it does not mean the data is guessed. Agronomic facts (season,
soil preference, temperature range, water requirement) are stable, widely documented published
knowledge from ICAR package-of-practices conventions. What could not be confirmed is anything
volatile or specific enough to require a live page: prices, current scheme amounts, current
institution counts.

## 2. The no-fabrication rule and how it was applied

The instruction was explicit: never fabricate; use `PENDING_VERIFICATION` wherever official
public data cannot be confirmed. Applied consistently, this rule produced a package where
**132 of 6,062 cells (2.18%) are sentinelled** — and the distribution of those sentinels is
the most informative thing about the release:

| Dataset | Sentinel cells | What is sentinelled |
|---|---|---|
| `farm_machinery.csv` | 50 | Every price, maintenance cost and most capacity figures |
| `agri_processing_opportunities.csv` | 34 | Every investment band and capacity figure |
| `crops.csv` | 25 | `duration_days` for perennials; `major_districts` for non-TG/AP crops; two yields |
| `agri_business_mapping.csv` | 13 | Package004 opportunity names with no v1.0.0 counterpart |
| `ai_precision_agriculture.csv` | 10 | Every `approximate_cost_inr` |
| All other 11 datasets | 0 | — |

Three patterns are worth naming, because each is a place where an estimate would have been
easy and wrong:

**Equipment and plant costs.** A tractor price depends on make, model, dealer and state
subsidy; a rice mill's capital cost depends on throughput and degree of automation. There is
no single official public figure for any of them. Writing "₹400,000" for a tractor would look
authoritative and be fabrication. All such fields are sentinelled. Where costs genuinely
matter to a consumer, Package004_Industries already carries sourced investment detail for the
overlapping food-processing opportunities — that is the right source, and this package
deliberately does not approximate it.

**Concepts that do not apply.** `duration_days` is meaningless for a perennial like mango or
black pepper. Rather than write a number that would corrupt any downstream aggregation, those
cells carry the sentinel and the `notes` column explains why.

**Cross-package links that do not exist.** Thirteen of thirty `agri_business_mapping` rows
have no counterpart opportunity in Package004 v1.0.0 — there is no rice-milling, dal-milling,
jaggery, cold-storage, essential-oil, animal-feed, vermicompost or cashew-shelling opportunity
there. Those links are sentinelled rather than pointed at the nearest loosely-similar row,
because a wrong FK is worse than an absent one: it silently corrupts every join that uses it.

## 3. Source tiers and confidence scoring

| Band | Tier | Sources | Datasets scored here |
|---|---|---|---|
| 70–85 | Tier 1 | ICAR and its institutes (IIWBR, IIPR, IIOR, IIVR, IIHR, IISR, CICR, CPRI, DOGR, NBSS&LUP, CRIDA, IIMR), Ministry of Agriculture & Farmers Welfare, statutory boards (Spices, Tea, Coffee, Coconut, Tobacco, Silk, Bee), APEDA, NABARD, named scheme portals | Most of the package |
| 60–69 | Tier 2 | State agriculture departments, MoFPI programme literature, MCA, NRLM | Machinery, processing, some institutions |
| 55–59 | Tier 3 | Sector associations, published research aggregates | Hydroponics/aquaponics categories, CV grading |
| 50–54 | Tier 4 | Forward-looking technology assessment | `ai_precision_agriculture` rows for robotics, autonomous tractors, digital twins |

**Ceiling: 85.** Not reached anywhere. Observed range is **50–78**.

**Floor: 50**, occurring only in `ai_precision_agriculture` (average 58.2, the lowest in the
package). This is deliberate. Rows describing farm robotics, autonomous tractors and digital
twin simulation score 50–52 because they describe research and pilot stages in India, not
commercially available offerings. The low score *is* the finding. Padding those rows to 70 to
make the package look more uniform would misrepresent the state of the technology.

Scores were assigned per row, not per dataset, on three factors:

1. **Source authority** — a crop's season from ICAR scores higher than a technology's ROI from
   pilot reporting.
2. **Fact volatility** — stable agronomy scores higher than current scheme amounts.
3. **Specificity attempted** — a national average scores higher than a district claim.

## 4. Per-layer collection approach

### Reference taxonomies (`crop_categories`, `soil_types`, `climate_zones`)

The 24 categories cover the full agriculture domain requested, and deliberately mix three
kinds of thing, which the `category_group` column distinguishes:

- **Botanical groups** (Food Grains, Millets, Pulses, Oil Seeds, Commercial, Vegetables,
  Fruits, Spices, Medicinal Plants, Plantation, Flowers, Fodder)
- **Production systems** (Organic Farming, Protected Cultivation, Hydroponics, Aquaponics) —
  these are cultivation modes, not crop groups; any crop can be grown under them
- **Allied activities** (Forest Produce, Sericulture, Apiculture, Mushroom, Fisheries,
  Livestock, Poultry, Dairy) — outside crop taxonomy but inside agri-business scope

Consumers filtering for crops only should restrict to `category_group` in
`{Field Crops, Horticulture, Plantation}`.

Soil classes come from the ICAR-NBSS&LUP national classification. All four problem-soil classes
(saline, acidic, alkaline, clay) were retained because reclamation and crop-choice decisions
depend on them. The eight climate zones are a collapsed form of the ICAR-CRIDA framing —
tractable, but explicitly a screening model, not the 127-zone NARP classification.

### Core entity (`crops`)

45 crops selected on national acreage significance plus Telangana/Andhra Pradesh relevance.
Agronomic fields follow ICAR package-of-practices conventions.

`major_districts` was populated **only** where a district is publicly and specifically
associated with the crop — Anantapur for groundnut, Guntur for chilli, Nizamabad and the
Duggirala belt for turmeric, Nalgonda for sweet orange, Krishna and the Nuzvid belt for mango.
For crops with no TG/AP footprint (wheat, lentil, soybean, jute, cumin, cardamom, black pepper,
mustard, barley, pearl millet, finger millet, ashwagandha, tulsi) the field is the sentinel, not
an invented list.

`avg_yield_tons_per_ha` carries a caveat that matters: it is **not comparable across crops**.
Cotton is stated as lint, not seed cotton. Turmeric and ginger are stated as dry and fresh
respectively. Coconut is sentinelled entirely because its conventional unit is nuts per palm
per year, and forcing it into tonnes/ha would produce a number no agronomist would recognise.

### Relational mappings (`crop_soil_mapping`, `crop_climate_mapping`)

Both give complete coverage: every one of the 45 crops carries exactly two rows — its optimal
match and a documented alternative — producing 90 mappings each.

`suitability_score` (0–100) is an **ordinal** rating anchored to ICAR guidance, banded as
Optimal (85+), Suitable (70–84), Marginal (55–69). It is comparable within a crop, not across
crops, and it is not a measured yield ratio. Absence of a crop-soil pair is not a claim that
the combination fails.

For climate, `yield_potential` is deliberately a rating (Optimal/Good/Marginal) rather than a
tonnage, because zone-level tonnage cannot be asserted from public sources without district
qualification. The field that carries the real operational value is
`primary_climatic_risk`, which names the specific failure mode — "rain at boll opening degrades
lint" for cotton in semi-arid, "terminal heat stress at grain filling" for wheat in temperate,
"rain during drying degrades colour value" for chilli. That is what a decision-maker needs.

### Domain layers

**`farm_machinery`** — 16 types across land preparation, sowing, crop protection, harvesting,
post-harvest, processing, packaging, cold chain, irrigation and monitoring. The highest-value
field is `subsidy_scheme`, because the practical question is not what a machine costs but which
scheme pays for part of it. Costs are sentinelled (see §2).

**`agri_processing_opportunities`** — 17 opportunities across primary processing, secondary
processing, infrastructure, packaging, by-product processing and input manufacturing. Priority
went to `licenses_required` and `linked_scheme` — the fields that gate whether an enterprise
can legally operate at all. FSSAI licence, Udyam registration, FCO registration for
bio-fertilisers, Legal Metrology for packaged goods.

**`agriculture_schemes`** — 12 central schemes, each attributed to its own portal. Every
benefit figure carries the standing caveat that amounts change by budget cycle and state
top-up. This is the agriculture slice; Package007_Government_Schemes will hold the
comprehensive registry.

**`crop_disease_management`** — 10 high-incidence problems. `affected_crops` is deliberately
free text, not a `crop_id` FK, because most of these pathogens have host ranges wider than the
45 crops in this release. Chemical entries are **named actives, not doses** — pesticide
legality and dosage are governed by current CIB&RC label approval and change over time.

**`ai_precision_agriculture`** — the ten technologies named in the specification, each assessed
on Indian adoption, AI readiness and, most usefully, `primary_constraint`: DGCA licensing for
drones, rural connectivity for IoT, ground-truth data scarcity for yield models, average
holding size for autonomous tractors. Naming the binding constraint is more actionable than an
adoption percentage.

### Cross-package spine (`agri_business_mapping`)

The integration dataset, and the one where FK correctness mattered most. Both external FKs were
resolved by **reading the released packages directly**, not by matching on remembered names:

- `package006_skill_id` holds actual UUIDs from Package006's `skills.csv`. All 30 rows resolve,
  across four skills: Food Processing & Preservation, Organic Farming, Precision Agriculture &
  IoT, Modern Farming Techniques.
- `package004_opportunity_name` was matched against the `name` and `adapted_indian_concept`
  columns of Package004's CSVs. 17 rows resolve to exact names — the turmeric, chilli, kachi
  ghani oil, coconut oil, atta milling, millet, avakaya pickle, multi-product and seed
  processing units. 13 are sentinelled.

Both FK sets are re-verified on every `validate.py` run (check V9), so a rename in either
upstream package fails the build rather than silently breaking.

## 5. Validation

`validate.py` runs ten checks and is re-runnable from the package root. Notable design points:

- **V5 (bare-sentinel discipline)** flags any cell that *contains* `PENDING_VERIFICATION`
  without *equalling* it. This caught a real breach during the release: a `crops.csv` note read
  "district attribution left PENDING_VERIFICATION", which would have made naive
  sentinel-counting wrong. The note was rewritten.
- **V8 checks denormalised names, not just IDs.** Mapping tables carry both `crop_id` and
  `crop_name` for readability, which is a consistency hazard. V8 verifies the name matches what
  `crops.csv` says for that ID. This is what caught the `crop_id` renumbering when `crops.csv`
  expanded from 35 to 45 rows and shifted every ID past `crop-004` — the mapping datasets were
  regenerated rather than patched.
- **V10 rejects blank cells.** A gap must be the explicit sentinel. A silently empty cell is
  indistinguishable from an oversight.

Final state: **388 records, 6,062 cells, 0 violations.**

## 6. Reproducibility

The generator scripts ship with the package:

| Script | Produces |
|---|---|
| `enrich_datasets.py` | `crop_categories`, `crops`, `farm_machinery`, `agri_processing_opportunities`, `ai_precision_agriculture` |
| `regen_mappings.py` | `crop_soil_mapping`, `crop_climate_mapping`, `agri_business_mapping` |
| `build_artifacts.py` | schema catalog, 16 metadata files, registry, manifest, 16 collection reports |
| `validate.py` | `validation_summary.json`, exit status |

They are retained deliberately. A reviewer can diff a claim against its generator, see which
fields were asserted and which were sentinelled, and regenerate the whole package from source.

Full rebuild:

```bash
python3 enrich_datasets.py && python3 regen_mappings.py \
  && python3 validate.py && python3 build_artifacts.py
```

Note the order: `build_artifacts.py` reads `validation_summary.json`, so validation must run
first. Every count in the manifest, registry, schema catalog and collection reports is derived
from the actual CSVs rather than hand-maintained, which is why they cannot drift out of
agreement with the data.

## 7. What would raise confidence

In priority order, for a future release:

1. **Unblock government-domain fetching.** This alone would lift the ceiling above 85 and let
   scheme amounts, institution counts and export figures be confirmed rather than attributed.
2. **DIC and MSME project profiles** for equipment and plant costs — the single largest
   sentinel block (84 cells across machinery and processing).
3. **District-level crop statistics** to convert `major_districts` from free text into a hard
   Package001 `dist_id` foreign key.
4. **Package004 expansion** to populate the 13 sentinelled opportunity links.
5. **Human data-steward review** to move rows from `VST-NEEDS_REVIEW` to `VST-VERIFIED`. No row
   in this package has had human sign-off.
