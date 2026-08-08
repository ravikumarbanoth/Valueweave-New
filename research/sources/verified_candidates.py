#!/usr/bin/env python3
"""
Primary-source verification of the ten highest-value queued candidates.

WHAT "VERIFIED" MEANS HERE, AND WHAT IT DOES NOT
-------------------------------------------------
Each record below names a government qualification — a DGT/NCVT craftsman
trade or an NSQC-approved Sector Skill Council qualification pack — with its
code, its NSQF level and the URL of the official document. That is a large
step up from the five LLM datasets, which asserted role names with no citation
at all: a QP code and a gov.in URL can be checked by one person in one click.

It is NOT a direct read of those documents. **This environment's egress policy
blocks dgt.gov.in, nqr.gov.in, essc-india.org, asdc.org.in and nsdcindia.org**,
so every field here comes from a search index quoting the official document,
corroborated by a second independent search pass. The repository already has
precedent for exactly this situation — the UGC row in entities.csv carries the
note "Website content could not be directly re-fetched due to proxy access
restriction on gov.in domains" — and the same honesty applies: the URL is
recorded so a person with unrestricted network can confirm it, and the
confidence sits below the direct-fetch band.

    CEILING: 75.  Above the 60 given to an uncited secondary document,
    below the 88 the repository gives a fact it fetched itself.

WHY NOTHING IS PROMOTED AND NO VOCABULARY WAS WRITTEN
------------------------------------------------------
Verification answers "does this trade exist and who certifies it". It does not
answer "should ValueWeave hold it as an entity", which is a curation decision
for a person, and it does not license the salary and fee tables in the source
documents, which remain uncited.

None of these ten is a class-A merge, so none of them has an existing Skill to
point vocabulary at. Writing aliases now would be the Field Technician mistake:
sending a reader to an approximately-related entity is worse than sending them
nowhere, because they cannot tell. The vocabulary is therefore PREPARED here
and attaches only when the Skill exists — see `PROPOSED_VOCABULARY`.
"""

CEILING = 75

#: How every field below was obtained, recorded once rather than repeated.
METHOD = (
    "WebSearch against the official domain, corroborated by a second "
    "independent search pass. Direct WebFetch of the source PDF was attempted "
    "and BLOCKED by this environment's egress proxy for dgt.gov.in, "
    "nqr.gov.in, essc-india.org, asdc.org.in and nsdcindia.org. The codes and "
    "NSQF levels are quoted from the search index's extract of the official "
    "document, not read from the document."
)

MERGE, NEW, DUPLICATE, DISPUTED, REJECT = "A", "B", "C", "D", "E"

