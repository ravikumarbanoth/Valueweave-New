#!/usr/bin/env python3
"""
The reviewer's map of the 52 queued trade candidates.

WHY THIS FILE EXISTS AND WHAT IT IS NOT
----------------------------------------
It is NOT an approval, and it creates nothing. Every one of the 52 candidates
stays `NEEDS_REVIEW` in `collection/state/review_queue.jsonl` until a named
person decides it through `collection.cli`. Nothing here writes a package row,
an entity, or a relationship.

What it IS: the output of the consolidated five-document review, written down
where it can be checked instead of in a document where it can rot. A reviewer
opening the queue cold sees 52 rows of equal weight. Nineteen of those rows are
really eight decisions, one row is a rejection, four need a person rather than
a source, and eighteen share a single root cause that no amount of reviewing
will fix. That shape is the useful part, and it took measurement to find.

THE FIVE CLASSES
----------------
A  likely MERGE into an existing entity once a primary source confirms it
B  likely requires a NEW Skill entity
C  DUPLICATE — decide together with the rest of its group, not one at a time
D  DISPUTED — the sources contradict each other or themselves; needs a person
E  REJECT — should not become an entity

"Likely" is load-bearing. A and B are predictions about what a reviewer will
conclude after checking a primary source, not permission to skip the check.

WHAT MAY NOT BE PROMOTED FROM THESE DOCUMENTS, EVER
----------------------------------------------------
Salaries, course fees, institute contacts, placement claims, employer names and
demand estimates. Five LLM-generated secondary documents, zero citations. The
role NAMES and the ALIASES are observable facts about how words are used and
were verifiable here; the numbers are claims about the world and are not.
`UNVERIFIED_FIELDS` in each source module names them so the promoter blanks
them mechanically rather than relying on somebody to remember.
"""

MERGE, NEW, DUPLICATE, DISPUTED, REJECT = "A", "B", "C", "D", "E"

CLASSES = {
    MERGE: "likely merge into an existing entity after primary-source check",
    NEW: "likely requires a new Skill entity",
    DUPLICATE: "duplicate — decide with its group",
    DISPUTED: "disputed — requires a human decision",
    REJECT: "reject — should not become an entity",
}

