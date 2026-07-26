# ValueWeave Knowledge Engine — Architecture

## 1. Purpose

Package001_Geography through Package004_Industries were each built the same way, by hand: research a
domain via WebSearch, assemble CSVs with a fixed provenance schema, validate PK/FK/schema consistency,
write a matching set of manifests and reports, and promote through an RC → Stable lifecycle. That
process is sound but does not scale past a handful of packages built by a person driving an AI agent
turn by turn. The Knowledge Engine extracts that process into reusable software so that collecting,
validating, and packaging a new domain becomes a matter of configuring collectors and rules, not
re-deriving the methodology each time.

## 2. Design Principles

1. **Structured sources first, AI last.** Every collector and parser in this foundation works on
   structured or semi-structured input (API responses, CSV, JSON, XML, RSS, HTML tables) with zero AI
   involvement. AI is planned only for sources that have no structured form: PDFs, news synthesis, and
   arbitrary unstructured web pages — see `docs/ai_integration_plan.md`.
2. **Provenance is not optional.** Every record that leaves the Collector/Parser stage carries the
   same eight fields used in every ValueWeave package so far: Source, Source URL, Collection Date,
   Last Verified, Collector, Confidence, Verification Status, Package Version. A record without
   provenance cannot pass validation, by construction — see `docs/provenance_spec.md`.
3. **Validation is reusable, not bespoke per package.** The same seven rule types (required fields,
   foreign keys, duplicate detection, source validation, confidence scoring, schema validation, data
   freshness) apply to any dataset; a new package configures which rules apply to which fields rather
   than writing new validation logic — see `docs/validation_spec.md`.
4. **Packages remain immutable releases.** The Package Builder produces a versioned package folder
   that matches the existing `packages/README.md` convention exactly. Once released, a package version
   is not edited in place; a new version is built from an updated Knowledge Database snapshot — see
   `docs/package_builder_spec.md` and `docs/versioning_spec.md`.
5. **Human approval remains a required gate.** The Update Engine's workflow ends every cycle at a
   `PENDING_HUMAN_APPROVAL` state before a package can be promoted to Stable. Nothing in this
   foundation auto-promotes a package or a record's verification status — see
   `docs/update_engine_workflow.md`.
6. **Every module is independently testable.** Each of the 8 modules has a narrow interface
   (documented as an ABC/Protocol in code) so a new collector, parser, or validation rule can be added
   without touching the others — see `docs/collector_plugin_spec.md`.

## 3. High-Level Data Flow

```
                    ┌─────────────────────┐
                    │   External Sources   │
                    │  API / CSV / JSON /  │
                    │   XML / RSS / HTML   │
                    └──────────┬───────────┘
                               │
                     ┌─────────▼─────────┐
                     │  Collector Engine  │  (module 1 — no AI)
                     │  fetch raw payload │
                     └─────────┬─────────┘
                               │ raw payload + fetch metadata
                     ┌─────────▼─────────┐
                     │   Parser Engine    │  (module 2 — no AI)
                     │ normalize → records│
                     └─────────┬─────────┘
                               │ list[dict] candidate records
                     ┌─────────▼─────────┐
                     │  Provenance Engine │  (module 4)
                     │ attach 8-field     │
                     │ evidence per record│
                     └─────────┬─────────┘
                               │ provenanced records
                     ┌─────────▼─────────┐
                     │ Validation Engine  │  (module 3)
                     │ required fields,   │
                     │ FK, dupes, source, │
                     │ confidence, schema,│
                     │ freshness          │
                     └─────────┬─────────┘
                       pass    │    fail
                     ┌─────────▼─────────┐        ┌───────────────────┐
                     │  Knowledge         │        │  Validation Report │
                     │  Database (staging)│        │  (rejected records, │
                     │  accepted records  │        │   reasons, per-rule) │
                     └─────────┬─────────┘        └───────────────────┘
                               │
                     ┌─────────▼─────────┐
                     │  Update Engine     │  (module 7 — orchestrates
                     │  check→detect→     │   the above end-to-end for
                     │  validate→update→  │   a single collector run,
                     │  draft→approve→    │   then hands off to the
                     │  release           │   Package Builder)
                     └─────────┬─────────┘
                               │ approved snapshot
                     ┌─────────▼─────────┐
                     │  Package Builder   │  (module 5)
                     │  assembles the     │
                     │  packages/PackageNNN│
                     │  folder structure  │
                     └─────────┬─────────┘
                               │
                     ┌─────────▼─────────┐
                     │  Version Engine    │  (module 6)
                     │  SemVer bump,      │
                     │  changelog, history│
                     └─────────┬─────────┘
                               │
                     ┌─────────▼─────────┐
                     │  Released Package  │
                     │  packages/PackageNNN│
                     │  _Domain/vX.Y.Z    │
                     └─────────┬─────────┘
                               │
                     ┌─────────▼─────────┐
                     │   Rule Engine      │  (module 8 — queries
                     │  structured queries│   released package data;
                     │  over released data│   does not touch staging)
                     └────────────────────┘
```

## 4. Module Responsibilities

