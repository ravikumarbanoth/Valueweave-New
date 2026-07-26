# Knowledge Graph Health — ValueWeave v2.1 Phase 2

**Read-only audit.** Figures computed by `audit/run_audit.py`.

## Headline

| Metric | Value | Verdict |
|---|---|---|
| Entities | 647 | — |
| Relationships | 865 | — |
| **Directed cycles** | **0** | Clean |
| **Self-loops** | **0** | Clean |
| **Duplicate edges** | **0** | Clean |
| **Alias conflicts** | **0** | Clean |
| Alias shadowing a canonical name | 1 | Clean |
| Entity collisions (cross-package) | 9 | Handled correctly |
| Connected components | **150** | Fragmented |
| Largest component | 489 entities (75.58%) | — |
| Singleton components | 142 | = orphan count |
| Mean degree | 2.67 | Sparse |
| Unresolved endpoints | 132 | Logged with reasons |
| Unused relationship types | 4 of 19 | Known |
| Unused entity types | 0 of 19 | Clean |

A directed acyclic graph with no duplicate edges, no self-loops and no alias conflicts is
a structurally sound graph. **The weakness is not integrity — it is density.**

## Finding 1 — 150 connected components

The graph is not one graph. It is one large component holding 75.58% of entities, plus
**142 isolated singletons** and **7 small islands**.

### Secondary components (size > 1)

| Size | Composition | Example |
|---|---|---|
| 4 | BusinessOpportunity 3, Industry 1 | Instagram Live Selling / YouTube Live Shopping / |
| 2 | BusinessOpportunity 1, Industry 1 | Bridal Wear & Traditional Telugu Dress Rental |
| 2 | BusinessOpportunity 1, Industry 1 | Common Service Centres (CSC) + One District One  |
| 2 | BusinessOpportunity 1, Industry 1 | Farmer Producer Organisations (FPOs) + eNAM + ON |
| 2 | BusinessOpportunity 1, Industry 1 | Instagram / YouTube Creator Commerce & Affiliate |
| 2 | BusinessOpportunity 1, Industry 1 | Telangana Homestays / Andhra Pradesh Heritage &  |
| 2 | BusinessOpportunity 1, Industry 1 | WhatsApp Business Automation / Digital Catalog & |

Every one is the same shape: a Package004 `BusinessOpportunity` attached to its own
`Industry` label and nothing else. These are the china-inspired opportunities, whose
industry categories ("Retail & Local Commerce / Creator Economy") are unique to
Package004 and connect to no skill, scheme or district.

**Fix:** these opportunities need `REQUIRES_SKILL` or `SUPPORTED_BY_SCHEME` mappings in
their own package. It is an upstream data gap surfaced by the graph, not a graph defect.

## Finding 2 — orphan entities by type

| Type | Orphans |
|---|---|
| Certification | 30 |
| TrainingProvider | 22 |
| GovernmentScheme | 21 |
| Industry | 17 |
| FinancialInstitution | 13 |
| Market | 10 |
| Institution | 8 |
| Machinery | 8 |
| ExportCountry | 7 |
| Skill | 5 |
| Soil | 1 |

The three largest are each a single, specific, fixable upstream problem:

**Certification (30 — every certification in the platform).** `CERTIFIED_BY` has zero
edges because Package006's `certifications.related_skill_names` uses a different
vocabulary than its own `skills.csv`: "Two-Wheeler Servicing" where the skill is
"Two-Wheeler Mechanic", "Data Entry" where no such skill exists. **This is a
single-package vocabulary reconciliation and it is the highest-value fix in the platform.**

**TrainingProvider (22 of 25).** Only 3 `TRAINED_BY` edges exist. No package
systematically links a provider to the skills it teaches.

**GovernmentScheme (21 of 40+).** Schemes with no Package007 or Package008 mapping row.

## Finding 3 — relationship type usage is heavily skewed

