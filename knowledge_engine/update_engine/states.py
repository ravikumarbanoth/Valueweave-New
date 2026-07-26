"""WorkflowState — the states of the Update Engine's check-detect-validate-update-draft-approve-
release workflow, named directly from the Phase-2 brief."""

from __future__ import annotations

from enum import Enum


class WorkflowState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    CHECKING_SOURCE = "CHECKING_SOURCE"
    DETECTING_CHANGES = "DETECTING_CHANGES"
    NO_CHANGES_DETECTED = "NO_CHANGES_DETECTED"
    VALIDATING = "VALIDATING"
    UPDATING_DATABASE = "UPDATING_DATABASE"
    GENERATING_DRAFT = "GENERATING_DRAFT"
    PENDING_HUMAN_APPROVAL = "PENDING_HUMAN_APPROVAL"
    STABLE_RELEASE = "STABLE_RELEASE"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

    @property
    def is_terminal(self) -> bool:
        return self in (
            WorkflowState.NO_CHANGES_DETECTED,
            WorkflowState.STABLE_RELEASE,
            WorkflowState.REJECTED,
            WorkflowState.FAILED,
        )


#: The happy-path order. The workflow does not skip states even when, e.g., a collector has no
#: validation rules configured — every stage still runs (a no-op validation still "runs"), so the
#: transition history is a complete, honest record of what happened during a given update cycle.
HAPPY_PATH_ORDER = [
    WorkflowState.CHECKING_SOURCE,
    WorkflowState.DETECTING_CHANGES,
    WorkflowState.VALIDATING,
    WorkflowState.UPDATING_DATABASE,
    WorkflowState.GENERATING_DRAFT,
    WorkflowState.PENDING_HUMAN_APPROVAL,
    WorkflowState.STABLE_RELEASE,
]
