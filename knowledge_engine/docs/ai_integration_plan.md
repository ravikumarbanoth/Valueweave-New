# Future AI Integration Plan

This foundation release (v0.1.0) implements **zero** AI-based extraction, per explicit instruction.
This document specifies where AI is planned to be added later, why it's deferred, and — most
importantly — the constraints any future AI integration must satisfy so it never becomes a way to
bypass the discipline (provenance, validation, human approval) the rest of this engine enforces.

## 1. Why AI Is Deferred, Not Just Delayed

Every deterministic collector/parser in this release (API, CSV, JSON, XML, RSS, HTML tables) produces
records whose correctness is verifiable by construction: a CSV cell either contains what the source
file contained, or the parser raised an error. An AI-based extractor's output is a *claim* about what
a source document says, not a mechanical transcription of it — it can be wrong in ways that look
identical to being right. Package001 through Package004 encountered this exact tension repeatedly:
WebSearch-snippet-sourced research (already partially AI-mediated, since an agent reads and summarizes
search results) required confidence-score capping, a `PENDING_VERIFICATION` sentinel discipline, and
multiple rounds of catching a subtle formatting bug (`PENDING_VERIFICATION - <explanation>` instead of
the bare sentinel) that a fully mechanical parser would never introduce. AI extraction should be added
only where structured methods genuinely cannot reach a source, and only with the same or stronger
validation wrapped around it.

## 2. Priority Order (Restated From the Brief)

**Always prefer, in this order, before considering AI:**

1. Official API
2. RSS/Atom feed
3. CSV
4. JSON
5. XML
6. HTML table (structured, on a page)

**AI is added only for the sources below, which have no structured form to fall back to:**

1. PDF documents (especially the government DIC/PMFME/KVIC project-profile PDFs flagged repeatedly in
   Package001-004's `acquisition_backlog.json` as "located by URL but never directly read" — this is
   the single clearest, most concrete unblock this plan targets).
2. News article synthesis (Tier 4 in the existing package methodology — trusted news used for scheme
   renames and policy transitions; currently done by a human-driven WebSearch agent, a process this
   plan would eventually mechanize behind the same collector/parser interface).
3. Complex or unstructured webpages — a page with no clean `<table>`, no API, and no downloadable
   structured export.

## 3. Design Constraints for Every Future AI-Assisted Collector/Parser

Any `PDFCollector`/`PDFParser`, `NewsCollector`/`NewsParser`, or general unstructured-webpage
extractor added in a future phase **must**:

1. **Implement the exact same `BaseCollector`/`BaseParser` interfaces** as every deterministic
   plugin in this release. An AI-assisted parser is still a `BaseParser` returning `list[dict]` —
   nothing downstream (Provenance, Validation, Package Builder) should need to know or care that AI
   was involved in producing a given record.
2. **Route every output record through the same `ValidationEngine`** as deterministic sources — no
   AI-specific bypass path. If an AI-extracted record can't pass `SourceValidationRule`,
   `ConfidenceScoringRule`, etc., it fails exactly like a malformed CSV row would.
3. **Cap confidence scores lower by convention**, mirroring how Package001-004 already capped
   portal/blog-only estimates at 55-69 versus 70-85 for government-document-traced facts. An
   AI-extracted claim from a PDF the model read directly should score in a band that reflects "an AI
   summarized this document," not "this was mechanically transcribed."
4. **Never auto-promote `verification_status`.** Exactly like every deterministic collector, an
   AI-assisted one produces `VST-NEEDS_REVIEW` records. If anything, AI-sourced records are the
   category *most* in need of human review before promotion, not less.
5. **Preserve the source document/page itself as evidence**, not just a citation URL — e.g. store the
   specific PDF page number or article URL an AI extraction claim is based on, so a human reviewer can
   check the claim against the primage source directly, the same way a `source_url` lets a reviewer
   check a WebSearch-derived fact today.
6. **Never fabricate.** The single rule stated in every package's methodology (`docs/METHODOLOGY.md`)
   applies without exception to AI-assisted extraction: where a document doesn't contain a clear
   answer, the output field is the `PENDING_VERIFICATION` sentinel, never a plausible-sounding guess
   an AI model might otherwise be inclined to produce.

## 4. Sequencing

See `ROADMAP.md` Phase 5 for where this sits relative to the rest of the engine's build-out: AI
integration is planned *after* the Knowledge Database (Phase 1), a first live deterministic collector
(Phase 2), a first engine-built package (Phase 3), and Rule Engine/API wiring (Phase 4) — deliberately
last, so the discipline this plan depends on (validation, provenance, human approval) is already
proven against real deterministic data before any AI-produced record needs to pass through it.

## 5. What This Plan Explicitly Does Not Authorize

This document is a plan, not an implementation. Nothing in this Knowledge Engine foundation release
calls an AI model, and nothing in `ROADMAP.md` Phase 5 should be started without a separate, explicit
decision to do so — this plan exists so that decision, when made, has a design to follow rather than
being improvised per-source.
