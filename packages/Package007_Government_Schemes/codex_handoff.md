# Codex Handoff — Package007_Government_Schemes v1.0.0

For whoever picks this up next, human or agent. What exists, what was deliberately left undone, and
where the traps are.

## State

**Released, Stable v1.0.0.** 15 datasets, 655 records, 40 schemes, validation clean (0 violations
across 12 checks). Branch `claude/package007-government-schemes-import`, merged to `main`.

## Read first, in order

1. `README.md` — structure, cross-package surface, what the package does not assert
2. `quality_report.md` — **what this is and is not fit for**; read before building on it
3. `docs/METHODOLOGY.md` §2 — why no monetary amount appears anywhere
4. `validation_report.md` — the five defect classes the checks caught
5. `schemas/schema_catalog.json` — canonical PK/FK reference

## Rebuild

```bash
cd packages/Package007_Government_Schemes
python3 gen_core.py         # 7 scheme-intrinsic datasets
python3 gen_mappings.py     # 8 relational/workflow datasets; resolves upstream FKs live
python3 validate.py         # 12 checks; writes validation_summary.json; exit 0 = clean
python3 build_artifacts.py  # schema catalog, 15 metadata, registry, manifest, 15 reports
python3 build_docs.py       # data dictionary, import guide, validation + quality reports,
                            # version history, release notes
```

**Order matters.** Both builders read `validation_summary.json`, so validation runs first. Every
count in every artifact is derived from the CSVs — nothing is hand-maintained, which is why the
manifest, registry, reports and docs cannot drift.

`README.md`, `CHANGELOG.md`, `docs/METHODOLOGY.md`, `docs/USAGE.md` and this file are hand-written.
Everything else is generated.

## The one decision that needs making

**Six packages now hold scheme data.** Package002 (25 scholarships), Package003 (9 health
insurance), Package004 (18 MSME support), Package005 (12 agriculture), Package006 (15 skill), and
Package007 (40 cross-domain). That is ~119 scheme rows across six packages with real overlap.

`government_schemes.also_in_package` declares each overlap, and the mapping datasets carry hard
foreign keys to the domain records. **That makes the problem visible. It does not solve it.**

Three options, in descending order of my recommendation:

1. **Package007 becomes canonical.** Domain packages keep their scheme datasets but mark them
   `DEPRECATED_REFERENCE` and point at `scheme_id`. New schemes land in Package007 only. Cost: one
   coordinated release across five packages. Benefit: one place to update when a scheme changes.
2. **Domain packages stay canonical for their slice; Package007 holds only cross-domain schemes.**
   Cost: Package007 loses ~19 of its 40 rows. Benefit: no coordinated release needed.
3. **Do nothing.** Cost: the copies drift, and the drift is silent because nothing compares them.

Every release that passes without deciding makes the eventual reconciliation larger. If you take
option 1 or 2, add a validation check that fails when a scheme name appears in two packages without
an `also_in_package` declaration.

## Traps

**Do not fill the monetary fields with estimates.** ~85 sentinelled cells are benefit quantum and
financial assistance. They are empty because scheme amounts change by notification and budget
cycle, not because nobody got round to it. Filling them with plausible figures would be the single
worst thing you could do to this package — it would make it look citizen-ready while being
unverifiable and silently going stale. If you obtain primary-source access, cite the notification
per row and raise `confidence_score` accordingly.

**Trust the datasets, not the collection reports.** A Package006 collection report describes an
"MSME Entrepreneurship & Startup Launch" skill. The released `skills.csv` does not contain it.
`gen_mappings.py` resolves every upstream id against the actual CSV and aborts on failure, which is
how that was caught. Keep that discipline: if you add a cross-package link, resolve it against the
file, not against documentation or memory.

**`scheme_short_name` is denormalised into six datasets.** Change it in `government_schemes.csv`
and V8 fails until you regenerate the children. That is the check working — a `SUI` /
`Stand-Up India` mismatch shipped into five datasets before V8 caught it.

**`related_scheme_ids` is semicolon-delimited.** V8 validates each member. If you add profiles,
keep the delimiter — the import guide's normalisation SQL assumes it.

**`priority_score` is not evidence.** If you build a recommender on this, validate against actual
eligibility determination. The scores encode sequencing logic and eligibility overlap, nothing
more. Confidence is 60 on every row for that reason.

## Where the gaps are, ranked

| # | Gap | Effort | Notes |
|---|---|---|---|
| 1 | **Duplication governance unresolved** | Medium | Decision, not code. See above. |
| 2 | **~85 sentinelled monetary cells** | High | Needs primary-source access. The main blocker to citizen-facing use. |
| 3 | **43 sentinelled timelines** | High | Needs published service standards; may not exist for most schemes. |
| 4 | **No Package003 hard FK** | Low | `health_scheme_mapping.csv` — the one released package with no structural link. |
| 5 | **All 40 schemes are Central** | Medium | State registry, reconciled against Package002/003/004 state slices. |
| 6 | **32 of 40 schemes lack workflows** | Medium | `application_process.csv` covers 8. |
| 7 | **305 sentinelled district-variation cells** | High | Requires per-district data that may not be public. |
| 8 | **Zero rows `VST-VERIFIED`** | High | Human data-steward review. Start with the 40 registry rows. |
| 9 | **No scheme-currency monitoring** | Medium | `status` has Closed/Subsumed/Revised values but nothing detects when one applies. |

## Environment constraint you will also hit

WebFetch to `.gov.in`, `.nic.in` and `.ac.in` is blocked by organizational egress policy. Every row
is attributed to its scheme portal or ministry but no primary page was read, which is why
`confidence_score` is capped at 85 (observed max 78). Same constraint applied to Package004,
Package005 and Package006 — environmental, not a collection failure.

This bites harder here than in any previous package. Scheme data is the most time-sensitive
material in the knowledge base, and currency is exactly what could not be verified. If that policy
changes, re-collection priority is: (1) benefit amounts, (2) current scheme status — several
schemes in this registry may have been renamed, merged or subsumed since launch, (3) eligibility
thresholds, (4) processing timelines.

## Verification checklist before any future release

```bash
python3 validate.py
python3 -c "import json; s=json.load(open('validation_summary.json')); \
            assert s['violations']==0 and s['result']=='PASS'; print('clean')"
git status --short
```

Then confirm `package_manifest.json`, `registry/dataset_registry.csv`, `validation_report.md` and
`quality_report.md` were regenerated — they all carry record counts, and a stale one is a silent
lie about the release.

## Upstream versions this was built against

Package001 v1.0.0, Package002 v1.0.0, Package003 v1.0.0, Package004 v1.0.0, Package005 v1.0.0,
Package006 v1.0.0. If any upstream release renames an id this package references, V9 fails and
Package007 needs a corresponding release. `VERSION_HISTORY.md` lists exactly which ids are
referenced from each.
