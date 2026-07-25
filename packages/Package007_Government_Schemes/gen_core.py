#!/usr/bin/env python3
"""
Package007_Government_Schemes v1.0.0 — Core Dataset Generator

Builds the seven scheme-intrinsic datasets:
  1  scheme_categories.csv         24 categories
  2  government_schemes.csv        canonical scheme registry
  3  eligibility_criteria.csv      criterion rows per scheme
  4  required_documents.csv        document catalogue
  6  implementing_agencies.csv     agency catalogue
  7  scheme_benefits.csv           benefit rows per scheme
 13  financial_institutions.csv    lending/implementing institutions

Design note — this package is the CANONICAL scheme registry. Five already-released
packages carry domain scheme slices (Package002 scholarships 25, Package003 health
insurance 9, Package004 MSME support 18, Package005 agriculture 12, Package006 skill 15).
Package007 does not silently duplicate them: government_schemes.csv carries an
`also_in_package` column naming every package that already holds the scheme, so the
overlap is explicit and reconcilable rather than a hidden fork.

Source tiers (confidence ceiling 85, per project policy):
  Tier 1  Scheme's own portal, administering ministry, India.gov.in, MyScheme   70-85
  Tier 2  Government notification / gazette                                     62-74
  Tier 3  Official scheme guidelines and operational manuals                    56-69
  Tier 4  Ministry annual reports                                               45-55

No fabricated values. Any fact not confirmable in a public source is the bare
sentinel PENDING_VERIFICATION.
"""

import csv
from pathlib import Path

CD = "2026-07-25"
VST = "VST-NEEDS_REVIEW"
PV = "PENDING_VERIFICATION"
DATASETS = Path("datasets")


