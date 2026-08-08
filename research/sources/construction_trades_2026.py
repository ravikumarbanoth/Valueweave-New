#!/usr/bin/env python3
"""
The Construction & Infrastructure career dataset, normalised.

WHAT THIS FILE IS
-----------------
A 48-page career dataset covering 15 construction and interior-finishing trades
with a Telangana / Andhra Pradesh focus. Same treatment as
`electrician_trades_2026.py`: a RESEARCH SOURCE, not knowledge.

HOW IT DIFFERS FROM THE ELECTRICIAN DOCUMENT — IT IS BETTER
------------------------------------------------------------
Worth recording, because the two were handled the same way and only one of them
deserved the suspicion by its own admission:

  · **No `XXXX` placeholders.** The electrician document had five institutes
    with literal placeholder phone numbers. This one has none.
  · **Real institute web addresses** — `itimallepally.telangana.gov.in`,
    `iti.ap.gov.in` — rather than invented contact details.
  · **No self-declared confidence caveat.** It does not say its salaries are
    estimates.

That last point cuts both ways. The electrician document told the reader where
it was weak; this one does not, which makes it *less* self-aware, not more
reliable. It is still LLM output, its salary tables are still uncited, and its
confidence ceiling is still 60. Absence of a caveat is not evidence of accuracy.

A DEFECT IN THE SOURCE, FOUND AND NOT PROPAGATED
-------------------------------------------------
ROLE 3 (Aluminium Fabricator) lists its "Alternative Job Titles" as *"uPVC
Window Technician, Fenestration Installer, uPVC Fitting Specialist"* — which is
ROLE 4's list, copied verbatim. Aluminium fabrication and uPVC fitting are
different trades with different materials and different tools; the document's
own tool tables for the two roles disagree with each other, which is what makes
the copy-paste visible.

The wrong aliases are NOT carried across. `aliases` for that role below is
built from the trade itself and is marked in `notes`.

THE TELUGU IS DAMAGED HERE TOO
-------------------------------
The same conjunct-cluster loss: `ఇండసి్ట` for industrial, `ఎక్స్కవేటర్ డై` for
excavator driver, `జిప్సమ్ పా` for gypsum plaster, `మేసీ` for మేస్త్రీ. None of
it is used. See `electrician_trades_2026.py` for the full explanation.

WHAT MAKES THIS DOCUMENT VALUABLE
----------------------------------
All fifteen trades are absent from the graph as Skills. Five of them already
exist as BUSINESSES:

    POP Works / False Ceiling Installation   <- False Ceiling Installer
                                             <- POP Gypsum Technician
    Aluminium Fabrication                    <- Aluminium Fabricator
    Borewell Drilling Services               <- Borewell Technician
    Submersible Pump Installation & Repair   <- Pump Technician

So today a reader can find "you could start a borewell drilling business" and
nothing at all about learning to do the work. That asymmetry — a business you
cannot learn — is the single most useful thing this document exposes, and it is
what the review candidates are pointed at.
"""

SOURCE = {
    "source_id": "doc-construction-trades-2026",
    "title": ("ValueWeave Career Decision Dataset: Construction & Infrastructure "
              "Sector (India / TG & AP Focus)"),
    "kind": "DATASET",
    "origin": "LLM-generated research document, supplied by the maintainer",
    "pages": 48,
    "retrieved": "2026-08-07",
    "self_declared_limits": [],   # it declares none — see the module docstring
    "url": "",
}

#: Same as the electrician source. Salary tables here are uncited even though
#: the document does not admit it.
UNVERIFIED_FIELDS = ("salary_range", "course_fees", "institute_contact",
                     "placement_claim", "equipment_cost")