VERIFIED = {
    # ------------------------------------------------------------------
    "doc-automobile-trades-2026:service-advisor": {
        "role": "Service Advisor",
        "exists": True,
        "authority": "Automotive Skills Development Council (ASDC)",
        "code": "ASC/Q1426",
        "version": "2.0",
        "nsqf_level": "4.5",
        "url": "https://www.asdc.org.in/images/job_roles/ASC_Q1426_v2.0%20Service%20Advisor.pdf_.pdf",
        "decision": NEW,
        "proposed_entity": "Automotive Service Advisor",
        "note": ("Confirmed as a distinct NSQC-approved job role, not a "
                 "variant of a workshop trade: the QP describes customer "
                 "relationship handling and translating a complaint into a "
                 "repair order. This is the one non-manual role in 205 pages "
                 "of documents and the graph has nothing like it — the only "
                 "automotive career reachable by somebody who cannot do heavy "
                 "physical work."),
        "confidence": 75,
    },
    # ------------------------------------------------------------------
    "doc-manufacturing-trades-2026:fitter": {
        "role": "Fitter",
        "exists": True,
        "authority": "DGT / NCVT — Craftsman Training Scheme (CTS 2.0)",
        "code": "CTS trade: Fitter",
        "version": "CTS 2.0",
        "nsqf_level": "4",
        "url": "https://dgt.gov.in/sites/default/files/2023-12/Fitter_CTS2.0_NSQF-4_0.pdf",
        "decision": DUPLICATE,
        "proposed_entity": "Fitter",
        "note": ("Two years, Capital Goods & Manufacturing sector, National "
                 "Trade Certificate on completion. One of the largest ITI "
                 "trades in India and the graph does not hold it — search "
                 "currently answers `fitter` with *Filter Press*. Verification "
                 "settles the group `maintenance-fitter`: Fitter is the "
                 "nationally recognised trade and document A's 'Machine "
                 "Maintenance Technician' is a workplace title for it, so the "
                 "pair should resolve to ONE entity named Fitter."),
        "confidence": 75,
    },
    # ------------------------------------------------------------------
    "doc-manufacturing-trades-2026:tool-and-die-maker": {
        "role": "Tool & Die Maker",
        "exists": True,
        "authority": "DGT / NCVT — Craftsman Training Scheme (CTS 2.0)",
        "code": "CTS trades: Tool & Die Maker (Dies & Moulds); "
                "Tool & Die Maker (Press Tools, Jigs & Fixtures)",
        "version": "CTS 2.0",
        "nsqf_level": "4 (Dies & Moulds) / 5 (Press Tools, Jigs & Fixtures)",
        "url": "https://dgt.gov.in/sites/default/files/2023-12/TDM%20(D_M)_CTS2.0_NSQF-4.pdf",
        "url_2": "https://bharatskills.gov.in/pdf/Qp_Curriculum/TDM-PJF_CTS_NSQF-5.pdf",
        "decision": NEW,
        "proposed_entity": "Tool & Die Making",
        "note": ("VERIFICATION CHANGED THE SHAPE OF THIS ONE. The document "
                 "presents a single role; DGT runs TWO trades at two "
                 "different NSQF levels. The graph already holds 'Tool and "
                 "Die Making Unit' as an MSME — a business a person could run "
                 "with no skill entity teaching the work. Recommend ONE Skill "
                 "covering the craft, with the two specialisations recorded "
                 "as qualifications rather than as separate Skills; splitting "
                 "is the over-splitting error §15 records."),
        "confidence": 75,
    },
    # ------------------------------------------------------------------
    "doc-electrician-trades-2026:painter": {
        "role": "Painter",
        "exists": True,
        "authority": "DGT / NCVT — Craftsman Training Scheme (CTS 2.0)",
        "code": "CTS trades: Painter (General); Domestic Painter; "
                "Industrial Painter",
        "version": "CTS 2.0",
        "nsqf_level": "4 (Painter General, 2 yr) / 3 (Domestic, 1 yr) / "
                      "3 (Industrial, 1 yr)",
        "url": "https://dgt.gov.in/sites/default/files/Painter%20(General)_CTS2.0_NSQF-4.pdf",
        "url_2": "https://dgt.gov.in/sites/default/files/Domestic%20Painter_CTS2.0_NSQF-3.pdf",
        "decision": NEW,
        "proposed_entity": "Painting (Building & Decorative)",
        "note": ("THE STRONGEST RESULT OF THE TEN, because it settles a "
                 "KEEP_DISTINCT pair with a primary source rather than a "
                 "judgement. DGT runs building painting and automotive "
                 "refinishing as SEPARATE trades: Painter (General) / "
                 "Domestic Painter / Industrial Painter on one side, and "
                 "'Mechanic Auto Body Painting' (NSQF 3.5) on the other. The "
                 "source modules said keep them apart; the national trade "
                 "structure agrees. Search currently returns 'Painting "
                 "Services' for both, and promoting these must fix that."),
        "confidence": 75,
    },
    # ------------------------------------------------------------------
    "doc-electrician-trades-2026:mechatronics-technician": {
        "role": "Mechatronics Technician",
        "exists": True,
        "authority": "DGT / NCVT — Craftsman Training Scheme (CTS 2.0)",
        "code": "CTS trade: Technician Mechatronics",
        "version": "CTS 2.0",
        "nsqf_level": "4",
        "url": "https://dgt.gov.in/sites/default/files/Technician%20Mechatronics_CTS2.0_NSQF-4%20(1).pdf",
        "decision": NEW,
        "proposed_entity": "Mechatronics Technician",
        "note": ("Two years, National Trade Certificate. Sits between the "
                 "graph's existing Industrial Electrician, PLC Programming & "
                 "Control Systems and Industrial Robotics without being any "
                 "of them — which is the argument for holding it rather than "
                 "merging: a student choosing an ITI trade is choosing "
                 "between these by name."),
        "confidence": 75,
    },
    # ------------------------------------------------------------------
    "doc-electrician-trades-2026:lift-technician": {
        "role": "Lift Technician",
        "exists": True,
        "authority": "DGT / NCVT — Craftsman Training Scheme (CTS 2.0)",
        "code": "CTS trade: Lift & Escalator Mechanic",
        "version": "CTS 2.0",
        "nsqf_level": "4 (CTS); a Lift Mechanic variant exists at NSQF 5",
        "url": "https://dgt.gov.in/sites/default/files/2024-01/Lift%20_%20Escalator%20Mechanic_CTS2.0_NSQF-4.pdf",
        "decision": NEW,
        "proposed_entity": "Lift & Escalator Mechanic",
        "note": ("CORRECTS MY EARLIER CLASSIFICATION NOTE, which said there "
                 "was no sector-council qualification and pointed only at "
                 "state lifts-and-escalators licensing. There is a named DGT "
                 "craftsman trade, which is a stronger and easier check. The "
                 "state licensing still applies to who may sign off an "
                 "installation and remains worth recording separately — but "
                 "it is not the qualification a student would train for."),
        "confidence": 75,
    },
    # ------------------------------------------------------------------
    "doc-electronics-trades-2026:cctv-technician": {
        "role": "CCTV Technician",
        "exists": True,
        "authority": "Electronics Sector Skills Council of India (ESSCI)",
        "code": "ELE/Q4605",
        "version": "4.0",
        "nsqf_level": "3.5",
        "url": "https://essc-india.org/images/QP-Qualification-PACK/CCTV%20Installation%20Technician_ELE_Q4605_v4.0.pdf",
        "decision": DUPLICATE,
        "proposed_entity": "CCTV Installation Technician",
        "note": ("NSQC approved 08/05/2025; entry at class 10 and age 18 — "
                 "which matters, because it is one of the few verified roles "
                 "here open to a 10th-pass reader. Bears directly on the "
                 "group `physical-security`: ESSCI holds ONE qualification "
                 "covering surveillance installation, so document E's split "
                 "into 'CCTV Technician' and 'Security System Installer' is "
                 "not reflected in the national structure. Recommend the pair "
                 "resolves to this one entity unless the reviewer finds a "
                 "separate access-control QP."),
        "confidence": 75,
    },
    # ------------------------------------------------------------------
    "doc-electronics-trades-2026:networking-technician": {
        "role": "Networking Technician",
        "exists": True,
        "authority": "Electronics Sector Skills Council of India (ESSCI)",
        "code": "ELE/Q4606",
        "version": "3.0",
        "nsqf_level": "4",
        "url": "https://www.essc-india.org/images/QPs/Field%20Technician%20-%20Networking%20%26%20Stoarge%20-%20ELE_Q4606_v3.0.pdf",
        "decision": NEW,
        "proposed_entity": "Field Technician — Networking & Storage",
        "note": ("400 hours total (180 theory, 180 practical, 40 "
                 "employability). THE KEY RESULT FOR THE MAGNET: this "
                 "qualification is the direct sibling of ELE/Q4601, the "
                 "Certification the graph already holds and which is the top "
                 "hit for 18 queued trades. The trade the reader wants and "
                 "the row the graph returns are two members of one ESSCI "
                 "family — see FIELD_TECHNICIAN_FAMILY below. Confirms the "
                 "refusal to carry 'Network Engineer' across as an alias: "
                 "this is a technician qualification at NSQF 4, not an "
                 "engineering degree role."),
        "confidence": 75,
    },
    # ------------------------------------------------------------------
    "doc-electronics-trades-2026:fire-alarm-technician": {
        "role": "Fire Alarm Technician",
        "exists": None,                       # could not be established
        "authority": "NOT FOUND — no NSQC-approved SSC qualification located",
        "code": None,
        "version": None,
        "nsqf_level": None,
        "url": "",
        "decision": DISPUTED,
        "proposed_entity": None,
        "note": ("A GENUINE GAP, and the one candidate of the ten that "
                 "verification did not confirm. Searching ESSCI and the "
                 "National Qualification Register returns adjacent roles that "
                 "are NOT this job — Firefighter, Fire Safety Officer, Fire "
                 "Safety Technician (Oil & Gas) — all of which are about "
                 "responding to fire rather than installing detection. The "
                 "only fire-alarm-specific credential found is a private "
                 "'Global Occupational Skill Standard' certificate from a "
                 "commercial training company, which is not a national "
                 "qualification and must not be recorded as one.\n\n"
                 "So the honest position is: the OCCUPATION plainly exists — "
                 "somebody installs the panels — but a national qualification "
                 "for it could not be found from this environment. Two "
                 "explanations are open and a person must pick: it may sit "
                 "under state fire-services licensing rather than NSQF, or it "
                 "may be covered inside a broader ESSCI security-systems "
                 "pack that this search did not surface. Reclassified from B "
                 "to D for that reason."),
        "confidence": 30,
    },
    # ------------------------------------------------------------------
    "doc-automobile-trades-2026:ev-charging-station-technician": {
        "role": "EV Charging Station Technician",
        "exists": True,
        "authority": "Power Sector Skill Council (PSSC) — NOT ASDC",
        "code": "NQR qualification: EV Charging Station Technician "
                "(Operation & Maintenance); an Installation & Commissioning "
                "role is described in PSSC material but its code was not "
                "pinned from this environment",
        "version": None,
        "nsqf_level": "NOT ESTABLISHED — approved at the 14th NSQC meeting",
        "url": "https://nqr.gov.in/sites/default/files/Q-File_EV%20Charging%20Station%20Technician%20(operation%20and%20maintenance).pdf",
        "decision": NEW,
        "proposed_entity": "EV Charging Station Technician",
        "note": ("VERIFICATION CORRECTED MY EARLIER RECOMMENDATION. The "
                 "classification register sent this to ASDC because the role "
                 "arrived in an automobile document. It is a POWER sector "
                 "qualification: PSSC, promoted by the Ministry of Power and "
                 "MNRE, covering site survey, installation and commissioning "
                 "of charging infrastructure. That is a different sector, a "
                 "different regulator and a different training route from the "
                 "graph's existing EV Technician, and it is the reason to "
                 "hold it as its own Skill rather than folding it into EV "
                 "work. The exact QP code and NSQF level are NOT established "
                 "and are marked so."),
        "confidence": 55,
    },
}

