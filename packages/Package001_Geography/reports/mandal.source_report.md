# Source Report — `mandal` Dataset

## Source Reliability Analysis

| Source | Type | Reliability (0–100) | Access Status | License |
|---|---|---|---|---|
| Local Government Directory (lgdirectory.gov.in) | Official Government Portal/API | 95 | Not yet retrieved — dynamic portal, see Collection Report §3 | Government Open Data License – India (confirmed via community mirror's citation) |
| Census of India 2011, Part-I State Administrative Divisions | Official Government Statistical Source | 95 | Blocked (robots.txt) | Government of India Open Data (NDSAP, 2012) — standard for Census publications |
| Telangana State Statistical Abstract 2022 | Official Government Statistical Source | 90 | Fetch failed (server error) | Government of Telangana publication — license not directly confirmed this pass |
| Individual district portals (e.g. medak.telangana.gov.in) | Official Government Portal | 92 | Blocked (robots.txt) | Government of Telangana — license not directly confirmed this pass |
| Wikipedia "List of mandals in Telangana" | Secondary/Tertiary Compilation | 60 *(downgraded)* | Retrieved, but structurally unreliable for automated per-row extraction in this session | CC BY-SA 4.0 |
| Wikipedia "Medak district" / "Medak mandal" (individual pages) | Secondary/Tertiary Compilation | 70 | Retrieved (summary/infobox level only) | CC BY-SA 4.0 |
| villageinfo.in | Unofficial aggregator | 40 | Retrieved, found to reference obsolete (pre-2016) district boundaries | Unknown/unconfirmed |

**Note on the Wikipedia compilation's reliability downgrade:** in the State/District dataset (previous collection run), Wikipedia's compiled tables were scored 78–80 because their table structure rendered cleanly and every figure traced to a footnoted official source. In this run, the equivalent page for Mandals rendered with its table structure collapsed, making it impossible to reliably attribute individual mandal names to the correct district without reintroducing guesswork. The source's underlying reliability is likely still good (it is the same citation chain: Census 2011 + Telangana Statistical Abstract 2022) — the downgrade reflects **this session's ability to safely extract from it**, not a judgment on Wikipedia's editorial quality for this article.

## Source Priority Ranking Applied (per the mandated hierarchy)
1. Official Government Sources — attempted first (LGD, Census, State Portal, District Portal) ✓
2. Government APIs — LGD's underlying data model supports this; portal-level automated access not available in this session
3. Government CSV Downloads — attempted via LGD community mirror; found stale (2022) and non-trivial to isolate to TG/AP sub-districts within this session
4. Gazette Notifications — not separately pursued this run (would be the next step for Revenue Division and any remaining District-level conflicts)
5. Government GIS Data — not yet in scope for Mandal (relevant instead to Infrastructure/Natural Resource datasets queued next)
6. Government PDFs — attempted (Census 2011 atlas PDF, Telangana Statistical Abstract PDF); both inaccessible this session
7. Educational Institutions — not applicable to this dataset
8. Industry Associations — not applicable to this dataset
9. International Standards — not applicable to this dataset
10. Trusted Secondary Sources — used for context/conflict-detection only, not for row-level data, per the reliability downgrade above

No unofficial source was substituted in place of an official one for any actual data value in this dataset — the entire dataset remains empty of data rows rather than accept that substitution.
