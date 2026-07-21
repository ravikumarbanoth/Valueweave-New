# Package003_Healthcare — Future Expansion Roadmap (post-RC2)

1. **Re-verify at higher confidence** once WebFetch access to .gov.in/.ac.in domains is available, promoting confirmed rows to `VST-VERIFIED` — this has now been attempted twice (RC1, RC2) without WebFetch access being restored.
2. **Unlock TVVP/APVVP full hospital rosters** — still the biggest single expansion opportunity; two collection passes have failed to surface their tabular list content via search.
3. **Fill the remaining ~13-15 missing Telangana medical colleges** and any newer AP colleges via a further deep-dive pass.
4. **Add PHCs/CHCs/Urban Health Centres** once a bulk source (HMIS/NHM facility registry) is available.
5. **Expand to specialty hospital categories** (cancer, eye, dental, children's, maternity, super-specialty) as standalone datasets.
6. **Add service-infrastructure domains**: blood banks, dialysis centres, ambulance services, trauma/mental-health/rehab centres, diagnostic centres, public health labs.
7. **Add programme/campaign domains**: vaccination programmes, disease surveillance, public health campaigns, national health programmes beyond insurance, telemedicine, health helplines, pharmaceutical support services (Jan Aushadhi), health NGOs.
8. **Extend geographic coverage** beyond Telangana & Andhra Pradesh to remaining states/UTs.
9. **Extend the RC2 field-depth additions further**: government_scheme_coverage_summary and email fill rates are still well under 100% for both institution datasets; a dedicated pass could raise these substantially.
10. **Evaluate cross-package FK wiring** — to Package001_Geography's district_id once a defensible mapping is verified, and formalize the medical_colleges/government_hospitals cross-references (currently free-text only) if a reliable matching approach is found.
