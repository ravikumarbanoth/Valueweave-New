#!/usr/bin/env python3
"""
The Entrepreneurship Decision Datasets, normalised.

WHAT THIS FILE IS
-----------------
A 49-page dataset covering 20 employment-generating businesses with a Telangana
/ Andhra Pradesh focus. Sixth supplied document, same treatment as the five
trade datasets: a RESEARCH SOURCE, not knowledge.

IT IS A DIFFERENT SHAPE FROM THE FIRST FIVE
--------------------------------------------
Those described **trades** — things a person learns. This one describes
**businesses** — things a person starts. That changes what may be extracted
and what must be refused:

* the business names, alternative names and sectors are vocabulary, and were
  checkable here against the graph;
* the investment tables, revenue scenarios, margins, break-even periods,
  licence fees, subsidy percentages and employment counts are the bulk of the
  document and are ALL uncited estimates. The document says so itself.

It is also the first document whose own subject matter is money. Every one of
the twenty entries leads with an investment range and a profit scenario, which
is precisely the material a person is most likely to act on and precisely the
material with the least support behind it. `UNVERIFIED_FIELDS` is therefore
longer here than in any trade module.

WHAT IT SAYS ABOUT ITSELF
--------------------------
Better than average, and it earns a small amount of credit for it:

    "All data is based on publicly available information, Indian regulatory
     frameworks, and industry estimates. Research Gaps have been clearly
     marked where verified sources are unavailable."

`Research Gap` appears **10 times across 49 pages**, plus one explicit "Not
publicly verified" on an institute row and seven "verify" instructions. That is
thinner than document D's 23 markers in 37 pages but honest in kind — and
unlike document E it makes no claim of high confidence.

It declares no contact numbers as `XXXX` placeholders, but it does list named
institutes (ATI Hyderabad, TASK, ITI Mallepally, APSSDC, NDRI, IIFPT) and named
companies (Tata Power, Bosch, Ather, Ola, Hikvision, CP Plus) as training and
internship routes. None of those relationships is carried across: "Bosch offers
apprenticeships in Vijayawada" is a claim about a company's current hiring, the
most perishable kind of fact there is.

CEILING STAYS 60. One uncited secondary document.
"""

SOURCE = {
    "source_id": "doc-entrepreneurship-businesses-2026",
    "title": ("ValueWeave Entrepreneurship Decision Datasets — 20 "
              "Employment-Generating Businesses (India, Telangana & AP focus)"),
    "kind": "DATASET",
    "origin": "LLM-generated research document, supplied by the maintainer",
    "pages": 49,
    "retrieved": "2026-08-08",
    "self_declared_limits": [
        "the document states its data is 'based on publicly available "
        "information, Indian regulatory frameworks, and industry estimates' "
        "and that 'Research Gaps have been clearly marked' — 10 such markers "
        "across 49 pages",
        "investment ranges carry the note 'Estimates based on industry "
        "discussions; actuals vary by city'",
        "training-institute rows are marked 'Not publicly verified' and "
        "'Research Gap: actual course availability to verify'",
    ],
    "url": "",
}

#: Longer than any trade module's, because this document is ABOUT money.
UNVERIFIED_FIELDS = (
    "investment_range", "startup_capital", "working_capital", "revenue_range",
    "gross_margin", "net_income", "break_even_months", "payback_months",
    "employment_count", "course_fees", "institute_contact", "licence_fee",
    "subsidy_percentage", "market_demand", "placement_claim", "employer_list",
    "supplier_list", "rental_rate",
)

#: The document's central claim type, named so a promoter cannot mistake a
#: star rating for a measurement. Every business carries seven of these.
STAR_RATINGS_ARE_NOT_DATA = (
    "demand", "investment", "skill_requirement", "profit_potential",
    "employment_potential", "competition", "risk")