def write(filename, headers, rows):
    for i, r in enumerate(rows):
        if len(r) != len(headers):
            raise ValueError(f"{filename} row {i} ({r[0]}): {len(r)} values, expected {len(headers)}")
    with open(DATASETS / filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  {filename}: {len(rows)} rows x {len(headers)} cols")


# ===========================================================================
# 1. scheme_categories.csv — the 24 categories named in the specification
# ===========================================================================
H_CAT = ["category_id", "category_name", "category_group", "description",
         "primary_beneficiary", "typical_benefit_type", "data_source", "source_url",
         "collection_date", "confidence_score", "verification_status", "notes"]

INDIA = "India.gov.in national portal; MyScheme"
INDIA_URL = "https://www.india.gov.in/"
MYSCH = "MyScheme national scheme platform"
MYSCH_URL = "https://www.myscheme.gov.in/"

CATEGORIES = [
    ("cat-001", "Education", "Sector", "School and higher-education access, retention and quality support", "Students", "Grant; Fee reimbursement; Infrastructure", "Ministry of Education", "https://www.education.gov.in/", CD, "78", VST, "Overlaps Package002_Education"),
    ("cat-002", "Scholarships", "Sector", "Merit and means-based financial support for students", "Students", "Scholarship", "National Scholarship Portal", "https://scholarships.gov.in/", CD, "78", VST, "25 scholarship schemes already released in Package002"),
    ("cat-003", "Healthcare", "Sector", "Health insurance, treatment assistance and public health delivery", "Citizens; Patients", "Insurance; Treatment cover", "Ministry of Health and Family Welfare", "https://mohfw.gov.in/", CD, "77", VST, "Overlaps Package003_Healthcare"),
    ("cat-004", "Agriculture", "Sector", "Crop production, income support, insurance and farm infrastructure", "Farmers", "Grant; Subsidy; Insurance; Credit", "Ministry of Agriculture and Farmers Welfare", "https://agricoop.gov.in/", CD, "78", VST, "12 agriculture schemes already released in Package005"),
    ("cat-005", "MSME", "Sector", "Micro, small and medium enterprise finance, formalisation and market access", "Entrepreneurs; Enterprises", "Loan; Credit guarantee; Subsidy", "Ministry of MSME", "https://msme.gov.in/", CD, "77", VST, "Overlaps Package004; Package008_MSME will extend"),
    ("cat-006", "Women", "Beneficiary Group", "Schemes reserved for or prioritising women beneficiaries", "Women", "Loan; Grant; Training", "Ministry of Women and Child Development", "https://wcd.gov.in/", CD, "75", VST, "Cross-cutting; overlaps sector categories"),
    ("cat-007", "Youth", "Beneficiary Group", "Schemes targeting young citizens for skilling, employment and enterprise", "Youth (15-35)", "Training; Stipend; Loan", "Ministry of Youth Affairs and Sports", "https://yas.gov.in/", CD, "72", VST, "Age bands differ by scheme"),
    ("cat-008", "Scheduled Castes", "Beneficiary Group", "Schemes reserved for Scheduled Caste beneficiaries", "SC citizens", "Scholarship; Loan; Grant", "Ministry of Social Justice and Empowerment", "https://socialjustice.gov.in/", CD, "76", VST, "Caste certificate is a universal eligibility document here"),
    ("cat-009", "Scheduled Tribes", "Beneficiary Group", "Schemes reserved for Scheduled Tribe beneficiaries", "ST citizens", "Scholarship; Loan; Grant", "Ministry of Tribal Affairs", "https://tribal.nic.in/", CD, "76", VST, "Includes forest-rights and MFP-linked support"),
    ("cat-010", "Backward Classes", "Beneficiary Group", "Schemes for Other Backward Classes and Economically Backward Classes", "OBC/BC/EBC citizens", "Scholarship; Loan", "Ministry of Social Justice and Empowerment", "https://socialjustice.gov.in/", CD, "74", VST, "State BC/EBC lists differ from the central OBC list"),
    ("cat-011", "Minorities", "Beneficiary Group", "Schemes for notified minority communities", "Minority communities", "Scholarship; Loan; Skill training", "Ministry of Minority Affairs", "https://minorityaffairs.gov.in/", CD, "74", VST, "Six notified minority communities"),
    ("cat-012", "Senior Citizens", "Beneficiary Group", "Pension, health and welfare support for the elderly", "Citizens 60+", "Pension; Health cover", "Ministry of Social Justice and Empowerment", "https://socialjustice.gov.in/", CD, "73", VST, "Age threshold 60 for most; 80 for enhanced benefits"),
    ("cat-013", "Persons with Disabilities", "Beneficiary Group", "Support for persons with benchmark disabilities", "PwD citizens", "Scholarship; Aid; Pension", "Department of Empowerment of Persons with Disabilities", "https://disabilityaffairs.gov.in/", CD, "74", VST, "Requires UDID or disability certificate"),
    ("cat-014", "Employment", "Sector", "Wage employment, self-employment and job placement support", "Workers; Job seekers", "Wage; Stipend; Placement", "Ministry of Labour and Employment", "https://labour.gov.in/", CD, "75", VST, "Includes MGNREGA and urban livelihood missions"),
    ("cat-015", "Housing", "Sector", "Rural and urban housing construction and subsidy", "Households", "Grant; Interest subsidy", "Ministry of Housing and Urban Affairs", "https://mohua.gov.in/", CD, "76", VST, "PMAY has separate rural and urban verticals"),
    ("cat-016", "Insurance", "Instrument", "Life, accident and crop insurance with government premium support", "Citizens; Farmers", "Insurance", "Department of Financial Services", "https://financialservices.gov.in/", CD, "76", VST, "Jan Suraksha schemes; PMFBY for crops"),
    ("cat-017", "Social Welfare", "Sector", "Pension, food security and social assistance", "Vulnerable households", "Pension; Entitlement", "Ministry of Rural Development", "https://rural.nic.in/", CD, "74", VST, "Includes NSAP pension verticals"),
    ("cat-018", "Financial Inclusion", "Instrument", "Banking access, zero-balance accounts and direct benefit transfer", "Unbanked citizens", "Account access; DBT rails", "Department of Financial Services", "https://financialservices.gov.in/", CD, "77", VST, "PMJDY is the foundational layer for most DBT schemes"),
    ("cat-019", "Livelihood", "Sector", "Self-help group formation, community finance and rural livelihoods", "Rural households; SHGs", "Revolving fund; Credit linkage", "Ministry of Rural Development (DAY-NRLM)", "https://nrlm.gov.in/", CD, "74", VST, "SHG-based delivery model"),
    ("cat-020", "Entrepreneurship", "Sector", "New enterprise creation, incubation and first-generation entrepreneur support", "Entrepreneurs", "Loan; Margin money subsidy; Incubation", "Ministry of MSME; DPIIT", "https://msme.gov.in/", CD, "76", VST, "PMEGP, Stand-Up India, Startup India"),
    ("cat-021", "Digital India", "Sector", "Digital infrastructure, service delivery and digital literacy", "Citizens", "Service access; Training", "Ministry of Electronics and IT", "https://www.meity.gov.in/", CD, "73", VST, "CSC network is the rural delivery arm"),
    ("cat-022", "Innovation", "Sector", "Research, startup innovation and technology commercialisation", "Startups; Researchers", "Grant; Seed fund", "DPIIT; Department of Science and Technology", "https://dpiit.gov.in/", CD, "72", VST, "Startup India Seed Fund; Atal Innovation Mission"),
    ("cat-023", "Renewable Energy", "Sector", "Solar, wind and clean energy adoption subsidy", "Households; Enterprises; Farmers", "Subsidy; Capital support", "Ministry of New and Renewable Energy", "https://mnre.gov.in/", CD, "75", VST, "PM Surya Ghar; PM-KUSUM for agriculture"),
    ("cat-024", "Skill Development", "Sector", "Vocational training, apprenticeship and certification", "Youth; Workers", "Training; Stipend; Certification", "Ministry of Skill Development and Entrepreneurship", "https://msde.gov.in/", CD, "77", VST, "15 skill schemes already released in Package006"),
]

# ===========================================================================
# 2. government_schemes.csv — canonical registry
# ===========================================================================
H_SCH = ["scheme_id", "scheme_name", "short_name", "category_id", "category_name",
         "ministry", "department", "government_level", "launch_year", "objective",
         "benefit_summary", "financial_assistance", "subsidy_component",
         "loan_support", "coverage", "application_mode", "official_portal",
         "status", "also_in_package", "data_source", "source_url",
         "collection_date", "confidence_score", "verification_status", "notes"]

MOA = "Ministry of Agriculture and Farmers Welfare"
MSME_M = "Ministry of Micro, Small and Medium Enterprises"
MOE = "Ministry of Education"
MOHFW = "Ministry of Health and Family Welfare"
MSDE = "Ministry of Skill Development and Entrepreneurship"
MORD = "Ministry of Rural Development"
DFS = "Department of Financial Services, Ministry of Finance"

SCHEMES = [
    # --- Financial Inclusion / Insurance (foundational DBT layer) ---
    ("sch-001", "Pradhan Mantri Jan Dhan Yojana", "PMJDY", "cat-018", "Financial Inclusion",
     "Ministry of Finance", DFS, "Central", "2014",
     "Universal access to banking, remittance, credit, insurance and pension for unbanked households",
     "Zero-balance savings account with RuPay debit card, accident cover and overdraft facility",
     PV, "No", "Overdraft up to a prescribed limit after satisfactory operation", "National (all districts)",
     "Offline (bank branch); Online (bank portal); Business Correspondent", "https://pmjdy.gov.in/",
     "Active", PV, "PMJDY scheme portal; Department of Financial Services", "https://pmjdy.gov.in/",
     CD, "78", VST, "Foundational account layer that most DBT schemes credit into"),
    ("sch-002", "Pradhan Mantri Suraksha Bima Yojana", "PMSBY", "cat-016", "Insurance",
     "Ministry of Finance", DFS, "Central", "2015",
     "Affordable accidental death and disability insurance for bank account holders",
     "Accidental death and permanent disability cover on annual auto-debit premium",
     PV, "No", "No", "National; age 18-70 bank account holders",
     "Offline (bank branch); Online (net banking auto-debit)", "https://jansuraksha.gov.in/",
     "Active", PV, "Jan Suraksha portal; Department of Financial Services", "https://jansuraksha.gov.in/",
     CD, "76", VST, "Premium and cover amounts revised periodically; re-verify at portal"),
    ("sch-003", "Pradhan Mantri Jeevan Jyoti Bima Yojana", "PMJJBY", "cat-016", "Insurance",
     "Ministry of Finance", DFS, "Central", "2015",
     "Affordable life insurance for bank account holders",
     "Life cover on annual auto-debit premium, renewable yearly",
     PV, "No", "No", "National; age 18-50 bank account holders at entry",
     "Offline (bank branch); Online (net banking auto-debit)", "https://jansuraksha.gov.in/",
     "Active", PV, "Jan Suraksha portal; Department of Financial Services", "https://jansuraksha.gov.in/",
     CD, "76", VST, "Entry age capped at 50; cover continues to a prescribed exit age"),
    ("sch-004", "Atal Pension Yojana", "APY", "cat-012", "Senior Citizens",
     "Ministry of Finance", DFS, "Central", "2015",
     "Guaranteed minimum pension after age 60 for unorganised-sector workers",
     "Defined monthly pension from age 60 based on contribution slab chosen",
     PV, "No", "No", "National; age 18-40 at enrolment",
     "Offline (bank branch); Online (net banking)", "https://www.npscra.nsdl.co.in/scheme-details.php",
     "Active", PV, "PFRDA; NPS Trust", "https://www.pfrda.org.in/", CD, "74", VST,
     "Administered by PFRDA; income-tax payers excluded from co-contribution"),

    # --- Agriculture (all also in Package005) ---
    ("sch-005", "Pradhan Mantri Kisan Samman Nidhi", "PM-KISAN", "cat-004", "Agriculture",
     MOA, "Department of Agriculture and Farmers Welfare", "Central", "2019",
     "Direct income support to land-holding farmer families",
     "Income support paid in three equal instalments per year by direct benefit transfer",
     PV, "No", "No", "National; land-holding farmer families",
     "Online (PM-KISAN portal); Offline (Common Service Centre; village revenue office)",
     "https://pmkisan.gov.in/", "Active", "Package005_Agriculture",
     "PM-KISAN scheme portal", "https://pmkisan.gov.in/", CD, "78", VST,
     "Amount per instalment is set by scheme rules and revised by notification; re-verify at portal"),
    ("sch-006", "Pradhan Mantri Fasal Bima Yojana", "PMFBY", "cat-004", "Agriculture",
     MOA, "Department of Agriculture and Farmers Welfare", "Central", "2016",
     "Crop insurance against yield loss from natural calamity, pest and disease",
     "Sum-insured cover per notified crop with subsidised farmer premium share",
     PV, "Yes", "No", "National; notified crops in notified areas",
     "Online (PMFBY portal); Offline (bank; insurance intermediary; CSC)",
     "https://pmfby.gov.in/", "Active", "Package005_Agriculture",
     "PMFBY scheme portal", "https://pmfby.gov.in/", CD, "76", VST,
     "Farmer premium share differs for kharif, rabi and commercial/horticultural crops"),
    ("sch-007", "Kisan Credit Card", "KCC", "cat-004", "Agriculture",
     MOA, "Department of Agriculture and Farmers Welfare", "Central", "1998",
     "Short-term working capital credit for crop production and allied activity",
     "Revolving credit limit with interest subvention and prompt-repayment incentive",
     PV, "Yes", "Yes", "National; all categories of farmers including tenant farmers and sharecroppers",
     "Offline (bank branch); Online (bank portal)", "https://www.nabard.org/",
     "Active", "Package005_Agriculture", "NABARD; Department of Agriculture", "https://www.nabard.org/",
     CD, "76", VST, "Collateral-free up to a prescribed limit; extended to animal husbandry and fisheries"),
    ("sch-008", "Pradhan Mantri Krishi Sinchayee Yojana", "PMKSY", "cat-004", "Agriculture",
     "Ministry of Jal Shakti", "Department of Water Resources", "Central", "2015",
     "Expand irrigation coverage and improve water-use efficiency (Per Drop More Crop)",
     "Capital subsidy on micro-irrigation systems and watershed development support",
     PV, "Yes", "No", "National; differs by command and non-command area",
     "Offline (district or block agriculture office); Online (state portal)",
     "https://pmksy.gov.in/", "Active", "Package005_Agriculture",
     "PMKSY scheme portal", "https://pmksy.gov.in/", CD, "74", VST,
     "Subsidy share differs by state and farmer category (small/marginal vs other)"),
    ("sch-009", "Sub-Mission on Agricultural Mechanization", "SMAM", "cat-004", "Agriculture",
     MOA, "Department of Agriculture and Farmers Welfare", "Central", "2014",
     "Increase farm mechanisation reach for small and marginal holdings",
     "Capital subsidy on farm machinery purchase and custom-hiring centre establishment",
     PV, "Yes", "No", "National; individual farmers, SHGs, FPOs and cooperatives",
     "Online (state agriculture portal); Offline (district agriculture office)",
     "https://agrimachinery.nic.in/", "Active", "Package005_Agriculture",
     "Farm Mechanization portal; Department of Agriculture", "https://agrimachinery.nic.in/",
     CD, "75", VST, "Subsidy percentage differs for SC/ST/small/marginal/women farmers"),
    ("sch-010", "Paramparagat Krishi Vikas Yojana", "PKVY", "cat-004", "Agriculture",
     MOA, "Department of Agriculture and Farmers Welfare", "Central", "2015",
     "Promote organic farming through cluster-based conversion and certification support",
     "Per-hectare assistance across a three-year conversion cycle plus certification support",
     PV, "Yes", "No", "National; cluster-based (minimum farmer group per cluster)",
     "Offline (district agriculture office); Online (state portal)",
     "https://agricoop.gov.in/", "Active", "Package005_Agriculture",
     "Department of Agriculture and Farmers Welfare", "https://agricoop.gov.in/",
     CD, "72", VST, "Operates on a cluster model; individual application is not the route"),
    ("sch-011", "Soil Health Card Scheme", "SHC", "cat-004", "Agriculture",
     MOA, "Department of Agriculture and Farmers Welfare", "Central", "2015",
     "Provide farmers with soil nutrient status and fertiliser recommendations",
     "Free soil testing and a nutrient-recommendation card per holding",
     "Not applicable (service, not cash)", "No", "No", "National",
     "Offline (soil testing laboratory; village agriculture office); Online (SHC portal)",
     "https://soilhealth.dac.gov.in/", "Active", "Package005_Agriculture",
     "Soil Health Card portal", "https://soilhealth.dac.gov.in/", CD, "74", VST,
     "Service delivery scheme; no cash transfer component"),
    ("sch-012", "Agriculture Infrastructure Fund", "AIF", "cat-004", "Agriculture",
     MOA, "Department of Agriculture and Farmers Welfare", "Central", "2020",
     "Finance post-harvest management and community farming asset creation",
     "Interest subvention and credit guarantee on term loans for eligible projects",
     PV, "No", "Yes", "National; FPOs, PACS, cooperatives, agri-entrepreneurs, startups",
     "Online (AIF portal); Offline (lending bank)", "https://agriinfra.dac.gov.in/",
     "Active", "Package005_Agriculture", "Agriculture Infrastructure Fund portal",
     "https://agriinfra.dac.gov.in/", CD, "72", VST,
     "Interest subvention applies up to a prescribed loan ceiling per project"),
    ("sch-013", "Pradhan Mantri Kisan Urja Suraksha evam Utthaan Mahabhiyan", "PM-KUSUM", "cat-023", "Renewable Energy",
     "Ministry of New and Renewable Energy", "MNRE", "Central", "2019",
     "Solarise agriculture pumps and enable farmer solar power generation",
     "Capital subsidy on standalone solar pumps, grid-connected pump solarisation and small solar plants",
     PV, "Yes", "Yes", "National; three components (A, B, C) with differing eligibility",
     "Online (state nodal agency portal); Offline (DISCOM; state nodal agency)",
     "https://pmkusum.mnre.gov.in/", "Active", PV,
     "PM-KUSUM portal; Ministry of New and Renewable Energy", "https://pmkusum.mnre.gov.in/",
     CD, "72", VST, "Central and state subsidy shares plus farmer contribution; ratios differ by component"),

    # --- MSME / Entrepreneurship (overlap Package004) ---
    ("sch-014", "Prime Minister's Employment Generation Programme", "PMEGP", "cat-020", "Entrepreneurship",
     MSME_M, "Office of Development Commissioner (MSME); KVIC", "Central", "2008",
     "Generate self-employment through micro-enterprise creation in rural and urban areas",
     "Bank loan with margin money subsidy on project cost",
     PV, "Yes", "Yes", "National; individuals above 18, SHGs, institutions, cooperatives",
     "Online (PMEGP e-portal)", "https://www.kviconline.gov.in/pmegpeportal/",
     "Active", "Package004_Industries_and_Livelihoods", "PMEGP e-portal; KVIC",
     "https://www.kviconline.gov.in/pmegpeportal/", CD, "76", VST,
     "Margin money subsidy percentage differs by category (general vs special) and area (rural vs urban)"),
    ("sch-015", "Pradhan Mantri MUDRA Yojana", "PMMY", "cat-005", "MSME",
     "Ministry of Finance", DFS, "Central", "2015",
     "Collateral-free institutional credit to non-farm micro enterprises",
     "Term loan or working capital under Shishu, Kishore, Tarun and Tarun Plus categories",
     PV, "No", "Yes", "National; non-corporate non-farm micro enterprises",
     "Offline (bank; NBFC; MFI); Online (Jan Samarth portal)", "https://www.mudra.org.in/",
     "Active", "Package004_Industries_and_Livelihoods", "MUDRA; Department of Financial Services",
     "https://www.mudra.org.in/", CD, "77", VST,
     "Loan ceilings per category are revised by notification; re-verify at portal"),
    ("sch-016", "Stand-Up India Scheme", "Stand-Up India", "cat-008", "Scheduled Castes",
     "Ministry of Finance", DFS, "Central", "2016",
     "Facilitate bank loans to SC, ST and women entrepreneurs for greenfield enterprises",
     "Composite bank loan (term loan plus working capital) for a first-time greenfield venture",
     PV, "No", "Yes", "National; SC, ST and women entrepreneurs above 18",
     "Online (Stand-Up India portal); Offline (scheduled commercial bank)",
     "https://www.standupmitra.in/", "Active", "Package004_Industries_and_Livelihoods",
     "Stand-Up India portal", "https://www.standupmitra.in/", CD, "75", VST,
     "Greenfield requirement: applicant must be a first-time entrepreneur in that activity"),
    ("sch-017", "Credit Guarantee Fund Trust for Micro and Small Enterprises", "CGTMSE", "cat-005", "MSME",
     MSME_M, "Office of Development Commissioner (MSME); SIDBI", "Central", "2000",
     "Enable collateral-free credit to micro and small enterprises through guarantee cover",
     "Guarantee cover to the lender on eligible credit facilities, removing the collateral barrier",
     "Not applicable (guarantee to lender, not cash to borrower)", "No", "Yes",
     "National; micro and small enterprises borrowing from member lending institutions",
     "Offline (through the lending institution; not a direct citizen application)",
     "https://www.cgtmse.in/", "Active", "Package004_Industries_and_Livelihoods",
     "CGTMSE", "https://www.cgtmse.in/", CD, "74", VST,
     "The borrower does not apply directly; the lender invokes cover"),
    ("sch-018", "PM Vishwakarma", "PM Vishwakarma", "cat-020", "Entrepreneurship",
     MSME_M, "Ministry of MSME", "Central", "2023",
     "End-to-end support to traditional artisans and craftspeople in eighteen trades",
     "Skill training with stipend, toolkit incentive, collateral-free credit and digital/marketing support",
     PV, "Yes", "Yes", "National; artisans in eighteen notified traditional trades",
     "Online (PM Vishwakarma portal); Offline (Common Service Centre)",
     "https://pmvishwakarma.gov.in/", "Active", "Package004_Industries_and_Livelihoods",
     "PM Vishwakarma portal", "https://pmvishwakarma.gov.in/", CD, "73", VST,
     "Multi-component scheme; credit is released in tranches conditional on training"),
    ("sch-019", "PM Formalisation of Micro Food Processing Enterprises", "PMFME", "cat-005", "MSME",
     "Ministry of Food Processing Industries", "MoFPI", "Central", "2020",
     "Formalise and upgrade micro food-processing enterprises with a One District One Product focus",
     "Credit-linked capital subsidy on project cost, plus seed capital to SHG members and branding support",
     PV, "Yes", "Yes", "National; individual micro food processors, SHGs, FPOs, cooperatives",
     "Online (PMFME portal)", "https://pmfme.mofpi.gov.in/", "Active", PV,
     "PMFME portal; Ministry of Food Processing Industries", "https://pmfme.mofpi.gov.in/",
     CD, "73", VST, "Subsidy is capped per unit; ODOP alignment affects prioritisation"),
    ("sch-020", "Startup India Seed Fund Scheme", "SISFS", "cat-022", "Innovation",
     "Ministry of Commerce and Industry", "DPIIT", "Central", "2021",
     "Provide early-stage capital for proof of concept, prototype and market entry",
     "Grant for validation and prototyping, plus convertible debenture or debt for scale-up",
     PV, "No", "Yes", "National; DPIIT-recognised startups incorporated within a prescribed period",
     "Online (Startup India portal, via selected incubators)", "https://seedfund.startupindia.gov.in/",
     "Active", "Package004_Industries_and_Livelihoods", "Startup India Seed Fund portal",
     "https://seedfund.startupindia.gov.in/", CD, "72", VST,
     "Applications are routed through empanelled incubators, not filed directly with DPIIT"),

    # --- Skill Development (overlap Package006) ---
    ("sch-021", "Pradhan Mantri Kaushal Vikas Yojana 4.0", "PMKVY 4.0", "cat-024", "Skill Development",
     MSDE, "MSDE; NSDC", "Central", "2015",
     "Short-term skill training, upskilling and Recognition of Prior Learning with certification",
     "Free NSQF-aligned training with assessment, certification and placement assistance",
     PV, "No", "No", "National; youth and workers, with RPL for existing workers",
     "Online (Skill India Digital); Offline (empanelled training centre)",
     "https://www.skillindiadigital.gov.in/", "Active", "Package006_Skills_and_Training",
     "MSDE; NSDC; Skill India Digital", "https://www.skillindiadigital.gov.in/",
     CD, "76", VST, "Successive versions (1.0 to 4.0) changed funding and delivery model"),
    ("sch-022", "Pradhan Mantri National Apprenticeship Promotion Scheme", "PM-NAPS", "cat-024", "Skill Development",
     MSDE, "Directorate General of Training", "Central", "2016",
     "Promote apprenticeship training by sharing stipend cost with employers",
     "Government share of apprentice stipend reimbursed to the employer via DBT",
     PV, "No", "No", "National; establishments engaging apprentices and the apprentices themselves",
     "Online (apprenticeshipindia.gov.in)", "https://www.apprenticeshipindia.gov.in/",
     "Active", "Package006_Skills_and_Training", "Apprenticeship India portal; DGT",
     "https://www.apprenticeshipindia.gov.in/", CD, "75", VST,
     "Formerly NAPS; stipend-sharing ratio set by scheme guidelines"),
    ("sch-023", "Deen Dayal Upadhyaya Grameen Kaushalya Yojana", "DDU-GKY", "cat-014", "Employment",
     MORD, "Ministry of Rural Development", "Central", "2014",
     "Placement-linked skill training for rural poor youth",
     "Free residential or non-residential training with mandatory placement linkage and post-placement support",
     PV, "No", "No", "National; rural youth 15-35 from poor households (relaxed for vulnerable groups)",
     "Offline (project implementing agency); Online (Kaushal Panjee)",
     "https://ddugky.gov.in/", "Active", "Package006_Skills_and_Training",
     "DDU-GKY portal; Ministry of Rural Development", "https://ddugky.gov.in/",
     CD, "74", VST, "Placement percentage is a contractual obligation on the training partner"),
    ("sch-024", "Skill Loan Scheme", "Skill Loan", "cat-024", "Skill Development",
     DFS, "Indian Banks' Association model scheme", "Central", "2015",
     "Institutional credit for vocational training and skill courses",
     "Collateral-free education loan for skill courses with moratorium during training",
     PV, "No", "Yes", "National; candidates admitted to eligible NSQF-aligned courses",
     "Online (Jan Samarth / Vidya Lakshmi); Offline (bank branch)",
     "https://www.jansamarth.in/", "Active", "Package006_Skills_and_Training",
     "Indian Banks' Association model scheme; Department of Financial Services",
     "https://www.jansamarth.in/", CD, "70", VST,
     "Loan ceiling and eligible-course list are set by the IBA model scheme"),

    # --- Education / Scholarships (overlap Package002) ---
    ("sch-025", "National Means-cum-Merit Scholarship Scheme", "NMMSS", "cat-002", "Scholarships",
     MOE, "Department of School Education and Literacy", "Central", "2008",
     "Arrest dropout at class VIII and encourage continuation to secondary stage",
     "Annual scholarship to selected students from class IX to XII, paid by DBT",
     PV, "No", "No", "National; class VIII students below a prescribed parental income ceiling",
     "Online (National Scholarship Portal)", "https://scholarships.gov.in/",
     "Active", "Package002_Education", "National Scholarship Portal; Ministry of Education",
     "https://scholarships.gov.in/", CD, "76", VST,
     "Selection is by state-conducted examination; renewal requires prescribed marks"),
    ("sch-026", "Central Sector Scheme of Scholarships for College and University Students", "CSSS", "cat-002", "Scholarships",
     MOE, "Department of Higher Education", "Central", "2008",
     "Support meritorious students from low-income families in higher education",
     "Annual scholarship for graduation and post-graduation, paid by DBT",
     PV, "No", "No", "National; top percentile of class XII boards below an income ceiling",
     "Online (National Scholarship Portal)", "https://scholarships.gov.in/",
     "Active", "Package002_Education", "National Scholarship Portal; Ministry of Education",
     "https://scholarships.gov.in/", CD, "75", VST,
     "Quota is allocated by board and stream; professional-course rates differ"),
    ("sch-027", "PM Young Achievers Scholarship Award Scheme for Vibrant India", "PM-YASASVI", "cat-010", "Backward Classes",
     "Ministry of Social Justice and Empowerment", "Department of Social Justice and Empowerment", "Central", "2021",
     "Scholarship support for OBC, EBC and DNT students at school and higher-education stages",
     "Pre-matric and post-matric scholarship, and top-class school education support",
     PV, "No", "No", "National; OBC, EBC and DNT students below an income ceiling",
     "Online (National Scholarship Portal / YASASVI portal)", "https://yet.nta.ac.in/",
     "Active", "Package002_Education", "Ministry of Social Justice and Empowerment; NTA",
     "https://socialjustice.gov.in/", CD, "72", VST,
     "Consolidated several earlier OBC/EBC/DNT scholarship schemes"),
    ("sch-028", "Post-Matric Scholarship for Scheduled Caste Students", "PMS-SC", "cat-008", "Scheduled Castes",
     "Ministry of Social Justice and Empowerment", "Department of Social Justice and Empowerment", "Central", "1944",
     "Enable SC students to pursue post-matriculation education",
     "Maintenance allowance, fee reimbursement and additional allowances",
     PV, "No", "No", "National; SC students below a prescribed parental income ceiling",
     "Online (National Scholarship Portal; state portal)", "https://scholarships.gov.in/",
     "Active", PV, "Ministry of Social Justice and Empowerment; National Scholarship Portal",
     "https://socialjustice.gov.in/", CD, "74", VST,
     "One of India's oldest continuing scholarship schemes; delivered largely through states"),
    ("sch-029", "Samagra Shiksha", "Samagra Shiksha", "cat-001", "Education",
     MOE, "Department of School Education and Literacy", "Central", "2018",
     "Integrated school education programme from pre-school to class XII",
     "Infrastructure, teacher training, learning materials and equity interventions to states",
     PV, "No", "No", "National; delivered to states, not individual applicants",
     "Not applicable (state-implemented programme, no citizen application)",
     "https://samagra.education.gov.in/", "Active", PV,
     "Samagra Shiksha portal; Ministry of Education", "https://samagra.education.gov.in/",
     CD, "73", VST, "Institutional scheme: schools and states are beneficiaries, not individuals"),
    ("sch-030", "PM Poshan Shakti Nirman", "PM POSHAN", "cat-001", "Education",
     MOE, "Department of School Education and Literacy", "Central", "2021",
     "Provide one hot cooked meal to school children to improve nutrition and attendance",
     "Hot cooked mid-day meal in government and government-aided schools",
     "Not applicable (in-kind entitlement)", "No", "No",
     "National; children in classes I-VIII (and pre-primary in some states) in eligible schools",
     "Not applicable (automatic entitlement on school enrolment)",
     "https://pmposhan.education.gov.in/", "Active", PV,
     "PM POSHAN portal; Ministry of Education", "https://pmposhan.education.gov.in/",
     CD, "74", VST, "Formerly the Mid-Day Meal Scheme; entitlement, not application-based"),

    # --- Healthcare (overlap Package003) ---
    ("sch-031", "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana", "AB PM-JAY", "cat-003", "Healthcare",
     MOHFW, "National Health Authority", "Central", "2018",
     "Health cover for secondary and tertiary hospitalisation for poor and vulnerable families",
     "Cashless family floater hospitalisation cover per year at empanelled hospitals",
     PV, "No", "No", "National; families identified by deprivation criteria, plus state extensions",
     "Offline (empanelled hospital; Ayushman Mitra; CSC); Online (beneficiary portal)",
     "https://pmjay.gov.in/", "Active", "Package003_Healthcare",
     "National Health Authority; PM-JAY portal", "https://pmjay.gov.in/", CD, "77", VST,
     "Cover amount per family per year is set by scheme rules; several states run converged schemes"),
    ("sch-032", "Ayushman Bharat Health and Wellness Centres", "AB-HWC", "cat-003", "Healthcare",
     MOHFW, "National Health Mission", "Central", "2018",
     "Deliver comprehensive primary health care closer to the community",
     "Free essential drugs, diagnostics, screening and teleconsultation at upgraded facilities",
     "Not applicable (service delivery)", "No", "No", "National; universal at the facility level",
     "Not applicable (walk-in service at facility)", "https://ab-hwc.nhp.gov.in/",
     "Active", PV, "National Health Mission; Ministry of Health and Family Welfare",
     "https://ab-hwc.nhp.gov.in/", CD, "72", VST,
     "Renamed Ayushman Arogya Mandir; infrastructure scheme with no citizen application"),
    ("sch-033", "Pradhan Mantri Matru Vandana Yojana", "PMMVY", "cat-006", "Women",
     "Ministry of Women and Child Development", "Ministry of Women and Child Development", "Central", "2017",
     "Partial wage compensation and nutrition support for pregnant and lactating mothers",
     "Conditional cash transfer in instalments on meeting maternal and child health conditions",
     PV, "No", "No", "National; pregnant women and lactating mothers, conditions apply by birth order",
     "Online (PMMVY portal); Offline (Anganwadi centre; approved health facility)",
     "https://pmmvy.wcd.gov.in/", "Active", PV, "PMMVY portal; Ministry of Women and Child Development",
     "https://pmmvy.wcd.gov.in/", CD, "73", VST,
     "Instalment structure and birth-order conditions revised in the Mission Shakti reorganisation"),

    # --- Employment / Livelihood / Housing / Welfare ---
    ("sch-034", "Mahatma Gandhi National Rural Employment Guarantee Scheme", "MGNREGS", "cat-014", "Employment",
     MORD, "Department of Rural Development", "Central", "2006",
     "Legal guarantee of wage employment days per rural household per financial year",
     "Guaranteed unskilled manual wage employment with statutory wage paid to a bank or post office account",
     PV, "No", "No", "National (rural); every rural household demanding work",
     "Offline (Gram Panchayat work demand); Online (NREGASoft)",
     "https://nrega.nic.in/", "Active", PV, "MGNREGA portal; Ministry of Rural Development",
     "https://nrega.nic.in/", CD, "77", VST,
     "Rights-based statutory entitlement under the MGNREG Act 2005, not a discretionary scheme"),
    ("sch-035", "Deendayal Antyodaya Yojana - National Rural Livelihoods Mission", "DAY-NRLM", "cat-019", "Livelihood",
     MORD, "Department of Rural Development", "Central", "2011",
     "Mobilise rural poor households into self-help groups and build sustainable livelihoods",
     "Revolving fund and community investment support to SHGs, plus bank credit linkage",
     PV, "No", "Yes", "National (rural); rural poor households through SHG membership",
     "Offline (SHG formation via village organisation and block unit)",
     "https://nrlm.gov.in/", "Active", PV, "DAY-NRLM portal; Ministry of Rural Development",
     "https://nrlm.gov.in/", CD, "74", VST,
     "Delivery is through SHG federations; individuals cannot apply directly"),
    ("sch-036", "Pradhan Mantri Awas Yojana - Gramin", "PMAY-G", "cat-015", "Housing",
     MORD, "Department of Rural Development", "Central", "2016",
     "Provide a pucca house with basic amenities to eligible rural households",
     "Unit assistance in instalments, plus MGNREGA labour days and toilet convergence",
     PV, "Yes", "No", "National (rural); households identified by prescribed deprivation criteria",
     "Offline (Gram Panchayat; block office); Online (AwaasSoft)",
     "https://pmayg.nic.in/", "Active", PV, "PMAY-G portal; Ministry of Rural Development",
     "https://pmayg.nic.in/", CD, "75", VST,
     "Unit assistance differs for plain and hilly/difficult areas"),
    ("sch-037", "Pradhan Mantri Awas Yojana - Urban", "PMAY-U", "cat-015", "Housing",
     "Ministry of Housing and Urban Affairs", "MoHUA", "Central", "2015",
     "Provide affordable housing to urban poor including a credit-linked interest subsidy",
     "Interest subsidy on home loans, plus assistance under beneficiary-led and partnership verticals",
     PV, "Yes", "Yes", "National (urban); EWS, LIG and MIG categories by vertical",
     "Online (PMAY-U portal); Offline (urban local body; CSC)",
     "https://pmay-urban.gov.in/", "Active", PV, "PMAY-U portal; Ministry of Housing and Urban Affairs",
     "https://pmay-urban.gov.in/", CD, "74", VST,
     "Four verticals with different eligibility; CLSS operated through lending institutions"),
    ("sch-038", "National Social Assistance Programme", "NSAP", "cat-017", "Social Welfare",
     MORD, "Department of Rural Development", "Central", "1995",
     "Social assistance pensions for the elderly, widows and persons with disabilities below poverty line",
     "Monthly pension under old age, widow and disability verticals, with state top-up",
     PV, "No", "No", "National; BPL households in the respective beneficiary categories",
     "Offline (Gram Panchayat; municipal office); Online (NSAP portal)",
     "https://nsap.nic.in/", "Active", PV, "NSAP portal; Ministry of Rural Development",
     "https://nsap.nic.in/", CD, "73", VST,
     "Central rates are low; most states add a substantial top-up, so the amount received varies widely"),
    ("sch-039", "National Food Security Act entitlements (Public Distribution System)", "NFSA/PDS", "cat-017", "Social Welfare",
     "Ministry of Consumer Affairs, Food and Public Distribution", "Department of Food and Public Distribution", "Central", "2013",
     "Legal entitlement to subsidised food grain for priority households and AAY families",
     "Subsidised food grain per person per month through fair price shops; portable via One Nation One Ration Card",
     "Not applicable (in-kind entitlement)", "Yes", "No",
     "National; priority households and Antyodaya Anna Yojana families",
     "Offline (fair price shop; district supply office); Online (state PDS portal)",
     "https://dfpd.gov.in/", "Active", PV,
     "Department of Food and Public Distribution", "https://dfpd.gov.in/", CD, "74", VST,
     "Statutory entitlement under the NFSA 2013; ration card is the access instrument"),
    ("sch-040", "PM Surya Ghar: Muft Bijli Yojana", "PM Surya Ghar", "cat-023", "Renewable Energy",
     "Ministry of New and Renewable Energy", "MNRE", "Central", "2024",
     "Enable residential rooftop solar adoption with free electricity up to a monthly limit",
     "Central financial assistance on rooftop solar capacity plus concessional loan access",
     PV, "Yes", "Yes", "National; residential electricity consumers owning a suitable roof",
     "Online (National Portal for Rooftop Solar)", "https://pmsuryaghar.gov.in/",
     "Active", PV, "PM Surya Ghar portal; Ministry of New and Renewable Energy",
     "https://pmsuryaghar.gov.in/", CD, "71", VST,
     "Launched 2024; subsidy slabs by sanctioned capacity, revised by notification"),
]

# ===========================================================================
# 3. eligibility_criteria.csv
# ===========================================================================
H_ELIG = ["criterion_id", "scheme_id", "scheme_short_name", "criterion_type",
          "criterion_value", "is_mandatory", "verification_document_hint",
          "data_source", "source_url", "collection_date", "confidence_score",
          "verification_status", "notes"]

# (scheme_id, short, type, value, mandatory, doc_hint, conf, note)
ELIG = [
    ("sch-001", "PMJDY", "Age", "10 years and above (minor accounts with guardian)", "Yes", "Aadhaar", 74, "Minor accounts operated with a guardian"),
    ("sch-001", "PMJDY", "Citizenship", "Indian resident", "Yes", "Aadhaar", 74, "Resident status, not necessarily domicile of the branch state"),
    ("sch-002", "PMSBY", "Age", "18 to 70 years", "Yes", "Aadhaar", 74, "Cover ceases at the prescribed exit age"),
    ("sch-002", "PMSBY", "Banking", "Holds a savings bank account with auto-debit consent", "Yes", "Bank Passbook", 74, "Auto-debit consent is the enrolment mechanism"),
    ("sch-003", "PMJJBY", "Age", "18 to 50 years at entry", "Yes", "Aadhaar", 74, "Entry age capped at 50; existing cover continues to exit age"),
    ("sch-004", "APY", "Age", "18 to 40 years at enrolment", "Yes", "Aadhaar", 72, "Minimum 20 years of contribution by design"),
    ("sch-004", "APY", "Income", "Income-tax payers are excluded from government co-contribution", "No", "PAN", 70, "Exclusion applies to co-contribution, not to enrolment"),
    ("sch-005", "PM-KISAN", "Land Holding", "Cultivable land held in the applicant's name", "Yes", "Land Records", 76, "Institutional landholders excluded"),
    ("sch-005", "PM-KISAN", "Exclusion", "Income-tax payers, professionals and higher-grade government employees excluded", "Yes", "PAN", 74, "Exclusion list defined in scheme guidelines"),
    ("sch-006", "PMFBY", "Occupation", "Cultivator of a notified crop in a notified area", "Yes", "Land Records", 74, "Includes tenant farmers and sharecroppers with valid documentation"),
    ("sch-007", "KCC", "Occupation", "Farmer, including tenant farmer, oral lessee and sharecropper", "Yes", "Land Records", 74, "Extended to animal husbandry and fisheries activity"),
    ("sch-008", "PMKSY", "Land Holding", "Cultivable land with an assured water source", "Yes", "Land Records", 72, "Subsidy share differs by holding size category"),
    ("sch-009", "SMAM", "Category", "Higher subsidy for SC, ST, small, marginal and women farmers", "No", "Caste Certificate", 73, "Category affects subsidy percentage, not eligibility"),
    ("sch-010", "PKVY", "Other", "Membership of a farmer cluster meeting the minimum group size", "Yes", PV, 70, "Cluster-based; individual application is not the route"),
    ("sch-011", "SHC", "Occupation", "All farmers holding cultivable land; no income or category test", "Yes", "Land Records", 72, "Universal within the farmer population; service scheme with no screening"),
    ("sch-012", "AIF", "Business Size", "FPO, PACS, cooperative, agri-entrepreneur or startup", "Yes", "Udyam Registration", 70, "Individual farmers are eligible only for certain project types"),
    ("sch-013", "PM-KUSUM", "Occupation", "Farmer, farmer group, panchayat or cooperative depending on component", "Yes", "Land Records", 70, "Three components with materially different eligibility"),
    ("sch-014", "PMEGP", "Age", "18 years and above", "Yes", "Aadhaar", 75, "No upper age limit"),
    ("sch-014", "PMEGP", "Education", "Class VIII pass required above a prescribed project cost threshold", "No", "Educational Certificates", 73, "Applies only above the cost threshold"),
    ("sch-014", "PMEGP", "Other", "New enterprise only; existing units and prior subsidy beneficiaries excluded", "Yes", PV, 74, "Greenfield requirement"),
    ("sch-015", "PMMY", "Business Size", "Non-corporate, non-farm micro or small enterprise", "Yes", "Udyam Registration", 75, "Agriculture allied activities included; crop loans excluded"),
    ("sch-016", "Stand-Up India", "Category", "SC, ST or woman entrepreneur", "Yes", "Caste Certificate", 74, "For non-individual entities, 51 percent holding by SC/ST/women required"),
    ("sch-016", "Stand-Up India", "Other", "Greenfield project; applicant must be a first-time entrepreneur in that activity", "Yes", PV, 73, "Greenfield is the defining condition"),
    ("sch-017", "CGTMSE", "Business Size", "Micro or small enterprise as defined under the MSMED Act", "Yes", "Udyam Registration", 73, "Borrower does not apply; the lender invokes guarantee cover"),
    ("sch-018", "PM Vishwakarma", "Occupation", "Artisan or craftsperson working in one of eighteen notified trades", "Yes", PV, 72, "Family-based traditional trade practice is the qualifying basis"),
    ("sch-018", "PM Vishwakarma", "Age", "18 years and above", "Yes", "Aadhaar", 72, "Self-employed in the trade on an own-account basis"),
    ("sch-019", "PMFME", "Business Size", "Micro food-processing enterprise, SHG member, FPO or cooperative", "Yes", "Udyam Registration", 72, "ODOP alignment affects prioritisation, not eligibility"),
    ("sch-020", "SISFS", "Business Size", "DPIIT-recognised startup incorporated within the prescribed period", "Yes", PV, 71, "Must not have received substantial prior government funding"),
    ("sch-021", "PMKVY 4.0", "Age", "Candidate within the scheme's prescribed age band", "Yes", "Aadhaar", 73, "RPL is aimed at existing workers rather than fresh entrants"),
    ("sch-021", "PMKVY 4.0", "Education", "Course-specific minimum qualification per the Qualification Pack", "Yes", "Educational Certificates", 73, "Varies by job role, not by scheme"),
    ("sch-022", "PM-NAPS", "Education", "Meets the apprenticeship trade's entry qualification", "Yes", "Educational Certificates", 73, "Employer-side eligibility applies in parallel"),
    ("sch-023", "DDU-GKY", "Age", "15 to 35 years, relaxed for specified vulnerable groups", "Yes", "Aadhaar", 73, "Relaxation for women, PwD, and certain marginalised groups"),
    ("sch-023", "DDU-GKY", "Income", "Rural poor household as identified by prescribed criteria", "Yes", "Income Certificate", 72, "Rural residence is a separate condition"),
    ("sch-024", "Skill Loan", "Education", "Admitted to an eligible NSQF-aligned course at a recognised institution", "Yes", "Educational Certificates", 70, "Eligible-course list set by the IBA model scheme"),
    ("sch-025", "NMMSS", "Education", "Studying in class VIII in a government, local body or aided school", "Yes", "Bonafide / Study Certificate", 74, "Selection by state-conducted examination"),
    ("sch-025", "NMMSS", "Income", "Parental income below the prescribed ceiling", "Yes", "Income Certificate", 74, "Ceiling revised by notification"),
    ("sch-026", "CSSS", "Education", "Above the prescribed percentile in the class XII board examination", "Yes", "Educational Certificates", 73, "Percentile computed board-wise and stream-wise"),
    ("sch-026", "CSSS", "Income", "Family income below the prescribed ceiling", "Yes", "Income Certificate", 73, "Verified through the National Scholarship Portal"),
    ("sch-027", "PM-YASASVI", "Category", "OBC, EBC or DNT student", "Yes", "Caste Certificate", 71, "Central OBC list governs; state BC lists may differ"),
    ("sch-028", "PMS-SC", "Category", "Scheduled Caste student", "Yes", "Caste Certificate", 73, "Delivered largely through state governments"),
    ("sch-028", "PMS-SC", "Education", "Enrolled in a post-matriculation course", "Yes", "Bonafide / Study Certificate", 73, "Course-level rates differ by group"),
    ("sch-029", "Samagra Shiksha", "Other", "Institutional: government and government-aided schools, not individual applicants", "Yes", PV, 70, "No citizen eligibility test exists; states and schools are the beneficiaries"),
    ("sch-030", "PM POSHAN", "Education", "Enrolled in classes I-VIII in an eligible school (pre-primary in some states)", "Yes", "Bonafide / Study Certificate", 72, "Automatic entitlement on enrolment; no separate application or means test"),
    ("sch-032", "AB-HWC", "Other", "Universal: any person presenting at an Ayushman Arogya Mandir facility", "No", PV, 70, "No eligibility screening; service scheme open to all"),
    ("sch-031", "AB PM-JAY", "Income", "Household identified by prescribed deprivation and occupational criteria", "Yes", PV, 75, "Several states extend cover beyond the central beneficiary base"),
    ("sch-031", "AB PM-JAY", "Other", "No cap on family size, age or gender within an eligible household", "No", "Aadhaar", 74, "A deliberate design feature of the scheme"),
    ("sch-033", "PMMVY", "Gender", "Pregnant woman or lactating mother", "Yes", "Aadhaar", 72, "Conditions differ by birth order"),
    ("sch-034", "MGNREGS", "Other", "Adult member of a rural household willing to do unskilled manual work", "Yes", "Job Card", 76, "Statutory entitlement on demand; no income test"),
    ("sch-035", "DAY-NRLM", "Income", "Rural poor household identified through participatory identification", "Yes", PV, 72, "Access is via SHG membership, not individual application"),
    ("sch-036", "PMAY-G", "Other", "Houseless or living in a kutcha house, per prescribed deprivation criteria", "Yes", PV, 73, "Automatic exclusion criteria also apply"),
    ("sch-037", "PMAY-U", "Income", "EWS, LIG or MIG household by the vertical applied for", "Yes", "Income Certificate", 72, "Income bands differ by vertical"),
    ("sch-038", "NSAP", "Age", "60 and above for old age pension; no age bar for widow and disability verticals", "Yes", "Aadhaar", 72, "Enhanced rate above 80 in the old age vertical"),
    ("sch-038", "NSAP", "Income", "Below poverty line household", "Yes", "Income Certificate", 71, "State top-up rules vary widely"),
    ("sch-039", "NFSA/PDS", "Income", "Priority household or Antyodaya Anna Yojana family", "Yes", "Ration Card", 73, "Coverage ratio differs for rural and urban populations"),
    ("sch-040", "PM Surya Ghar", "Other", "Residential electricity consumer with a suitable and legally owned roof", "Yes", PV, 70, "Requires an existing DISCOM connection"),
]

# ===========================================================================
# 4. required_documents.csv
# ===========================================================================
H_DOC = ["document_id", "document_name", "document_type", "issuing_authority",
         "typical_use", "is_digital_available", "digilocker_available",
         "data_source", "source_url", "collection_date", "confidence_score",
         "verification_status", "notes"]

DOCS = [
    ("doc-001", "Aadhaar", "Identity", "Unique Identification Authority of India (UIDAI)", "Identity and DBT authentication in nearly every scheme", "Yes", "Yes", "UIDAI", "https://uidai.gov.in/", CD, "78", VST, "Effectively universal; DBT seeding requires bank-Aadhaar linkage"),
    ("doc-002", "PAN", "Identity/Tax", "Income Tax Department", "Tax identity; exclusion screening; enterprise loan applications", "Yes", "Yes", "Income Tax Department", "https://www.incometax.gov.in/", CD, "76", VST, "Used to apply income-tax-payer exclusion in several schemes"),
    ("doc-003", "Income Certificate", "Eligibility", "State revenue authority (Tahsildar / MRO)", "Income-ceiling verification for scholarships and welfare schemes", "Yes", "Partial", "State revenue departments; MeeSeva", "https://ts.meeseva.telangana.gov.in/", CD, "72", VST, "Validity period and issuing rank differ by state"),
    ("doc-004", "Caste Certificate", "Eligibility", "State revenue authority", "SC, ST, OBC, BC and EBC category verification", "Yes", "Partial", "State revenue departments; MeeSeva", "https://ts.meeseva.telangana.gov.in/", CD, "73", VST, "Central OBC and state BC lists are not identical"),
    ("doc-005", "Bonafide / Study Certificate", "Education", "Head of the educational institution", "Confirms current enrolment for scholarship claims", "Partial", "No", "National Scholarship Portal guidance", "https://scholarships.gov.in/", CD, "70", VST, "Institution-issued; format is not standardised nationally"),
    ("doc-006", "Land Records (Pattadar Passbook / RoR)", "Asset", "State revenue department", "Land-holding proof for agriculture schemes", "Yes", "Partial", "State land records portals (Dharani, Webland)", "https://dharani.telangana.gov.in/", CD, "72", VST, "Digitisation state varies; tenant farmers often lack documentation"),
    ("doc-007", "Bank Passbook / Account Proof", "Financial", "Scheduled bank or post office", "DBT credit destination and account verification", "Yes", "No", "Department of Financial Services", "https://financialservices.gov.in/", CD, "75", VST, "Account must be Aadhaar-seeded for most DBT schemes"),
    ("doc-008", "GST Registration Certificate", "Business", "Goods and Services Tax Network", "Business identity for enterprise credit and subsidy claims", "Yes", "Yes", "GSTN", "https://www.gst.gov.in/", CD, "74", VST, "Required only above the turnover threshold for most schemes"),
    ("doc-009", "Udyam Registration Certificate", "Business", "Ministry of MSME", "MSME classification proof for MSME schemes and credit guarantee", "Yes", "Yes", MSME_M, "https://udyamregistration.gov.in/", CD, "76", VST, "Replaced Udyog Aadhaar; self-declaration based, PAN and GST linked"),
    ("doc-010", "Educational Certificates / Marksheets", "Education", "Board, university or examining body", "Qualification proof for scholarships, skilling and loan schemes", "Partial", "Yes", "National Academic Depository; DigiLocker", "https://www.digilocker.gov.in/", CD, "72", VST, "DigiLocker availability depends on board or university onboarding"),
    ("doc-011", "Domicile / Residence Certificate", "Eligibility", "State revenue authority", "State-scheme eligibility and district-specific benefit claims", "Yes", "Partial", "State revenue departments", "https://ts.meeseva.telangana.gov.in/", CD, "70", VST, "Residence-duration requirement differs by state"),
    ("doc-012", "Ration Card", "Eligibility", "State civil supplies department", "Household composition and NFSA entitlement proof", "Yes", "Partial", "Department of Food and Public Distribution", "https://dfpd.gov.in/", CD, "72", VST, "Also used as a household-unit proxy in several welfare schemes"),
    ("doc-013", "Disability Certificate / UDID", "Eligibility", "Notified medical authority", "Benchmark-disability proof for PwD schemes and relaxations", "Yes", "Yes", "Department of Empowerment of Persons with Disabilities", "https://www.swavlambancard.gov.in/", CD, "72", VST, "UDID is the standardised national instrument"),
    ("doc-014", "Job Card", "Eligibility", "Gram Panchayat", "MGNREGA work-demand and wage-payment record", "Yes", "No", "Ministry of Rural Development", "https://nrega.nic.in/", CD, "73", VST, "Household-level document, issued per household not per worker"),
    ("doc-015", "Project Report / DPR", "Business", "Applicant (often with DIC or bank support)", "Enterprise viability assessment for credit-linked subsidy schemes", "No", "No", "Office of Development Commissioner (MSME)", "https://msme.gov.in/", CD, "68", VST, "Quality of the report materially affects sanction outcomes"),
]

# ===========================================================================
# 6. implementing_agencies.csv
# ===========================================================================
H_AG = ["agency_id", "agency_name", "agency_type", "government_level",
         "jurisdiction", "primary_role", "sectors_covered", "official_website",
         "data_source", "source_url", "collection_date", "confidence_score",
         "verification_status", "notes"]

AGENCIES = [
    ("ag-001", "Ministry of Agriculture and Farmers Welfare", "Central Ministry", "Central", "National", "Policy, scheme design and central funding for agriculture", "Agriculture", "https://agricoop.gov.in/", "Government of India", "https://agricoop.gov.in/", CD, "78", VST, "Implements through state agriculture departments"),
    ("ag-002", "Ministry of Micro, Small and Medium Enterprises", "Central Ministry", "Central", "National", "MSME policy, credit facilitation and enterprise development", "MSME; Entrepreneurship", "https://msme.gov.in/", "Government of India", "https://msme.gov.in/", CD, "77", VST, "Operates through DC-MSME, MSME-DIs and KVIC"),
    ("ag-003", "Ministry of Education", "Central Ministry", "Central", "National", "School and higher education policy and central scholarship schemes", "Education; Scholarships", "https://www.education.gov.in/", "Government of India", "https://www.education.gov.in/", CD, "77", VST, "Two departments: school education, and higher education"),
    ("ag-004", "Ministry of Health and Family Welfare", "Central Ministry", "Central", "National", "Health policy, national health missions and insurance schemes", "Healthcare", "https://mohfw.gov.in/", "Government of India", "https://mohfw.gov.in/", CD, "77", VST, "PM-JAY is executed by the National Health Authority"),
    ("ag-005", "Ministry of Skill Development and Entrepreneurship", "Central Ministry", "Central", "National", "Skilling policy, apprenticeship and certification framework", "Skill Development", "https://msde.gov.in/", "Government of India", "https://msde.gov.in/", CD, "77", VST, "Operates through NSDC, DGT and NCVET"),
    ("ag-006", "Ministry of Rural Development", "Central Ministry", "Central", "National", "Rural employment, livelihoods, housing and social assistance", "Employment; Livelihood; Housing; Social Welfare", "https://rural.nic.in/", "Government of India", "https://rural.nic.in/", CD, "76", VST, "Largest scheme portfolio by beneficiary count"),
    ("ag-007", "Department of Financial Services", "Central Department", "Central", "National", "Financial inclusion, Jan Suraksha and banking-linked schemes", "Financial Inclusion; Insurance", "https://financialservices.gov.in/", "Ministry of Finance", "https://financialservices.gov.in/", CD, "76", VST, "Coordinates public sector banks for scheme delivery"),
    ("ag-008", "National Health Authority", "Central Authority", "Central", "National", "Implementation of Ayushman Bharat PM-JAY", "Healthcare", "https://nha.gov.in/", "Ministry of Health and Family Welfare", "https://nha.gov.in/", CD, "75", VST, "State Health Agencies execute at state level"),
    ("ag-009", "NABARD", "Development Financial Institution", "Central", "National", "Refinance and development support for agriculture and rural sectors", "Agriculture; Livelihood", "https://www.nabard.org/", "NABARD", "https://www.nabard.org/", CD, "76", VST, "Refinances banks rather than lending directly to most citizens"),
    ("ag-010", "SIDBI", "Development Financial Institution", "Central", "National", "MSME refinance, credit guarantee administration and fund-of-funds", "MSME", "https://www.sidbi.in/", "SIDBI", "https://www.sidbi.in/", CD, "75", VST, "Administers CGTMSE jointly with the MSME Ministry"),
    ("ag-011", "KVIC (Khadi and Village Industries Commission)", "Statutory Body", "Central", "National", "PMEGP nodal agency and village industry promotion", "Entrepreneurship; MSME", "https://www.kvic.gov.in/", "Ministry of MSME", "https://www.kvic.gov.in/", CD, "74", VST, "One of three PMEGP implementing agencies with KVIB and DIC"),
    ("ag-012", "NSDC (National Skill Development Corporation)", "Public Private Partnership", "Central", "National", "Skill scheme implementation, training partner empanelment and funding", "Skill Development", "https://nsdcindia.org/", MSDE, "https://nsdcindia.org/", CD, "75", VST, "Operates Skill India Digital and Sector Skill Councils"),
    ("ag-013", "District Industries Centre (DIC)", "District Office", "State", "District", "District-level MSME facilitation, PMEGP processing and subsidy claims", "MSME; Entrepreneurship", PV, "State industries departments", "https://msme.gov.in/", CD, "70", VST, "The practical first point of contact for enterprise schemes"),
    ("ag-014", "District Collector / District Administration", "District Office", "State", "District", "District-level convergence, grievance redress and welfare scheme oversight", "All sectors", PV, "State governments", "https://www.india.gov.in/", CD, "68", VST, "Chairs district-level convergence committees for most schemes"),
    ("ag-015", "State Agriculture Department", "State Department", "State", "State", "Delivery of central and state agriculture schemes at field level", "Agriculture", PV, "State governments", "https://agricoop.gov.in/", CD, "70", VST, "Extension delivery through KVKs and block offices"),
    ("ag-016", "State Skill Development Mission / Corporation", "State Agency", "State", "State", "State-level skilling delivery and convergence with central schemes", "Skill Development", PV, "State governments; MSDE", "https://msde.gov.in/", CD, "69", VST, "TSSDC and APSSDC are the Telangana and AP bodies"),
    ("ag-017", "Gram Panchayat", "Local Body", "Local", "Village", "Work demand registration, beneficiary identification and social audit", "Employment; Housing; Social Welfare", PV, "Ministry of Panchayati Raj", "https://panchayat.gov.in/", CD, "70", VST, "The statutory entry point for MGNREGA and PMAY-G"),
    ("ag-018", "Common Service Centre (CSC)", "Service Delivery Network", "Central", "National (village level)", "Assisted digital application filing for citizen schemes", "All sectors", "https://csc.gov.in/", "CSC e-Governance Services India Limited", "https://csc.gov.in/", CD, "72", VST, "Village Level Entrepreneur model; service charges apply"),
    ("ag-019", "MeeSeva (Telangana) / AP Seva", "Service Delivery Network", "State", "Telangana; Andhra Pradesh", "Assisted certificate issuance and scheme application counters", "All sectors", "https://ts.meeseva.telangana.gov.in/", "State governments", "https://ts.meeseva.telangana.gov.in/", CD, "71", VST, "Primary channel for revenue certificates in both states"),
    ("ag-020", "Scheduled Commercial Banks", "Financial Institution", "Central", "National", "Credit delivery, subsidy routing and DBT crediting", "Financial Inclusion; MSME; Agriculture; Housing", PV, "Reserve Bank of India; Department of Financial Services", "https://financialservices.gov.in/", CD, "73", VST, "The actual delivery point for every credit-linked scheme"),
]

# ===========================================================================
# 7. scheme_benefits.csv
# ===========================================================================
H_BEN = ["benefit_id", "scheme_id", "scheme_short_name", "benefit_type",
         "benefit_description", "benefit_quantum", "disbursement_mode",
         "frequency", "data_source", "source_url", "collection_date",
         "confidence_score", "verification_status", "notes"]

BEN = [
    ("sch-001", "PMJDY", "Insurance", "Accident insurance cover bundled with the RuPay debit card", PV, "Insurance claim settlement", "On event", 72, "Cover amount differs by card issue date; re-verify at portal"),
    ("sch-001", "PMJDY", "Loan", "Overdraft facility after satisfactory account operation", PV, "Credit to account", "On sanction", 72, "Subject to a satisfactory operating history"),
    ("sch-002", "PMSBY", "Insurance", "Accidental death and permanent disability cover", PV, "Insurance claim settlement", "On event", 74, "Annual auto-debit premium; amounts set by scheme rules"),
    ("sch-003", "PMJJBY", "Insurance", "Life cover, renewable annually", PV, "Insurance claim settlement", "On event", 74, "Annual auto-debit premium"),
    ("sch-004", "APY", "Pension", "Guaranteed minimum monthly pension from age 60", PV, "Direct Benefit Transfer", "Monthly after 60", 72, "Pension slab chosen at enrolment determines contribution"),
    ("sch-005", "PM-KISAN", "Grant", "Income support to land-holding farmer families", PV, "Direct Benefit Transfer", "Three instalments per year", 76, "Amount per instalment is set by scheme rules; re-verify at portal"),
    ("sch-006", "PMFBY", "Insurance", "Yield-loss cover on notified crops", PV, "Direct Benefit Transfer", "Per season on claim", 74, "Sum insured is crop and area specific"),
    ("sch-006", "PMFBY", "Subsidy", "Government share of the insurance premium", PV, "Paid to insurer", "Per season", 73, "Farmer share differs for kharif, rabi and commercial crops"),
    ("sch-007", "KCC", "Loan", "Revolving short-term crop production credit", PV, "Credit limit on card/account", "Revolving", 74, "Collateral-free up to a prescribed limit"),
    ("sch-007", "KCC", "Interest Subvention", "Interest subvention with a prompt-repayment incentive", PV, "Adjusted in loan account", "On repayment", 73, "Effective rate depends on timely repayment"),
    ("sch-008", "PMKSY", "Subsidy", "Capital subsidy on micro-irrigation installation", PV, "Paid to vendor or reimbursed", "One time per installation", 72, "Share differs by state and farmer category"),
    ("sch-009", "SMAM", "Equipment Support", "Capital subsidy on farm machinery purchase", PV, "Paid to vendor or reimbursed", "One time per machine", 73, "Percentage differs by category and machine type"),
    ("sch-009", "SMAM", "Infrastructure", "Assistance for custom-hiring centres and farm machinery banks", PV, "Project-based release", "One time per project", 71, "Aimed at FPOs, SHGs and cooperatives"),
    ("sch-010", "PKVY", "Grant", "Per-hectare assistance across a three-year organic conversion cycle", PV, "Direct Benefit Transfer", "Annual within the cycle", 70, "Includes certification and cluster support components"),
    ("sch-011", "SHC", "Training", "Soil testing with a nutrient-recommendation card", "Not applicable (service)", "Physical or digital card", "Per cycle", 73, "Service delivery; no cash component"),
    ("sch-012", "AIF", "Interest Subvention", "Interest subvention on term loans for post-harvest projects", PV, "Adjusted in loan account", "Annual over tenure", 71, "Applies up to a prescribed loan ceiling"),
    ("sch-013", "PM-KUSUM", "Subsidy", "Central financial assistance on solar pump or plant capacity", PV, "Paid to vendor or state nodal agency", "One time", 70, "Central, state and farmer shares differ by component"),
    ("sch-014", "PMEGP", "Subsidy", "Margin money subsidy on project cost", PV, "Credited to the loan account as back-ended subsidy", "One time", 74, "Percentage differs by category and rural/urban location"),
    ("sch-014", "PMEGP", "Loan", "Bank term loan and working capital for the micro enterprise", PV, "Credit to enterprise account", "On sanction", 74, "Subsidy is released only after loan disbursement"),
    ("sch-015", "PMMY", "Loan", "Collateral-free micro credit under Shishu, Kishore, Tarun and Tarun Plus", PV, "Credit to borrower account", "On sanction", 75, "Category ceilings revised by notification"),
    ("sch-016", "Stand-Up India", "Loan", "Composite loan (term plus working capital) for a greenfield venture", PV, "Credit to enterprise account", "On sanction", 74, "Loan band defined by scheme guidelines"),
    ("sch-017", "CGTMSE", "Loan", "Guarantee cover enabling collateral-free credit", PV, "Guarantee to lender", "On credit sanction", 73, "Benefit accrues to the borrower indirectly"),
    ("sch-018", "PM Vishwakarma", "Training", "Basic and advanced skill training with a training stipend", PV, "Direct Benefit Transfer", "During training", 72, "Advanced training is conditional on completing basic"),
    ("sch-018", "PM Vishwakarma", "Equipment Support", "Toolkit incentive for trade tools", PV, "e-Voucher or DBT", "One time", 72, "Released after basic training"),
    ("sch-018", "PM Vishwakarma", "Loan", "Collateral-free enterprise credit in tranches", PV, "Credit to account", "Tranche based", 71, "Second tranche requires repayment of the first"),
    ("sch-019", "PMFME", "Subsidy", "Credit-linked capital subsidy on eligible project cost", PV, "Back-ended subsidy to loan account", "One time", 72, "Capped per unit"),
    ("sch-019", "PMFME", "Grant", "Seed capital to SHG members for working capital and small tools", PV, "Through the SHG federation", "One time", 70, "Routed via the SHG structure, not paid individually"),
    ("sch-020", "SISFS", "Grant", "Grant for proof of concept, prototype development and market entry", PV, "Milestone-based release by incubator", "Tranche based", 71, "Disbursed by the selected incubator, not by DPIIT"),
    ("sch-021", "PMKVY 4.0", "Training", "Free NSQF-aligned short-term training with assessment", "Not applicable (training cost borne by scheme)", "Paid to training provider", "Per batch", 74, "Placement assistance included but not guaranteed"),
    ("sch-021", "PMKVY 4.0", "Scholarship", "Certification on successful assessment", "Not applicable", "Digital certificate", "On completion", 73, "Certificate is NCVET-recognised"),
    ("sch-022", "PM-NAPS", "Grant", "Government share of apprentice stipend reimbursed to the employer", PV, "Direct Benefit Transfer to apprentice or employer", "Monthly during apprenticeship", 73, "Sharing ratio set by scheme guidelines"),
    ("sch-023", "DDU-GKY", "Training", "Free training with residential option, food and post-placement support", "Not applicable (cost borne by scheme)", "Paid to project implementing agency", "Per batch", 72, "Placement is a contractual obligation on the training partner"),
    ("sch-024", "Skill Loan", "Loan", "Collateral-free loan for vocational course fees", PV, "Paid to institution", "On sanction", 70, "Moratorium during the course period"),
    ("sch-025", "NMMSS", "Scholarship", "Annual scholarship from class IX to XII", PV, "Direct Benefit Transfer", "Annual", 74, "Renewal requires prescribed academic performance"),
    ("sch-026", "CSSS", "Scholarship", "Annual scholarship for graduation and post-graduation", PV, "Direct Benefit Transfer", "Annual", 73, "Rate differs for professional courses"),
    ("sch-027", "PM-YASASVI", "Scholarship", "Pre-matric and post-matric scholarship for OBC, EBC and DNT students", PV, "Direct Benefit Transfer", "Annual", 71, "Top-class school component operates separately"),
    ("sch-028", "PMS-SC", "Scholarship", "Maintenance allowance with fee reimbursement", PV, "Direct Benefit Transfer", "Annual", 73, "Course group determines the maintenance rate"),
    ("sch-029", "Samagra Shiksha", "Infrastructure", "School infrastructure, teacher training and learning materials", PV, "Grant to state implementation society", "Annual", 72, "Institutional benefit; no individual entitlement"),
    ("sch-030", "PM POSHAN", "Grant", "One hot cooked meal per school day", "Not applicable (in-kind)", "Served at school", "Per school day", 73, "Nutritional norms prescribed by class group"),
    ("sch-031", "AB PM-JAY", "Insurance", "Cashless secondary and tertiary hospitalisation cover", PV, "Cashless settlement at empanelled hospital", "Per family per year", 75, "Cover amount set by scheme rules; states may enhance"),
    ("sch-032", "AB-HWC", "Infrastructure", "Free essential drugs, diagnostics and screening at upgraded facilities", "Not applicable (service)", "At facility", "On visit", 71, "Renamed Ayushman Arogya Mandir"),
    ("sch-033", "PMMVY", "Grant", "Conditional maternity cash benefit in instalments", PV, "Direct Benefit Transfer", "Instalments on conditions", 72, "Conditions linked to registration, immunisation and birth order"),
    ("sch-034", "MGNREGS", "Grant", "Statutory wage for guaranteed days of unskilled manual work", PV, "Direct Benefit Transfer", "Per fortnight worked", 75, "Wage rate notified per state and revised annually"),
    ("sch-035", "DAY-NRLM", "Grant", "Revolving fund and community investment support to SHGs", PV, "To SHG bank account", "One time per SHG", 72, "Precondition for subsequent bank credit linkage"),
    ("sch-035", "DAY-NRLM", "Interest Subvention", "Interest subvention on SHG bank loans", PV, "Adjusted in SHG loan account", "Annual", 70, "Rate differs between category and non-category districts"),
    ("sch-036", "PMAY-G", "Grant", "Unit assistance for pucca house construction, in instalments", PV, "Direct Benefit Transfer", "Instalments on construction milestones", 73, "Rate differs for plain and hilly areas"),
    ("sch-037", "PMAY-U", "Interest Subvention", "Credit-linked interest subsidy on home loans", PV, "Credited upfront to the loan account", "One time (NPV basis)", 72, "Subsidy differs by income vertical"),
    ("sch-038", "NSAP", "Pension", "Monthly social assistance pension", PV, "Direct Benefit Transfer", "Monthly", 72, "Central rate plus a widely varying state top-up"),
    ("sch-039", "NFSA/PDS", "Grant", "Subsidised food grain entitlement per person per month", PV, "In-kind at fair price shop", "Monthly", 73, "Portable nationally via One Nation One Ration Card"),
    ("sch-040", "PM Surya Ghar", "Subsidy", "Central financial assistance on rooftop solar capacity", PV, "Direct Benefit Transfer after installation", "One time", 70, "Slab structure by sanctioned capacity"),
    ("sch-040", "PM Surya Ghar", "Loan", "Concessional collateral-free loan for the consumer share", PV, "Credit to account", "On sanction", 69, "Offered through participating banks"),
]

# ===========================================================================
# 13. financial_institutions.csv
# ===========================================================================
H_FI = ["institution_id", "institution_name", "institution_type", "ownership",
        "government_level", "scheme_roles", "priority_sector_lending",
        "official_website", "data_source", "source_url", "collection_date",
        "confidence_score", "verification_status", "notes"]

RBI = "Reserve Bank of India"
RBI_URL = "https://www.rbi.org.in/"

FI = [
    ("fi-001", "State Bank of India", "Public Sector Bank", "Government majority", "Central", "PMMY; Stand-Up India; PMEGP; KCC; PMAY CLSS; Skill Loan", "Yes", "https://sbi.co.in/", RBI, RBI_URL, CD, "76", VST, "Largest scheme-lending footprint among Indian banks"),
    ("fi-002", "Punjab National Bank", "Public Sector Bank", "Government majority", "Central", "PMMY; Stand-Up India; PMEGP; KCC; PMAY CLSS", "Yes", "https://www.pnbindia.in/", RBI, RBI_URL, CD, "74", VST, "Lead bank in several north Indian districts"),
    ("fi-003", "Canara Bank", "Public Sector Bank", "Government majority", "Central", "PMMY; PMEGP; KCC; Skill Loan; education loans", "Yes", "https://canarabank.com/", RBI, RBI_URL, CD, "74", VST, "Strong presence in southern states"),
    ("fi-004", "Union Bank of India", "Public Sector Bank", "Government majority", "Central", "PMMY; Stand-Up India; PMEGP; KCC", "Yes", "https://www.unionbankofindia.co.in/", RBI, RBI_URL, CD, "74", VST, "Lead bank for several Telangana and AP districts"),
    ("fi-005", "Bank of Baroda", "Public Sector Bank", "Government majority", "Central", "PMMY; PMEGP; KCC; PMAY CLSS", "Yes", "https://www.bankofbaroda.in/", RBI, RBI_URL, CD, "73", VST, "Wide rural branch network"),
    ("fi-006", "NABARD", "Development Financial Institution", "Government owned", "Central", "Refinance for KCC and rural credit; SHG bank linkage; AIF support", "Not applicable", "https://www.nabard.org/", "NABARD", "https://www.nabard.org/", CD, "76", VST, "Refinances lenders; does not lend directly to most citizens"),
    ("fi-007", "SIDBI", "Development Financial Institution", "Government owned", "Central", "MSME refinance; CGTMSE administration; Fund of Funds for Startups", "Not applicable", "https://www.sidbi.in/", "SIDBI", "https://www.sidbi.in/", CD, "75", VST, "Apex MSME financier; largely an institutional lender"),
    ("fi-008", "NSIC (National Small Industries Corporation)", "Public Sector Enterprise", "Government owned", "Central", "Raw material assistance; bank credit facilitation; marketing support", "Not applicable", "https://www.nsic.co.in/", MSME_M, "https://www.nsic.co.in/", CD, "72", VST, "Support services rather than direct term lending"),
    ("fi-009", "Regional Rural Banks", "Regional Rural Bank", "Government sponsored", "State", "KCC; PMMY; SHG credit linkage; PMEGP", "Yes", PV, RBI, RBI_URL, CD, "71", VST, "Sponsored by public sector banks; district-level rural focus"),
    ("fi-010", "District Central Cooperative Banks", "Cooperative Bank", "Cooperative", "District", "KCC; crop loans; SHG lending", "Yes", PV, "NABARD; state cooperative departments", "https://www.nabard.org/", CD, "69", VST, "Significant crop-loan share in many districts; governance quality varies"),
    ("fi-011", "Primary Agricultural Credit Societies (PACS)", "Cooperative Society", "Cooperative", "Village", "Crop loans; AIF-eligible infrastructure projects", "Not applicable", PV, "NABARD; Ministry of Cooperation", "https://www.nabard.org/", CD, "68", VST, "Village-level cooperative credit; AIF-eligible for infrastructure"),
    ("fi-012", "Small Finance Banks", "Small Finance Bank", "Private", "Central", "PMMY; micro credit; Jan Suraksha enrolment", "Yes", PV, RBI, RBI_URL, CD, "70", VST, "Licensed with a mandated small-ticket and unserved focus"),
]


def rows_elig():
    out = []
    for i, (sid, short, ctype, val, mand, doc, conf, note) in enumerate(ELIG, start=1):
        out.append((f"elig-{i:03d}", sid, short, ctype, val, mand, doc, MYSCH,
                    MYSCH_URL, CD, str(conf), VST, note))
    return out


def rows_ben():
    out = []
    for i, (sid, short, btype, desc, quantum, mode, freq, conf, note) in enumerate(BEN, start=1):
        out.append((f"ben-{i:03d}", sid, short, btype, desc, quantum, mode, freq,
                    MYSCH, MYSCH_URL, CD, str(conf), VST, note))
    return out


if __name__ == "__main__":
    print("Generating Package007_Government_Schemes core datasets:\n")
    write("scheme_categories.csv", H_CAT, CATEGORIES)
    write("government_schemes.csv", H_SCH, SCHEMES)
    write("eligibility_criteria.csv", H_ELIG, rows_elig())
    write("required_documents.csv", H_DOC, DOCS)
    write("implementing_agencies.csv", H_AG, AGENCIES)
    write("scheme_benefits.csv", H_BEN, rows_ben())
    write("financial_institutions.csv", H_FI, FI)
    print("\nCore generation complete.")