### 4.1 Collector Engine (`collectors/`)
Fetches raw payloads from a named source and returns them unparsed, tagged with fetch metadata
(source URL, fetch timestamp, HTTP status/exit code, collector name/version). Collectors do not
interpret the payload — that's the Parser Engine's job. New source types are added by implementing
`BaseCollector` and registering with `CollectorRegistry`; nothing else in the engine needs to change.
See `docs/collector_plugin_spec.md`.

### 4.2 Parser Engine (`parsers/`)
Takes a raw payload (from a Collector or from a file) and normalizes it into a list of flat
`dict` records ready for provenance-tagging and validation. Each parser handles exactly one input
format (CSV, JSON, XML, RSS, HTML tables); `pdf_parser.py` is an explicit placeholder that raises
`NotImplementedError`, documented rather than silently stubbed, because PDF text extraction without
either a structured layer (form fields/tables) or an AI reader produces unreliable data — see
`docs/ai_integration_plan.md`.

### 4.3 Validation Engine (`validation/`)
Runs a configurable list of `ValidationRule` instances over a batch of records and produces a
`ValidationReport` (per-record pass/fail, per-rule failure counts, and the specific reason for each
failure). The same 7 rule types used by hand in Package001–004's `validation_report.md` files
(required fields, FK integrity, duplicate detection, source validation, confidence scoring, schema
validation, data freshness) are implemented once and reused across every future package. See
`docs/validation_spec.md`.

### 4.4 Provenance Engine (`core/provenance.py`, `provenance/`)
Defines `ProvenanceRecord`, the exact 8-field evidence model every ValueWeave package has carried
since Package001: `source`, `source_url`, `collection_date`, `last_verified`, `collector`,
`confidence`, `verification_status`, `package_version`. `provenance/tracker.py` attaches or updates
this record on any record dict without mutating the record's substantive fields. See
`docs/provenance_spec.md`.

### 4.5 Package Builder (`package_builder/`)
Given a set of validated, provenanced record batches (one per dataset) plus a package name/number and
schema definitions, assembles the exact folder structure documented in `packages/README.md`: `README.md`,
`VERSION`, `CHANGELOG.md`, `package_manifest.json`, `datasets/*.csv`, `metadata/*.metadata.json`,
`schemas/schema_catalog.json`, `registry/dataset_registry.csv`, `evidence/*.evidence_manifest.json`,
`imports/*.import_manifest.json`, `raw_sources/*.source_inventory.md`, and starter `reports/` and
`docs/` content. It does not decide package *content* — that's upstream — it mechanizes the
*packaging convention* so every future package is structurally identical to Package001–004 without
manual folder assembly. See `docs/package_builder_spec.md`.

### 4.6 Version Engine (`versioning/`)
Implements semantic versioning (`semver.py`: parse, compare, bump major/minor/patch) and a
JSON-backed `VersionHistory` (`history.py`) that records every version transition for a package with a
timestamp, change summary, and enough information to roll back to a prior version's manifest. See
`docs/versioning_spec.md`.

### 4.7 Update Engine (`update_engine/`)
Implements the workflow named in the brief as an explicit state machine:
`CHECK_SOURCE → DETECT_CHANGES → VALIDATE → UPDATE_DATABASE → GENERATE_DRAFT → PENDING_HUMAN_APPROVAL
→ STABLE_RELEASE` (with `REJECTED` and `FAILED` as terminal non-happy-path states). Each transition is
a method with a hook point so a caller can inject collector/validator/builder instances rather than
the workflow hard-coding them. No transition auto-advances past `PENDING_HUMAN_APPROVAL`. See
`docs/update_engine_workflow.md`.

### 4.8 Rule Engine (`rule_engine/`)
A small, dependency-free structured query engine over lists of record dicts, supporting the
comparison/membership operators needed for the brief's example queries ("Investment < ₹5 lakh",
"District = Medak", "Skill Level = Beginner", "Suitable for Women", "Suitable for Students", "Suitable
for Rural Areas") via a chainable `RuleQuery` builder. This is the same engine that will power
ValueWeave's user-facing filtering before any LLM-based query understanding is added. See
`docs/rule_engine_spec.md`.

## 5. Where AI Fits Later (and Where It Deliberately Doesn't Yet)

See `docs/ai_integration_plan.md` for the full plan. In summary: AI is planned as an additional
Collector+Parser pair for PDF documents, news article synthesis, and complex/unstructured webpages —
each one still required to emit records that pass through the same Validation and Provenance engines
as every deterministic source, with confidence scores calibrated lower by convention (mirroring how
Package001–004 already capped confidence for portal/blog-only estimates versus government-document
sources). No module in this v0.1.0 foundation calls an AI model.

## 6. Relationship to Existing Packages

This foundation does not modify `packages/Package001_Geography` through `packages/Package004_Industries`
in any way. It is designed so that a future `packages/Package005_*` (or a new minor version of an
existing package) *could* be produced by configuring Collectors + Validation rules + a Package Builder
run rather than by hand — but making that switch for any specific package is a separate, explicit
future task, not something this foundation does automatically.
