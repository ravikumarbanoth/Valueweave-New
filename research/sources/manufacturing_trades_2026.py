#!/usr/bin/env python3
"""
The Manufacturing & Factory Careers dataset, normalised.

WHAT THIS FILE IS
-----------------
A 56-page dataset covering 15 machine-shop and factory-floor careers with a
Telangana / Andhra Pradesh focus — the largest of the three supplied documents.
Same treatment: a RESEARCH SOURCE, not knowledge.

IT MAKES THE STRONGEST CLAIM OF THE THREE, AND MOSTLY KEEPS IT
---------------------------------------------------------------
Its first page says:

    "Where exact data is unavailable, a confidence note is added.
     No statistics are invented."

and it closes with a global note that is the most candid of the three
documents:

    "Salary ranges are indicative based on market surveys (Naukri, Indeed,
     industry contacts) as of 2025. Training institute contacts verified from
     official websites; always confirm current status. Entrepreneurship
     investment estimates vary by location and condition of machinery."

That is a better provenance statement than either of the others gave. It is
still not a citation: "based on market surveys" names no survey and links to
nothing, and the word "verified" is the author's assertion about their own
process. The claim is also only sparsely honoured in the body — the string
"Confidence" appears eight times across 56 pages and fifteen roles.

So the ceiling stays **60**, the same as the others. A document that describes
its own method well is easier to trust than one that says nothing; it is not
thereby a primary source.

TWO INTERNAL DUPLICATION DEFECTS
---------------------------------
Both are the same failure mode found in the construction document — a role's
fields copied from its neighbour — which now looks like a property of how these
documents are generated rather than a one-off.

  1. **Turner (11) and Machinist (12) carry identical alternative job titles**:
     "All-round Machinist, Machine Shop Machinist, General Machinist, Tool Room
     Machinist". Those are the machinist's names. A turner's are lathe names.

  2. **Turner is already an alias of role 1.** Lathe Machine Operator lists
     "Turner, Manual Lathe Operator, Conventional Turner, Machine Man" as its
     own alternative titles — so the document presents the same trade as both
     an alias and a separate career.

The graph agrees with the alias reading: `Lathe Operation` is one Skill, and
roles 1, 11 and 12 all map onto it. They are recorded here as merges rather
than as three new careers, and `aliases` for role 11 is the turner's own.

A CROSS-DOCUMENT COLLISION
---------------------------
Role 10 (**Fitter**) shares two alternative titles — "Mechanical Fitter" and
"Maintenance Fitter" — with `machine-maintenance-technician`, already queued
from the electrician document. They are close to the same trade.

`collection/dedupe.py` does NOT catch it: it scores the two TITLES at 0.00
against a 0.80 threshold, because it compares titles and these are two
different words for one job. That is a real limit of the deduper, found only
by having three documents instead of one. The overlap is surfaced by hand in
the candidate so the reviewer decides them together.
"""

SOURCE = {
    "source_id": "doc-manufacturing-trades-2026",
    "title": ("Career Decision Datasets — Manufacturing & Factory Careers "
              "(India, Telangana & AP focus)"),
    "kind": "DATASET",
    "origin": "LLM-generated research document, supplied by the maintainer",
    "pages": 56,
    "retrieved": "2026-08-07",
    "self_declared_limits": [
        "salary ranges are indicative, based on unnamed market surveys as of 2025",
        "institute contacts self-described as verified; always confirm current status",
        "entrepreneurship investment estimates vary by location and machinery condition",
    ],
    "url": "",
}

UNVERIFIED_FIELDS = ("salary_range", "course_fees", "institute_contact",
                     "placement_claim", "machine_cost")

