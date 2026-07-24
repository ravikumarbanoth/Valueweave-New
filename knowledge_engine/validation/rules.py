"""The 7 reusable validation rule types named in the Phase-2 brief.

Every rule here reimplements, as reusable software, a check that was previously run by hand (or by a
one-off Python snippet) against every ValueWeave package's `validation_report.md` so far: required
fields, foreign keys, duplicate detection, source validation, confidence scoring, schema validation,
and data freshness.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Optional

from knowledge_engine.core.types import PENDING_VERIFICATION
from knowledge_engine.validation.base import RuleViolation, ValidationRule

_URL_RE = re.compile(r"^https?://[^\s]+$")


class RequiredFieldsRule(ValidationRule):
    """Fails a record if any of `fields` is missing or blank.

    A field holding the literal `PENDING_VERIFICATION` sentinel counts as present — it is an
    explicit, disclosed "known unknown," not missing data, matching the convention used throughout
    Package001-004.
    """

    name = "required_fields"

    def __init__(self, fields: list[str]):
        self.fields = fields

    def check(self, records: list[dict[str, Any]], context: dict[str, Any]) -> list[RuleViolation]:
        violations = []
        for i, record in enumerate(records):
            for field_name in self.fields:
                value = record.get(field_name)
                if value is None or (isinstance(value, str) and not value.strip()):
                    violations.append(
                        RuleViolation(
                            record_index=i,
                            rule_name=self.name,
                            field=field_name,
                            reason=f"required field '{field_name}' is missing or blank",
                            record_id=record.get("id"),
                        )
                    )
        return violations


class ForeignKeyRule(ValidationRule):
    """Fails a record if `field`'s value is not found among the referenced dataset's key values.

    Reads `context["datasets"]`, a `dict[str, list[dict]]` mapping dataset name to its records —
    matching how a package's other CSVs would be supplied during a real validation run.
    """

    name = "foreign_key"

    def __init__(self, field: str, references_dataset: str, references_field: str = "id"):
        self.field = field
        self.references_dataset = references_dataset
        self.references_field = references_field

    def check(self, records: list[dict[str, Any]], context: dict[str, Any]) -> list[RuleViolation]:
        datasets = context.get("datasets", {})
        if self.references_dataset not in datasets:
            raise KeyError(
                f"ForeignKeyRule needs context['datasets']['{self.references_dataset}'] to validate "
                f"field '{self.field}'"
            )
        valid_keys = {row.get(self.references_field) for row in datasets[self.references_dataset]}
        violations = []
        for i, record in enumerate(records):
            value = record.get(self.field)
            if value in (None, "", PENDING_VERIFICATION):
                continue
            if value not in valid_keys:
                violations.append(
                    RuleViolation(
                        record_index=i,
                        rule_name=self.name,
                        field=self.field,
                        reason=(
                            f"value {value!r} not found in "
                            f"{self.references_dataset}.{self.references_field}"
                        ),
                        record_id=record.get("id"),
                    )
                )
        return violations


class DuplicateDetectionRule(ValidationRule):
    """Fails every record sharing a `key_fields` tuple with another record.

    Checks within the current batch by default; also checks against `context["existing_keys"]`
    (an iterable of key tuples already committed elsewhere, e.g. other datasets in the same package)
    when provided, matching the cross-dataset ID-collision check every package has run since
    Package001.
    """

    name = "duplicate_detection"

    def __init__(self, key_fields: list[str]):
        self.key_fields = key_fields

    def check(self, records: list[dict[str, Any]], context: dict[str, Any]) -> list[RuleViolation]:
        existing_keys = set(context.get("existing_keys", set()))
        seen: dict[tuple[Any, ...], int] = {}
        violations = []
        for i, record in enumerate(records):
            key = tuple(record.get(f) for f in self.key_fields)
            if key in existing_keys:
                violations.append(
                    RuleViolation(
                        record_index=i,
                        rule_name=self.name,
                        field=",".join(self.key_fields),
                        reason=f"key {key} collides with a record outside this batch",
                        record_id=record.get("id"),
                    )
                )
            elif key in seen:
                violations.append(
                    RuleViolation(
                        record_index=i,
                        rule_name=self.name,
                        field=",".join(self.key_fields),
                        reason=f"key {key} duplicates record at index {seen[key]} in this batch",
                        record_id=record.get("id"),
                    )
                )
            else:
                seen[key] = i
        return violations


class SourceValidationRule(ValidationRule):
    """Fails a record if `data_source` is blank or `source_url` is not a well-formed http(s) URL
    (or, when `allow_local_paths=True`, a non-empty local path/reference)."""

    name = "source_validation"

    def __init__(self, allow_local_paths: bool = False):
        self.allow_local_paths = allow_local_paths

    def check(self, records: list[dict[str, Any]], context: dict[str, Any]) -> list[RuleViolation]:
        violations = []
        for i, record in enumerate(records):
            data_source = str(record.get("data_source", "")).strip()
            source_url = str(record.get("source_url", "")).strip()
            if not data_source:
                violations.append(
                    RuleViolation(i, self.name, "data_source", "data_source is blank", record.get("id"))
                )
            if not source_url:
                violations.append(
                    RuleViolation(i, self.name, "source_url", "source_url is blank", record.get("id"))
                )
                continue
            urls = [u.strip() for u in source_url.split(";") if u.strip()]
            for url in urls:
                if _URL_RE.match(url):
                    continue
                if self.allow_local_paths:
                    continue
                violations.append(
                    RuleViolation(
                        i, self.name, "source_url", f"'{url}' is not a well-formed http(s) URL", record.get("id")
                    )
                )
        return violations


class ConfidenceScoringRule(ValidationRule):
    """Fails a record if `confidence_score` is missing, out of [0, 100], or (when `max_score` is
    given) exceeds a package-wide ceiling — matching the "no confidence score exceeds N" check run
    by hand in every package's `validation_report.md`."""

    name = "confidence_scoring"

    def __init__(self, max_score: int = 100):
        self.max_score = max_score

    def check(self, records: list[dict[str, Any]], context: dict[str, Any]) -> list[RuleViolation]:
        violations = []
        for i, record in enumerate(records):
            raw = record.get("confidence_score")
            try:
                score = int(raw)
            except (TypeError, ValueError):
                violations.append(
                    RuleViolation(i, self.name, "confidence_score", f"'{raw}' is not an integer", record.get("id"))
                )
                continue
            if not (0 <= score <= self.max_score):
                violations.append(
                    RuleViolation(
                        i,
                        self.name,
                        "confidence_score",
                        f"{score} is outside the allowed range [0, {self.max_score}]",
                        record.get("id"),
                    )
                )
        return violations