#: Twenty businesses. `existing` names the entity the graph ALREADY holds, and
#: was determined by reading entities.csv rather than guessing from the name —
#: eight of the twenty are already covered, which is the highest overlap rate
#: of the six documents and the reason this one queues fewer rows than its
#: length suggests.
BUSINESSES = [
    {
        "slug": "ev-garage",
        "title": "EV Garage / Electric Vehicle Service Centre",
        "existing": "EV Two-Wheeler Service Centre",
        "entity_type": "MSME",
        "aliases": ["EV Repair Shop", "EV Workshop", "Electric Car Service",
                    "EV Diagnostics Centre"],
        "industry": "Automotive Service & Repair (Electric Vehicles)",
        "notes": ("PARTIAL OVERLAP, not a clean duplicate: the graph's entity "
                  "is two-wheeler specific and this covers 2/3/4-wheelers and "
                  "e-buses. Whether to broaden the existing MSME or hold a "
                  "second, wider entity is a curation decision — recorded, "
                  "not taken."),
        "confidence": 55,
    },
    {
        "slug": "battery-recycling",
        "title": "Battery Recycling Unit (Li-ion & Lead-acid)",
        "existing": None,
        "entity_type": "MSME",
        "aliases": ["Battery Dismantling & Recycling", "EV Battery Recycler",
                    "Li-ion Battery Recovery"],
        "industry": "Waste Management & Recycling",
        "notes": ("Adjacent to the graph's 'E-Waste Dismantling and Recovery' "
                  "but not the same: lead-acid recovery and EPR registration "
                  "under the Battery Waste Management Rules are a separate "
                  "regulatory regime from e-waste."),
        "confidence": 55,
    },
    {
        "slug": "solar-installation-business",
        "title": "Solar Installation Business (Rooftop Solar EPC)",
        "existing": "Solar Rooftop EPC Contractor",
        "entity_type": "MSME",
        "aliases": ["Solar Panel Installer", "Solar Rooftop Contractor",
                    "Solar EPC Company"],
        "industry": "Renewable Energy",
        "notes": "Clean duplicate. Not queued.",
        "confidence": 55,
    },
    {
        "slug": "lift-installation-business",
        "title": "Lift Installation & Maintenance Contractor",
        "existing": None,
        "entity_type": "BusinessOpportunity",
        "aliases": ["Elevator Contractor", "Lift AMC Contractor"],
        "industry": "Vertical Transportation",
        "notes": ("PAIRS WITH A QUEUED SKILL. "
                  "doc-electrician-trades-2026:lift-technician is already in "
                  "the queue as a Skill; this is the business built on it. "
                  "Decide them together — approving one without the other "
                  "recreates the 'business you cannot learn' gap in reverse."),
        "confidence": 55,
    },
    {
        "slug": "ac-service-business",
        "title": "AC Service & Repair Business",
        "existing": None,
        "entity_type": "BusinessOpportunity",
        "aliases": ["AC Repair Business", "Air Conditioning Service",
                    "AC AMC Contractor"],
        "industry": "HVAC",
        "notes": ("THE INVERSE OF THE RECURRING PATTERN. Five documents kept "
                  "finding businesses the graph holds with no Skill teaching "
                  "them. Here the graph holds the Skill — 'HVAC Technician' — "
                  "and has no business a trained person could start. Worth "
                  "noting as the mirror image, and worth approving for the "
                  "same reason."),
        "confidence": 55,
    },
    {
        "slug": "electrical-contractor",
        "title": "Electrical Contractor",
        "existing": "Electrical Contracting (Licensed Supervisor/Contractor)",
        "entity_type": "BusinessOpportunity",
        "aliases": ["Electrical Works Contractor", "Wiring Contractor",
                    "Licensed Electrician Business"],
        "industry": "Construction & Electrical Services",
        "notes": "Clean duplicate. Not queued.",
        "confidence": 55,
    },
    {
        "slug": "plumbing-contractor",
        "title": "Plumbing Contractor",
        "existing": "Plumbing Services",
        "entity_type": "BusinessOpportunity",
        "aliases": ["Sanitary & Plumbing Works", "Water System Contractor"],
        "industry": "Construction/Plumbing",
        "notes": ("Duplicate of the existing business. Its ALIASES were "
                  "useful though — `plumbing contractor` returned the "
                  "Construction sector before this document supplied the "
                  "word."),
        "confidence": 55,
    },
    {
        "slug": "civil-contractor",
        "title": "Civil Contractor",
        "existing": None,
        "entity_type": "BusinessOpportunity",
        "aliases": ["Building Contractor", "Construction Contractor",
                    "Subcontractor (Civil Works)"],
        "industry": "Construction",
        "notes": ("The graph holds Masonry & Brickwork as a Skill and "
                  "Construction as a sector, and nothing in between. Note "
                  "the document's own employment figure — '20-200+ "
                  "labourers' — is exactly the kind of number that must not "
                  "be promoted."),
        "confidence": 50,
    },
    {
        "slug": "interior-contractor",
        "title": "Interior Contractor / Interior Works",
        "existing": None,
        "entity_type": "BusinessOpportunity",
        "aliases": ["Turnkey Interior Contractor", "Interior Fit-Out Contractor",
                    "Interior Execution"],
        "industry": "Interior Design & Execution",
        "notes": ("BEARS ON AN OPEN CLASS-D QUESTION. The construction "
                  "document queued 'Interior Finishing Technician' and the "
                  "classification register marked it DISPUTED because "
                  "'interior finishing' reads as an umbrella over false "
                  "ceiling, painting, tiling and joinery rather than one "
                  "trade. This document independently treats interior work as "
                  "a BUSINESS that coordinates those trades — which is "
                  "evidence for the umbrella reading. Two documents, two "
                  "framings, and they agree once you separate the trade "
                  "question from the business question."),
        "confidence": 50,
    },
    {
        "slug": "cctv-installation-business",
        "title": "CCTV Installation & Security Systems Business",
        "existing": None,
        "entity_type": "BusinessOpportunity",
        "aliases": ["Security Systems Integrator", "CCTV Dealer & Installer",
                    "Electronic Security Contractor"],
        "industry": "Electronic Security",
        "notes": ("PAIRS WITH A QUEUED AND VERIFIED SKILL. "
                  "doc-electronics-trades-2026:cctv-technician is queued and "
                  "was verified against ESSCI ELE/Q4605. Decide together."),
        "confidence": 55,
    },
    {
        "slug": "mobile-repair-shop",
        "title": "Mobile Repair Shop",
        "existing": None,
        "entity_type": "BusinessOpportunity",
        "aliases": ["Mobile Service Centre", "Phone Repair Shop",
                    "Mobile Spares & Service"],
        "industry": "Electronics Repair",
        "notes": ("The Skill exists — 'Electronics Repair & Maintenance' — "
                  "and the document's own investment figure of ₹15,000 makes "
                  "this the lowest-capital business in all six documents. "
                  "That figure is NOT carried across; it is the reviewer's to "
                  "check, and it is the single most consequential number in "
                  "the file for a reader with no money."),
        "confidence": 55,
    },
    {
        "slug": "computer-service-center",
        "title": "Computer Service Center",
        "existing": "IT Hardware and Network Services",
        "entity_type": "MSME",
        "aliases": ["Laptop Service Centre", "Computer Repair Shop",
                    "IT AMC Provider"],
        "industry": "IT Services & Repair",
        "notes": "Duplicate of the existing MSME. Not queued.",
        "confidence": 55,
    },
    {
        "slug": "cnc-job-work-unit",
        "title": "CNC Job Work Unit",
        "existing": "CNC Machining Job Shop",
        "entity_type": "MSME",
        "aliases": ["CNC Job Shop", "Precision Machining Unit"],
        "industry": "Precision Manufacturing",
        "notes": "Clean duplicate. Not queued.",
        "confidence": 55,
    },
    {
        "slug": "fabrication-workshop",
        "title": "Fabrication Workshop",
        "existing": "Welding & Metal Fabrication",
        "entity_type": "BusinessOpportunity",
        "aliases": ["Steel Fabrication Workshop", "Gate & Grill Fabrication",
                    "Structural Fabrication Shop"],
        "industry": "Metal Fabrication",
        "notes": ("Duplicate. Its aliases did real work: `fabrication "
                  "workshop` and `gate and grill fabrication` returned "
                  "*Masala Powder Manufacturing Unit* before this document "
                  "supplied them."),
        "confidence": 55,
    },
    {
        "slug": "welding-shop",
        "title": "Welding Shop",
        "existing": "Welding & Metal Fabrication",
        "entity_type": "BusinessOpportunity",
        "aliases": ["Welding Works", "On-site Welding Service"],
        "industry": "Metal Joining Services",
        "notes": ("Duplicate, and a duplicate of the row above it — the "
                  "document splits fabrication and welding into two "
                  "businesses that share one entity. Same over-splitting the "
                  "trade documents showed."),
        "confidence": 55,
    },
    {
        "slug": "granite-tiles-contracting",
        "title": "Granite & Tiles Contracting",
        "existing": "Tiles Fixing (Tile Mason)",
        "entity_type": "BusinessOpportunity",
        "aliases": ["Granite Contractor", "Marble & Granite Laying",
                    "Flooring Contractor"],
        "industry": "Building Finishing",
        "notes": ("Duplicate of the existing business. Relates to the queued "
                  "construction-document candidate 'Granite Cutter', which "
                  "the classification register already marks class A onto the "
                  "same entity — consistent, and worth noting that two "
                  "documents reached the same answer independently."),
        "confidence": 55,
    },
    {
        "slug": "borewell-services-business",
        "title": "Borewell Drilling & Services",
        "existing": "Borewell Drilling Services",
        "entity_type": "BusinessOpportunity",
        "aliases": ["Borewell Contractor", "Rig Owner"],
        "industry": "Water Resources",
        "notes": "Clean duplicate. Not queued.",
        "confidence": 55,
    },
    {
        "slug": "water-purification-services",
        "title": "Water Purification Services (RO Plant Service & Supply)",
        "existing": None,
        "entity_type": "BusinessOpportunity",
        "aliases": ["RO Service Business", "Water Purifier AMC",
                    "Water Can Filling Station"],
        "industry": "Water Treatment",
        "notes": ("Nothing comparable in the graph. Search currently answers "
                  "`ro plant` with *Tractor (35-45 HP)* and `water purifier` "
                  "with *Micro-Irrigation System (Drip)* — but no alias was "
                  "written, because there is no true entity to point at. "
                  "Approving this is the fix."),
        "confidence": 55,
    },
    {
        "slug": "dairy-processing-unit",
        "title": "Dairy Processing Unit (Mini Dairy)",
        "existing": None,
        "entity_type": "MSME",
        "aliases": ["Mini Dairy Plant", "Milk Chilling & Processing Unit",
                    "Paneer & Curd Unit"],
        "industry": "Dairy & Food Processing",
        "notes": ("The graph holds general food-processing entities and no "
                  "dairy one. `dairy processing`, `mini dairy` and `milk "
                  "processing` all return *Cattle Dung and Farm Waste* today "
                  "— badly wrong, and deliberately left wrong: no entity "
                  "exists to point at and a sector expansion is what §11 "
                  "forbids."),
        "confidence": 55,
    },
    {
        "slug": "cold-storage-business",
        "title": "Cold Storage Business",
        "existing": "Cold Storage Facility",
        "entity_type": "MSME",
        "aliases": ["Cold Chain Storage", "Refrigerated Warehouse"],
        "industry": "Agri-logistics & Cold Chain",
        "notes": ("Duplicate of the existing MSME. Note the graph also holds "
                  "'Cold Storage Unit' as MACHINERY — a different thing, and "
                  "the reason no alias was written for that phrase."),
        "confidence": 55,
    },
]