#: The eight groups the consolidated review found. Reviewing by group turns 52
#: decisions into roughly 38 and — the actual point — stops the same trade
#: being approved twice under two names, which the deduper cannot catch because
#: it keys on the role slug and these groups have different slugs.
DUPLICATE_GROUPS = {
    "maintenance-fitter": {
        "members": ("doc-electrician-trades-2026:machine-maintenance-technician",
                    "doc-manufacturing-trades-2026:fitter"),
        "why": ("both carry the aliases 'maintenance fitter' and 'mechanical "
                "fitter'. The same trade under two titles in two documents; "
                "the deduper keys on the slug and saw two different ones."),
        "primary_source": "DGT/NCVT ITI trade list — Fitter",
    },
    "false-ceiling": {
        "members": ("doc-construction-trades-2026:false-ceiling-installer",
                    "doc-construction-trades-2026:pop-gypsum-technician"),
        "why": ("both pair to the same existing business, 'POP Works / False "
                "Ceiling Installation'. A duplicate inside one document."),
        "primary_source": "CSDCI QP list — False Ceiling Installer / Gypsum Plasterer",
    },
    "fenestration": {
        "members": ("doc-construction-trades-2026:aluminium-fabricator",
                    "doc-construction-trades-2026:upvc-window-installer",
                    "doc-construction-trades-2026:glass-installer"),
        "why": ("one fenestration trade family. The source module records the "
                "copy-paste defect that pasted uPVC alternative titles onto "
                "the aluminium role, which is how the overlap surfaced."),
        "primary_source": "CSDCI QP list — Aluminium Fabricator / Glazier",
    },
    "plant-operator": {
        "members": ("doc-construction-trades-2026:road-equipment-operator",
                    "doc-construction-trades-2026:excavator-operator",
                    "doc-construction-trades-2026:crane-operator"),
        "why": ("all three resolve to the same Industry today and all three "
                "are plant, not personal tools — the distinction the source "
                "module already records."),
        "primary_source": "Infrastructure Equipment Skill Council (IESC) QP list",
    },
    "fluid-power": {
        "members": ("doc-manufacturing-trades-2026:hydraulic-technician",
                    "doc-manufacturing-trades-2026:pneumatic-technician",
                    "doc-manufacturing-trades-2026:compressor-technician"),
        "why": ("one fluid-power family. A `fluid-power` concept was written "
                "for exactly this group during document C and deleted for "
                "making search worse — the trades are real, the anchor was not."),
        "primary_source": "Capital Goods & Strategic Skill Council QP list",
    },
    "battery": {
        "members": ("doc-automobile-trades-2026:battery-technician",
                    "doc-automobile-trades-2026:battery-refurbishment-technician"),
        "why": ("adjacent bench work on the same component. The first member "
                "is additionally DISPUTED between documents A and D."),
        "primary_source": "ASDC QP list — Automotive Battery Technician",
    },
    "tyre-and-alignment": {
        "members": ("doc-automobile-trades-2026:tyre-technician",
                    "doc-automobile-trades-2026:wheel-alignment-technician"),
        "why": "same bay, same equipment, usually the same person.",
        "primary_source": "ASDC QP list — Tyre Service Technician",
    },
    "physical-security": {
        "members": ("doc-electronics-trades-2026:cctv-technician",
                    "doc-electronics-trades-2026:security-system-installer"),
        "why": ("document E lists 'Security System Installer' as BOTH an "
                "alternative title of CCTV Technician and a role in its own "
                "right. Surveillance versus access control — adjacent, and "
                "the document does not resolve it."),
        "primary_source": "ESSCI QP list — CCTV Installation Technician",
    },
}

#: Pairs that share a word and must NOT be merged. Recorded because the
#: pressure runs the other way: a reviewer working through a long queue merges
#: to make it shorter, and both of these look mergeable from the title alone.
KEEP_DISTINCT = {
    ("doc-electrician-trades-2026:painter",
     "doc-automobile-trades-2026:auto-painting-technician"):
        ("A building painter and an automotive refinisher share a word and "
         "nothing else — different materials, different booth, different "
         "certification, different customer. Search currently returns "
         "'Painting Services' for both, which is the conflation document D's "
         "module explicitly forbids; promoting them must fix that, not "
         "ratify it."),
    ("doc-electrician-trades-2026:fabricator",
     "doc-construction-trades-2026:aluminium-fabricator"):
        ("Steel fabrication and aluminium fenestration are different metals, "
         "different joining methods and different sites. The shared word is "
         "the only thing they have in common."),
}

