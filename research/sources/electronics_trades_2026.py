#!/usr/bin/env python3
"""
The Electrical & Electronics careers dataset, normalised.

WHAT THIS FILE IS
-----------------
A 28-page dataset covering 15 electronics-service and low-voltage careers with
a Telangana / Andhra Pradesh focus. Fifth of the supplied documents, same
treatment: a RESEARCH SOURCE, not knowledge.

THE BOLDEST CLAIM AND THE THINNEST SELF-AUDIT
----------------------------------------------
It closes with a self-assessment the other four do not attempt:

    "Confidence Level: High. Salary ranges reflect 2025-2026 Indian market
     realities for tier-1/tier-2 cities in TS/AP."
    "Research Gaps: Exact district-wise hiring numbers for private local
     integrators are not centrally tracked."
    "Graph Optimization: Headings and sub-bullets are standardized for
     automated JSON/Knowledge Graph extraction."

The third line is the interesting one — the author wrote this expecting a
pipeline like ours to read it, and the structure is genuinely the cleanest of
the five: every role has the same headings in the same order, which is why the
extraction above needed no per-role special cases.

The first two are the problem. It declares **high** confidence and flags
exactly **one** research gap across 15 roles — the boldest claim in the batch
paired with the least self-auditing. Compare document D, which made a weaker
claim and marked 23 gaps in 37 pages.

Well-structured is not the same as well-sourced. A document that is easy to
parse invites you to trust it, which is precisely when to check. Ceiling stays
**60**.

THE FIRST DOCUMENT WITH NO COPY-PASTE DEFECT
---------------------------------------------
Documents B and C each carried a role whose alternative titles belonged to its
neighbour. This one does not: all fifteen roles have distinct, appropriate
alias lists. Worth recording, because after three occurrences the defect looked
systemic and it turns out not to be universal.

One mild inconsistency remains: **"Security System Installer" is listed as an
alt title of role 1 (CCTV Technician) and is also role 4** — with its own
distinct aliases, "Physical Security Technician, Access Control Tech". Reading
both, role 1 is surveillance and role 4 is access control; they overlap in the
field and are distinguishable. Recorded in role 4's `notes` rather than
resolved, because which way a Telangana integrator splits the work is a
question for a person who has hired one.

FOUR ROLES ARE ONE SKILL
-------------------------
Mobile Phone Repair, Laptop Repair, LED TV Repair and Electronics Service
Technician all map onto `Electronics Repair & Maintenance`. The same
over-splitting document C showed with the lathe trades — the document sells
specialisations as careers, and the graph is right to hold one skill.
"""

SOURCE = {
    "source_id": "doc-electronics-trades-2026",
    "title": ("ValueWeave Career Decision Datasets — Electrical & Electronics "
              "(India, Telangana & AP focus)"),
    "kind": "DATASET",
    "origin": "LLM-generated research document, supplied by the maintainer",
    "pages": 28,
    "retrieved": "2026-08-07",
    "self_declared_limits": [
        "self-assessed 'Confidence Level: High' — the boldest claim of the "
        "five documents, paired with exactly ONE flagged research gap across "
        "15 roles",
        "district-wise hiring numbers for private integrators are not "
        "centrally tracked, so demand figures are macro-industry estimates",
    ],
    "url": "",
}

UNVERIFIED_FIELDS = ("salary_range", "course_fees", "institute_contact",
                     "placement_claim", "employer_list")

#: Four roles onto one Skill. Named for the same reason as document C's lathe
#: collapse: it is the clearest evidence the document over-splits.
COLLAPSES_ONTO_ELECTRONICS_REPAIR = (
    "mobile-phone-repair-technician", "laptop-repair-technician",
    "led-tv-repair-technician", "electronics-service-technician")

