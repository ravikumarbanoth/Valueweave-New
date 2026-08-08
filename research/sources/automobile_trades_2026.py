#!/usr/bin/env python3
"""
The Automobile & Mobility Careers dataset, normalised.

WHAT THIS FILE IS
-----------------
A 37-page dataset covering 15 automotive and EV-service careers with a
Telangana / Andhra Pradesh focus. Fourth of the supplied documents, same
treatment: a RESEARCH SOURCE, not knowledge.

IT IS THE MOST HONEST OF THE FOUR, AND THE ONLY ONE THAT PROVES IT
-------------------------------------------------------------------
Its first page makes the same claim document C made:

    "Where data gaps exist, 'Research Gap' is noted. No statistics are
     invented."

The difference is that this one **keeps it**. `Research Gap` appears **23
times** across 37 pages. Document C's equivalent word appeared eight times
across 56. That is the first document in this batch whose stated method can be
checked against its own body and found to hold.

It still ends with the familiar admission:

    "For brevity, later role sections assumed similar thoroughness."

and the structure shows it — roles 1 and 2 have full alternative-title tables,
roles 3 onward are condensed bullets. So aliases below are drawn from the
document where it gives them and from the trade's own names where it does not,
with the difference recorded in `notes`.

Ceiling stays **60**. Marking a gap honestly is a good practice, not a
citation.

WHAT MAKES IT USEFUL
--------------------
Five roles merge onto three existing Skills, and ten are new. The graph's
automotive coverage is currently three Skills — `Automobile Mechanic
(Diesel/Petrol)`, `Two-Wheeler Mechanic`, `EV Technician` — against a sector
this document splits fifteen ways. Body repair, tyres, batteries and the
customer-facing service advisor are all absent.

A DISAGREEMENT WITH THE ELECTRICIAN DOCUMENT
---------------------------------------------
Document A lists **"Battery Technician"** as an ALIAS of EV Technician. This
document makes it role 6, a separate career with its own salary band and its
own PMKVY course.

Both readings are defensible — battery work is a specialisation, and whether a
specialisation is a career depends on whether anyone hires for it alone. The
graph has no Battery Technician entity, so the vocabulary follows document A
(the term resolves to the EV trade) while the candidate follows this document
(a reviewer gets to decide). That split is deliberate: search should not wait
on a taxonomy question, and the taxonomy question should not be settled by
whoever edited the alias list last.
"""

SOURCE = {
    "source_id": "doc-automobile-trades-2026",
    "title": ("ValueWeave Career Decision Datasets — Automobile & Mobility "
              "Careers (India, Telangana & AP focus)"),
    "kind": "DATASET",
    "origin": "LLM-generated research document, supplied by the maintainer",
    "pages": 37,
    "retrieved": "2026-08-07",
    "self_declared_limits": [
        "compiled from publicly available resources and general domain "
        "knowledge as of 2026",
        "'Research Gap' is noted where data is missing — and unlike the other "
        "documents in this batch, it actually is, 23 times",
        "later role sections are condensed 'for brevity'",
    ],
    "url": "",
}

UNVERIFIED_FIELDS = ("salary_range", "course_fees", "institute_contact",
                     "placement_claim", "employer_list")

#: Role -> the BusinessOpportunity or MSME the graph already holds. Same
#: pattern the construction document exposed: a business a reader cannot learn.
BUSINESS_WITHOUT_A_SKILL = {
    "ev-charging-station-technician": "EV Charging Station Operator",
}

#: The term this document and the electrician document disagree about.
DISPUTED_WITH_ELECTRICIAN_DOC = {
    "battery-technician": (
        "doc-electrician-trades-2026 lists 'Battery Technician' as an ALIAS of "
        "EV Technician; this document makes it a separate career with its own "
        "salary band and PMKVY course. The graph has no Battery Technician "
        "entity. Search follows the alias reading; the reviewer decides the "
        "taxonomy."),
}