#: ---------------------------------------------------------------------------
#: THE FIELD TECHNICIAN MAGNET, DIAGNOSED
#: ---------------------------------------------------------------------------
#: §18 recorded the magnet as a knowledge-coverage problem. Verification says
#: what the coverage problem actually IS, and it is sharper than "the graph is
#: missing some skills".
#:
#: ESSCI publishes a family of "After Sales Support" qualifications sharing the
#: ELE/Q46xx prefix. The graph holds exactly ONE of them, ELE/Q4601, and holds
#: it as a **Certification**. It holds no Skill for any trade in the family. So
#: any query ending in the word "technician" that has no Skill to reach finds
#: the one Certification that does contain the word — not because ranking is
#: broken, but because that row is the only thing in the graph that resembles
#: the question.
#:
#: The same asymmetry produced the second magnet: `Automotive Service
#: Technician (Two and Three Wheelers) - ASC/Q1411` is also a Certification
#: with no matching Skill, and it too surfaced as a wrong top hit during the
#: five-document work.
#:
#: THE FIX IS COVERAGE, NOT RANKING AND NOT ALIASES. Two of the three named
#: family members below are already queued candidates; promoting them removes
#: their queries from the magnet and gives the vocabulary somewhere true to
#: point.
FIELD_TECHNICIAN_FAMILY = {
    "ELE/Q4601": {
        "title": "Field Technician — Computing & Peripherals",
        "nsqf_level": "4", "version": "3.0",
        "in_graph_as": "Certification",
        "url": "https://www.essc-india.org/images/QPs/Field%20Technician%20-%20Computing%20&%20Peripherals%20-%20ELE_Q4601_v3.0.pdf",
        "status": "the magnet — top hit for 18 queued trades",
    },
    "ELE/Q4605": {
        "title": "CCTV Installation Technician",
        "nsqf_level": "3.5", "version": "4.0",
        "in_graph_as": None,
        "url": "https://essc-india.org/images/QP-Qualification-PACK/CCTV%20Installation%20Technician_ELE_Q4605_v4.0.pdf",
        "status": "queued as doc-electronics-trades-2026:cctv-technician",
    },
    "ELE/Q4606": {
        "title": "Field Technician — Networking & Storage",
        "nsqf_level": "4", "version": "3.0",
        "in_graph_as": None,
        "url": "https://www.essc-india.org/images/QPs/Field%20Technician%20-%20Networking%20%26%20Stoarge%20-%20ELE_Q4606_v3.0.pdf",
        "status": "queued as doc-electronics-trades-2026:networking-technician",
    },
}