| Type | Edges |
|---|---|
| `RELATED_TO` | 190 |
| `LOCATED_IN` | 121 |
| `SUPPORTED_BY_SCHEME` | 92 |
| `PART_OF` | 90 |
| `REQUIRES_SKILL` | 86 |
| `EXPORTS_TO` | 68 |
| `USES_MACHINERY` | 64 |
| `SUPPORTED_BY_BANK` | 36 |
| `USES_RAW_MATERIAL` | 33 |
| `GENERATES_EMPLOYMENT` | 32 |
| `USES_AI` | 16 |
| `SELLS_TO` | 12 |
| `FUNDED_BY` | 12 |
| `PROCESSES` | 10 |
| `TRAINED_BY` | 3 |

`RELATED_TO` at 190 is the most-used type in the graph. That is a
**modelling smell**: the catch-all should not be the leader. 180 of those are crop-soil
and crop-climate suitability edges, which deserve their own `SUITABLE_FOR_SOIL` and
`SUITABLE_FOR_CLIMATE` types — the qualifier is already carried in `notes`.

### Registered but unused

| Type |
|---|
| `STUDIED_AT` |
| `CERTIFIED_BY` |
| `SUCCESSOR_OF` |
| `PREDECESSOR_OF` |

- `CERTIFIED_BY` — blocked on the Package006 vocabulary mismatch above
- `STUDIED_AT` — deliberately vacated in v2.0.0; the institution-industry edge was
  correctly retyped `RELATED_TO` rather than abusing this type
- `SUCCESSOR_OF` / `PREDECESSOR_OF` — scheme renames are prose in `notes`, not
  structured fields. Deriving them would require parsing free text.

## Finding 4 — 132 unresolved endpoints

Mapping rows that exist upstream but whose endpoint does not resolve to an entity:

