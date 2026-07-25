# Codex Handoff — Package008_MSME v1.0.0

For whoever picks this up next, human or agent. What exists, what was deliberately left undone, and
where the traps are.

This is the **last package in the eight-package programme**, and the one that binds the rest
together. If you are new to the knowledge base, read this file and then `quality_report.md` before
touching anything.

## State

**Released, Stable v1.0.0.** 18 datasets, 477 records, 40 businesses, validation clean (0 violations
across 13 checks, including V13 normalization). Branch `claude/package008-msme-import`, merged to
`main`.

## Read first, in order

1. `README.md` — structure, and the normalization rule that defines the package
2. `quality_report.md` — **what this is and is not fit for**; read before building on it
3. `docs/METHODOLOGY.md` §2 — why no rupee figure appears anywhere, and §3 — why V13 exists
4. `validation_report.md` — the five defect classes the checks caught
5. `docs/IMPORT_GUIDE.md` §5 — how to join upstream without undoing the normalization

## Rebuild

```bash
cd packages/Package008_MSME
python3 gen_core.py         # 9 datasets, no upstream dependency
python3 gen_mappings.py     # 9 datasets, resolves upstream FKs live and aborts on failure
python3 validate.py         # 13 checks; writes validation_summary.json; exit 0 = clean
python3 build_artifacts.py  # schema catalog, 18 metadata, registry, manifest, 18 reports
python3 build_docs.py       # data dictionary, import guide, validation + quality reports,
                            # version history, release notes
```

**Order matters.** Both builders read `validation_summary.json`, so validation runs first. Every
count in every artifact is derived from the CSVs — nothing hand-maintained.

`README.md`, `CHANGELOG.md`, `docs/METHODOLOGY.md`, `docs/USAGE.md` and this file are hand-written.
Everything else is generated.

**A shell-hygiene note that cost time during this release:** `Bash` working directory persists
between calls. A `cd` into another package's directory earlier in a session means a later
`python3 build_artifacts.py` runs *that* package's builder. Always `cd` to the package root
explicitly, or use absolute paths.

## The one thing not to do

**Do not fill the investment fields with estimates.**

`investment_range` is sentinelled on all 40 businesses. So is every machinery cost. This is not an
oversight — it is documented in six places. A per-business project cost depends on throughput,
automation level, whether premises are owned, and which state you are in. Writing "₹15–25 lakh"
would make the package look entrepreneur-ready while being unverifiable and wrong for most readers.

If you obtain **DIC or MSME-DI project profiles** — which are published free of charge and are the
correct primary source — cite the specific profile per row, state the configuration it assumes, and
raise `confidence_score` accordingly. Anything else is fabrication in the field that matters most.

The same applies to `investment_intelligence`. It contains no percentage, no payback period and no
IRR by design. Adding one without the underlying figures would be inventing a number and calling it
analysis.

## Traps

**V13 will fight you if you "improve" the schema.** Adding a `scheme_benefit`, `nsqf_level`,
`crop_season` or `population` column to any Package008 dataset fails the build. That is the check
working. If you genuinely need the attribute, join to the upstream package — see `docs/USAGE.md`
Recipe 3 for the full path, and `docs/IMPORT_GUIDE.md` §5 for why a view is correct and a table is
not.

If you hit a V13 false positive (as `official_portal` was), **narrow the rule to be correct rather
than adding a blanket exception**. A suppressed check stops finding anything.

**Guessing an id format is not reading it.** Ten district refs in the first draft (`AP-GNT`,
`TG-SGR`, …) were plausible and do not exist. The real refs are `AP-GUN`, `TG-SNG`. V9 caught every
one only because the generator resolves against the actual CSV. Keep that discipline: if you add a
cross-package link, resolve it against the file, not against memory or documentation.

**Trust the dataset, not its collection report.** Package007 recorded this and it bit again here:
Package006's documentation describes skills its `skills.csv` does not contain.

**`business_id` values are positional** (`mb-001`…`mb-040`). Appending new businesses at `mb-041`
onward is safe. Inserting mid-list shifts every id after it and silently invalidates all eight
mapping datasets plus `investment_intelligence`. V8's denormalised-name check will catch it, but
appending avoids the work.

