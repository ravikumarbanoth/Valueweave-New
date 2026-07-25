#!/usr/bin/env python3
"""
Package007_Government_Schemes v1.0.0 — Mapping & Workflow Dataset Generator

Builds the eight relational and workflow datasets:
   5  application_process.csv          step-by-step workflow per scheme
   8  education_scheme_mapping.csv     -> Package002_Education
   9  agriculture_scheme_mapping.csv   -> Package005_Agriculture
  10  skill_scheme_mapping.csv         -> Package006_Skills_and_Training
  11  industry_scheme_mapping.csv      -> Package004_Industries_and_Livelihoods
  12  district_scheme_mapping.csv      -> Package001_Geography
  14  scheme_application_status.csv    generic status workflow
  15  scheme_ai_recommendations.csv    profile -> scheme priority

Cross-package foreign keys are read from the released upstream CSVs AT GENERATION
TIME, so an ID that no longer exists upstream fails here rather than shipping broken.
Where no genuine upstream counterpart exists, the bare sentinel PENDING_VERIFICATION
is written instead of an invented reference.
"""

import csv
import sys
from pathlib import Path

CD = "2026-07-25"
VST = "VST-NEEDS_REVIEW"
PV = "PENDING_VERIFICATION"

PKG = Path(__file__).resolve().parent
DATASETS = PKG / "datasets"
PACKAGES = PKG.parent

MYSCH = "MyScheme national scheme platform"
MYSCH_URL = "https://www.myscheme.gov.in/"