| Reason | Count |
|---|---|
| Package006 has no skill record for this requirement | 7 |
| related_skill_names entry 'Employability Skills' is not a registered Skill: Package006 cer | 3 |
| related_skill_names entry 'Cloud Computing Fundamentals' is not a registered Skill: Packag | 2 |
| related_skill_names entry 'Cloud Security Basics' is not a registered Skill: Package006 ce | 2 |
| crop_product 'Tea (Orthodox/CTC)' does not name a registered crop entity | 1 |
| crop_product 'Coffee' does not name a registered crop entity | 1 |
| crop_product 'Seafood (Fish, Shrimp)' does not name a registered crop entity | 1 |
| related_skill_names entry 'Vocational Training' is not a registered Skill: Package006 cert | 1 |
| related_skill_names entry 'Sector-Specific Trade Skills' is not a registered Skill: Packag | 1 |
| related_skill_names entry 'Prior Learning Assessment' is not a registered Skill: Package00 | 1 |
| related_skill_names entry 'Sector-Specific Vocational Skills' is not a registered Skill: P | 1 |
| related_skill_names entry 'Two-Wheeler Servicing' is not a registered Skill: Package006 ce | 1 |
| related_skill_names entry 'Three-Wheeler Servicing' is not a registered Skill: Package006  | 1 |
| related_skill_names entry 'Automotive Electrical Systems' is not a registered Skill: Packa | 1 |
| related_skill_names entry 'Automotive Mechanical Repair' is not a registered Skill: Packag | 1 |
| related_skill_names entry 'Data Entry' is not a registered Skill: Package006 certification | 1 |
| related_skill_names entry 'Typing Speed & Accuracy' is not a registered Skill: Package006  | 1 |
| related_skill_names entry 'Basic Computer Operation' is not a registered Skill: Package006 | 1 |
| related_skill_names entry 'MS Office Usage' is not a registered Skill: Package006 certific | 1 |
| related_skill_names entry 'Computer Hardware Repair' is not a registered Skill: Package006 | 1 |
| related_skill_names entry 'Peripheral Installation & Troubleshooting' is not a registered  | 1 |
| related_skill_names entry 'Laptop Servicing' is not a registered Skill: Package006 certifi | 1 |
| related_skill_names entry 'Customer-Premise Technical Support' is not a registered Skill:  | 1 |
| related_skill_names entry 'CNC Turning Machine Operation' is not a registered Skill: Packa | 1 |
| related_skill_names entry 'Metal Machining' is not a registered Skill: Package006 certific | 1 |
| related_skill_names entry 'Tooling & Workholding Setup' is not a registered Skill: Package | 1 |
| related_skill_names entry 'Quality Inspection of Machined Parts' is not a registered Skill | 1 |
| related_skill_names entry 'Computer Fundamentals' is not a registered Skill: Package006 ce | 1 |
| related_skill_names entry 'Programming Basics' is not a registered Skill: Package006 certi | 1 |
| related_skill_names entry 'IT Applications' is not a registered Skill: Package006 certific | 1 |
| related_skill_names entry 'Web Design Basics' is not a registered Skill: Package006 certif | 1 |
| related_skill_names entry 'Basic Computer Literacy' is not a registered Skill: Package006  | 1 |
| related_skill_names entry 'Internet & Email Usage' is not a registered Skill: Package006 c | 1 |
| related_skill_names entry 'Digital Literacy' is not a registered Skill: Package006 certifi | 1 |
| related_skill_names entry 'MS Office Basics' is not a registered Skill: Package006 certifi | 1 |
| related_skill_names entry 'Networking Fundamentals' is not a registered Skill: Package006  | 1 |
| related_skill_names entry 'Network Security' is not a registered Skill: Package006 certifi | 1 |
| related_skill_names entry 'Routing & Switching' is not a registered Skill: Package006 cert | 1 |
| related_skill_names entry 'IP Connectivity' is not a registered Skill: Package006 certific | 1 |
| related_skill_names entry 'Microsoft Azure' is not a registered Skill: Package006 certific | 1 |
| related_skill_names entry 'Cloud Service Models' is not a registered Skill: Package006 cer | 1 |
| related_skill_names entry 'MS Word' is not a registered Skill: Package006 certifications u | 1 |
| related_skill_names entry 'MS Excel' is not a registered Skill: Package006 certifications  | 1 |
| related_skill_names entry 'MS PowerPoint' is not a registered Skill: Package006 certificat | 1 |
| related_skill_names entry 'Office Productivity Tools' is not a registered Skill: Package00 | 1 |
| related_skill_names entry 'AWS Cloud Services' is not a registered Skill: Package006 certi | 1 |
| related_skill_names entry 'Cloud Economics' is not a registered Skill: Package006 certific | 1 |
| related_skill_names entry 'IT Support' is not a registered Skill: Package006 certification | 1 |
| related_skill_names entry 'Troubleshooting' is not a registered Skill: Package006 certific | 1 |
| related_skill_names entry 'Networking Basics' is not a registered Skill: Package006 certif | 1 |
| related_skill_names entry 'System Administration' is not a registered Skill: Package006 ce | 1 |
| related_skill_names entry 'Customer Service (IT)' is not a registered Skill: Package006 ce | 1 |
| related_skill_names entry 'Digital Marketing' is not a registered Skill: Package006 certif | 1 |
| related_skill_names entry 'SEO Basics' is not a registered Skill: Package006 certification | 1 |
| related_skill_names entry 'Social Media Marketing' is not a registered Skill: Package006 c | 1 |
| related_skill_names entry 'Online Advertising Fundamentals' is not a registered Skill: Pac | 1 |
| related_skill_names entry 'Computer-Aided Design (CAD)' is not a registered Skill: Package | 1 |
| related_skill_names entry 'AutoCAD Drafting' is not a registered Skill: Package006 certifi | 1 |
| related_skill_names entry '2D/3D Modeling' is not a registered Skill: Package006 certifica | 1 |
| related_skill_names entry 'Technical Drawing' is not a registered Skill: Package006 certif | 1 |
| related_skill_names entry 'Mechatronics' is not a registered Skill: Package006 certificati | 1 |
| related_skill_names entry 'Industrial Automation' is not a registered Skill: Package006 ce | 1 |
| related_skill_names entry 'Machine Operation' is not a registered Skill: Package006 certif | 1 |
| related_skill_names entry 'Troubleshooting of Automated Systems' is not a registered Skill | 1 |
| related_skill_names entry 'Industrial Robot Operation' is not a registered Skill: Package0 | 1 |
| related_skill_names entry 'Robot Programming' is not a registered Skill: Package006 certif | 1 |
| related_skill_names entry 'CNC Operation' is not a registered Skill: Package006 certificat | 1 |
| related_skill_names entry 'ROBOGUIDE Simulation' is not a registered Skill: Package006 cer | 1 |
| related_skill_names entry 'Industrial Robot Programming' is not a registered Skill: Packag | 1 |
| related_skill_names entry 'RAPID Programming Language' is not a registered Skill: Package0 | 1 |
| related_skill_names entry 'Robot Coordinate Systems' is not a registered Skill: Package006 | 1 |
| related_skill_names entry 'Flex Pendant Operation' is not a registered Skill: Package006 c | 1 |
| related_skill_names entry 'Building Automation' is not a registered Skill: Package006 cert | 1 |
| related_skill_names entry 'Power Management' is not a registered Skill: Package006 certifi | 1 |
| related_skill_names entry 'EcoStruxure Platform' is not a registered Skill: Package006 cer | 1 |
| related_skill_names entry 'Energy Efficiency Systems' is not a registered Skill: Package00 | 1 |
| related_skill_names entry 'Sector-Specific Vocational Skills (varies by job role)' is not  | 1 |
| related_skill_names entry 'Entrepreneurship Basics' is not a registered Skill: Package006  | 1 |
| related_skill_names entry 'Varies by course (Engineering' is not a registered Skill: Packa | 1 |
| related_skill_names entry 'Science' is not a registered Skill: Package006 certifications u | 1 |
| related_skill_names entry 'Humanities' is not a registered Skill: Package006 certification | 1 |
| related_skill_names entry 'Management subjects)' is not a registered Skill: Package006 cer | 1 |
| related_skill_names entry 'Varies by course (School' is not a registered Skill: Package006 | 1 |
| related_skill_names entry 'Undergraduate' is not a registered Skill: Package006 certificat | 1 |
| related_skill_names entry 'Postgraduate subjects across disciplines)' is not a registered  | 1 |
| related_skill_names entry 'Free and Open Source Software (FOSS)' is not a registered Skill | 1 |
| related_skill_names entry 'Linux' is not a registered Skill: Package006 certifications use | 1 |
| related_skill_names entry 'LaTeX' is not a registered Skill: Package006 certifications use | 1 |
| related_skill_names entry 'PHP & MySQL' is not a registered Skill: Package006 certificatio | 1 |
| related_skill_names entry 'Java' is not a registered Skill: Package006 certifications use  | 1 |
| related_skill_names entry 'C/C++ Programming' is not a registered Skill: Package006 certif | 1 |
| related_skill_names entry 'LibreOffice' is not a registered Skill: Package006 certificatio | 1 |
| related_skill_names entry 'Artificial Intelligence' is not a registered Skill: Package006  | 1 |
| related_skill_names entry 'Data Science & Machine Learning' is not a registered Skill: Pac | 1 |
| related_skill_names entry 'Internet of Things (IoT)' is not a registered Skill: Package006 | 1 |
| related_skill_names entry 'Cybersecurity' is not a registered Skill: Package006 certificat | 1 |
| related_skill_names entry 'Robotic Process Automation (RPA)' is not a registered Skill: Pa | 1 |
| related_skill_names entry 'Blockchain' is not a registered Skill: Package006 certification | 1 |
| related_skill_names entry 'Java Programming' is not a registered Skill: Package006 certifi | 1 |
| related_skill_names entry 'Sector-Specific Vocational Skills (varies by Qualification Pack | 1 |
| related_skill_names entry 'Industry-Aligned Technical Skills' is not a registered Skill: P | 1 |
| related_skill_names entry 'Patient Care Support' is not a registered Skill: Package006 cer | 1 |
| related_skill_names entry 'Basic Nursing Assistance' is not a registered Skill: Package006 | 1 |
| related_skill_names entry 'Hospital Hygiene & Safety' is not a registered Skill: Package00 | 1 |
| related_skill_names entry 'First Aid' is not a registered Skill: Package006 certifications | 1 |
| related_skill_names entry 'Beauty Treatments' is not a registered Skill: Package006 certif | 1 |
| related_skill_names entry 'Skin Care Services' is not a registered Skill: Package006 certi | 1 |
| related_skill_names entry 'Hair Styling Basics' is not a registered Skill: Package006 cert | 1 |
| related_skill_names entry 'Salon Hygiene Practices' is not a registered Skill: Package006  | 1 |
| related_skill_names entry 'Accounting Software' is not a registered Skill: Package006 cert | 1 |
| related_skill_names entry 'GST Compliance' is not a registered Skill: Package006 certifica | 1 |
| related_skill_names entry 'Inventory Management' is not a registered Skill: Package006 cer | 1 |
| related_skill_names entry 'Bookkeeping' is not a registered Skill: Package006 certificatio | 1 |
| related_skill_names entry 'Linux System Administration' is not a registered Skill: Package | 1 |
| related_skill_names entry 'Red Hat Enterprise Linux' is not a registered Skill: Package006 | 1 |
| related_skill_names entry 'Open Source Software' is not a registered Skill: Package006 cer | 1 |
| related_skill_names entry 'IT Infrastructure Management' is not a registered Skill: Packag | 1 |
| related_skill_names entry 'Advanced Programming' is not a registered Skill: Package006 cer | 1 |
| related_skill_names entry 'Software Engineering' is not a registered Skill: Package006 cer | 1 |
| related_skill_names entry 'Database Management' is not a registered Skill: Package006 cert | 1 |
| related_skill_names entry 'Computer Networking' is not a registered Skill: Package006 cert | 1 |
| related_skill_names entry 'IT Systems Design' is not a registered Skill: Package006 certif | 1 |

