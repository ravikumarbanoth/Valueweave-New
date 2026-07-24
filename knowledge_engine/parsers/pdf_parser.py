"""PDFParser — explicit placeholder, by design.

PDF text extraction without either a structured layer (fillable form fields, tagged tables) or an
AI-assisted reader produces unreliable, hard-to-validate data — exactly the kind of "government
DIC/PMFME project-profile PDF located by URL but never directly read" gap flagged repeatedly in
Package001-004's `acquisition_backlog.json`. Rather than ship a brittle text-scraping heuristic that
would silently produce low-quality records indistinguishable in shape from the engine's other,
reliable parsers, this module raises `NotImplementedError` until the AI-assisted PDF extraction path
described in `docs/ai_integration_plan.md` is built. When it is built, it must still route every
extracted record through the same `ValidationEngine` and `ProvenanceTracker` as every other parser —
this class exists so that call site is already wired and just needs its `NotImplementedError`
replaced with a real implementation.
"""

from __future__ import annotations

from typing import Any

from knowledge_engine.parsers.base import BaseParser


class PDFParser(BaseParser):
    name = "pdf_parser"
    version = "0.1.0"

    def parse(self, payload: Any, **kwargs: Any) -> list[dict[str, Any]]:
        raise NotImplementedError(
            "PDFParser is an intentional placeholder. PDF extraction requires either a structured "
            "form-field/table layer or AI-assisted reading, neither of which is implemented in this "
            "foundation release. See docs/ai_integration_plan.md for the planned design before "
            "implementing this method."
        )