#: Central schemes the document names that the graph does NOT hold. Names and
#: administering bodies only — every subsidy percentage, ceiling and
#: eligibility rule the document states is an uncited claim and is excluded.
SCHEMES_NOT_IN_GRAPH = [
    {
        "slug": "clcss",
        "title": "Credit Linked Capital Subsidy Scheme (CLCSS)",
        "body": "Ministry of MSME",
        "notes": ("Named twice in the document as a route to machinery "
                  "finance. The graph holds CGTMSE, PMEGP, MUDRA and "
                  "Stand-Up India but not this one."),
        "confidence": 50,
    },
    {
        "slug": "nabard-deds",
        "title": "Dairy Entrepreneurship Development Scheme (DEDS)",
        "body": "NABARD",
        "notes": ("Named for the dairy business. NEEDS_RESEARCH before any "
                  "promotion: DEDS has been reported as discontinued or "
                  "restructured in some years, and a scheme entity that no "
                  "longer accepts applications is worse than no entity — a "
                  "reader would waste a trip to a bank."),
        "confidence": 35,
    },
    {
        "slug": "midh",
        "title": "Mission for Integrated Development of Horticulture (MIDH)",
        "body": "Ministry of Agriculture & Farmers Welfare",
        "notes": ("Named as the cold-storage subsidy route. The document's "
                  "'up to 50%' figure is not carried across."),
        "confidence": 50,
    },
]

