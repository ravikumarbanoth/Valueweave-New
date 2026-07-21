# Package003_Healthcare — Future Expansion Roadmap

1. **Re-verify RC1 at higher confidence** once WebFetch access to .gov.in/.ac.in domains is available, promoting confirmed rows to `VST-VERIFIED`.
2. **Unlock TVVP/APVVP full hospital rosters** — the biggest single expansion opportunity for government_hospitals_telangana_andhra_pradesh; requires either a working fetch of their list pages or a bulk data request.
3. **Fill the ~17-19 missing Telangana medical colleges and remaining AP colleges** via a dedicated deep-dive pass.
4. **Add PHCs/CHCs/Urban Health Centres** once a bulk source (HMIS/NHM facility registry) is available — these are BLOCKED, not merely queued, because per-institution research cannot reach the necessary scale.
5. **Expand to specialty hospital categories** (cancer, eye, dental, children's, maternity, super-specialty) as standalone datasets.
6. **Add service-infrastructure domains**: blood banks, dialysis centres, ambulance services, trauma/mental-health/rehab centres, diagnostic centres, public health labs.
7. **Add programme/campaign domains**: vaccination programmes, disease surveillance, public health campaigns, national health programmes beyond insurance, telemedicine, health helplines, pharmaceutical support services (Jan Aushadhi), health NGOs.
8. **Extend geographic coverage** beyond Telangana & Andhra Pradesh to remaining states/UTs.
9. **Populate the field-depth fields descoped in RC1**: latitude/longitude, ICU availability, dialysis availability, working hours, email, Google Maps links, departments/specialties detail.
10. **Evaluate cross-package FK wiring** — to Package001_Geography's district_id once a defensible mapping is verified, and to Package002_Education's medical college data (currently free-text cross-references between this package's own two datasets).