#: Every one of the 52, with the reason and the source that would settle it.
#: `merge_target` is filled only for class A and names an entity that is in the
#: graph today — a target that does not exist is the kind of claim this whole
#: pipeline is built to prevent, and a test checks each one against entities.csv.
CANDIDATES = {
    # ---- document A · Electrician & Allied Trades ----------------------
    "doc-electrician-trades-2026:lift-technician": {
        "cls": NEW, "merge_target": None,
        "why": "no comparable entity; lift work is licensed separately",
        "primary_source": "Telangana Lifts & Escalators Act licensing; NCO-2015",
    },
    "doc-electrician-trades-2026:tile-marble-fixer": {
        "cls": MERGE, "merge_target": "Tiles Fixing (Tile Mason)",
        "why": "search already resolves the trade's words here",
        "primary_source": "CSDCI QP list; DGT ITI Marble Mason",
    },
    "doc-electrician-trades-2026:fabricator": {
        "cls": MERGE, "merge_target": "Welding (MIG/TIG/Arc)",
        "why": "structural fabrication is the welding trade in the graph",
        "primary_source": "DGT/NCVT ITI trade list — Sheet Metal Worker, Fitter",
    },
    "doc-electrician-trades-2026:painter": {
        "cls": NEW, "merge_target": None,
        "why": ("'Painting Services' exists as a business a person could run "
                "with no Skill entity teaching the trade; keep distinct from "
                "the automotive refinisher"),
        "primary_source": "DGT/NCVT ITI trade list — Painter (General)",
    },
    "doc-electrician-trades-2026:steel-fixer": {
        "cls": MERGE, "merge_target": "Masonry & Brickwork",
        "why": ("search resolves it here today. CSDCI lists a separate Bar "
                "Bender & Steel Fixer QP, so a reviewer may upgrade this to a "
                "new Skill — that is the check, not a formality"),
        "primary_source": "CSDCI QP list — Bar Bender & Steel Fixer",
    },
    "doc-electrician-trades-2026:scaffolding-technician": {
        "cls": NEW, "merge_target": None,
        "why": "work at height with its own safety certification",
        "primary_source": "CSDCI QP list — Scaffolder",
    },
    "doc-electrician-trades-2026:machine-maintenance-technician": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `maintenance-fitter`",
        "primary_source": "DGT/NCVT ITI trade list — Fitter",
    },
    "doc-electrician-trades-2026:mechatronics-technician": {
        "cls": NEW, "merge_target": None,
        "why": "a named ITI trade with no entity in the graph",
        "primary_source": "DGT/NCVT ITI trade list — Mechatronics",
    },

    # ---- document B · Construction & Infrastructure ---------------------
    "doc-construction-trades-2026:false-ceiling-installer": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `false-ceiling`",
        "primary_source": "CSDCI QP list — False Ceiling Installer",
    },
    "doc-construction-trades-2026:pop-gypsum-technician": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `false-ceiling`",
        "primary_source": "CSDCI QP list — Gypsum Plasterer",
    },
    "doc-construction-trades-2026:aluminium-fabricator": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `fenestration`; keep distinct from document A's Fabricator",
        "primary_source": "CSDCI QP list — Aluminium Fabricator",
    },
    "doc-construction-trades-2026:upvc-window-installer": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `fenestration`",
        "primary_source": "CSDCI QP list",
    },
    "doc-construction-trades-2026:glass-installer": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `fenestration`",
        "primary_source": "CSDCI QP list — Glazier",
    },
    "doc-construction-trades-2026:waterproofing-technician": {
        "cls": NEW, "merge_target": None,
        "why": ("no waterproofing entity of any kind; the words currently "
                "resolve to 'Painting Services', which is a different trade"),
        "primary_source": "CSDCI QP list — Waterproofing Applicator",
    },
    "doc-construction-trades-2026:borewell-technician": {
        "cls": NEW, "merge_target": None,
        "why": "'Borewell Drilling Services' exists as a business, not a skill",
        "primary_source": "IESC QP list; NCO-2015 Water Well Driller",
    },
    "doc-construction-trades-2026:pump-technician": {
        "cls": NEW, "merge_target": None,
        "why": ("'Submersible Pump Installation & Repair' exists as a "
                "business, not a skill"),
        "primary_source": "Indian Plumbing Skills Council; NCO-2015",
    },
    "doc-construction-trades-2026:roofing-technician": {
        "cls": NEW, "merge_target": None,
        "why": ("no roofing entity; the words resolve to 'Welding & Metal "
                "Fabrication', an accepted approximation and not the trade"),
        "primary_source": "CSDCI QP list — Roofer",
    },
    "doc-construction-trades-2026:modular-kitchen-installer": {
        "cls": MERGE, "merge_target": "Carpentry",
        "why": "fitted joinery; search already resolves it here",
        "primary_source": "Furniture & Fittings Skill Council QP list",
    },
    "doc-construction-trades-2026:interior-finishing-technician": {
        "cls": DISPUTED, "merge_target": None,
        "why": ("the document presents it as a role, but 'interior finishing' "
                "reads as an umbrella over false ceiling, painting, tiling "
                "and joinery — all of which it also queues separately. "
                "Whether this is a trade or a category is a judgement, not a "
                "lookup, and getting it wrong creates a sector-shaped entity"),
        "primary_source": "CSDCI QP list; NCO-2015",
    },
    "doc-construction-trades-2026:granite-cutter": {
        "cls": MERGE, "merge_target": "Tiles Fixing (Tile Mason)",
        "why": "stone finishing; search resolves it here",
        "primary_source": "CSDCI QP list; NCO-2015 Stone Cutter",
    },
    "doc-construction-trades-2026:road-equipment-operator": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `plant-operator`",
        "primary_source": "IESC QP list",
    },
    "doc-construction-trades-2026:excavator-operator": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `plant-operator`",
        "primary_source": "IESC QP list — Excavator Operator",
    },
    "doc-construction-trades-2026:crane-operator": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `plant-operator`",
        "primary_source": "IESC QP list — Crane Operator",
    },

    # ---- document C · Manufacturing & Factory ---------------------------
    "doc-manufacturing-trades-2026:milling-machine-operator": {
        "cls": MERGE, "merge_target": "Lathe Operation",
        "why": ("the same machine-shop skill the document already over-split "
                "three ways onto this entity"),
        "primary_source": "DGT/NCVT ITI trade list — Machinist",
    },
    "doc-manufacturing-trades-2026:injection-moulding-operator": {
        "cls": NEW, "merge_target": None,
        "why": "plastics processing; nothing comparable in the graph",
        "primary_source": "CIPET / Plastics Sector Skill Council QP list",
    },
    "doc-manufacturing-trades-2026:press-machine-operator": {
        "cls": NEW, "merge_target": None,
        "why": ("'Sheet Metal Fabrication Unit' is an MSME, not a skill"),
        "primary_source": "Capital Goods & Strategic Skill Council QP list",
    },
    "doc-manufacturing-trades-2026:quality-inspector": {
        "cls": NEW, "merge_target": None,
        "why": ("a shop-floor inspection role; the only near name in the "
                "graph is an AI tooling Industry, which is not the job"),
        "primary_source": "Capital Goods & Strategic Skill Council QP list",
    },
    "doc-manufacturing-trades-2026:production-operator": {
        "cls": REJECT, "merge_target": None,
        "why": ("sector-shaped rather than a defined trade. Search returns "
                "'Manufacturing' for it, which is the honest answer: the term "
                "names an industry position, not a skill anybody teaches or "
                "certifies. Creating it would repeat the §11 mistake at the "
                "entity layer instead of the concept layer"),
        "primary_source": "n/a — rejected on definition, not on evidence",
    },
    "doc-manufacturing-trades-2026:assembly-line-technician": {
        "cls": NEW, "merge_target": None,
        "why": "assembly work is a named QP even though the title is broad",
        "primary_source": "CGSC / ASDC QP list — Assembly Operator",
    },
    "doc-manufacturing-trades-2026:tool-and-die-maker": {
        "cls": NEW, "merge_target": None,
        "why": ("'Tool and Die Making Unit' exists as an MSME with no skill "
                "that teaches it; a named ITI trade"),
        "primary_source": "DGT/NCVT ITI trade list — Tool & Die Maker",
    },
    "doc-manufacturing-trades-2026:fitter": {
        "cls": DUPLICATE, "merge_target": None,
        "why": ("group `maintenance-fitter`. Independently the largest ITI "
                "trade in India, and search currently answers it with "
                "'Filter Press'"),
        "primary_source": "DGT/NCVT ITI trade list — Fitter",
    },
    "doc-manufacturing-trades-2026:hydraulic-technician": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `fluid-power`",
        "primary_source": "Capital Goods & Strategic Skill Council QP list",
    },
    "doc-manufacturing-trades-2026:pneumatic-technician": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `fluid-power`",
        "primary_source": "Capital Goods & Strategic Skill Council QP list",
    },
    "doc-manufacturing-trades-2026:compressor-technician": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `fluid-power`",
        "primary_source": "Capital Goods & Strategic Skill Council QP list",
    },

    # ---- document D · Automobile & Mobility -----------------------------
    "doc-automobile-trades-2026:tractor-mechanic": {
        "cls": NEW, "merge_target": None,
        "why": ("search sends it to the car trade, which is an acceptable "
                "approximation and not the job; DGT treats it as its own trade"),
        "primary_source": "DGT/NCVT ITI trade list — Mechanic Tractor",
    },
    "doc-automobile-trades-2026:heavy-vehicle-technician": {
        "cls": MERGE, "merge_target": "Automobile Mechanic (Diesel/Petrol)",
        "why": ("the graph's entity already names diesel; commercial-vehicle "
                "work is the same trade at a larger scale"),
        "primary_source": "ASDC QP list — Commercial Vehicle Technician",
    },
    "doc-automobile-trades-2026:battery-technician": {
        "cls": DISPUTED, "merge_target": None,
        "why": ("document A lists it as an ALIAS of EV Technician; document D "
                "makes it a career with its own course. Both readings are "
                "defensible and the graph has no entity to settle it. Search "
                "follows A today, the candidate follows D — deliberately, so "
                "that a taxonomy question is not decided by whichever alias "
                "list was edited last. Also in group `battery`"),
        "primary_source": "ASDC QP list — Automotive Battery Technician",
    },
    "doc-automobile-trades-2026:battery-refurbishment-technician": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `battery`",
        "primary_source": "ASDC QP list",
    },
    "doc-automobile-trades-2026:ev-charging-station-technician": {
        "cls": NEW, "merge_target": None,
        "why": ("'EV Charging Station Operator' exists as an MSME with no "
                "skill that teaches the installation and service work"),
        "primary_source": "ASDC QP list",
    },
    "doc-automobile-trades-2026:tyre-technician": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `tyre-and-alignment`",
        "primary_source": "ASDC QP list — Tyre Service Technician",
    },
    "doc-automobile-trades-2026:wheel-alignment-technician": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `tyre-and-alignment`",
        "primary_source": "ASDC QP list",
    },
    "doc-automobile-trades-2026:denting-technician": {
        "cls": NEW, "merge_target": None,
        "why": "panel beating is a named ITI trade with no entity",
        "primary_source": "DGT/NCVT ITI trade list — Mechanic Auto Body Repair",
    },
    "doc-automobile-trades-2026:auto-painting-technician": {
        "cls": DISPUTED, "merge_target": None,
        "why": ("must stay distinct from document A's building Painter — the "
                "source module says so explicitly. Search disagrees: it "
                "returns 'Painting Services' for both today. A person has to "
                "confirm the split and accept that promoting it requires "
                "re-pointing the `painter` vocabulary, not just adding a row"),
        "primary_source": "DGT/NCVT ITI trade list — Mechanic Auto Body Painting",
    },
    "doc-automobile-trades-2026:service-advisor": {
        "cls": NEW, "merge_target": None,
        "why": ("the only non-manual role in 205 pages — the one automotive "
                "career open to somebody who cannot do heavy physical work, "
                "and the graph has nothing like it"),
        "primary_source": "ASDC QP list — Service Advisor",
    },

    # ---- document E · Electrical & Electronics --------------------------
    "doc-electronics-trades-2026:cctv-technician": {
        "cls": DUPLICATE, "merge_target": None,
        "why": "group `physical-security`",
        "primary_source": "ESSCI QP list — CCTV Installation Technician",
    },
    "doc-electronics-trades-2026:fire-alarm-technician": {
        "cls": NEW, "merge_target": None,
        "why": "life-safety work; statutory testing is part of the job",
        "primary_source": ("ESSCI QP list AND Telangana / Andhra Pradesh Fire "
                           "Services licensing — two authorities, check both"),
    },
    "doc-electronics-trades-2026:security-system-installer": {
        "cls": DISPUTED, "merge_target": None,
        "why": ("the document contradicts itself — this is both role 4 and an "
                "alternative title of role 1. Whether a local integrator "
                "splits surveillance from access control is a question for "
                "somebody who has hired one. Also in group `physical-security`"),
        "primary_source": "ESSCI QP list",
    },
    "doc-electronics-trades-2026:inverter-technician": {
        "cls": NEW, "merge_target": None,
        "why": ("power-backup service; adjacent to UPS Technician but a "
                "domestic rather than a critical-systems trade — flagged for "
                "the reviewer without being grouped, because the review that "
                "produced these groups did not examine the pair"),
        "primary_source": "ESSCI QP list — Power Electronics",
    },
    "doc-electronics-trades-2026:ups-technician": {
        "cls": NEW, "merge_target": None,
        "why": "critical-power service under AMC; see Inverter Technician",
        "primary_source": "ESSCI QP list",
    },
    "doc-electronics-trades-2026:networking-technician": {
        "cls": NEW, "merge_target": None,
        "why": ("structured cabling and switch work; the document's 'Network "
                "Engineer' alias was refused because that is a degree-entry job"),
        "primary_source": "ESSCI / TSSC QP list — Network Technician",
    },
    "doc-electronics-trades-2026:fiber-optic-technician": {
        "cls": NEW, "merge_target": None,
        "why": "splicing is a distinct certified skill with its own equipment",
        "primary_source": "TSSC QP list — Optical Fibre Splicer",
    },
    "doc-electronics-trades-2026:telecom-tower-technician": {
        "cls": NEW, "merge_target": None,
        "why": "work at height, safety critical, its own certification",
        "primary_source": "TSSC QP list — Tower Technician",
    },
}

