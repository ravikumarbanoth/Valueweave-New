# Package003_Healthcare v1.0.0-RC1 — Coverage Report

## Datasets Released

| Dataset | Records | Jurisdictions Covered |
|---|---|---|
| medical_regulatory_bodies_and_health_missions | 23 | Andhra Pradesh, National, Telangana |
| medical_colleges_telangana_andhra_pradesh | 54 | Andhra Pradesh, Telangana |
| government_hospitals_telangana_andhra_pradesh | 49 | Andhra Pradesh, Telangana |
| government_health_insurance_schemes | 8 | Andhra Pradesh, National, Telangana |

**Total records released in v1.0.0-RC1: 134**

## Domains Released vs. Full Task Scope

This release covers 4 of the 40 healthcare data domains named in the package brief: Medical Regulatory Bodies & Health Missions, Medical Colleges, Government Hospitals (District/Area/Teaching), and Government Health Insurance Schemes. The remaining 36 domains (PHCs, CHCs, Urban Health Centres, Private Hospitals, Super Specialty/Children's/Maternity/Cancer/Eye/Dental Hospitals, Diagnostic Centres, Blood Banks, Organ Donation, Dialysis Centres, Ambulance Services, Trauma/Mental Health/Rehabilitation Centres, Telemedicine, Public Health Labs, Health Helplines, Vaccination Programmes, Disease Surveillance, Public Health Campaigns, other National Health Programmes, Pharmaceutical Support Services, Health NGOs, and all states/UTs beyond Telangana & Andhra Pradesh) are explicitly tracked as BLOCKED or QUEUED in `registry/dataset_registry.csv` and `acquisition_backlog.json` rather than shipped as unverified placeholders — this mirrors Package001_Geography and Package002_Education's precedent of prioritizing depth and verification over maximum coverage, per this package's own brief.

## Geographic Scope

- **Primary (deep coverage):** Telangana, Andhra Pradesh
- **National-level entities included:** where a body/scheme's jurisdiction is genuinely national (e.g. NMC, PM-JAY), it is included once and tagged `jurisdiction: National` rather than duplicated per state.
- **Secondary (remaining states/UTs):** not covered in RC1; queued for future releases.