**`employment_generation` is a range string** (`'6-15'`), not a number. Sorting it as text gives
wrong order.

## Where the gaps are, ranked

| # | Gap | Effort | Notes |
|---|---|---|---|
| 1 | **Investment bands unsourced** | High | Needs DIC/MSME-DI project profiles. The main blocker to entrepreneur-facing use. |
| 2 | **Zero rows `VST-VERIFIED`** | High | Start with the 40 business rows — everything hangs off them. |
| 3 | **21 of 24 categories populated; several thin** | Medium | Semiconductors, robotics, creative industries have one business each. |
| 4 | **7 skill requirements have no Package006 record** | Low (for Package008) | Already documented as sentinel rows with the requirement stated. This is a Package006 task. |
| 5 | **54 machinery rows sentinel the Package005 ref** | Medium | Needs a general industrial machinery reference, or an expanded Package005 `farm_machinery`. |
| 6 | **`industry_mapping` covers 19 of 40** | Low | Blocked on Package004 expanding its opportunity coverage. |
| 7 | **No state MSME incentive mapping** | Medium | Package004 holds the TG/AP policy records to reconcile against. |
| 8 | **No Package003 link** | Low | Would need Package003 to add healthcare *enterprise* records, not just institutions. |

## What this package owes back to the rest of the programme

Package008 is the integration layer, so it surfaces upstream gaps that no other package can see.
Three concrete requests:

1. **To Package006:** seven skills exist as MSME requirements with no Package006 record — foundry
   casting, handloom weaving, corrugation machine operation, plastic reprocessing, chemical
   formulation, data entry, training delivery. Query
   `SELECT business_name, skill_role FROM skill_mapping WHERE package006_skill_id =
   'PENDING_VERIFICATION'` for the exact list.
2. **To Package005:** `farm_machinery` is agriculture-scoped, which is correct, but it means 54 of
   64 MSME machinery references cannot resolve. Either broaden it or create a sibling industrial
   machinery dataset.
3. **To Package004:** 21 of 40 businesses have no Package004 counterpart. Package004's own
   `acquisition_backlog.json` already queues several of the relevant categories.

## Programme-level note

With this release all eight packages are Stable v1.0.0. Two governance questions remain open across
the programme, neither of which Package008 can resolve alone:

1. **Scheme data ownership.** Six packages hold scheme rows (Package002 scholarships, Package003
   health insurance, Package004 MSME support, Package005 agriculture, Package006 skill, Package007
   canonical). Package007's `also_in_package` declares every overlap; nothing resolves it. See
   `Package007_Government_Schemes/codex_handoff.md` for three options and a recommendation.
2. **No package has had human data-steward review.** Every row across all eight packages is
   `VST-NEEDS_REVIEW`. Machine validation is thorough — 13 checks here, 10 to 12 elsewhere — but it
   confirms structure and references, never factual accuracy.

## Environment constraint you will also hit

WebFetch to `.gov.in`, `.nic.in` and `.ac.in` is blocked by organizational egress policy. Every row
is attributed to the governing body but no primary page was read, which is why `confidence_score` is
capped at 85 (observed max 78). Environmental, not a collection failure, and identical across
Package004 through Package008.

If that policy changes, the highest-value re-collection target for this package is unambiguous:
**MSME-DI project profiles for investment bands.** Nothing else would improve the package as much.

## Verification checklist before any future release

```bash
python3 validate.py
python3 -c "import json; s=json.load(open('validation_summary.json')); \
            assert s['violations']==0 and s['result']=='PASS' \
            and s['normalization_check']=='V13 PASS'; print('clean')"
git status --short
```

Then confirm `package_manifest.json`, `registry/dataset_registry.csv`, `validation_report.md` and
`quality_report.md` were regenerated — they all carry record counts, and a stale one is a silent lie
about the release.

## Upstream versions this was built against

Package001 v1.0.0, Package002 v1.0.0, Package003 v1.0.0, Package004 v1.0.0, Package005 v1.0.0,
Package006 v1.0.0, Package007 v1.0.0. `VERSION_HISTORY.md` lists exactly which ids are referenced
from each. This is the most upstream-dependent package in the programme by design — if any upstream
release renames a referenced id, V9 fails and Package008 needs a corresponding release.