#: ---------------------------------------------------------------------------
#: RESEARCH GAP · the Field Technician ranking magnet
#: ---------------------------------------------------------------------------
#: Eighteen of the 52 queued careers — better than a third — return the SAME
#: unrelated row as their top search result:
#:
#:     Field Technician - Computing & Peripherals - ELE/Q4601   [Certification]
#:
#: This is not a vocabulary problem and MUST NOT be fixed with aliases. Every
#: one of these is a trade with no Skill entity to point at; an alias would
#: only move the wrong answer somewhere else, which is the confidently-wrong
#: failure §11 records making and §17 records repeating. It is a KNOWLEDGE
#: COVERAGE problem: the graph has nothing to return, and one broad
#: certification wins by default because it contains the word "Technician".
#:
#: It resolves as the queue resolves. Each candidate promoted to a Skill takes
#: its queries off this list. Whatever remains afterwards is a ranking question
#: — why one Certification outranks everything for a bare occupational suffix —
#: and belongs in the search backlog, not here.
FIELD_TECHNICIAN_MAGNET = {
    "entity": "Field Technician - Computing & Peripherals - ELE/Q4601",
    "entity_type": "Certification",
    "kind": "knowledge-coverage",
    "do_not_fix_with": "aliases",
    "candidates": (
        "doc-electrician-trades-2026:lift-technician",
        "doc-electrician-trades-2026:scaffolding-technician",
        "doc-electrician-trades-2026:mechatronics-technician",
        "doc-construction-trades-2026:interior-finishing-technician",
        "doc-manufacturing-trades-2026:assembly-line-technician",
        "doc-manufacturing-trades-2026:hydraulic-technician",
        "doc-manufacturing-trades-2026:pneumatic-technician",
        "doc-manufacturing-trades-2026:compressor-technician",
        "doc-automobile-trades-2026:tyre-technician",
        "doc-automobile-trades-2026:wheel-alignment-technician",
        "doc-automobile-trades-2026:denting-technician",
        "doc-electronics-trades-2026:cctv-technician",
        "doc-electronics-trades-2026:fire-alarm-technician",
        "doc-electronics-trades-2026:inverter-technician",
        "doc-electronics-trades-2026:ups-technician",
        "doc-electronics-trades-2026:networking-technician",
        "doc-electronics-trades-2026:fiber-optic-technician",
        "doc-electronics-trades-2026:telecom-tower-technician",
    ),
}

