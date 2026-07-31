# District Pipeline Report

**ValueWeave v1.0 · why Medak says "we have not researched this yet"**

---

## The brief's question

> Is this because **A.** no data exists, **B.** relationship missing,
> **C.** query wrong, or **D.** import never happened?

**Answer: D primarily, B substantially. Not A, not C.**

Both were verified against the data, not reasoned about.

---

## The trace

```
/districts/medak
        │
        ▼
resolveTerms("district", ["Medak"])
        │        reads knowledge.kg_vocabulary_map          ← EMPTY (never imported)
        ▼
getDistrictKnowledge(vw:district:medak)
        │        reads knowledge.kg_relationships           ← EMPTY (never imported)
        │        then knowledge.kg_entities                 ← EMPTY (never imported)
        ▼
{} → DistrictIntelligencePanel → "We have not linked our research to Medak yet"
```

---

## Checking each hypothesis

**A · No data exists?** — **No, data exists.**

```
vw:district:medak   Medak   (District, Package001_Geography)
```

The entity is in `entities.csv`, along with 60 other districts, each with
population, area, literacy rate, headquarters and mandal count.

**C · Query wrong?** — **No, the query is right.** The crosswalk resolves the
term cleanly:

```
Medak -> vw:district:medak   via EXACT_NAME
```

District resolution is the platform's *best* crosswalk coverage: 100% for the 14
editorial districts, including the curated cases (Anantapur → Ananthapuramu,
Nellore → Sri Potti Sriramulu Nellore, Vijayawada → NTR).

**D · Import never happened?** — **Yes. This is the primary cause.** Every table
in the chain is empty. Two dry runs, nothing applied, no CI.

**B · Relationship missing?** — **Yes, and this is the part that survives the fix.**

Medak's edges in the graph:

```
incoming:  1   GENERATES_EMPLOYMENT  (from one MSME)
outgoing:  1   LOCATED_IN            (to its state)
```

`getDistrictKnowledge()` reads **incoming** edges. Medak has one. So on a
perfectly synced database, the Medak page would show **a single MSME** and
nothing else — no industries, no schemes, no training, no institutions.

---

## The scale of B, across all 61 districts

| Incoming links | Districts |
|---|---:|
| **0** | **34** |
| 1–2 | 13 |
| 3+ | 14 |
| median | **0** |
| max | 17 (Hyderabad) |

Best covered: Hyderabad 17 · Guntur 8 · Tirupati 7 · Visakhapatnam 5 ·
Sangareddy 4 · Krishna 4.

> **More than half of all districts have no link at all.** Running the import
> takes them from "no data" to "no data", because the limiting factor is edges,
> not rows. This was the central finding of the Phase 1 knowledge assessment and
> it has not changed.

---

## What would actually fix district pages

| Step | Effect on Medak | Effect on all districts |
|---|---|---|
| 1 · Run the import | 0 → 1 record | 27 of 61 get something |
| 2 · Read `district_scheme_mapping.csv` (305 pairs, already researched, builder does not read it) | + schemes | **34 empty districts get content** |
| 3 · Recover `GENERATES_EMPLOYMENT` edges (410 identified at 100% both-endpoint verification, zero new research) | + businesses | median rises above 0 |

Step 1 is this sprint. Steps 2 and 3 are graph work, specified in
`RELATIONSHIP_RECOVERY_REPORT.md` and `GRAPH_CONNECTIVITY_PLAN.md`, and neither
needs new research — the data is in Git and unread.

---

## The editorial layer keeps working regardless

`/districts/medak` shows a hand-written economic profile above the researched
panel, from `lib/districts-data.js` and `data/districts.json`. Those are files in
the repository and do not depend on the database. The page is not blank today; it
is missing its researched half.

---

**Companions:** `KNOWLEDGE_ARCHITECTURE_AUDIT.md` · `KNOWLEDGE_GRAPH_REPORT.md`
