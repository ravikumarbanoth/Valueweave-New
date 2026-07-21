# Package002_Education v1.0.0 — Coverage Report

## Datasets Released

| Dataset | Records | Jurisdictions Covered |
|---|---|---|
| education_boards_regulatory_bodies | 21 | Andhra Pradesh, National, Telangana |
| universities_telangana_andhra_pradesh | 61 | Andhra Pradesh, Telangana |
| entrance_exams | 28 | Andhra Pradesh, National, Telangana |
| scholarships | 25 | Andhra Pradesh, National, Telangana |

**Total records released in v1.0.0: 135**

## Domains Released vs. Full Task Scope

This release covers 4 of the 40 education data domains named in the package brief: Educational Boards & Regulatory Bodies, Universities, Entrance Exams, and Scholarships. The remaining 36 domains (Schools, Junior/Degree/Engineering/Medical/Polytechnic Colleges, ITI, Skill Development Institutes, Open/Distance/Online Education, Coaching Institutes, MOOCs, Fellowships, Rankings detail, Research Institutions, Libraries, Hostels, Career Guidance, Placement Cells, Innovation/Incubation/Startup Cells, Internships, Apprenticeships, Educational Policies/Schemes/Statistics/Technology, and all coverage of Indian states beyond Telangana & Andhra Pradesh) are explicitly tracked as BLOCKED or QUEUED in `registry/dataset_registry.csv` and `acquisition_backlog.json` rather than shipped as unverified placeholders — this mirrors Package001_Geography's precedent of not shipping guessed data merely to appear complete.

## Geographic Scope

- **Primary (deep coverage):** Telangana, Andhra Pradesh
- **National-level entities included:** where a body/exam/scheme's jurisdiction is genuinely national (e.g. UGC, JEE Main, National Means-cum-Merit Scholarship), it is included once and tagged `jurisdiction: National` rather than duplicated per state.
- **Secondary (remaining states/UTs):** not covered in v1.0.0; queued for future releases.