def read(rel):
    p = PACKAGES / rel
    if not p.exists():
        sys.exit(f"FATAL: upstream dataset missing: {rel}")
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(filename, headers, rows):
    for i, r in enumerate(rows):
        if len(r) != len(headers):
            raise ValueError(f"{filename} row {i} ({r[0]}): {len(r)} values, expected {len(headers)}")
    with open(DATASETS / filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  {filename}: {len(rows)} rows x {len(headers)} cols")


# --------------------------------------------------------- upstream FK lookups
P001_DIST = read("Package001_Geography/datasets/district.csv")
P002_SCHOL = read("Package002_Education/datasets/scholarships.csv")
P002_UNIV = read("Package002_Education/datasets/universities_telangana_andhra_pradesh.csv")
P004_MSME = read("Package004_Industries/datasets/msme_entrepreneurship_support_schemes.csv")
P004_FOOD = read("Package004_Industries/datasets/food_agro_processing_micro_enterprises.csv")
P004_CONST = read("Package004_Industries/datasets/construction_skilled_trade_services.csv")
P004_DIGI = read("Package004_Industries/datasets/digital_technology_livelihoods.csv")
P005_CROPS = read("Package005_Agriculture/datasets/crops.csv")
P005_SCH = read("Package005_Agriculture/datasets/agriculture_schemes.csv")
P006_SKILLS = read("Package006_Skills_and_Training/datasets/skills.csv")
P006_CERTS = read("Package006_Skills_and_Training/datasets/certifications.csv")
P006_PROV = read("Package006_Skills_and_Training/datasets/training_providers.csv")
P006_SCH = read("Package006_Skills_and_Training/datasets/government_skill_schemes.csv")


def find(rows, key, needle, idcol):
    """Resolve one upstream row by substring match on `key`; return its id or None."""
    hits = [r for r in rows if needle.lower() in r[key].lower()]
    if len(hits) == 1:
        return hits[0][idcol], hits[0][key]
    return None, None


def must(rows, key, needle, idcol, label):
    i, n = find(rows, key, needle, idcol)
    if i is None:
        sys.exit(f"FATAL: could not uniquely resolve {label!r} in upstream via {key}~{needle!r}")
    return i, n


# ===========================================================================
# 5. application_process.csv
# ===========================================================================
H_AP = ["step_id", "scheme_id", "scheme_short_name", "step_number", "step_name",
        "step_description", "channel", "responsible_actor", "typical_timeline",
        "output_of_step", "data_source", "source_url", "collection_date",
        "confidence_score", "verification_status", "notes"]

ONLINE = "Online"
OFFLINE = "Offline"
CSC = "CSC / MeeSeva"
BANK = "Bank branch"
DIST = "District office"

# (scheme_id, short, [(step_name, desc, channel, actor, timeline, output, conf)])
PROCESS = [
    ("sch-005", "PM-KISAN", [
        ("Registration", "Farmer registers with land details, Aadhaar and bank account", ONLINE, "Farmer (self) or CSC operator", PV, "Registration number generated", 74),
        ("Land record verification", "State revenue department verifies landholding against records", OFFLINE, "State revenue department", PV, "Land ownership confirmed or query raised", 72),
        ("eKYC completion", "Aadhaar-based eKYC completed to activate the beneficiary record", ONLINE, "Farmer (self) or CSC operator", PV, "eKYC status marked complete", 73),
        ("State approval", "State government approves the verified beneficiary list", OFFLINE, "State agriculture department", PV, "Beneficiary added to the payment file", 71),
        ("Instalment credit", "Instalment credited by direct benefit transfer", ONLINE, "Central government (PFMS)", "Three instalments per year", "Amount credited to bank account", 74),
    ]),
    ("sch-014", "PMEGP", [
        ("Online application", "Applicant files the project application with the project report", ONLINE, "Applicant", PV, "Application ID generated", 74),
        ("Agency scrutiny", "KVIC, KVIB or DIC scrutinises and shortlists the application", OFFLINE, "KVIC / KVIB / DIC", PV, "Shortlisted for task force interview", 72),
        ("Task force interview", "District task force committee appraises the proposal", DIST, "District Task Force Committee", PV, "Recommended or rejected", 71),
        ("Bank appraisal and sanction", "Financing bank appraises viability and sanctions the loan", BANK, "Financing bank", PV, "Loan sanction letter", 73),
        ("EDP training", "Applicant completes entrepreneurship development programme training", OFFLINE, "Empanelled training institution", PV, "EDP completion certificate", 71),
        ("Disbursement and subsidy claim", "Loan disbursed and margin money subsidy claimed by the bank", BANK, "Financing bank; KVIC", PV, "Subsidy parked as back-ended term deposit", 72),
    ]),
    ("sch-015", "PMMY", [
        ("Approach lender", "Borrower approaches a bank, NBFC or MFI, or applies via Jan Samarth", BANK, "Borrower", PV, "Application accepted", 73),
        ("Document submission", "Identity, address, business and quotation documents submitted", BANK, "Borrower", PV, "File complete for appraisal", 72),
        ("Credit appraisal", "Lender appraises the activity and repayment capacity", BANK, "Lending institution", PV, "Sanction or rejection", 72),
        ("Disbursement", "Loan disbursed to the borrower's account", BANK, "Lending institution", PV, "Funds credited; MUDRA card issued where applicable", 72),
    ]),
    ("sch-025", "NMMSS", [
        ("State selection examination", "Student appears in the state-conducted selection examination", OFFLINE, "State examination authority", PV, "Merit list published", 73),
        ("NSP registration", "Selected student registers on the National Scholarship Portal", ONLINE, "Student or parent", PV, "Application reference number", 74),
        ("Institution verification", "School verifies enrolment and the student's details", ONLINE, "School (institute nodal officer)", PV, "Application verified at level 1", 73),
        ("District and state verification", "District and state nodal officers verify in sequence", ONLINE, "District / state nodal officer", PV, "Application forwarded to ministry", 71),
        ("Scholarship disbursal", "Scholarship credited by direct benefit transfer", ONLINE, "Ministry of Education (PFMS)", "Annual", "Amount credited to student account", 73),
        ("Annual renewal", "Student renews on NSP subject to prescribed academic performance", ONLINE, "Student", "Annual", "Renewal approved", 72),
    ]),
    ("sch-031", "AB PM-JAY", [
        ("Eligibility check", "Beneficiary checks eligibility on the portal or at a facility", ONLINE, "Beneficiary or Ayushman Mitra", PV, "Eligibility confirmed", 73),
        ("Ayushman card generation", "Card generated after Aadhaar-based identity verification", CSC, "Ayushman Mitra / CSC operator", PV, "Ayushman card issued", 72),
        ("Hospital admission", "Beneficiary presents the card at an empanelled hospital", OFFLINE, "Empanelled hospital; Ayushman Mitra", PV, "Case registered under the scheme", 73),
        ("Pre-authorisation", "Hospital seeks pre-authorisation for the treatment package", ONLINE, "Hospital; State Health Agency", PV, "Pre-authorisation approved", 71),
        ("Cashless treatment", "Treatment provided with no payment at the point of care", OFFLINE, "Empanelled hospital", PV, "Treatment completed", 73),
        ("Claim settlement", "Hospital claim settled by the State Health Agency", ONLINE, "State Health Agency", PV, "Payment released to hospital", 70),
    ]),
    ("sch-034", "MGNREGS", [
        ("Job card application", "Household applies to the Gram Panchayat for a job card", OFFLINE, "Household", PV, "Job card issued", 74),
        ("Work demand", "Adult member submits a written demand for work", OFFLINE, "Worker", PV, "Dated receipt of demand issued", 73),
        ("Work allocation", "Panchayat allocates work, statutorily within a prescribed period", OFFLINE, "Gram Panchayat", PV, "Muster roll opened", 72),
        ("Attendance and measurement", "Attendance recorded and work measured for wage computation", OFFLINE, "Mate; technical assistant", PV, "Measurement book entry", 70),
        ("Wage payment", "Wages paid to the worker's account by direct benefit transfer", ONLINE, "Programme officer (NREGASoft / PFMS)", "Within the statutory period", "Wages credited", 73),
    ]),
    ("sch-021", "PMKVY 4.0", [
        ("Candidate registration", "Candidate registers on Skill India Digital and selects a job role", ONLINE, "Candidate", PV, "Candidate profile created", 73),
        ("Training centre enrolment", "Candidate enrols in a batch at an empanelled training centre", OFFLINE, "Training centre", PV, "Batch enrolment confirmed", 72),
        ("Training delivery", "NSQF-aligned training delivered per the Qualification Pack", OFFLINE, "Training partner", PV, "Training hours completed", 72),
        ("Assessment", "Third-party assessment conducted by the Sector Skill Council", OFFLINE, "Sector Skill Council assessor", PV, "Assessment result recorded", 72),
        ("Certification", "NCVET-recognised certificate issued on passing", ONLINE, "NSDC / Sector Skill Council", PV, "Digital certificate issued", 73),
        ("Placement assistance", "Training partner provides placement linkage support", OFFLINE, "Training partner", PV, "Placement offer (not guaranteed)", 68),
    ]),
    ("sch-036", "PMAY-G", [
        ("Beneficiary identification", "Household identified from the permanent wait list and verified", OFFLINE, "Gram Panchayat; block office", PV, "Name in the sanctioned list", 72),
        ("Gram Sabha validation", "Gram Sabha validates the list publicly", OFFLINE, "Gram Sabha", PV, "List validated", 71),
        ("Sanction and first instalment", "Sanction issued and first instalment released", ONLINE, "District Rural Development Agency", PV, "First instalment credited", 72),
        ("Milestone inspection", "Construction progress geo-tagged and inspected per stage", OFFLINE, "Block technical staff", PV, "Milestone certified", 70),
        ("Subsequent instalments", "Remaining instalments released against certified milestones", ONLINE, "DRDA (AwaasSoft / PFMS)", PV, "House completed", 71),
    ]),
]


def rows_process():
    out = []
    n = 0
    for sid, short, steps in PROCESS:
        for num, (name, desc, chan, actor, tl, outp, conf) in enumerate(steps, start=1):
            n += 1
            out.append((f"step-{n:03d}", sid, short, str(num), name, desc, chan,
                        actor, tl, outp, MYSCH, MYSCH_URL, CD, str(conf), VST,
                        "Timelines are the bare sentinel where no statutory or published "
                        "service-standard period was found"))
    return out


# ===========================================================================
# 8. education_scheme_mapping.csv  -> Package002_Education
# ===========================================================================
H_EDU = ["mapping_id", "scheme_id", "scheme_short_name", "package002_dataset",
         "package002_record_id", "package002_record_name", "student_category",
         "education_stage", "institution_type", "data_source", "source_url",
         "collection_date", "confidence_score", "verification_status", "notes"]

EDU_LINKS = [
    ("sch-025", "NMMSS", "scholarships", "National Means-cum-Merit", "All (income-tested)", "Secondary (IX-XII)", "Government / local body / aided school", 76, "Exact one-to-one match with the Package002 scholarship record"),
    ("sch-026", "CSSS", "scholarships", "Central Sector Scheme of Scholarships", "All (merit plus income-tested)", "Higher education (UG/PG)", "Recognised college or university", 75, "Exact one-to-one match with the Package002 scholarship record"),
    ("sch-027", "PM-YASASVI", "scholarships", "PM YASASVI", "OBC / EBC / DNT", "Secondary and higher education", "Government and aided institutions", 72, "Exact one-to-one match with the Package002 scholarship record"),
    ("sch-028", "PMS-SC", "scholarships", "Top Class Education Scheme for SC", "Scheduled Caste", "Post-matriculation", "Recognised institution", 70, "Package002 holds the Top Class vertical; the general PMS-SC vertical is not separately released there"),
]


def rows_edu():
    out = []
    n = 0
    for sid, short, ds, needle, cat, stage, inst, conf, note in EDU_LINKS:
        rid, rname = must(P002_SCHOL, "scheme_name", needle, "id", f"{short} in Package002")
        n += 1
        out.append((f"edum-{n:03d}", sid, short, ds, rid, rname, cat, stage, inst,
                    "National Scholarship Portal; Package002_Education reconciliation",
                    "https://scholarships.gov.in/", CD, str(conf), VST, note))
    # Institutional education schemes with no Package002 counterpart record
    for sid, short, cat, stage, inst, conf, note in [
        ("sch-029", "Samagra Shiksha", "All students", "Pre-school to class XII",
         "Government and government-aided schools", 70,
         "Institutional scheme; Package002 holds universities and boards, not schools, so no record to link"),
        ("sch-030", "PM POSHAN", "All enrolled children", "Classes I-VIII",
         "Government and government-aided schools", 70,
         "Entitlement scheme; no Package002 counterpart record exists"),
        ("sch-024", "Skill Loan", "Vocational learners", "Post-secondary vocational",
         "NSQF-aligned training institution", 68,
         "Education-financing scheme; Package002 covers scholarships not loans, so no record to link"),
    ]:
        n += 1
        out.append((f"edum-{n:03d}", sid, short, PV, PV, PV, cat, stage, inst,
                    "Ministry of Education; Package002_Education reconciliation",
                    "https://www.education.gov.in/", CD, str(conf), VST, note))
    return out


# ===========================================================================
# 9. agriculture_scheme_mapping.csv  -> Package005_Agriculture
# ===========================================================================
H_AGRI = ["mapping_id", "scheme_id", "scheme_short_name", "package005_scheme_id",
          "package005_scheme_name", "package005_crop_id", "package005_crop_name",
          "farmer_category", "farm_activity", "data_source", "source_url",
          "collection_date", "confidence_score", "verification_status", "notes"]

# (P007 scheme, short, P005 scheme needle | None, crop needle | None, farmer cat, activity, conf, note)
AGRI_LINKS = [
    ("sch-005", "PM-KISAN", "PM-KISAN", None, "Land-holding farmer families", "Income support (crop-agnostic)", 76, "Crop-agnostic: support is per landholding, not per crop"),
    ("sch-006", "PMFBY", "PMFBY", "Rice", "All categories; notified-area cultivators", "Crop insurance", 74, "Rice is the highest-enrolment notified crop"),
    ("sch-006", "PMFBY", "PMFBY", "Cotton", "All categories; notified-area cultivators", "Crop insurance", 73, "Cotton is a high-risk rainfed crop with heavy PMFBY uptake"),
    ("sch-007", "KCC", "Kisan Credit Card", "Rice", "All categories including tenant farmers", "Short-term crop credit", 74, "Crop loan limits are scale-of-finance based per crop"),
    ("sch-007", "KCC", "Kisan Credit Card", "Chilli", "All categories including tenant farmers", "Short-term crop credit", 72, "High input-cost crop; significant working capital need"),
    ("sch-008", "PMKSY", "PMKSY", "Sugarcane", "All categories; higher subsidy for small and marginal", "Micro-irrigation", 73, "Water-intensive crop; drip conversion is a policy priority"),
    ("sch-008", "PMKSY", "PMKSY", "Banana", "All categories; higher subsidy for small and marginal", "Micro-irrigation", 71, "High water requirement; drip-suited horticulture crop"),
    ("sch-009", "SMAM", "Sub-Mission on Agri-Mechanization", "Rice", "Small, marginal, SC, ST and women farmers get higher subsidy", "Farm mechanisation", 73, "Paddy transplanters and combine harvesters are principal SMAM items"),
    ("sch-010", "PKVY", "Paramparagat Krishi Vikas Yojana", "Turmeric", "Cluster members willing to convert to organic", "Organic conversion", 71, "Organic turmeric commands a substantial export premium"),
    ("sch-010", "PKVY", "Paramparagat Krishi Vikas Yojana", "Ashwagandha", "Cluster members willing to convert to organic", "Organic conversion", 68, "Medicinal crops have strong organic-certification demand"),
    ("sch-011", "SHC", "Soil Health Card", None, "All farmers", "Soil testing and nutrient advisory", 73, "Crop-agnostic diagnostic service"),
    ("sch-012", "AIF", "Agricultural Infrastructure Fund", "Tomato", "FPOs, PACS, cooperatives, agri-entrepreneurs", "Post-harvest infrastructure", 70, "Highly perishable crop; cold storage is the classic AIF project"),
    ("sch-013", "PM-KUSUM", None, "Rice", "Farmers, farmer groups, panchayats, cooperatives", "Solar pump irrigation", 68, "PM-KUSUM is not in Package005 v1.0.0; only the crop side resolves"),
    ("sch-019", "PMFME", None, "Turmeric", "Micro food processors, SHG members, FPOs", "Value-add processing", 70, "PMFME is not in Package005 v1.0.0; ODOP turmeric districts are the target"),
]


def rows_agri():
    out = []
    n = 0
    for sid, short, p5s, cropn, cat, act, conf, note in AGRI_LINKS:
        if p5s:
            p5id, p5name = must(P005_SCH, "scheme_name", p5s, "scheme_id", f"{short} in Package005")
        else:
            p5id, p5name = PV, PV
        if cropn:
            cid, cname = must(P005_CROPS, "crop_name", cropn, "crop_id", f"crop {cropn}")
        else:
            cid, cname = PV, PV
        n += 1
        out.append((f"agrm-{n:03d}", sid, short, p5id, p5name, cid, cname, cat, act,
                    "Ministry of Agriculture and Farmers Welfare; Package005_Agriculture reconciliation",
                    "https://agricoop.gov.in/", CD, str(conf), VST, note))
    return out


# ===========================================================================
# 10. skill_scheme_mapping.csv  -> Package006_Skills_and_Training
# ===========================================================================
H_SKILL = ["mapping_id", "scheme_id", "scheme_short_name", "package006_scheme_id",
           "package006_scheme_name", "package006_skill_id", "package006_skill_name",
           "package006_certification_id", "package006_certification_name",
           "package006_provider_id", "package006_provider_name", "data_source",
           "source_url", "collection_date", "confidence_score",
           "verification_status", "notes"]

# (P007 sch, short, P006 scheme needle|None, skill needle|None, cert needle|None, provider needle|None, conf, note)
SKILL_LINKS = [
    ("sch-021", "PMKVY 4.0", "PMKVY 4.0", "Python Programming", "Skill India Certificate", None, 73, "Digital skills are a major PMKVY 4.0 job-role family"),
    ("sch-021", "PMKVY 4.0", "PMKVY 4.0", "Food Processing & Preservation", "Skill India Certificate", None, 72, "Food processing Qualification Packs are widely offered under PMKVY"),
    ("sch-021", "PMKVY 4.0", "PMKVY 4.0", "Precision Agriculture & IoT", "Skill India Certificate", None, 68, "Emerging job role; limited centre availability"),
    ("sch-021", "PMKVY 4.0", "Recognition of Prior Learning", "Welding (MIG/TIG/Arc)", "Recognition of Prior Learning (RPL)", None, 72, "RPL certifies existing informal-sector welders"),
    ("sch-022", "PM-NAPS", "PM-NAPS", "Automobile Mechanic", None, "Industrial Training Institutes (ITI) -- Telangana", 72, "Apprenticeship in automotive trades is ITI-anchored"),
    ("sch-022", "PM-NAPS", "PM-NAPS", "CNC Machine Operator", None, "Industrial Training Institutes (ITI) -- Andhra Pradesh", 71, "Machining apprenticeships run through ITI-linked establishments"),
    ("sch-023", "DDU-GKY", "DDU-GKY", "Garment Manufacturing", None, None, 70, "Apparel is a high-volume DDU-GKY placement sector"),
    ("sch-023", "DDU-GKY", "DDU-GKY", "Warehouse Management", None, None, 69, "Logistics is a growing rural-to-urban placement sector"),
    ("sch-024", "Skill Loan", "Skill Loan Scheme", "Full Stack Web Development", None, "Polytechnic Colleges (SBTET) -- Telangana", 68, "Longer high-fee courses are the typical skill-loan use case"),
    ("sch-018", "PM Vishwakarma", None, "Carpentry", None, None, 70, "PM Vishwakarma is not in Package006 v1.0.0; carpentry is a notified trade"),
    ("sch-018", "PM Vishwakarma", None, "Welding (MIG/TIG/Arc)", None, None, 69, "Blacksmith and metal trades are notified under the scheme"),
    ("sch-014", "PMEGP", None, None, None, None, 62, "EDP training is a mandatory PMEGP step, but Package006 v1.0.0 has no entrepreneurship skill record and no scheme counterpart, so both links are unasserted"),
]


def rows_skill():
    out = []
    n = 0
    for sid, short, p6s, skilln, certn, provn, conf, note in SKILL_LINKS:
        if p6s:
            p6id, p6name = must(P006_SCH, "scheme_name", p6s, "scheme_id", f"{short} in Package006")
        else:
            p6id, p6name = PV, PV
        skid, skname = (must(P006_SKILLS, "skill_name", skilln, "skill_id", f"skill {skilln}")
                        if skilln else (PV, PV))
        cid, cname = (must(P006_CERTS, "certification_name", certn, "certification_id", f"cert {certn}")
                      if certn else (PV, PV))
        pid, pname = (must(P006_PROV, "provider_name", provn, "provider_id", f"provider {provn}")
                      if provn else (PV, PV))
        n += 1
        out.append((f"skm-{n:03d}", sid, short, p6id, p6name, skid, skname, cid, cname,
                    pid, pname,
                    "Ministry of Skill Development and Entrepreneurship; Package006 reconciliation",
                    "https://msde.gov.in/", CD, str(conf), VST, note))
    return out


# ===========================================================================
# 11. industry_scheme_mapping.csv  -> Package004_Industries_and_Livelihoods
# ===========================================================================
H_IND = ["mapping_id", "scheme_id", "scheme_short_name",
         "package004_dataset", "package004_opportunity_name", "industry_sector",
         "investment_stage", "enterprise_size", "data_source", "source_url",
         "collection_date", "confidence_score", "verification_status", "notes"]

P004_SETS = {
    "food_agro_processing_micro_enterprises": (P004_FOOD, "name"),
    "construction_skilled_trade_services": (P004_CONST, "name"),
    "digital_technology_livelihoods": (P004_DIGI, "name"),
    "msme_entrepreneurship_support_schemes": (P004_MSME, "scheme_name"),
}

IND_LINKS = [
    ("sch-014", "PMEGP", "food_agro_processing_micro_enterprises", "Turmeric Processing & Powder-Making Unit", "Food Processing", "New enterprise (greenfield)", "Micro", 73, "PMEGP margin money is the standard route for a new spice unit"),
    ("sch-014", "PMEGP", "food_agro_processing_micro_enterprises", "Andhra-Style Pickle", "Food Processing", "New enterprise (greenfield)", "Micro", 72, "Classic PMEGP food-processing project profile"),
    ("sch-014", "PMEGP", "construction_skilled_trade_services", "Metal Fabrication", "Construction & Trades", "New enterprise (greenfield)", "Micro", 71, "Fabrication workshops are a common PMEGP activity"),
    ("sch-015", "PMMY", "food_agro_processing_micro_enterprises", "Small-Scale Flour/Atta Milling Unit", "Food Processing", "Working capital / small expansion", "Micro", 72, "Kishore-category MUDRA is typical for a small mill"),
    ("sch-015", "PMMY", "digital_technology_livelihoods", "Digital Marketing", "Technology Services", "Early stage", "Micro", 70, "Low-asset service business; MUDRA suits equipment and working capital"),
    ("sch-016", "Stand-Up India", "food_agro_processing_micro_enterprises", "Cold-Pressed Groundnut/Sesame Oil", "Food Processing", "New enterprise (greenfield)", "Small", 71, "Greenfield requirement fits a first-time SC/ST or woman promoter"),
    ("sch-017", "CGTMSE", "construction_skilled_trade_services", "Metal Fabrication", "Construction & Trades", "Growth (collateral-constrained)", "Micro to Small", 71, "Guarantee cover substitutes for absent collateral"),
    ("sch-019", "PMFME", "food_agro_processing_micro_enterprises", "Small-Scale Millet Processing Unit", "Food Processing", "Formalisation / upgradation", "Micro", 72, "Millets are a frequent ODOP product; PMFME is the fitted scheme"),
    ("sch-019", "PMFME", "food_agro_processing_micro_enterprises", "Chilli Processing, Grading & Powder-Making Unit", "Food Processing", "Formalisation / upgradation", "Micro", 72, "Guntur chilli is a strong ODOP candidate"),
    ("sch-019", "PMFME", "food_agro_processing_micro_enterprises", "FPO-Level Primary Millet Processing Unit", "Food Processing", "Collective enterprise", "Micro (FPO)", 71, "PMFME explicitly supports FPO and SHG collective units"),
    ("sch-020", "SISFS", "digital_technology_livelihoods", "Software Development Startup", "Technology", "Ideation to prototype", "Startup", 68, "Seed fund targets pre-revenue DPIIT-recognised startups"),
    ("sch-018", "PM Vishwakarma", "construction_skilled_trade_services", "Carpentry", "Construction & Trades", "Artisan / own-account", "Micro (artisan)", 70, "Carpenter is one of the eighteen notified trades"),
]


def rows_ind():
    out = []
    n = 0
    for sid, short, dsname, needle, sector, stage, size, conf, note in IND_LINKS:
        rows, key = P004_SETS[dsname]
        hits = [r for r in rows if needle.lower() in r[key].lower()]
        if len(hits) != 1:
            sys.exit(f"FATAL: {needle!r} matched {len(hits)} rows in Package004 {dsname}")
        n += 1
        out.append((f"indm-{n:03d}", sid, short, dsname, hits[0][key], sector, stage, size,
                    "Ministry of MSME; Package004_Industries reconciliation",
                    "https://msme.gov.in/", CD, str(conf), VST, note))
    return out


# ===========================================================================
# 12. district_scheme_mapping.csv  -> Package001_Geography
# ===========================================================================
H_DIST = ["mapping_id", "scheme_id", "scheme_short_name", "package001_dist_id",
          "dist_ref", "district_name", "state_scope", "district_level_agency",
          "application_channel", "district_specific_variation", "data_source",
          "source_url", "collection_date", "confidence_score",
          "verification_status", "notes"]

# Schemes whose application is genuinely mediated by a district-level institution.
# Central coverage is national; what varies by district is WHO you approach.
DIST_SCHEMES = [
    ("sch-014", "PMEGP", "District Industries Centre / KVIB", "Online application, district task force appraisal", 72,
     "Every district has a DIC; the task force is constituted at district level"),
    ("sch-034", "MGNREGS", "Gram Panchayat / District Programme Coordinator", "Offline work demand at Gram Panchayat", 73,
     "District Programme Coordinator is statutorily the District Collector or CEO"),
    ("sch-036", "PMAY-G", "District Rural Development Agency / Gram Panchayat", "Gram Sabha validation of the permanent wait list", 71,
     "Sanction and instalment release are administered at district level"),
    ("sch-005", "PM-KISAN", "District Agriculture Office / village revenue office", "Online self-registration or CSC-assisted", 72,
     "Land record verification is a district revenue function"),
    ("sch-031", "AB PM-JAY", "District hospital / empanelled facility; State Health Agency", "Card generation at CSC or facility", 71,
     "Empanelled hospital availability differs materially by district"),
]


def rows_dist():
    out = []
    n = 0
    for sid, short, agency, channel, conf, note in DIST_SCHEMES:
        for d in P001_DIST:
            state = "Telangana" if d["dist_ref"].startswith("TG") else "Andhra Pradesh"
            n += 1
            out.append((f"dsm-{n:04d}", sid, short, d["dist_id"], d["dist_ref"],
                        d["district_name"], state, agency, channel, PV,
                        "Package001_Geography district master; scheme guidelines",
                        MYSCH_URL, CD, str(conf), VST, note))
    return out


# ===========================================================================
# 14. scheme_application_status.csv
# ===========================================================================
H_STAT = ["status_id", "status_code", "status_name", "status_order", "status_group",
          "description", "typical_next_status", "is_terminal",
          "citizen_action_required", "data_source", "source_url",
          "collection_date", "confidence_score", "verification_status", "notes"]

STATUSES = [
    ("stat-001", "DRAFT", "Draft", "1", "Pre-submission", "Application created but not yet submitted", "SUBMITTED", "No", "Yes - complete and submit", 70, "Most portals retain drafts for a limited period"),
    ("stat-002", "SUBMITTED", "Submitted", "2", "In-process", "Application submitted and acknowledgement number issued", "UNDER_REVIEW", "No", "No - await verification", 72, "Acknowledgement number is the tracking key"),
    ("stat-003", "UNDER_REVIEW", "Under Review", "3", "In-process", "Application under verification by the implementing authority", "APPROVED", "No", "No - unless a query is raised", 71, "Multi-level verification is common (institution, district, state)"),
    ("stat-004", "QUERY_RAISED", "Query Raised / Sent Back", "4", "In-process", "Verifying authority has sought clarification or a corrected document", "UNDER_REVIEW", "No", "Yes - respond within the stated period", 69, "A frequent cause of rejection when the applicant does not respond in time"),
    ("stat-005", "APPROVED", "Approved / Sanctioned", "5", "Decided", "Application approved and benefit sanctioned", "DISBURSED", "No", "No - await disbursement", 72, "For credit-linked schemes, sanction precedes disbursement"),
    ("stat-006", "REJECTED", "Rejected", "6", "Decided", "Application rejected on eligibility or documentation grounds", "Not applicable (terminal)", "Yes", "Optional - grievance or reapplication", 71, "Rejection reasons should be recorded; appeal routes differ by scheme"),
    ("stat-007", "DISBURSED", "Disbursed", "7", "Fulfilled", "Benefit credited, delivered or service rendered", "CLOSED", "No", "No", 72, "For instalment schemes this status recurs per instalment"),
    ("stat-008", "CLOSED", "Closed", "8", "Fulfilled", "Benefit cycle complete or loan fully repaid", "Not applicable (terminal)", "Yes", "No", 70, "For recurring schemes, closure applies to a cycle rather than the enrolment"),
]


# ===========================================================================
# 15. scheme_ai_recommendations.csv
# ===========================================================================
H_AI = ["recommendation_id", "profile_code", "profile_description",
        "profile_attributes", "scheme_id", "scheme_short_name", "priority_score",
        "priority_rank", "recommendation_basis", "suggested_next_scheme_id",
        "related_scheme_ids", "future_opportunity", "data_source", "source_url",
        "collection_date", "confidence_score", "verification_status", "notes"]

# (profile_code, description, attributes, [(scheme_id, short, score, rank, basis, next_id, related, future)])
PROFILES = [
    ("PROF-STUDENT-SC", "Scheduled Caste student entering higher education from a low-income household",
     "category=SC; stage=post-matric; income=below ceiling; age=17-23", [
        ("sch-028", "PMS-SC", 92, 1, "Category and stage match exactly; oldest and widest SC post-matric scheme", "sch-026", "sch-026;sch-024", "Skill certification after graduation via PMKVY 4.0"),
        ("sch-026", "CSSS", 74, 2, "Applies only if the class XII percentile threshold is met", "sch-024", "sch-025;sch-028", "Higher education completion then skill loan for specialisation"),
        ("sch-024", "Skill Loan", 61, 3, "Relevant only for a fee-bearing vocational course alongside or after study", PV, "sch-021", "Employment through certified skilling"),
     ]),
    ("PROF-STUDENT-CLASS8", "Class VIII student in a government school, household below the income ceiling",
     "category=any; stage=class VIII; income=below ceiling; age=13-14", [
        ("sch-025", "NMMSS", 90, 1, "Precisely the target stage and income profile for this scheme", "sch-026", "sch-027;sch-030", "Continue to CSSS at higher-education stage"),
        ("sch-030", "PM POSHAN", 78, 2, "Automatic entitlement at the school, no application needed", PV, "sch-029", "Retention through secondary stage"),
     ]),
    ("PROF-FARMER-SMALL", "Small farmer with under two hectares, cultivating rice and chilli in a Telangana district",
     "occupation=farmer; landholding=small; crops=rice,chilli; state=Telangana", [
        ("sch-005", "PM-KISAN", 94, 1, "Land-holding farmer family; unconditional income support", "sch-007", "sch-006;sch-011", "Layer crop credit and insurance on the same land record"),
        ("sch-007", "KCC", 89, 2, "Working capital need is structural for chilli's high input cost", "sch-006", "sch-005;sch-012", "Interest subvention on prompt repayment"),
        ("sch-006", "PMFBY", 85, 3, "Both crops are notified and rainfall-exposed", "sch-008", "sch-007", "Yield-loss protection stabilises credit repayment"),
        ("sch-008", "PMKSY", 76, 4, "Micro-irrigation raises water efficiency; higher subsidy for small farmers", "sch-009", "sch-013", "Solar pump under PM-KUSUM after drip installation"),
        ("sch-011", "SHC", 72, 5, "Free diagnostic that improves input efficiency at zero cost", PV, "sch-010", "Organic conversion pathway via PKVY"),
     ]),
    ("PROF-FARMER-ORGANIC", "Farmer in a cluster converting to organic turmeric cultivation",
     "occupation=farmer; crops=turmeric; intent=organic conversion", [
        ("sch-010", "PKVY", 88, 1, "Cluster-based organic conversion is exactly this scheme's design", "sch-019", "sch-011;sch-005", "Certified organic turmeric commands an export premium"),
        ("sch-019", "PMFME", 80, 2, "Turmeric powder processing captures the value-add margin", "sch-012", "sch-014", "ODOP branding and export market access"),
        ("sch-012", "AIF", 68, 3, "Relevant once post-harvest storage or processing infrastructure is needed", PV, "sch-019", "Collective infrastructure through an FPO"),
     ]),
    ("PROF-WOMAN-ENTREPRENEUR", "Woman first-time entrepreneur planning a food processing micro unit",
     "gender=female; intent=new enterprise; sector=food processing; experience=first-time", [
        ("sch-016", "Stand-Up India", 88, 1, "Woman entrepreneur with a greenfield project is the exact target", "sch-017", "sch-014;sch-015", "Scale beyond micro into small enterprise"),
        ("sch-014", "PMEGP", 86, 2, "Margin money subsidy materially reduces the own-contribution burden", "sch-019", "sch-015;sch-017", "PMFME upgradation once formalised"),
        ("sch-019", "PMFME", 82, 3, "Sector-specific: designed for micro food processing formalisation", "sch-012", "sch-014", "Branding and marketing support for retail entry"),
        ("sch-017", "CGTMSE", 74, 4, "Removes the collateral barrier; invoked by the lender not the borrower", PV, "sch-015", "Larger credit lines as the unit grows"),
        ("sch-021", "PMKVY 4.0", 68, 5, "Food processing Qualification Pack training before or during setup", PV, "sch-018", "Certified skill improves lender confidence"),
     ]),
    ("PROF-YOUTH-RURAL", "Rural youth aged 22, class XII pass, seeking employment",
     "age=22; education=class XII; residence=rural; intent=employment", [
        ("sch-023", "DDU-GKY", 88, 1, "Placement-linked training designed for exactly this profile", "sch-021", "sch-021;sch-022", "Placement then upskilling on the job"),
        ("sch-021", "PMKVY 4.0", 84, 2, "Short-term NSQF training with certification and placement assistance", "sch-022", "sch-023;sch-024", "Apprenticeship or direct employment"),
        ("sch-022", "PM-NAPS", 79, 3, "Apprenticeship provides stipend plus workplace experience", "sch-015", "sch-021", "Regular employment or own enterprise"),
        ("sch-034", "MGNREGS", 66, 4, "Immediate income floor while training or job search continues", PV, "sch-035", "Not a career path; a consumption bridge"),
        ("sch-015", "PMMY", 62, 5, "Relevant only if the intent shifts from employment to self-employment", PV, "sch-014", "Micro enterprise as an alternative track"),
     ]),
    ("PROF-ARTISAN", "Traditional carpenter working on own account in a rural district",
     "occupation=artisan; trade=carpentry; employment=own-account; residence=rural", [
        ("sch-018", "PM Vishwakarma", 92, 1, "Carpenter is a notified trade; the scheme is purpose-built for this profile", "sch-015", "sch-014;sch-021", "Toolkit, credit and digital market access in one package"),
        ("sch-015", "PMMY", 76, 2, "Working capital for materials once the trade is formalised", "sch-017", "sch-014", "Larger credit as order volume grows"),
        ("sch-014", "PMEGP", 70, 3, "Applies if scaling from own-account work to a small workshop", PV, "sch-017", "Employment generation beyond the family"),
     ]),
    ("PROF-URBAN-POOR-FAMILY", "Urban low-income family of four with no health insurance and no pucca house",
     "residence=urban; income=EWS; household size=4; assets=none", [
        ("sch-031", "AB PM-JAY", 90, 1, "Catastrophic health expenditure is the single largest impoverishment risk", "sch-001", "sch-032;sch-039", "Health security enables asset accumulation"),
        ("sch-039", "NFSA/PDS", 86, 2, "Statutory food entitlement; immediate consumption relief", "sch-001", "sch-038", "Frees income for other needs"),
        ("sch-037", "PMAY-U", 80, 3, "EWS vertical with credit-linked interest subsidy", "sch-001", "sch-036", "Housing asset creation"),
        ("sch-001", "PMJDY", 78, 4, "Account is the precondition for every DBT-based benefit", "sch-002", "sch-002;sch-003", "Enables all other scheme transfers"),
        ("sch-002", "PMSBY", 70, 5, "Very low premium accident cover for the earning member", "sch-003", "sch-003;sch-004", "Life and pension cover as income stabilises"),
     ]),
    ("PROF-SENIOR-CITIZEN", "Rural citizen aged 68 below the poverty line with no formal pension",
     "age=68; residence=rural; income=BPL; pension=none", [
        ("sch-038", "NSAP", 90, 1, "Old age pension vertical matches age and income criteria exactly", "sch-039", "sch-039;sch-031", "State top-up materially increases the amount"),
        ("sch-039", "NFSA/PDS", 84, 2, "Food entitlement is the second pillar of old-age security", "sch-031", "sch-038", "Reduces cash needed for food"),
        ("sch-031", "AB PM-JAY", 82, 3, "No upper age limit; health risk is highest in this group", PV, "sch-032", "Cashless hospitalisation removes distress borrowing"),
     ]),
    ("PROF-TECH-STARTUP", "Two-person technology startup, DPIIT-recognised, pre-revenue",
     "sector=technology; stage=pre-revenue; recognition=DPIIT; team=2", [
        ("sch-020", "SISFS", 88, 1, "Pre-revenue DPIIT-recognised startup is the precise eligibility profile", "sch-017", "sch-015", "Follow-on venture funding after prototype validation"),
        ("sch-015", "PMMY", 64, 2, "Fits only if the venture is better characterised as a micro enterprise", PV, "sch-014", "Bridge finance before institutional rounds"),
        ("sch-017", "CGTMSE", 60, 3, "Relevant later, when seeking collateral-free bank credit", PV, "sch-015", "Debt without dilution as revenue begins"),
     ]),
]


def rows_ai():
    out = []
    n = 0
    for pcode, pdesc, pattr, recs in PROFILES:
        for sid, short, score, rank, basis, nxt, related, future in recs:
            n += 1
            out.append((f"rec-{n:03d}", pcode, pdesc, pattr, sid, short, str(score),
                        str(rank), basis, nxt, related, future,
                        "Rule-based synthesis over this package's eligibility_criteria.csv",
                        MYSCH_URL, CD, "60", VST,
                        "priority_score is a deterministic rule-engine input derived from "
                        "eligibility overlap, not an empirical outcome measure"))
    return out


def rows_status():
    return [(s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8],
             MYSCH, MYSCH_URL, CD, str(s[9]), VST, s[10]) for s in STATUSES]


if __name__ == "__main__":
    print("Generating Package007_Government_Schemes mapping datasets:\n")
    write("application_process.csv", H_AP, rows_process())
    write("education_scheme_mapping.csv", H_EDU, rows_edu())
    write("agriculture_scheme_mapping.csv", H_AGRI, rows_agri())
    write("skill_scheme_mapping.csv", H_SKILL, rows_skill())
    write("industry_scheme_mapping.csv", H_IND, rows_ind())
    write("district_scheme_mapping.csv", H_DIST, rows_dist())
    write("scheme_application_status.csv", H_STAT, rows_status())
    write("scheme_ai_recommendations.csv", H_AI, rows_ai())
    print("\nMapping generation complete.")
