# ValueWeave Knowledge Engine (VKE)

**Version:** 0.1.0 (Foundation)
**Status:** New infrastructure — does not replace or modify Package001–Package004.

The ValueWeave Knowledge Engine is the reusable backend that will collect, validate, version, and
package every future ValueWeave knowledge domain (Agriculture, Skills, Government Schemes, MSME, and
beyond) using the same discipline that was applied by hand to Package001_Geography through
Package004_Industries: no fabricated data, explicit provenance on every record, an honest
`PENDING_VERIFICATION` sentinel where a fact can't be sourced, and immutable versioned releases.

Where Package001–004 were built by manually running research passes and hand-assembling the package
folder structure, the Knowledge Engine turns that same process into reusable software: a plugin-based
**Collector Engine** pulls raw data from APIs, files, and feeds; a **Parser Engine** normalizes it; a
**Validation Engine** checks it against reusable rules; a **Provenance Engine** attaches the same
eight-field evidence trail used in every package so far; a **Package Builder** assembles the result
into the exact folder structure documented in `packages/README.md`; a **Version Engine** manages
semantic versioning and rollback; an **Update Engine** orchestrates the check-detect-validate-update-
draft-approve-release workflow; and a **Rule Engine** answers structured queries like "Investment <
₹5 lakh AND District = Medak AND Suitable for Women" without needing an LLM in the loop.

## Design Principle: AI Is Optional, Never Required

Every module in this engine works completely without AI. Structured sources (APIs, CSV, JSON, XML,
RSS, HTML tables) are collected and parsed deterministically. AI is planned as a **later, additive**
capability for the sources structured methods cannot reach — PDF extraction, news synthesis, and
unstructured web pages — and even then it will run through the same Validation and Provenance engines
as every other source, never bypassing them. See `docs/ai_integration_plan.md`.

## Relationship to `packages/`

The Knowledge Engine does not contain data. It contains the machinery that produces packages living
under `packages/PackageNNN_Domain_Name/`. Package001–Package004 were built manually; from
Package005 onward, the goal is for the Package Builder to assemble that same folder structure (README,
VERSION, CHANGELOG, package_manifest.json, datasets/, metadata/, schemas/, registry/, evidence/,
imports/, raw_sources/, reports/, docs/) from records the Collector/Parser/Validation/Provenance
engines have already processed — see `docs/package_builder_spec.md`.

## Directory Structure

```
knowledge_engine/
├── README.md                      — this file
├── architecture.md                — system architecture and data flow
├── ROADMAP.md                     — development roadmap (phases, milestones)
├── requirements.txt                — Python dependencies (stdlib-first, minimal)
├── config/
│   └── example.config.json         — example engine configuration
├── core/
│   ├── types.py                     — shared enums (VerificationStatus, ConfidenceTier, SourceTier)
│   └── provenance.py                 — ProvenanceRecord: the 8-field evidence model
├── collectors/                        — Collector Engine (module 1)
│   ├── base.py                         — BaseCollector interface + CollectorRegistry
│   ├── api_collector.py                 — generic REST/JSON API collector
│   ├── csv_collector.py                  — local/remote CSV collector
│   ├── json_collector.py                  — local/remote JSON collector
│   ├── xml_collector.py                    — local/remote XML collector
│   └── rss_collector.py                     — RSS/Atom feed collector
├── parsers/                                  — Parser Engine (module 2)
│   ├── base.py                                — BaseParser interface
│   ├── csv_parser.py
│   ├── json_parser.py
│   ├── xml_parser.py
│   ├── rss_parser.py
│   ├── html_table_parser.py
│   └── pdf_parser.py                            — placeholder; raises NotImplementedError by design
├── validation/                                    — Validation Engine (module 3)
│   ├── base.py                                     — ValidationRule interface, ValidationReport
│   ├── rules.py                                     — the 7 reusable rule implementations
│   └── engine.py                                     — ValidationEngine: runs a ruleset over records
├── provenance/                                        — Provenance Engine (module 4)
│   ├── schema.json                                     — canonical JSON Schema for a provenance record
│   └── tracker.py                                       — ProvenanceTracker: attach/update provenance
├── package_builder/                                       — Package Builder (module 5)
│   ├── builder.py                                          — PackageBuilder: assembles a package folder
│   └── templates.py                                         — doc/manifest string templates
├── versioning/                                                — Version Engine (module 6)
│   ├── semver.py                                               — SemVer parsing, bumping, comparison
│   └── history.py                                               — VersionHistory: JSON-backed changelog
├── update_engine/                                                 — Update Engine (module 7)
│   ├── states.py                                                   — WorkflowState enum
│   └── workflow.py                                                  — UpdateWorkflow state machine
├── rule_engine/                                                       — Rule Engine (module 8)
│   ├── operators.py                                                    — comparison/membership operators
│   └── engine.py                                                        — RuleEngine: structured queries
├── docs/                                                                  — module specifications
│   ├── collector_plugin_spec.md
│   ├── validation_spec.md
│   ├── provenance_spec.md
│   ├── package_builder_spec.md
│   ├── versioning_spec.md
│   ├── update_engine_workflow.md
│   ├── rule_engine_spec.md
│   └── ai_integration_plan.md
├── examples/                                                                — runnable usage examples
│   ├── example_collect_and_validate.py
│   ├── example_build_package.py
│   └── example_rule_query.py
└── tests/                                                                    — unit tests (stdlib unittest)
    ├── test_validation.py
    ├── test_rule_engine.py
    ├── test_versioning.py
    └── test_collectors_parsers.py
```

## Getting Started

```bash
cd knowledge_engine
python -m pytest tests/ -v          # or: python -m unittest discover tests
python examples/example_collect_and_validate.py
python examples/example_rule_query.py
```

No network access or API keys are required to run the examples or tests — they operate on local
fixture data using the CSV/JSON collectors and parsers.

## Module Index

| # | Module | Folder | Spec |
|---|---|---|---|
| 1 | Collector Engine | `collectors/` | `docs/collector_plugin_spec.md` |
| 2 | Parser Engine | `parsers/` | `docs/collector_plugin_spec.md` (shared with collectors) |
| 3 | Validation Engine | `validation/` | `docs/validation_spec.md` |
| 4 | Provenance Engine | `provenance/`, `core/provenance.py` | `docs/provenance_spec.md` |
| 5 | Package Builder | `package_builder/` | `docs/package_builder_spec.md` |
| 6 | Version Engine | `versioning/` | `docs/versioning_spec.md` |
| 7 | Update Engine | `update_engine/` | `docs/update_engine_workflow.md` |
| 8 | Rule Engine | `rule_engine/` | `docs/rule_engine_spec.md` |

## What This Foundation Does NOT Do Yet

- It does not run any AI-based extraction. Every collector/parser in this release is deterministic.
- It does not yet have a live scheduler wired to `Package005` or any other in-progress package —
  Package001–004 remain the hand-built reference implementations this engine is designed to
  eventually replace the manual steps of, not something this release retrofits onto them.
- The PDF parser is an explicit placeholder (raises `NotImplementedError`) — see
  `docs/ai_integration_plan.md` for why PDF extraction is deliberately deferred to the AI-assisted
  phase rather than attempted with brittle heuristics now.
- The Update Engine's workflow is implemented as an explicit, testable state machine with hooks for
  each stage; it does not yet have a live cron/scheduler binding — see `ROADMAP.md`.

See `architecture.md` for the full data-flow diagram and `ROADMAP.md` for what's planned next.