#: The second Certification-without-a-Skill, recorded for the same reason.
SECOND_MAGNET = {
    "entity": "Automotive Service Technician (Two and Three Wheelers) - ASC/Q1411",
    "entity_type": "Certification",
    "matching_skill_in_graph": "Two-Wheeler Mechanic",
    "note": ("This one is HALF fixed. The graph does hold Two-Wheeler "
             "Mechanic, and the document-D vocabulary now routes `bike "
             "mechanic`, `scooter mechanic` and `motorcycle mechanic` to it. "
             "The Certification still wins for bare `service technician` and "
             "`automotive technician`, which the vocabulary redirects. Listed "
             "so the pattern is visible: a Certification imported without its "
             "Skill becomes a magnet, and this is the second instance."),
}

#: ---------------------------------------------------------------------------
#: VOCABULARY PREPARED, NOT SHIPPED
#: ---------------------------------------------------------------------------
#: None of these ten is a class-A merge, so not one of them has an existing
#: Skill for vocabulary to point at. Writing these into concepts.js today would
#: send readers to an approximately-related entity — the exact failure the
#: magnet gap forbids, and `test_the_magnet_is_not_being_papered_over_with_
#: aliases` would fail, correctly.
#:
#: They are held here so that promotion is one step rather than a rediscovery,
#: and so the second obligation §18 records — re-point the concept when the
#: Skill lands — has something concrete to point at.
#:
#: STATUS OF THE TELUGU: **PROPOSED, NEEDS A TELUGU-SPEAKING REVIEWER.** These
#: are transliterated loanwords, which is the dominant register for technical
#: trades in Telangana and Andhra Pradesh — a Hyderabad technician says
#: "లిఫ్ట్", not a Sanskritic coinage. That is a claim about usage and it is
#: checkable, but not by me and not by a search engine. Nothing here is
#: indexed until a person confirms it.
#:
#: The `<trade> pani` Tanglish forms follow the convention already in the
#: concept table ("current pani", "tiles pani", "ac repair pani").
PROPOSED_VOCABULARY = {
    "doc-automobile-trades-2026:service-advisor": {
        "en": ["service advisor", "automotive service advisor",
               "workshop service advisor", "service reception"],
        "te": ["సర్వీస్ అడ్వైజర్"],
        "tanglish": [],
    },
    "doc-manufacturing-trades-2026:fitter": {
        "en": ["fitter", "bench fitter", "maintenance fitter",
               "mechanical fitter", "assembly fitter"],
        "te": ["ఫిట్టర్"],
        "tanglish": [],
    },
    "doc-manufacturing-trades-2026:tool-and-die-maker": {
        "en": ["tool and die maker", "die maker", "tool room technician",
               "jigs and fixtures", "press tool maker", "mould maker"],
        "te": [],
        "tanglish": [],
    },
    "doc-electrician-trades-2026:painter": {
        #: NOTE: "painter", "painting", "building painter" and the Telugu
        #: పెయింటర్ are ALREADY claimed by the existing `painter` concept,
        #: which points at the Painting Services business. When this Skill is
        #: created that concept must be RE-POINTED, not duplicated — two
        #: concepts claiming one alias fails the integrity test, correctly.
        "en": ["painter", "house painting", "wall putty applicator",
               "decorative painter", "domestic painter"],
        "te": [],
        "tanglish": ["painting pani"],
        "repoint_existing_concept": "painter",
    },
    "doc-electrician-trades-2026:mechatronics-technician": {
        "en": ["mechatronics", "mechatronics technician",
               "technician mechatronics"],
        "te": ["మెకట్రానిక్స్"],
        "tanglish": [],
    },
    "doc-electrician-trades-2026:lift-technician": {
        "en": ["lift technician", "lift mechanic", "elevator technician",
               "escalator mechanic", "lift and escalator mechanic",
               "elevator repair"],
        "te": ["లిఫ్ట్ మెకానిక్"],
        "tanglish": ["lift pani"],
    },
    "doc-electronics-trades-2026:cctv-technician": {
        "en": ["cctv technician", "cctv installation", "cctv installer",
               "surveillance technician", "security camera technician",
               "camera fitting"],
        "te": ["సీసీటీవీ"],
        "tanglish": ["camera pani"],
    },
    "doc-electronics-trades-2026:networking-technician": {
        "en": ["networking technician", "network technician", "lan technician",
               "structured cabling", "field technician networking"],
        "te": ["నెట్‌వర్కింగ్"],
        "tanglish": [],
    },
    "doc-electronics-trades-2026:fire-alarm-technician": {
        #: Deliberately empty. The role was NOT verified, so there is nothing
        #: to prepare vocabulary for. An unverified role with ready-made
        #: aliases is an invitation to ship it.
        "en": [], "te": [], "tanglish": [],
    },
    "doc-automobile-trades-2026:ev-charging-station-technician": {
        "en": ["ev charging station technician", "charging station installer",
               "ev charger installation", "charging infrastructure technician"],
        "te": ["ఛార్జింగ్ స్టేషన్"],
        "tanglish": [],
    },
}

