"""Validation Engine — base interface and result types.

A ValidationRule inspects a batch of records (each a flat dict, typically already carrying the
`data_source`/`source_url`/`collection_date`/`confidence_score`/`verification_status`/`notes`
provenance columns from `core.provenance.ProvenanceRecord.to_csv_fields()`) and reports per-record
pass/fail with a reason. Rules never mutate records — a rule that could plausibly "fix" a record
(e.g. by filling in a missing field) belongs in the Parser Engine, not here, so that Validation stays
a pure, side-effect-free check.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RuleViolation:
    """A single record's failure against a single rule."""

    record_index: int
    rule_name: str
    field: Optional[str]
    reason: str
    record_id: Optional[str] = None


@dataclass
class ValidationReport:
    """The output of a full `ValidationEngine.run()` call over a batch of records."""

    total_records: int
    violations: list[RuleViolation] = field(default_factory=list)
    rules_run: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    @property
    def failed_record_indices(self) -> set[int]:
        return {v.record_index for v in self.violations}

    @property
    def pass_count(self) -> int:
        return self.total_records - len(self.failed_record_indices)

    def violations_for_rule(self, rule_name: str) -> list[RuleViolation]:
        return [v for v in self.violations if v.rule_name == rule_name]

    def summary(self) -> dict[str, Any]:
        by_rule: dict[str, int] = {}
        for v in self.violations:
            by_rule[v.rule_name] = by_rule.get(v.rule_name, 0) + 1
        return {
            "total_records": self.total_records,
            "passing_records": self.pass_count,
            "failing_records": len(self.failed_record_indices),
            "rules_run": self.rules_run,
            "violations_by_rule": by_rule,
        }


class ValidationRule(ABC):
    """The interface every validation rule must implement."""

    #: Short, stable identifier used in `RuleViolation.rule_name` and validation reports.
    name: str = "base_rule"

    @abstractmethod
    def check(self, records: list[dict[str, Any]], context: dict[str, Any]) -> list[RuleViolation]:
        """Check `records` and return the list of violations found (empty if all pass).

        `context` carries cross-record information a rule may need: the dataset's schema definition,
        other datasets in the same package (for foreign-key checks), the package's declared
        `as_of_date` (for freshness checks), etc. See `docs/validation_spec.md` for the exact keys
        each built-in rule reads from `context`.
        """
        raise NotImplementedError