#: ---------------------------------------------------------------------------
#: RESEARCH GAP · approving a candidate obliges you to re-point its vocabulary
#: ---------------------------------------------------------------------------
#: For these candidates the search vocabulary already resolves the trade's words
#: to an APPROXIMATE existing entity — usually a BusinessOpportunity or an
#: Industry rather than a learnable Skill. That is the "business you cannot
#: learn" gap and it is the strongest case for promoting them.
#:
#: It also carries a consequence nothing in the pipeline currently tracks: if a
#: candidate here is promoted and its concept keeps expanding to the old
#: approximation, the NEW Skill will be unreachable by the very words that were
#: added for it. Promotion is two edits, not one.
REPOINT_ON_PROMOTION = {
    "doc-electrician-trades-2026:painter": ("painter", "Painting Services"),
    "doc-construction-trades-2026:false-ceiling-installer":
        ("false-ceiling", "POP Works / False Ceiling Installation"),
    "doc-construction-trades-2026:pop-gypsum-technician":
        ("false-ceiling", "POP Works / False Ceiling Installation"),
    "doc-construction-trades-2026:aluminium-fabricator":
        ("aluminium-fabrication", "Aluminium Fabrication"),
    "doc-construction-trades-2026:glass-installer":
        ("aluminium-fabrication", "Aluminium Fabrication"),
    "doc-construction-trades-2026:waterproofing-technician":
        ("waterproofing", "Painting Services"),
    "doc-construction-trades-2026:borewell-technician":
        ("borewell", "Borewell Drilling Services"),
    "doc-construction-trades-2026:pump-technician":
        ("pump-technician", "Submersible Pump Installation & Repair"),
    "doc-construction-trades-2026:roofing-technician":
        ("roofing", "Welding & Metal Fabrication"),
    "doc-construction-trades-2026:excavator-operator":
        ("heavy-equipment-operator", "Construction & Skilled Trades"),
    "doc-construction-trades-2026:crane-operator":
        ("heavy-equipment-operator", "Construction & Skilled Trades"),
    "doc-construction-trades-2026:road-equipment-operator":
        ("heavy-equipment-operator", "Construction & Skilled Trades"),
    "doc-manufacturing-trades-2026:press-machine-operator":
        ("press-operator", "Sheet Metal Fabrication Unit"),
    "doc-automobile-trades-2026:tractor-mechanic":
        ("tractor-mechanic", "Automobile Mechanic (Diesel/Petrol)"),
    "doc-automobile-trades-2026:battery-technician":
        ("electric-vehicle", "Electric Vehicles"),
    "doc-automobile-trades-2026:battery-refurbishment-technician":
        ("electric-vehicle", "Electric Vehicles"),
    "doc-automobile-trades-2026:ev-charging-station-technician":
        ("electric-vehicle", "Electric Vehicles"),
    "doc-automobile-trades-2026:auto-painting-technician":
        ("painter", "Painting Services"),
}

#: Fields that must never be carried from these five documents into a package
#: row, restated here so the rule sits next to the promotion decision rather
#: than only inside each source module.
NEVER_PROMOTE_FIELDS = (
    "salary_range", "course_fees", "institute_contact", "placement_claim",
    "employer_list", "demand_estimate",
)


def by_class(cls):
    return {cid: row for cid, row in CANDIDATES.items() if row["cls"] == cls}


def group_of(candidate_id):
    for name, group in DUPLICATE_GROUPS.items():
        if candidate_id in group["members"]:
            return name
    return None


def counts():
    return {cls: len(by_class(cls)) for cls in CLASSES}
