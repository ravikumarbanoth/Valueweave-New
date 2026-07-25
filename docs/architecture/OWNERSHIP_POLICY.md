# Ownership Policy — ValueWeave Platform v2

## The rule

**Each entity type has exactly one owner package. Only the owner may publish that
entity's distinctive attributes. Everyone else references it by id.**

This is not new — Package008 introduced it as validation check V13 for one package.
Platform v2 generalises it to all eight as graph check **G7**.

## What "owns" means, precisely

The distinction that matters is between an **attribute** and a **relationship**:

| Statement | Kind | Owner |
|---|---|---|
| "Welding is NSQF level 4" | attribute of a Skill | Package006 |
| "This fabrication business requires Welding" | relationship | Package008 |
| "Turmeric grows in the kharif season" | attribute of a Crop | Package005 |
| "This spice unit processes Turmeric" | relationship | Package008 |
| "PM-KISAN pays in three instalments" | attribute of a Scheme | Package007 |
| "This business is supported by PM-KISAN" | relationship | Package008 |

A package may hold as many relationships as it likes. It may not restate the other
side's attributes.

## Enforcement

G7 reads `knowledge_graph/ownership/attribute_ownership.csv` and inspects the header of
every package CSV — 77 files. Three outcomes:

| Situation | Result |
|---|---|
| Owner publishes its own attribute | Allowed |
| Non-owner holds a foreign key, or a name denormalised beside it | Allowed |
| Non-owner publishes an owned attribute, **overlap declared** in `known_overlaps.csv` | **Warning**, citing the ADR |
| Non-owner publishes an owned attribute, **not declared** | **Build fails** |

That third row is the important one. It makes `known_overlaps.csv` load-bearing: a
governance registry that no check reads is a wish, one that gates the build is a control.
See ADR-005.

## Only distinctive attributes are enforceable

The first G7 implementation produced 22 violations, almost all false positives:
`jurisdiction` appears in four packages; `ownership` means one thing for a university and
another for a bank; `official_portal` on a licence is not a scheme portal.

Generic and context-dependent column names are excluded. Enforcement covers names that
mean one thing in one domain — `nsqf_level`, `avg_yield_tons_per_ha`,
`water_requirement_mm`, `udyam_classification`, `benefit_summary`.

This is the second time in the programme that an over-broad correctness rule needed
**narrowing rather than suppressing**. A suppressed check finds nothing.

## Declared overlaps

| Entity type | Canonical owner | Also held by | Status | ADR |
|---|---|---|---|---|
| `GovernmentScheme` | P007_Government_Schemes | P002_Education;P003_Healthcare;P004_Industries;P005_Agricult | **UNRESOLVED** | ADR-003 |
| `Industry` | P004_Industries | P005_Agriculture;P006_Skills_and_Training;P008_MSME | **PARTIALLY_RESOLVED** | ADR-005 |
| `FinancialInstitution` | P007_Government_Schemes | P008_MSME | **ACCEPTED** | ADR-005 |
| `Machinery` | P005_Agriculture | P008_MSME | **ACCEPTED** | ADR-005 |
| `ExportCountry` | P001_Geography | P005_Agriculture;P008_MSME | **UNRESOLVED** | ADR-005 |

**`GovernmentScheme` is the one that matters.** Six packages hold scheme rows and the
ownership question is open. Full analysis, three options and a recommendation in ADR-003.

## Ownership assignments

Full table with rationale in `knowledge_graph/ownership/ownership_registry.csv`. Summary:

| Owner | Entity types |
|---|---|
| Package001_Geography | District, State, Country, ExportCountry |
| Package002_Education | Institution |
| Package004_Industries | Industry, BusinessOpportunity |
| Package005_Agriculture | Crop, Soil, ClimateZone, Machinery |
| Package006_Skills_and_Training | Skill, Certification, TrainingProvider |
| Package007_Government_Schemes | GovernmentScheme, FinancialInstitution |
| Package008_MSME | MSME, RawMaterial, Market |

Two assignments are weaker than they look:

- **`ExportCountry` → Package001** is *nominal*. Package001 v1.0.0 has no country
  dataset. The 29 export-country entities are parsed out of destination text in
  Package005 and Package008. The assignment reserves the slot for a real country
  reference dataset.
- **`Machinery` → Package005** is *scope-limited*. Package005 catalogues agricultural
  machinery. 54 of Package008's 64 machinery references correctly have no upstream id,
  which is a scope boundary rather than duplication.
