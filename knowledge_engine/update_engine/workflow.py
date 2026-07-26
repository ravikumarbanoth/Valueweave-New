"""UpdateWorkflow — the CHECK_SOURCE -> DETECT_CHANGES -> VALIDATE -> UPDATE_DATABASE ->
GENERATE_DRAFT -> PENDING_HUMAN_APPROVAL -> STABLE_RELEASE state machine named in the Phase-2 brief.

Each stage is a separate method so a caller (or a test) can drive the workflow one step at a time and
inspect state between steps, or call `run_to_approval()` to execute the automatable prefix in one
call. No path through this class reaches `STABLE_RELEASE` without an explicit `approve()` call — the
brief's "no AI implementation required yet" instruction extends naturally to "no auto-approval either."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, MutableMapping, Optional

from knowledge_engine.collectors.base import BaseCollector
from knowledge_engine.parsers.base import BaseParser, ParseError
from knowledge_engine.update_engine.states import WorkflowState
from knowledge_engine.validation.base import ValidationReport
from knowledge_engine.validation.engine import ValidationEngine


@dataclass
class TransitionRecord:
    state: WorkflowState
    timestamp: str
    note: str = ""


def default_change_detector(
    previous_records: list[dict[str, Any]], current_records: list[dict[str, Any]]
) -> bool:
    """Returns True iff `current_records` differs from `previous_records` at all.

    A real deployment will usually supply a smarter detector (e.g. comparing only substantive fields
    and ignoring `collection_date`/`last_verified`), but this default is a safe, dependency-free
    starting point: any difference in the record list counts as a change.
    """
    return previous_records != current_records


class WorkflowStateError(Exception):
    """Raised when a method is called in a state that doesn't permit it, e.g. `approve()` outside
    `PENDING_HUMAN_APPROVAL`."""


class UpdateWorkflow:
    def __init__(
        self,
        name: str,
        collector: BaseCollector,
        source: str,
        parser: BaseParser,
        validation_engine: ValidationEngine,
        on_generate_draft: Optional[Callable[[list[dict[str, Any]]], Any]] = None,
        change_detector: Callable[[list[dict[str, Any]], list[dict[str, Any]]], bool] = default_change_detector,
    ):
        self.name = name
        self.collector = collector
        self.source = source
        self.parser = parser
        self.validation_engine = validation_engine
        self.on_generate_draft = on_generate_draft
        self.change_detector = change_detector

        self.state = WorkflowState.NOT_STARTED
        self.history: list[TransitionRecord] = []
        self.error: Optional[str] = None

        self.current_records: list[dict[str, Any]] = []
        self.accepted_records: list[dict[str, Any]] = []
        self.validation_report: Optional[ValidationReport] = None
        self.draft: Any = None
        self._fetch_result = None

    def _transition(self, state: WorkflowState, note: str = "") -> None:
        self.state = state
        self.history.append(TransitionRecord(state, datetime.now(timezone.utc).isoformat(), note))

    def _fail(self, message: str) -> None:
        self.error = message
        self._transition(WorkflowState.FAILED, message)

    def check_source(self) -> WorkflowState:
        self._transition(WorkflowState.CHECKING_SOURCE)
        fetch_result = self.collector.fetch(self.source)
        if not fetch_result.ok:
            self._fail(fetch_result.error or "collector reported an unspecified failure")
            return self.state
        self._fetch_result = fetch_result
        return self.state

    def detect_changes(self, previous_records: Optional[list[dict[str, Any]]] = None) -> WorkflowState:
        if self.state == WorkflowState.FAILED:
            return self.state
        self._transition(WorkflowState.DETECTING_CHANGES)
        try:
            self.current_records = self.parser.parse(self._fetch_result.payload)
        except ParseError as exc:
            self._fail(f"parsing failed: {exc}")
            return self.state
        changed = self.change_detector(previous_records or [], self.current_records)
        if not changed:
            self._transition(WorkflowState.NO_CHANGES_DETECTED, "no differences from previous snapshot")
        return self.state

    def validate(self, context: Optional[dict[str, Any]] = None) -> WorkflowState:
        if self.state.is_terminal:
            return self.state
        self._transition(WorkflowState.VALIDATING)
        self.validation_report = self.validation_engine.run(self.current_records, context or {})
        return self.state

    def update_database(
        self,
        database: MutableMapping[Any, dict[str, Any]],
        key_field: str = "id",
    ) -> WorkflowState:
        if self.state.is_terminal:
            return self.state
        self._transition(WorkflowState.UPDATING_DATABASE)
        failed_indices = self.validation_report.failed_record_indices if self.validation_report else set()
        self.accepted_records = [
            r for i, r in enumerate(self.current_records) if i not in failed_indices
        ]
        for record in self.accepted_records:
            database[record[key_field]] = record
        return self.state

    def generate_draft(self) -> WorkflowState:
        if self.state.is_terminal:
            return self.state
        self._transition(WorkflowState.GENERATING_DRAFT)
        self.draft = self.on_generate_draft(self.accepted_records) if self.on_generate_draft else list(self.accepted_records)
        self._transition(WorkflowState.PENDING_HUMAN_APPROVAL, "awaiting human review of generated draft")
        return self.state

    def approve(self, approver: str, note: str = "") -> WorkflowState:
        if self.state != WorkflowState.PENDING_HUMAN_APPROVAL:
            raise WorkflowStateError(
                f"cannot approve from state {self.state}; approval is only valid from "
                f"{WorkflowState.PENDING_HUMAN_APPROVAL}"
            )
        self._transition(WorkflowState.STABLE_RELEASE, f"approved by {approver}" + (f": {note}" if note else ""))
        return self.state

    def reject(self, approver: str, reason: str) -> WorkflowState:
        if self.state != WorkflowState.PENDING_HUMAN_APPROVAL:
            raise WorkflowStateError(
                f"cannot reject from state {self.state}; rejection is only valid from "
                f"{WorkflowState.PENDING_HUMAN_APPROVAL}"
            )
        self._transition(WorkflowState.REJECTED, f"rejected by {approver}: {reason}")
        return self.state

    def run_to_approval(
        self,
        database: MutableMapping[Any, dict[str, Any]],
        previous_records: Optional[list[dict[str, Any]]] = None,
        context: Optional[dict[str, Any]] = None,
        key_field: str = "id",
    ) -> WorkflowState:
        """Runs every automatable stage in sequence, stopping at the first terminal state reached
        (`FAILED`, `NO_CHANGES_DETECTED`, or the happy path's `PENDING_HUMAN_APPROVAL`).

        This method never reaches `STABLE_RELEASE` by itself — call `approve()` separately.
        """
        self.check_source()
        if self.state.is_terminal:
            return self.state
        self.detect_changes(previous_records)
        if self.state.is_terminal:
            return self.state
        self.validate(context)
        self.update_database(database, key_field)
        self.generate_draft()
        return self.state

    def history_summary(self) -> list[dict[str, str]]:
        return [{"state": t.state.value, "timestamp": t.timestamp, "note": t.note} for t in self.history]