#: Named in the document as training routes and NOT carried across. Recorded so
#: a later reader can see the decision was deliberate rather than an oversight.
#: Institutions are checkable and some may deserve TrainingProvider entities;
#: what may never be promoted from here is the COURSE claim attached to them,
#: which the document itself marks "Not publicly verified" and "Research Gap:
#: actual course availability to verify".
TRAINING_ROUTES_NOT_PROMOTED = (
    "Advanced Training Institute (ATI), Hyderabad",
    "Telangana Academy for Skill and Knowledge (TASK)",
    "ITI Mallepally, Hyderabad",
    "AP State Skill Development Corporation (APSSDC)",
    "National Dairy Research Institute (NDRI)",
    "Indian Institute of Food Processing Technology (IIFPT)",
    "Sri Venkateswara Polytechnic, Tirupati",
)

#: Place names the document uses that are LOCALITIES, not districts. The graph
#: holds 61 districts; these are neighbourhoods and industrial estates inside
#: Hyderabad and Vijayawada. Creating District entities for them would corrupt
#: a clean administrative hierarchy, so they are named here to be refused.
LOCALITIES_NOT_DISTRICTS = ("Ranigunj", "Secunderabad", "Balanagar",
                            "Mallepally")


def new_businesses():
    """Businesses with no comparable entity in the graph."""
    return [b for b in BUSINESSES if b["existing"] is None]


def merge_businesses():
    return [b for b in BUSINESSES if b["existing"] is not None]


def new_schemes():
    return list(SCHEMES_NOT_IN_GRAPH)


def new_roles():
    """What the emitter queues: the uncovered businesses, then the schemes.

    Named `new_roles` because that is the interface every source module in
    this directory already exposes and the emitter already calls. The rows
    carry `entity_type` so the classifier records BusinessOpportunity, MSME or
    GovernmentScheme rather than defaulting to Skill — a reviewer opening this
    queue is being asked "should ValueWeave hold this as a business", which is
    a different question from the one the five trade documents asked, and the
    entity type is how the queue says which.
    """
    rows = []
    for b in new_businesses():
        row = dict(b)
        row["queue_noun"] = "business"
        rows.append(row)
    for s in new_schemes():
        rows.append({
            "slug": s["slug"],
            "title": s["title"],
            "aliases": [s["title"].split("(")[0].strip()],
            "entity_type": "GovernmentScheme",
            "queue_noun": "central scheme",
            "body": s["body"],
            "notes": s["notes"],
            "confidence": s["confidence"],
        })
    return rows