#: Role -> the BusinessOpportunity the graph already holds. The gap this
#: document closes: a business a reader cannot currently learn the trade for.
BUSINESS_WITHOUT_A_SKILL = {
    "false-ceiling-installer": "POP Works / False Ceiling Installation",
    "pop-gypsum-technician": "POP Works / False Ceiling Installation",
    "aluminium-fabricator": "Aluminium Fabrication",
    "borewell-technician": "Borewell Drilling Services",
    "pump-technician": "Submersible Pump Installation & Repair",
}

ROLES = [
    {
        "slug": "false-ceiling-installer",
        "title": "False Ceiling Installer",
        "existing": None,
        "aliases": ["False Ceiling Worker", "Gypsum Board Installer",
                    "Ceiling Technician", "Drywall & Ceiling Erector",
                    "Drywall Installer"],
        "industries": ["Building Interiors", "Finishing & Fit-Outs",
                       "Civil Construction"],
        "nature": "Physical, site-based, measurement-driven, overhead material handling",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high — low barrier to sub-contracting",
        "tools": ["Laser level", "Metal snips", "Screw gun", "Grid cutter",
                  "Measuring tape", "Scaffold platform"],
        "relates": ["Drywall Installer", "Mason", "Interior Painter",
                    "Decorative Tile Laying Technician", "POP Gypsum Technician",
                    "Interior Finishing Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "pop-gypsum-technician",
        "title": "POP Gypsum Technician",
        "existing": None,
        "aliases": ["POP Plasterer", "Gypsum Finisher",
                    "Wall Plastering Technician", "POP Moulding Artisan"],
        "industries": ["Interior Design", "Building Finishing", "Civil Construction"],
        "nature": "Physical, site-based, finishing craft",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high",
        "tools": ["Plastering trowel", "Hawk board", "Mixing bucket",
                  "Moulding frames", "Sanding block"],
        "relates": ["Drywall Installer", "Mason", "Interior Painter",
                    "Decorative Tile Laying Technician", "False Ceiling Installer"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "aluminium-fabricator",
        "title": "Aluminium Fabricator",
        "existing": None,
        #: NOT the document's list. ROLE 3 carries ROLE 4's alternative titles
        #: verbatim — a copy-paste defect in the source. These are the trade's
        #: own names, and the role is flagged in `notes`.
        "aliases": ["Aluminium Fitter", "Aluminium Door & Window Fabricator",
                    "Glazing Fabricator", "Section Fabricator"],
        "industries": ["Fenestration", "Facade Architecture", "Building Construction"],
        "nature": "Workshop and site, precision cutting and assembly",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Aluminium mitre cut saw", "Bench drill", "Portable drill",
                  "Rivet gun", "Silicone gun", "Measuring square"],
        "relates": ["uPVC Window Installer", "Structural Steel Fabricator",
                    "Glass Installer", "Glazier"],
        "notes": ("SOURCE DEFECT: the document lists uPVC alternative titles for "
                  "this role, copied from ROLE 4. Its own tool tables for the two "
                  "roles disagree, which is what makes the copy-paste visible. "
                  "Aliases here are the trade's, not the document's."),
        "confidence": 45,
    },
    {
        "slug": "upvc-window-installer",
        "title": "uPVC Window Installer",
        "existing": None,
        "aliases": ["uPVC Window Technician", "Fenestration Installer",
                    "uPVC Fitting Specialist", "Window Fitter"],
        "industries": ["Modern Building Fenestration", "Residential Interiors"],
        "nature": "Site-based, precision fitting, sealing",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Heavy-duty hammer drill", "Caulking / silicone gun",
                  "Glass suction lifter", "Spirit level", "Allen key set"],
        "relates": ["Aluminium Fabricator", "Glass Installer", "Door Technician",
                    "Structural Glazier"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "glass-installer",
        "title": "Glass Installer",
        "existing": None,
        "aliases": ["Glazier", "Architectural Glass Technician",
                    "Facade Glass Fitter", "Glass Fitter"],
        "industries": ["Building Facades", "Interior Design", "Architectural Glass"],
        "nature": "Site-based, heavy and fragile material handling, at height",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Professional glass cutter", "Vacuum suction cup lifters",
                  "Silicone gun", "Safety gloves", "Glazing beads"],
        "relates": ["Aluminium Fabricator", "uPVC Window Installer",
                    "Facade Inspector", "Curtain Wall Erector"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "waterproofing-technician",
        "title": "Waterproofing Technician",
        "existing": None,
        "aliases": ["Waterproofing Applicator", "Leakage Treatment Specialist",
                    "Chemical Waterproofing Worker"],
        "industries": ["Construction Chemicals",
                       "Building Maintenance & Rehabilitation"],
        "nature": "Site-based, chemical handling, terrace and basement work",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high",
        "tools": ["High-pressure surface washer", "PU injection grout pump",
                  "Spray applicator", "Mixing paddle", "Trowel"],
        "relates": ["Concrete Repair Technician", "Painter", "Roofing Technician",
                    "Civil Inspector"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "borewell-technician",
        "title": "Borewell Technician",
        "existing": None,
        "aliases": ["Rig Operator", "Borewell Drilling Assistant", "Driller",
                    "Groundwater Drilling Technician"],
        "industries": ["Groundwater Extraction", "Civil Infrastructure",
                       "Agriculture & Domestic Water Supply"],
        "nature": "Field-based, heavy rig work, physically demanding",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High — rig ownership is capital-heavy",
        "tools": ["Heavy chain pipe wrench set",
                  "High-pressure air compressor (300+ PSI)", "DTH hammer",
                  "Drill rods", "Casing pipe tools"],
        "relates": ["Pump Technician", "Well Digger", "Piling Rig Operator",
                    "Heavy Vehicle Mechanic"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "pump-technician",
        "title": "Pump Technician",
        "existing": None,
        "aliases": ["Submersible Pump Fitter", "Water Pump Mechanic",
                    "Pump Electrician & Fitter", "Motor Winder"],
        "industries": ["Water Supply", "Plumbing & MEP", "Agricultural Machinery"],
        "nature": "Field and workshop, electrical and mechanical",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high",
        "tools": ["Insulation tester (megger)", "Clamp multimeter",
                  "Pipe wrench", "Puller set", "Winding tools"],
        "relates": ["Electrician", "Plumber", "Borewell Technician",
                    "Motor Winder"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "roofing-technician",
        "title": "Roofing Technician",
        "existing": None,
        "aliases": ["Roofing Fabricator", "Industrial Shed Erector",
                    "Sheet Roofing Installer"],
        "industries": ["Industrial Construction", "Warehousing",
                       "Structural Steel Buildings"],
        "nature": "At height, structural steel and sheet work, safety critical",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["High-torque cordless hex driver",
                  "Fall arrest full-body harness", "Sheet nibbler",
                  "Crimping tool", "Measuring tape"],
        "relates": ["Structural Steel Fabricator", "Welder",
                    "Waterproofing Technician", "Scaffolding Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "modular-kitchen-installer",
        "title": "Modular Kitchen Installer",
        "existing": None,
        "aliases": ["Modular Furniture Fitter", "Kitchen Carpenter",
                    "Cabinetry Technician"],
        "industries": ["Interior Design", "Wooden Furniture Manufacturing",
                       "Residential Interiors"],
        "nature": "Site-based, precision assembly, client-facing",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high",
        "tools": ["Multi-line laser level", "Cordless Li-ion screwdriver",
                  "Hole saw set", "Edge trimmer", "Clamps"],
        "relates": ["Interior Carpenter", "Furniture Maker", "Granite Cutter",
                    "Interior Supervisor"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "interior-finishing-technician",
        "title": "Interior Finishing Technician",
        "existing": None,
        "aliases": ["Interior Snagging Technician", "Interior Finisher",
                    "Fit-Out Handyman"],
        "industries": ["Premium Residential & Commercial Interior Fit-Outs"],
        "nature": "Site-based, multi-trade finishing and defect correction",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Electric hot melt glue gun", "Fine tooth mitre saw",
                  "Detail sander", "Filling knife", "Laser level"],
        "relates": ["False Ceiling Installer", "POP Gypsum Technician",
                    "Interior Painter", "Modular Kitchen Installer"],
        "notes": "",
        "confidence": 50,
    },
    {
        "slug": "granite-cutter",
        "title": "Granite Cutter",
        "existing": None,
        "aliases": ["Granite Mason", "Stone Fabricator",
                    "Marble Cutter & Polisher", "Stone Polisher"],
        "industries": ["Stone Processing", "Flooring & Masonry",
                       "Interior Architecture"],
        "nature": "Workshop and site, wet cutting, dust and silica exposure",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Heavy-duty wet stone cutter", "Variable speed angle polisher",
                  "Diamond blades", "Edge profiling wheels", "Suction lifter"],
        "relates": ["Tile & Marble Fixer", "Mason", "Marble Fitter",
                    "Modular Kitchen Installer"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "road-equipment-operator",
        "title": "Road Construction Equipment Operator",
        "existing": None,
        "aliases": ["Paver Operator", "Road Roller Operator", "Grader Operator",
                    "Highway Equipment Driver"],
        "industries": ["Transport Infrastructure", "Highways & Roads",
                       "Civil Construction"],
        "nature": "Machine-seat, outdoor, long shifts",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Low — equipment costs ₹22 lakh and up",
        "tools": ["Soil compactor roller (employer-owned)",
                  "Asphalt sensor paver (employer-owned)",
                  "Motor grader (employer-owned)"],
        "relates": ["Excavator Operator", "Crane Operator", "Heavy Truck Driver",
                    "Paving Supervisor"],
        "notes": "Machines here are plant, not personal tools — the document's "
                 "₹22–90 lakh figures are capital equipment, not a toolkit.",
        "confidence": 55,
    },
    {
        "slug": "excavator-operator",
        "title": "Excavator Operator",
        "existing": None,
        "aliases": ["Earthmover Operator", "JCB Driver", "Digger Operator",
                    "Backhoe Operator"],
        "industries": ["Civil Construction", "Mining", "Irrigation",
                       "Infrastructure"],
        "nature": "Machine-seat, outdoor, site-based",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Low — a backhoe loader is ₹30 lakh and up",
        "tools": ["Backhoe loader (employer-owned)",
                  "Hydraulic excavator (employer-owned)"],
        "relates": ["Crane Operator", "Road Roller Operator", "Heavy Truck Driver",
                    "Mining Machinery Operator"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "crane-operator",
        "title": "Crane Operator",
        "existing": None,
        "aliases": ["Tower Crane Operator", "Hydraulic Mobile Crane Driver",
                    "Rigging & Lifting Operator", "Rigger"],
        "industries": ["High-Rise Construction", "Metro Rail",
                       "Ports & Logistics", "Heavy Infrastructure"],
        "nature": "Cab-based, at height, safety critical, licensed",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Low — crane hire is capital-heavy",
        "tools": ["Tower crane (employer-owned)",
                  "Mobile crane (employer-owned)", "Rigging gear"],
        "relates": ["Excavator Operator", "Rigging Specialist",
                    "Heavy Equipment Mechanic", "Port Gantry Operator"],
        "notes": "",
        "confidence": 55,
    },
]


def new_roles():
    """All fifteen. Not one of these trades exists as a Skill in the graph."""
    return [r for r in ROLES if r["existing"] is None]


def merge_roles():
    return [r for r in ROLES if r["existing"] is not None]


def businesses_without_a_skill():
    """The gap worth showing a reviewer first: a business the graph offers and
    a trade it cannot teach."""
    return {r["slug"]: BUSINESS_WITHOUT_A_SKILL[r["slug"]]
            for r in ROLES if r["slug"] in BUSINESS_WITHOUT_A_SKILL}
