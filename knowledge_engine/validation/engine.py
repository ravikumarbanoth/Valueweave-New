"""ValidationEngine — runs a configured list of ValidationRule instances over a record batch."""

from __future__ import annotations

from typing import Any, Optional

from knowledge_engine.validation.base import ValidationReport, ValidationRule


class ValidationEngine:
    """Runs `rules` over `records` in order and aggregates their violations into one report.

    A single engine instance is typically configured once per dataset (the rules that apply to
    `food_agro_processing_micro_enterprises.csv` differ from those for `msme_entrepreneurship_
    support_schemes.csv`, e.g. different required fields and no foreign keys) and reused across every
    validation run for that dataset.
    """

    def __init__(self, rules: list[ValidationRule]):
        self.rules = rules

    def run(
        self,
        records: list[dict[str, Any]],
        context: Optional[dict[str, Any]] = None,
    ) -> ValidationReport:
        context = context or {}
        report = ValidationReport(total_records=len(records), rules_run=[r.name for r in self.rules])
        for rule in self.rules:
            report.violations.extend(rule.check(records, context))
        return report

    def valid_records(
        self,
        records: list[dict[str, Any]],
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[list[dict[str, Any]], ValidationReport]:
        """Convenience wrapper returning (records that passed every rule, the full report).

        Records that failed at least one rule are excluded from the first element but remain fully
        described in the report — nothing is silently dropped without a reason attached.
        """
        report = self.run(records, context)
        failed = report.failed_record_indices
        passing = [r for i, r in enumerate(records) if i not in failed]
        return passing, report