#: What verification changed relative to the §18 classification. Recorded
#: because a classification that silently rewrites itself teaches nobody
#: anything, and two of these were my errors rather than new information.
CLASSIFICATION_CHANGES = {
    "doc-electronics-trades-2026:fire-alarm-technician": (
        "B -> D. I predicted an ESSCI qualification pack and there is none to "
        "be found. The occupation exists; the credential could not be "
        "located, and the only fire-alarm-specific one found is commercial "
        "rather than national."),
    "doc-automobile-trades-2026:ev-charging-station-technician": (
        "primary source ASDC -> PSSC. My error: I assigned the authority from "
        "the document the role arrived in rather than from the work. Charging "
        "infrastructure is power sector, not automotive."),
    "doc-electrician-trades-2026:lift-technician": (
        "primary source 'state licensing; NCO-2015' -> 'DGT CTS Lift & "
        "Escalator Mechanic'. My error: I assumed no craftsman trade existed "
        "because no sector council covers lifts. DGT does."),
    "doc-manufacturing-trades-2026:tool-and-die-maker": (
        "still B, but the shape changed: DGT runs TWO trades at two NSQF "
        "levels where the document described one role."),
}


def verified():
    return {k: v for k, v in VERIFIED.items() if v["exists"] is True}


def unverified():
    return {k: v for k, v in VERIFIED.items() if v["exists"] is not True}


def sources():
    out = {}
    for cid, row in VERIFIED.items():
        urls = [row[k] for k in ("url", "url_2") if row.get(k)]
        if urls:
            out[cid] = urls
    return out