All are logged in `knowledge_graph/relationships/unresolved_endpoints.csv` with the
specific reason. None is a silent failure.

## Finding 5 — degree distribution

Mean degree 2.67, maximum 39. Most connected:

| Degree | Type | Entity |
|---|---|---|
| 39 | FinancialInstitution | Scheduled Commercial Banks |
| 34 | State | Telangana |
| 29 | State | Andhra Pradesh |
| 27 | Soil | Loamy |
| 22 | MSME | Spice Grinding and Packing Unit |
| 21 | Soil | Red Soil |
| 20 | GovernmentScheme | Pradhan Mantri MUDRA Yojana |
| 20 | ClimateZone | Semi-arid |
| 19 | MSME | Dal Milling Unit |
| 19 | MSME | Fruit Pulp and Beverage Unit |
| 19 | ClimateZone | Sub-tropical |
| 18 | District | Hyderabad |

The hubs are reference entities — banks, states, soils, climate zones — not the
business entities a user would query. That is expected in a graph derived from mapping
tables, and it is why review priority (Phase 4) is computed on degree.

## Verdict

| Dimension | Score |
|---|---|
| Structural integrity | **Excellent** — 0 cycles, 0 duplicates, 0 conflicts, 0 broken endpoints |
| Type discipline | **Good** — 15 of 19 types used, unused ones justified |
| Density | **Weak** — 2.67 mean degree, 150 components |
| Coverage | **Weak** — 37 datasets unextracted |

**The graph is correct and sparse.** Correctness came from validation; sparsity comes
from extraction coverage and upstream gaps, both of which are addressable in v2.1
without touching the graph's design.