ROLES = [
    {
        "slug": "lathe-machine-operator",
        "title": "Lathe Machine Operator",
        "existing": "Lathe Operation",
        "aliases": ["Turner", "Manual Lathe Operator", "Conventional Turner",
                    "Machine Man"],
        "industries": ["Manufacturing", "Automobile", "General Engineering",
                       "Job Shops", "Railways", "Defence"],
        "nature": "Shop floor, standing, coolant and swarf, repetitive precision work",
        "future_demand": "Steady",
        "automation_risk": "Medium — CNC displaces conventional turning",
        "entrepreneurship": "Medium — a job shop needs a machine",
        "tools": ["Vernier caliper", "Micrometer", "Cutting tools", "Chuck key",
                  "Dial indicator"],
        "relates": ["Machinist", "Turner", "CNC Machine Operator",
                    "Tool & Die Maker", "Fitter", "Quality Inspector"],
        "notes": "",
        "confidence": 60,
    },
    {
        "slug": "milling-machine-operator",
        "title": "Milling Machine Operator",
        "existing": None,
        "aliases": ["Miller", "Vertical Mill Operator", "Milling Machinist"],
        "industries": ["Manufacturing", "Tool rooms", "General Engineering"],
        "nature": "Shop floor, precision setup, fixture work",
        "future_demand": "Steady",
        "automation_risk": "Medium",
        "entrepreneurship": "Medium",
        "tools": ["End mills", "Vernier caliper", "Dial indicator",
                  "Machine vice", "Collet set"],
        "relates": ["Lathe Machine Operator", "CNC Machine Operator",
                    "Tool & Die Maker", "Machinist"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "vmc-cnc-programmer",
        "title": "VMC/CNC Programmer",
        "existing": "CNC Machine Operator",
        "aliases": ["CNC Programmer", "VMC Programmer", "CAM Programmer",
                    "CNC Machining Centre Operator", "CNC Setter-cum-Programmer"],
        "industries": ["Auto components", "Aerospace", "Die and mould",
                       "General engineering"],
        "nature": "Shop floor and desk, programming and setup",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Medium — a CNC job shop is capital-heavy",
        "tools": ["CAM software", "Tool presetter", "Micrometer",
                  "Edge finder", "Offset gauges"],
        "relates": ["Machinist", "Tool & Die Maker", "Quality Inspector",
                    "CAD/CAM Engineer", "Milling Machine Operator"],
        "notes": "",
        "confidence": 60,
    },
    {
        "slug": "injection-moulding-operator",
        "title": "Injection Moulding Operator",
        "existing": None,
        "aliases": ["Injection Molding Machine Operator", "IMM Operator",
                    "Plastic Moulding Technician", "Moulding Operator"],
        "industries": ["Plastics", "Auto components", "Packaging",
                       "Consumer goods"],
        "nature": "Shop floor, machine-side, heat and cycle timing",
        "future_demand": "High",
        "automation_risk": "Medium",
        "entrepreneurship": "Low — a moulding machine is capital-heavy",
        "tools": ["Mould temperature controller", "Vernier caliper",
                  "Purging tools", "Hoist"],
        "relates": ["Tool & Die Maker", "Production Operator",
                    "Quality Inspector", "Machine Maintenance Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "press-machine-operator",
        "title": "Press Machine Operator",
        "existing": None,
        "aliases": ["Power Press Operator", "Stamping Press Operator",
                    "Press Shop Worker", "Sheet Metal Press Operator"],
        "industries": ["Sheet metal", "Auto components", "White goods"],
        "nature": "Shop floor, high-force machinery, safety critical",
        "future_demand": "Steady",
        "automation_risk": "Medium",
        "entrepreneurship": "Low",
        "tools": ["Die setting tools", "Vernier caliper", "Safety guards",
                  "Feed gauges"],
        "relates": ["Tool & Die Maker", "Sheet Metal Worker",
                    "Production Operator", "Quality Inspector"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "quality-inspector",
        "title": "Quality Inspector",
        "existing": None,
        "aliases": ["QC Inspector", "Quality Technician", "Inspection Engineer",
                    "QA Inspector", "In-process Inspector"],
        "industries": ["Manufacturing", "Auto components", "Pharma", "Aerospace"],
        "nature": "Shop floor and metrology lab, measurement and documentation",
        "future_demand": "High",
        "automation_risk": "Medium — vision systems assist, do not replace",
        "entrepreneurship": "Medium — third-party inspection services",
        "tools": ["Vernier caliper", "Micrometer", "Height gauge",
                  "Bore gauge", "Surface plate", "CMM"],
        "relates": ["Machinist", "CNC Machine Operator", "Production Operator",
                    "Tool & Die Maker", "Metrology Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "production-operator",
        "title": "Production Operator",
        "existing": None,
        "aliases": ["Machine Operator", "Line Operator", "Process Operator",
                    "Manufacturing Associate", "Plant Operator"],
        "industries": ["Manufacturing", "FMCG", "Pharma", "Auto"],
        "nature": "Shop floor, shift work, standard operating procedures",
        "future_demand": "High",
        "automation_risk": "Medium",
        "entrepreneurship": "Low",
        "tools": ["Employer-provided line equipment", "Basic gauges"],
        "relates": ["Assembly Line Technician", "Quality Inspector",
                    "Machine Maintenance Technician", "Press Machine Operator"],
        "notes": "",
        "confidence": 50,
    },
    {
        "slug": "assembly-line-technician",
        "title": "Assembly Line Technician",
        "existing": None,
        "aliases": ["Assembly Operator", "Line Technician", "Assembly Mechanic",
                    "Production Technician"],
        "industries": ["Automotive", "Electronics", "White goods"],
        "nature": "Shop floor, takt-time paced, repetitive assembly",
        "future_demand": "High",
        "automation_risk": "Medium",
        "entrepreneurship": "Low",
        "tools": ["Torque wrench", "Pneumatic screwdriver", "Jigs and fixtures"],
        "relates": ["Production Operator", "Quality Inspector", "Fitter",
                    "Robotics Technician"],
        "notes": "",
        "confidence": 50,
    },
    {
        "slug": "tool-and-die-maker",
        "title": "Tool & Die Maker",
        "existing": None,
        "aliases": ["Tool Maker", "Die Maker", "Mould Maker",
                    "Tool Room Machinist", "Tool & Die Technician"],
        "industries": ["Tool rooms", "Auto components", "Plastics", "Press shops"],
        "nature": "Tool room, high-precision, long-cycle craft work",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Medium — a tool room is capital-heavy",
        "tools": ["Surface grinder", "Slip gauges", "Micrometer",
                  "Height gauge", "EDM electrodes"],
        "relates": ["Machinist", "CNC Machine Operator", "Press Machine Operator",
                    "Injection Moulding Operator", "Quality Inspector"],
        "notes": "",
        "confidence": 60,
    },
    {
        "slug": "fitter",
        "title": "Fitter",
        "existing": None,
        "aliases": ["Mechanical Fitter", "Maintenance Fitter", "Bench Fitter",
                    "Assembly Fitter"],
        "industries": ["Manufacturing", "Plant maintenance", "Fabrication"],
        "nature": "Bench and plant floor, marking, filing, assembly",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Medium",
        "tools": ["Bench vice", "Files", "Hacksaw", "Vernier caliper",
                  "Try square", "Scriber"],
        "relates": ["Machine Maintenance Technician", "Machinist", "Welder",
                    "Assembly Line Technician", "Millwright"],
        "notes": ("CROSS-DOCUMENT OVERLAP, AND THE DEDUPER DOES NOT CATCH IT: "
                  "shares 'Mechanical Fitter' and 'Maintenance Fitter' with "
                  "machine-maintenance-technician, already queued from the "
                  "electrician document. collection/dedupe.py scores the two "
                  "TITLES at 0.00 against a 0.80 threshold — it compares "
                  "titles, and these are two different words for one trade. "
                  "Surfaced here by hand so the reviewer sees it, because "
                  "nothing automatic will. Decide them together. "
                  "'Pipe Fitter' is dropped from the document's alias list — "
                  "it is the plumbing trade and already resolves there."),
        "confidence": 55,
    },
    {
        "slug": "turner",
        "title": "Turner",
        "existing": "Lathe Operation",
        #: NOT the document's list. Role 11 carries role 12's machinist titles
        #: verbatim; these are the turner's own, and the document itself names
        #: "Turner" as an alias of role 1.
        "aliases": ["Lathe Turner", "Conventional Turner", "Turning Operator"],
        "industries": ["Manufacturing", "Job shops", "Railways"],
        "nature": "Shop floor, lathe work",
        "future_demand": "Steady",
        "automation_risk": "Medium",
        "entrepreneurship": "Medium",
        "tools": ["Vernier caliper", "Micrometer", "Turning tools"],
        "relates": ["Lathe Machine Operator", "Machinist", "CNC Machine Operator"],
        "notes": ("SOURCE DEFECT: the document gives this role the machinist's "
                  "alternative titles, and separately lists 'Turner' as an alias "
                  "of role 1 (Lathe Machine Operator). The graph agrees with the "
                  "alias reading — one Skill, `Lathe Operation` — so this is "
                  "recorded as a merge, not a new career."),
        "confidence": 45,
    },
    {
        "slug": "machinist",
        "title": "Machinist",
        "existing": "Lathe Operation",
        "aliases": ["All-round Machinist", "Machine Shop Machinist",
                    "General Machinist", "Tool Room Machinist"],
        "industries": ["Manufacturing", "Tool rooms", "General Engineering"],
        "nature": "Shop floor, multi-machine, precision work",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Medium",
        "tools": ["Vernier caliper", "Micrometer", "Dial indicator",
                  "Surface plate", "Cutting tools"],
        "relates": ["Lathe Machine Operator", "Milling Machine Operator",
                    "Tool & Die Maker", "CNC Machine Operator",
                    "Quality Inspector"],
        "notes": "",
        "confidence": 60,
    },
    {
        "slug": "hydraulic-technician",
        "title": "Hydraulic Technician",
        "existing": None,
        "aliases": ["Hydraulic Mechanic", "Fluid Power Technician",
                    "Hydraulic Service Engineer", "Hydraulic Fitter"],
        "industries": ["Manufacturing", "Construction equipment", "Steel",
                       "Presses"],
        "nature": "Plant floor and field, oil systems, pressure work",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Medium — hydraulic AMC and hose services",
        "tools": ["Pressure gauge set", "Hose crimping machine",
                  "Flow meter", "Seal kits", "Spanner set"],
        "relates": ["Pneumatic Technician", "Machine Maintenance Technician",
                    "Industrial Electrician", "Millwright", "Fitter"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "pneumatic-technician",
        "title": "Pneumatic Technician",
        "existing": None,
        "aliases": ["Pneumatic Mechanic", "Air System Technician",
                    "Pneumatic Service Engineer"],
        "industries": ["Manufacturing", "Packaging", "Automation"],
        "nature": "Plant floor, compressed air systems, valve and cylinder work",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Medium",
        "tools": ["Pressure gauge", "Leak detector", "Tube cutter",
                  "Fitting set", "FRL units"],
        "relates": ["Hydraulic Technician", "Compressor Technician",
                    "Industrial Automation Technician", "Machine Maintenance Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "compressor-technician",
        "title": "Compressor Technician",
        "existing": None,
        "aliases": ["Air Compressor Mechanic", "Compressor Service Engineer",
                    "Compressed Air System Technician"],
        "industries": ["Manufacturing", "Plant utilities", "Process industries"],
        "nature": "Plant utility room and field, rotating equipment",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Medium — compressor AMC services",
        "tools": ["Pressure gauge", "Vibration meter", "Oil analysis kit",
                  "Spanner set", "Filter tools"],
        "relates": ["HVAC Technician", "Diesel Mechanic", "Hydraulic Technician",
                    "Pneumatic Technician", "Millwright",
                    "Plant Utility Technician", "Refrigeration Mechanic"],
        "notes": "",
        "confidence": 55,
    },
]

#: Three document roles collapse onto one Skill. Worth naming, because it is
#: the clearest evidence that the document over-splits: `Lathe Operation` is
#: one trade with specialisations, not three careers.
COLLAPSES_ONTO_LATHE = ("lathe-machine-operator", "turner", "machinist")

#: Role 10 against a candidate already in the queue from another document.
CROSS_DOCUMENT_OVERLAP = {
    "fitter": "doc-electrician-trades-2026:machine-maintenance-technician",
}


def new_roles():
    return [r for r in ROLES if r["existing"] is None]


def merge_roles():
    return [r for r in ROLES if r["existing"] is not None]
