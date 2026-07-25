# Relationship Model — ValueWeave Platform v2

865 edges across 15 populated types, all derived from mappings that already
exist inside packages.

## Edge structure

| Field | Meaning |
|---|---|
| `relationship_id` | `vwr:NNNNNN`, assigned in build order |
| `from_entity` / `to_entity` | `global_entity_id` on both ends, validated by G5 |
| `relationship_type` | One of the 19 registered types, validated by G6 |
| `confidence` | Inherited from the source mapping row |
| `provenance_package` / `provenance_dataset` / `provenance_row_id` | The exact CSV row that produced this edge |
| `notes` | The relationship qualifier the source row carried (criticality, relevance, suitability basis) |

**Every edge is traceable to one row in one package dataset.** This is what lets a query
answer say not just *that* a business needs a skill, but which package row asserts it.

## Registered types

| Type | Expected from | Expected to | Edges | Semantics |
|---|---|---|---|---|
| `REQUIRES_SKILL` | MSME|BusinessOpportunity|Industry | Skill | 86 | The subject cannot be operated without the object skill |
| `SUPPORTED_BY_SCHEME` | MSME|Crop|Skill|BusinessOpportunity | GovernmentScheme | 92 | A government scheme provides support to the subject |
| `LOCATED_IN` | District|State|Institution|MSME | State|District|Country | 121 | Geographic containment or siting |
| `TRAINED_BY` | Skill | TrainingProvider | 3 | The object provider delivers training for the subject skill |
| `STUDIED_AT` | Skill|Certification | Institution | 0 | The subject is studied at the object institution |
| `USES_MACHINERY` | MSME|Crop | Machinery | 64 | The subject requires the object machine to operate |
| `USES_RAW_MATERIAL` | MSME | RawMaterial|Crop | 33 | The subject consumes the object as a production input |
| `PROCESSES` | MSME | Crop | 10 | The subject transforms the object crop into a product |
| `SELLS_TO` | MSME | Market | 12 | The subject reaches buyers through the object channel |
| `EXPORTS_TO` | MSME|Crop | ExportCountry | 68 | The subject is exported to the object country |
| `FUNDED_BY` | MSME|GovernmentScheme | FinancialInstitution | 12 | The object institution provides finance for the subject |
| `CERTIFIED_BY` | Skill | Certification | 0 | Competence in the subject is evidenced by the object certification |
| `RELATED_TO` | * | * | 190 | A documented association that no more specific type captures |
| `PART_OF` | * | * | 90 | Taxonomic or compositional containment |
| `SUCCESSOR_OF` | * | * | 0 | The subject replaced the object (scheme renames, policy versions) |
| `PREDECESSOR_OF` | * | * | 0 | Inverse of SUCCESSOR_OF |
| `GENERATES_EMPLOYMENT` | MSME|BusinessOpportunity | District|State | 32 | The subject creates employment in the object geography |
| `SUPPORTED_BY_BANK` | MSME | FinancialInstitution | 36 | A bank or DFI is a named delivery channel for the subject |
| `USES_AI` | MSME|Crop|Industry | * | 16 | The subject has a documented AI or automation application |

Type constraints are enforced by check **G6**: an edge whose endpoint types do not match
the declaration fails the build.

## Three registered types carry zero edges

This is deliberate and worth reading, because the empty ones are informative:

**`CERTIFIED_BY` (0 edges).** Package006's `certifications.csv` has a
`related_skill_names` column, which should produce Skill → Certification edges. It
produces none, because Package006 populates it with descriptive labels
("Two-Wheeler Servicing", "Vocational Training", "Data Entry") rather than the canonical
`skill_name` values in its own `skills.csv` ("Two-Wheeler Mechanic", …). All 30
certifications are orphans as a result. **This is a vocabulary reconciliation task inside
one package**, and the graph is what made it visible. The 132 unresolved endpoints are
logged in `relationships/unresolved_endpoints.csv` with this exact reason.

**`SUCCESSOR_OF` / `PREDECESSOR_OF` (0 edges).** Scheme renames and policy versions are
recorded in package `notes` columns as prose — "formerly NAPS", "renamed Ayushman Arogya
Mandir". Deriving structured edges would require parsing free text, which would mean
inventing links. The types are registered so that when packages add structured
predecessor fields, the graph picks them up without a schema change.

## Type selection: a case where the honest type was the vaguer one

Package008's `education_support_mapping` records that an institution supplies graduates
to an industry. The first implementation typed this `STUDIED_AT`, which failed G6 —
`STUDIED_AT` is declared as Skill|Certification → Institution, and this was
Industry → Institution.

The fix was **not** to widen `STUDIED_AT` to accept Industry. "Industry STUDIED_AT
Institution" does not mean anything. The edge is now `RELATED_TO` with the note
"talent pipeline: institution supplies graduates to this industry" — the type that
exists precisely for documented associations no specific type captures.

Widening a type until it accepts everything is how a type system stops carrying
information.

## Multi-package edges

Some edges connect entities owned by different packages. That is the point of the layer:

| Edge | From (owner) | To (owner) | Derived from |
|---|---|---|---|
| `REQUIRES_SKILL` | MSME (P008) | Skill (P006) | P008 `skill_mapping.csv` |
| `SUPPORTED_BY_SCHEME` | MSME (P008) | GovernmentScheme (P007) | P008 `scheme_mapping.csv` |
| `PROCESSES` | MSME (P008) | Crop (P005) | P008 `agriculture_business_mapping.csv` |
| `GENERATES_EMPLOYMENT` | MSME (P008) | District (P001) | P008 `district_business_mapping.csv` |
| `USES_MACHINERY` | MSME (P008) | Machinery (P005) | P008 `machinery_mapping.csv` |
| `LOCATED_IN` | Institution (P002) | District (P001) | P002 universities `district` column |

The last one is worth noting: Package002 has always carried a `district` column that no
package used as a link. The graph turned an unused column into 66 edges.

## What the model does not have

- **No edge weights beyond inherited confidence.** No PageRank, no learned scores.
- **No inverse edges.** `PREDECESSOR_OF` is registered but a query walks `direction="in"`
  rather than materialising inverses.
- **No temporal edges.** Relationships have no validity period.
- **No hyperedges.** A three-way relationship is modelled as two edges through an
  intermediate entity.