ROLES = [
    {
        "slug": "automobile-mechanic",
        "title": "Automobile Mechanic",
        "existing": "Automobile Mechanic (Diesel/Petrol)",
        "aliases": ["Automotive Technician", "Motor Mechanic", "Car Mechanic",
                    "Service Technician"],
        "industries": ["Automotive Service & Repair"],
        "nature": "Hands-on, workshop floor, mechanical and electrical troubleshooting",
        "future_demand": "Steady, shifting towards EV and hybrid; reskilling needed",
        "automation_risk": "Low",
        "entrepreneurship": "High — independent garage",
        "tools": ["Spanner set", "Torque wrench", "Trolley jack",
                  "OBD scanner", "Multimeter"],
        "relates": ["Diesel Mechanic", "EV Technician", "Diagnostic Technician",
                    "Service Advisor", "Auto Electrician"],
        "notes": "",
        "confidence": 60,
    },
    {
        "slug": "diesel-mechanic",
        "title": "Diesel Mechanic",
        "existing": "Automobile Mechanic (Diesel/Petrol)",
        "aliases": ["Diesel Engine Mechanic", "Heavy Vehicle Mechanic",
                    "Power Generation Technician"],
        "industries": ["Commercial vehicles", "Generators", "Marine",
                       "Construction equipment"],
        "nature": "Workshop and field, heavy engines, fuel systems",
        "future_demand": "Steady",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Injector tester", "Compression gauge", "Torque wrench",
                  "Puller set"],
        "relates": ["Automobile Mechanic", "Heavy Vehicle Technician",
                    "Tractor Mechanic", "Machine Maintenance Technician"],
        "notes": "",
        "confidence": 60,
    },
    {
        "slug": "bike-mechanic",
        "title": "Bike Mechanic",
        "existing": "Two-Wheeler Mechanic",
        "aliases": ["Two-Wheeler Mechanic", "Scooter Mechanic",
                    "Motorcycle Mechanic"],
        "industries": ["Two-wheeler service", "Dealership workshops"],
        "nature": "Workshop, quick-turnaround service",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high — a bike shop is the lowest-capital garage",
        "tools": ["Spanner set", "Chain tool", "Bike lift", "Multimeter"],
        "relates": ["Battery Technician", "EV Scooter Technician",
                    "Tyre Technician", "Auto Electrician", "Spare Parts Retail"],
        "notes": "aliases reconstructed — the document gives no table for this role",
        "confidence": 55,
    },
    {
        "slug": "tractor-mechanic",
        "title": "Tractor Mechanic",
        "existing": None,
        "aliases": ["Farm Equipment Mechanic", "Agricultural Machinery Mechanic",
                    "Tractor Service Technician"],
        "industries": ["Agriculture", "Farm equipment dealerships"],
        "nature": "Field and workshop, heavy diesel and hydraulics",
        "future_demand": "High in both states",
        "automation_risk": "Low",
        "entrepreneurship": "High — rural service is under-supplied",
        "tools": ["Spanner set", "Hydraulic pressure gauge", "Injector tester",
                  "Puller set"],
        "relates": ["Diesel Mechanic", "Farm Equipment Service Engineer",
                    "Agri Drone Technician", "Heavy Vehicle Technician",
                    "Hydraulic Technician"],
        "notes": "aliases reconstructed — the document gives no table for this role",
        "confidence": 55,
    },
    {
        "slug": "heavy-vehicle-technician",
        "title": "Heavy Vehicle Technician",
        "existing": None,
        "aliases": ["Truck Mechanic", "Commercial Vehicle Technician",
                    "Bus Mechanic", "Fleet Technician"],
        "industries": ["Logistics", "Public transport", "Mining", "Construction"],
        "nature": "Workshop and roadside, heavy assemblies, air brakes",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Medium",
        "tools": ["Heavy spanner set", "Air brake tester", "Trolley jack",
                  "Diagnostic scanner"],
        "relates": ["Diesel Mechanic", "Automobile Mechanic", "Tractor Mechanic",
                    "Fleet Maintenance Manager"],
        "notes": "aliases reconstructed — the document gives no table for this role",
        "confidence": 55,
    },
    {
        "slug": "battery-technician",
        "title": "Battery Technician",
        "existing": None,
        "aliases": ["Automotive Battery Technician", "Battery Fitter",
                    "Battery Service Technician"],
        "industries": ["Battery manufacturers", "EV swapping stations",
                       "Dealership battery bays"],
        "nature": "Workshop and on-site, lead-acid and lithium-ion",
        "future_demand": "High — EV battery technology advancing",
        "automation_risk": "Low",
        "entrepreneurship": "Moderate — battery shop, on-site service",
        "tools": ["Battery load tester", "Hydrometer", "Multimeter",
                  "Charger", "Terminal cleaner"],
        "relates": ["EV Technician", "Battery Refurbishment Technician",
                    "BMS Technician", "Auto Electrician"],
        "notes": ("DISPUTED: doc-electrician-trades-2026 lists 'Battery "
                  "Technician' as an ALIAS of EV Technician; this document "
                  "makes it a separate career with its own salary band and a "
                  "PMKVY 'Automotive Battery Technician' course. The graph has "
                  "neither entity to settle it. Decide alongside the EV "
                  "Technician skill rather than in isolation."),
        "confidence": 50,
    },
    {
        "slug": "battery-refurbishment-technician",
        "title": "Battery Refurbishment Technician",
        "existing": None,
        "aliases": ["Battery Pack Refurbisher", "Cell Replacement Technician",
                    "Battery Reconditioning Technician"],
        "industries": ["EV aftermarket", "Battery recycling", "Swapping networks"],
        "nature": "Workshop, cell-level work, high-voltage safety",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Cell tester", "Spot welder", "Balancer", "Insulated tools"],
        "relates": ["Battery Technician", "BMS Technician", "EV Technician",
                    "Battery Recycling Technician"],
        "notes": "aliases reconstructed — the document gives no table for this role",
        "confidence": 50,
    },
    {
        "slug": "bms-technician",
        "title": "BMS Technician",
        "existing": "EV Technician",
        "aliases": ["Battery Management System Technician",
                    "BMS Diagnostic Technician"],
        "industries": ["EV OEMs", "Battery pack assembly", "EV service"],
        "nature": "Workshop and bench, electronics and firmware",
        "future_demand": "Very high",
        "automation_risk": "Low",
        "entrepreneurship": "Medium",
        "tools": ["CAN analyser", "Laptop with OEM software", "Multimeter",
                  "Cell balancer"],
        "relates": ["EV Technician", "Battery Technician",
                    "Electronics Repair Technician", "Diagnostic Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "ev-charging-station-technician",
        "title": "EV Charging Station Technician",
        "existing": None,
        "aliases": ["Charging Point Technician", "Charger Installer",
                    "EVSE Technician"],
        "industries": ["Charging networks", "EV infrastructure", "Utilities"],
        "nature": "Field-based, electrical installation and commissioning",
        "future_demand": "Very high",
        "automation_risk": "Low",
        "entrepreneurship": "High — charge point operation",
        "tools": ["Multimeter", "Earth tester", "Torque screwdriver",
                  "Insulation tester"],
        "relates": ["Electrician", "Industrial Electrician", "EV Technician",
                    "Solar PV Installer"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "tyre-technician",
        "title": "Tyre Technician",
        "existing": None,
        "aliases": ["Tyre Fitter", "Puncture Repair Technician",
                    "Tyre Service Technician", "Wheel Fitter"],
        "industries": ["Tyre retail", "Service chains", "Fleet operators"],
        "nature": "Quick-service bay, physical, customer-facing",
        "future_demand": "High — universal need",
        "automation_risk": "Very low",
        "entrepreneurship": "Very high — a tyre shop is easy to start",
        "tools": ["Tyre changer", "Wheel balancer", "Air gun",
                  "Tread depth gauge", "Puncture kit"],
        "relates": ["Wheel Alignment Technician", "Automobile Mechanic",
                    "Bike Mechanic"],
        "notes": "aliases reconstructed — the document gives no table for this role",
        "confidence": 55,
    },
    {
        "slug": "wheel-alignment-technician",
        "title": "Wheel Alignment Technician",
        "existing": None,
        "aliases": ["Alignment & Balancing Technician", "Suspension Technician",
                    "Wheel Balancing Technician"],
        "industries": ["Service chains", "Dealership workshops"],
        "nature": "Service bay, alignment rig, measurement-driven",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["3D alignment rig", "Wheel balancer", "Turn plates",
                  "Torque wrench"],
        "relates": ["Tyre Technician", "Automobile Mechanic",
                    "Suspension Specialist"],
        "notes": "aliases reconstructed — the document gives no table for this role",
        "confidence": 50,
    },
    {
        "slug": "denting-technician",
        "title": "Denting Technician",
        "existing": None,
        "aliases": ["Panel Beater", "Auto Body Repair Technician",
                    "Dent Removal Technician", "Body Shop Technician"],
        "industries": ["Body shops", "Insurance repair", "Dealership workshops"],
        "nature": "Body shop, panel work, welding and filling",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Dent puller", "Body hammer set", "Dolly", "Spot welder",
                  "Filler applicator"],
        "relates": ["Painting Technician (Automobile)", "Welder",
                    "Automobile Mechanic"],
        "notes": "aliases reconstructed — the document gives no table for this role",
        "confidence": 50,
    },
    {
        "slug": "auto-painting-technician",
        "title": "Painting Technician (Automobile)",
        "existing": None,
        "aliases": ["Automotive Refinisher", "Car Painter", "Spray Painter",
                    "Body Shop Painter"],
        "industries": ["Body shops", "Insurance repair", "Custom finishing"],
        "nature": "Spray booth, chemical handling, colour matching",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Spray gun", "Compressor", "Colour matching system",
                  "Sanding machine", "Respirator"],
        "relates": ["Denting Technician", "Painter", "Automobile Mechanic"],
        "notes": ("Distinct from the building Painter queued from "
                  "doc-electrician-trades-2026: different materials, different "
                  "booth, different certification. Do not merge them."),
        "confidence": 50,
    },
    {
        "slug": "service-advisor",
        "title": "Service Advisor",
        "existing": None,
        "aliases": ["Service Consultant", "Workshop Advisor",
                    "Customer Service Advisor (Automotive)"],
        "industries": ["Dealerships", "Multi-brand workshops", "EV service centres"],
        "nature": "Customer-facing, job cards, estimates, upselling",
        "future_demand": "High — high attrition, always hiring",
        "automation_risk": "Moderate — chatbots book, trust still needs a person",
        "entrepreneurship": "Medium — a route to service franchise ownership",
        "tools": ["Dealer management software", "Tablet", "Job card system"],
        "relates": ["Automobile Mechanic", "Diagnostic Technician",
                    "Workshop Manager"],
        "notes": ("The only non-manual role in this document. Worth keeping "
                  "distinct: it is the one automotive career reachable by "
                  "someone who cannot do heavy physical work."),
        "confidence": 55,
    },
    {
        "slug": "diagnostic-technician",
        "title": "Diagnostic Technician",
        "existing": "EV Technician",
        "aliases": ["Automotive Diagnostic Technician", "Master Technician",
                    "Electronics Diagnostic Technician"],
        "industries": ["Dealerships", "EV service", "Multi-brand workshops"],
        "nature": "Workshop, scan tools and fault trees, electronics-led",
        "future_demand": "Very high",
        "automation_risk": "Low",
        "entrepreneurship": "Medium",
        "tools": ["OEM scan tool", "Oscilloscope", "CAN analyser",
                  "Laptop with diagnostic software"],
        "relates": ["Automobile Mechanic", "EV Service Technician",
                    "Service Advisor", "Electronics Technician",
                    "Automotive Embedded Engineer"],
        "notes": "",
        "confidence": 55,
    },
]


def new_roles():
    return [r for r in ROLES if r["existing"] is None]


def merge_roles():
    return [r for r in ROLES if r["existing"] is not None]


def businesses_without_a_skill():
    return {r["slug"]: BUSINESS_WITHOUT_A_SKILL[r["slug"]]
            for r in ROLES if r["slug"] in BUSINESS_WITHOUT_A_SKILL}
