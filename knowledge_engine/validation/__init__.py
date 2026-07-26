"""Validation Engine — reusable data-quality rules and the engine that runs them."""

from knowledge_engine.validation.base import RuleViolation, ValidationReport, ValidationRule
from knowledge_engine.validation.engine import ValidationEngine
from knowledge_engine.validation.rules import (
    ConfidenceScoringRule,
    DataFreshnessRule,
    DuplicateDetectionRule,
    ForeignKeyRule,
    RequiredFieldsRule,
    SchemaValidationRule,
    SourceValidationRule,
)

__all__ = [
    "ValidationRule",
    "ValidationReport",
    "RuleViolation",
    "ValidationEngine",
    "RequiredFieldsRule",
    "ForeignKeyRule",
    "DuplicateDetectionRule",
    "SourceValidationRule",
    "ConfidenceScoringRule",
    "SchemaValidationRule",
    "DataFreshnessRule",
]
