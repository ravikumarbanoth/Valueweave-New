# ValueWeave Knowledge Engine — Development Roadmap

## Phase 0 — Foundation (this release, v0.1.0)

- [x] Define the 8-module architecture and interfaces (`architecture.md`).
- [x] Collector Engine: `BaseCollector` interface, `CollectorRegistry`, and working CSV/JSON/XML/
      RSS/generic-API collectors (local-file and HTTP-capable, stdlib-only).
- [x] Parser Engine: `BaseParser` interface and working CSV/JSON/XML/RSS/HTML-table parsers; PDF
      parser placeholder that raises `NotImplementedError` by design.
- [x] Validation Engine: `ValidationRule` interface and the 7 reusable rule types (required fields,
      foreign keys, duplicate detection, source validation, confidence scoring, schema validation,
      data freshness), plus `ValidationEngine` to run a ruleset and produce a `ValidationReport`.
- [x] Provenance Engine: `ProvenanceRecord` (8-field model matching every package shipped so far) and
      `ProvenanceTracker` to attach/update it on records.
- [x] Package Builder: `PackageBuilder` that assembles the `packages/PackageNNN_Domain/` folder
      structure from validated, provenanced record batches plus a schema definition.
- [x] Version Engine: SemVer parsing/bumping/comparison and a JSON-backed `VersionHistory` with
      rollback support.
- [x] Update Engine: the `CHECK_SOURCE → DETECT_CHANGES → VALIDATE → UPDATE_DATABASE →
      GENERATE_DRAFT → PENDING_HUMAN_APPROVAL → STABLE_RELEASE` workflow as an explicit, testable
      state machine with injectable hooks.
- [x] Rule Engine: chainable `RuleQuery` supporting `<`, `<=`, `>`, `>=`, `==`, `!=`, `in`,
      `contains`, and boolean AND/OR composition over record lists.
- [x] Unit tests for validation, rule engine, versioning, and collectors/parsers (stdlib
      `unittest`, no network access required).
- [x] Full module specifications in `docs/` (no placeholder text).

## Phase 1 — Knowledge Database & Persistence (next)

- [ ] Define the Knowledge Database schema: a persistent store (initially likely MongoDB, matching
      `backend/requirements.txt`'s existing `motor`/`pymongo` dependency) that holds staged records
      between collection and package-build time, keyed by package/dataset/record `id` with full
      version history.
- [ ] Implement a `KnowledgeDatabase` adapter with the same interface regardless of backing store, so
      the in-memory reference implementation used by Phase 0's tests can be swapped for the real store
      without changing any of the 8 modules above it.
- [ ] Wire `update_engine.workflow.UpdateWorkflow` to read from and write to the real Knowledge
      Database instead of an in-memory list.

## Phase 2 — First Live Collector Wiring

- [ ] Choose one narrow, genuinely open-API or open-CSV government/public data source (e.g. an
      Indian Open Government Data Platform (data.gov.in) API endpoint or a downloadable CSV dataset)
      and wire it end-to-end: Collector → Parser → Provenance → Validation → staged Knowledge Database
      records — as a proof that the pipeline works against a real external source, not just fixtures.
- [ ] Compare the resulting records' shape and provenance against Package001–004's hand-built
      convention and document any schema gaps found.

## Phase 3 — First Engine-Built Package (candidate: Package005 or a minor version bump)

- [ ] Run the full pipeline (Collector → Parser → Validation → Provenance → Update Engine workflow →
      Package Builder → Version Engine) end-to-end to produce one real package release candidate,
      with a human approval gate before promotion, exactly as `docs/update_engine_workflow.md`
      specifies.
- [ ] Compare the Package Builder's output folder structure against `packages/README.md`'s
      convention field-by-field and close any gaps.

## Phase 4 — Rule Engine Integration with the Application Layer

- [ ] Expose the Rule Engine's `RuleQuery` through a `backend/` FastAPI endpoint so the frontend can
      issue structured filters ("Investment < ₹5 lakh", "District = Medak", "Suitable for Women")
      against released package data without any AI in the request path.
- [ ] Add pagination, sorting, and basic full-text fallback (still non-AI) for fields the Rule Engine
      doesn't structurally index.

## Phase 5 — AI-Assisted Extraction (additive, optional, gated)

- [ ] Implement a `PDFCollector` + AI-assisted `PDFParser` for government project-profile PDFs (the
      exact gap flagged repeatedly in Package001–004's `acquisition_backlog.json` — DIC/PMFME
      documents located by URL but never directly read due to the WebFetch environment constraint).
- [ ] Implement a `NewsCollector`/`NewsParser` pair for trusted-news synthesis (Tier 4 in the existing
      package methodology), with confidence scores capped below structured-source records by
      convention.
- [ ] Implement a general unstructured-webpage extractor as a last resort, used only when no
      structured collector/parser can reach the source.
- [ ] Every AI-produced record must pass through the same `ValidationEngine` and
      `ProvenanceTracker` as deterministic sources — no exception path. See
      `docs/ai_integration_plan.md` for the full design.

## Phase 6 — Update Automation

- [ ] Add a scheduler (cron-style) that triggers `UpdateWorkflow.check_source()` on a per-collector
      cadence, auto-advancing through `DETECT_CHANGES` and `VALIDATE`, but always stopping at
      `PENDING_HUMAN_APPROVAL` — automation shortens the loop, it does not remove the human gate.
- [ ] Add change-notification (e.g. a summary of what changed since the last approved version) to make
      the human-approval step fast to review rather than a full re-audit each time.

## Explicitly Out of Scope for This Foundation

- No AI-based extraction is implemented in Phase 0 (by explicit instruction).
- No live scheduler/cron binding is implemented in Phase 0 — the Update Engine's state machine is
  complete and tested, but nothing calls it automatically yet.
- No existing package (001–004) is modified, migrated, or re-built through this engine in Phase 0.
- No new external service dependency (database, queue, cloud API) is introduced in Phase 0 — every
  module runs against local fixtures and in-memory structures so it can be reviewed and tested without
  provisioning anything.