ROLES = [
    {
        "slug": "cctv-technician",
        "title": "CCTV Technician",
        "existing": None,
        "aliases": ["Surveillance Technician", "CCTV Installer",
                    "Security Camera Technician"],
        "industries": ["Security & Surveillance", "IT", "Retail", "Real Estate"],
        "nature": "Fieldwork, commercial and residential sites, cabling and configuration",
        "future_demand": "High — Safe City projects, retail, IT parks",
        "automation_risk": "Low",
        "entrepreneurship": "Very high",
        "tools": ["Crimping tool", "Cable tester", "Drill", "Ladder",
                  "Laptop for NVR configuration", "PoE injector"],
        "relates": ["Security System Installer", "Networking Technician",
                    "Fire Alarm Technician", "Electrician"],
        "notes": ("'Security System Installer' is dropped from this role's "
                  "alias list: the document also makes it role 4 with its own "
                  "distinct aliases. See that role's notes."),
        "confidence": 55,
    },
    {
        "slug": "fire-alarm-technician",
        "title": "Fire Alarm Technician",
        "existing": None,
        "aliases": ["Life Safety Technician", "Fire Panel Engineer",
                    "Fire Detection Technician"],
        "industries": ["Building safety", "Facility management", "Construction"],
        "nature": "Fieldwork, panel wiring, statutory testing",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High — AMC contracts",
        "tools": ["Multimeter", "Smoke tester", "Panel programmer",
                  "Cable tester"],
        "relates": ["CCTV Technician", "Security System Installer",
                    "Electrician", "Building Automation Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "home-automation-technician",
        "title": "Home Automation Technician",
        "existing": "IoT Systems Development",
        "aliases": ["Smart Home Integrator", "IoT Technician",
                    "Smart Building Technician"],
        "industries": ["Residential interiors", "Smart buildings", "IoT"],
        "nature": "Fieldwork, configuration, app and hub setup",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Laptop", "Wi-Fi analyser", "Multimeter", "Crimping tool"],
        "relates": ["Electrician", "Networking Technician", "CCTV Technician",
                    "Building Automation Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "security-system-installer",
        "title": "Security System Installer",
        "existing": None,
        "aliases": ["Physical Security Technician", "Access Control Technician",
                    "Biometric System Installer"],
        "industries": ["Security & Surveillance", "Commercial buildings"],
        "nature": "Fieldwork, access control, door hardware and wiring",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high",
        "tools": ["Crimping tool", "Drill", "Multimeter", "Programming laptop"],
        "relates": ["CCTV Technician", "Fire Alarm Technician",
                    "Networking Technician", "Electrician"],
        "notes": ("OVERLAPS ROLE 1: the document also lists 'Security System "
                  "Installer' as an alt title of CCTV Technician. Reading both "
                  "sets of aliases, role 1 is surveillance and this is access "
                  "control — distinguishable but adjacent. Whether a local "
                  "integrator splits the work this way is a question for "
                  "somebody who has hired one; decide the two together."),
        "confidence": 45,
    },
    {
        "slug": "mobile-phone-repair-technician",
        "title": "Mobile Phone Repair Technician",
        "existing": "Electronics Repair & Maintenance",
        "aliases": ["Mobile Service Engineer", "Handset Technician",
                    "Phone Repair Technician"],
        "industries": ["Consumer electronics service", "Retail repair"],
        "nature": "Bench work, micro-soldering, screen and battery replacement",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high — the lowest-capital electronics shop",
        "tools": ["Precision screwdriver set", "Hot air rework station",
                  "Microscope", "Multimeter", "Opening tools"],
        "relates": ["Laptop Repair Technician", "PCB Repair Technician",
                    "Electronics Service Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "laptop-repair-technician",
        "title": "Laptop Repair Technician",
        "existing": "Electronics Repair & Maintenance",
        "aliases": ["Laptop Service Engineer", "IT Hardware Technician",
                    "Computer Hardware Technician"],
        "industries": ["IT service", "Retail repair", "Corporate AMC"],
        "nature": "Bench work, board-level and component replacement",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high",
        "tools": ["Precision screwdriver set", "Hot air rework station",
                  "Multimeter", "Thermal paste", "Diagnostic software"],
        "relates": ["Mobile Phone Repair Technician", "PCB Repair Technician",
                    "Networking Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "led-tv-repair-technician",
        "title": "LED TV Repair Technician",
        "existing": "Electronics Repair & Maintenance",
        "aliases": ["Consumer Electronics Technician", "TV Service Technician",
                    "Display Repair Technician"],
        "industries": ["Consumer electronics service", "Brand service centres"],
        "nature": "Bench and on-site, panel and power board work",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high",
        "tools": ["Multimeter", "Soldering station", "Panel tester",
                  "Screwdriver set"],
        "relates": ["Electronics Service Technician", "PCB Repair Technician",
                    "Mobile Phone Repair Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "inverter-technician",
        "title": "Inverter Technician",
        "existing": None,
        "aliases": ["Power Electronics Technician", "Home Inverter Technician",
                    "Battery Backup Technician"],
        "industries": ["Power backup", "Consumer electronics", "Retail service"],
        "nature": "On-site and bench, batteries and power boards",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high",
        "tools": ["Multimeter", "Soldering station", "Battery load tester",
                  "Hydrometer"],
        "relates": ["UPS Technician", "Solar Inverter Technician",
                    "Electronics Service Technician", "Electrician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "ups-technician",
        "title": "UPS Technician",
        "existing": None,
        "aliases": ["Critical Power Technician", "UPS Service Engineer",
                    "Power Backup Technician"],
        "industries": ["Data centres", "Hospitals", "Corporate AMC", "Industry"],
        "nature": "On-site, critical systems, scheduled maintenance",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High — AMC contracts",
        "tools": ["Multimeter", "Battery load tester", "Clamp meter",
                  "Thermal camera"],
        "relates": ["Inverter Technician", "Industrial Electrician",
                    "Electronics Service Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "solar-inverter-technician",
        "title": "Solar Inverter Technician",
        "existing": "Solar Panel Installation & Maintenance",
        "aliases": ["Solar Power Technician", "Renewable Energy Technician",
                    "PV Inverter Technician"],
        "industries": ["Rooftop solar", "Renewable EPC"],
        "nature": "On-site, string configuration, grid tie and monitoring",
        "future_demand": "Very high",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Multimeter", "Clamp meter", "Insulation tester",
                  "Laptop for inverter configuration"],
        "relates": ["Solar PV Installer", "Inverter Technician", "Electrician",
                    "Industrial Electrician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "pcb-repair-technician",
        "title": "PCB Repair Technician",
        "existing": "PCB Assembly & Soldering",
        "aliases": ["SMT Technician", "Component Level Technician",
                    "Board Repair Technician", "Chip Level Technician"],
        "industries": ["Electronics manufacturing", "Repair service", "EMS"],
        "nature": "Bench, microscope, rework and component replacement",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Hot air rework station", "Microscope", "Soldering station",
                  "Multimeter", "Reflow oven"],
        "relates": ["Mobile Phone Repair Technician", "Laptop Repair Technician",
                    "Electronics Service Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "electronics-service-technician",
        "title": "Electronics Service Technician",
        "existing": "Electronics Repair & Maintenance",
        "aliases": ["Multi-skilled Electronics Technician",
                    "Appliance Service Technician"],
        "industries": ["Consumer electronics", "Brand service centres", "AMC"],
        "nature": "Bench and on-site, mixed appliance work",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "Very high",
        "tools": ["Multimeter", "Soldering station", "Screwdriver set",
                  "Oscilloscope"],
        "relates": ["Mobile Phone Repair Technician", "LED TV Repair Technician",
                    "Inverter Technician", "PCB Repair Technician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "networking-technician",
        "title": "Networking Technician",
        "existing": None,
        "aliases": ["Field Network Technician", "LAN Technician",
                    "Structured Cabling Technician"],
        "industries": ["IT services", "ISPs", "Corporate IT", "System integrators"],
        "nature": "Fieldwork, cabling, switch and router configuration",
        "future_demand": "High",
        "automation_risk": "Low",
        "entrepreneurship": "High",
        "tools": ["Crimping tool", "Cable tester", "Punch-down tool",
                  "Laptop", "Toner probe"],
        "relates": ["Fiber Optic Technician", "CCTV Technician",
                    "Laptop Repair Technician", "Telecom Tower Technician"],
        "notes": ("The document's alias list includes 'Network Engineer', "
                  "dropped here: an engineer designs the network and a "
                  "technician installs it, and conflating them would send a "
                  "10th-pass reader to a degree-entry job."),
        "confidence": 55,
    },
    {
        "slug": "fiber-optic-technician",
        "title": "Fiber Optic Technician",
        "existing": None,
        "aliases": ["OFC Technician", "Splicer", "Fibre Splicing Technician",
                    "FTTH Technician"],
        "industries": ["Telecom", "ISPs", "BharatNet", "Cable operators"],
        "nature": "Fieldwork, splicing, trenching and testing",
        "future_demand": "Very high — fibre rollout across both states",
        "automation_risk": "Low",
        "entrepreneurship": "High — splicing contracts",
        "tools": ["Fusion splicer", "OTDR", "Power meter", "Cleaver",
                  "Fibre stripper"],
        "relates": ["Networking Technician", "Telecom Tower Technician",
                    "Cable Jointer", "Electrician"],
        "notes": "",
        "confidence": 55,
    },
    {
        "slug": "telecom-tower-technician",
        "title": "Telecom Tower Technician",
        "existing": None,
        "aliases": ["Tower Rigger", "Telecom Field Technician",
                    "BTS Technician", "Tower Climber"],
        "industries": ["Telecom infrastructure", "Tower companies", "5G rollout"],
        "nature": "At height, safety critical, outdoor, on-call",
        "future_demand": "Very high — 5G densification",
        "automation_risk": "Low",
        "entrepreneurship": "Medium",
        "tools": ["Safety harness", "Torque wrench", "Spectrum analyser",
                  "Power meter", "Climbing gear"],
        "relates": ["Fiber Optic Technician", "Networking Technician",
                    "Scaffolding Technician", "Industrial Electrician"],
        "notes": "",
        "confidence": 55,
    },
]


def new_roles():
    return [r for r in ROLES if r["existing"] is None]


def merge_roles():
    return [r for r in ROLES if r["existing"] is not None]