class SchemaValidationRule(ValidationRule):
    """Fails a record whose fields don't match a schema definition.

    `schema` is a list of column definitions in the same shape used by
    `packages/*/schemas/schema_catalog.json`: `[{"name": str, "type": str, "values": list[str]?}, ...]`.
    Checks: every schema column is present in the record; `type: "enum"` columns' values are within
    the declared `values`; `type: "integer"` columns parse as int.
    """

    name = "schema_validation"

    def __init__(self, schema: list[dict[str, Any]]):
        self.schema = schema

    def check(self, records: list[dict[str, Any]], context: dict[str, Any]) -> list[RuleViolation]:
        violations = []
        for i, record in enumerate(records):
            for column in self.schema:
                col_name = column["name"]
                if col_name not in record:
                    violations.append(
                        RuleViolation(i, self.name, col_name, "column missing from record", record.get("id"))
                    )
                    continue
                value = record[col_name]
                if column.get("type") == "enum" and value not in (column.get("values") or []):
                    if value == PENDING_VERIFICATION:
                        continue
                    violations.append(
                        RuleViolation(
                            i,
                            self.name,
                            col_name,
                            f"'{value}' is not one of the allowed values {column.get('values')}",
                            record.get("id"),
                        )
                    )
                elif column.get("type") == "integer":
                    try:
                        int(value)
                    except (TypeError, ValueError):
                        if value == PENDING_VERIFICATION:
                            continue
                        violations.append(
                            RuleViolation(i, self.name, col_name, f"'{value}' is not an integer", record.get("id"))
                        )
        return violations


class DataFreshnessRule(ValidationRule):
    """Fails a record if `date_field` is older than `max_age_days` relative to `as_of`
    (defaults to today)."""

    name = "data_freshness"

    def __init__(self, max_age_days: int, date_field: str = "collection_date", as_of: Optional[date] = None):
        self.max_age_days = max_age_days
        self.date_field = date_field
        self.as_of = as_of

    def check(self, records: list[dict[str, Any]], context: dict[str, Any]) -> list[RuleViolation]:
        as_of = self.as_of or context.get("as_of_date") or datetime.utcnow().date()
        violations = []
        for i, record in enumerate(records):
            raw = record.get(self.date_field)
            if not raw:
                violations.append(
                    RuleViolation(i, self.name, self.date_field, "date field is missing", record.get("id"))
                )
                continue
            try:
                record_date = raw if isinstance(raw, date) else date.fromisoformat(str(raw))
            except ValueError:
                violations.append(
                    RuleViolation(i, self.name, self.date_field, f"'{raw}' is not an ISO date", record.get("id"))
                )
                continue
            age = (as_of - record_date).days
            if age > self.max_age_days:
                violations.append(
                    RuleViolation(
                        i,
                        self.name,
                        self.date_field,
                        f"record is {age} days old, exceeding the {self.max_age_days}-day freshness limit",
                        record.get("id"),
                    )
                )
        return violations
