"""Rule Engine — structured, non-AI querying over record lists."""

from knowledge_engine.rule_engine.engine import (
    Condition,
    FieldCondition,
    RuleQuery,
    district_equals,
    investment_below,
    skill_level_equals,
    suitable_for,
)
from knowledge_engine.rule_engine.operators import OPERATORS

__all__ = [
    "Condition",
    "FieldCondition",
    "RuleQuery",
    "OPERATORS",
    "investment_below",
    "district_equals",
    "skill_level_equals",
    "suitable_for",
]
