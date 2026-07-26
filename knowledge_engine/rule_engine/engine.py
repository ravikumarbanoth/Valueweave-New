"""RuleQuery — a small, dependency-free structured query engine over lists of record dicts.

This is the engine that will power ValueWeave's user-facing filtering ("Investment < ₹5 lakh",
"District = Medak", "Skill Level = Beginner", "Suitable for Women") before any LLM-based query
understanding is added — see `docs/rule_engine_spec.md`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from knowledge_engine.rule_engine.operators import OPERATORS


class Condition(Protocol):
    def evaluate(self, record: dict[str, Any]) -> bool: ...


@dataclass
class FieldCondition:
    """A single `field <operator> value` check against one record."""

    field: str
    operator: str
    value: Any

    def __post_init__(self) -> None:
        if self.operator not in OPERATORS:
            raise ValueError(f"unknown operator '{self.operator}'; available: {sorted(OPERATORS)}")

    def evaluate(self, record: dict[str, Any]) -> bool:
        if self.field not in record:
            return False
        return OPERATORS[self.operator](record[self.field], self.value)


class RuleQuery:
    """A chainable, composable query: `RuleQuery().where("district", "==", "Medak").where(...)`.

    All conditions added via `.where()` on the same `RuleQuery` combine with this query's `combine`
    mode ("AND" by default, "OR" if constructed via `RuleQuery.any_of()`). Nest `RuleQuery` instances
    via `.where_group()` to mix AND/OR logic, e.g. "District = Medak AND (Skill Level = Beginner OR
    Skill Level = Intermediate)".
    """

    def __init__(self, combine: Literal["AND", "OR"] = "AND"):
        self.combine: Literal["AND", "OR"] = combine
        self.conditions: list[Condition] = []

    def where(self, field: str, operator: str, value: Any) -> "RuleQuery":
        self.conditions.append(FieldCondition(field, operator, value))
        return self

    def where_group(self, group: "RuleQuery") -> "RuleQuery":
        self.conditions.append(group)
        return self

    def evaluate(self, record: dict[str, Any]) -> bool:
        if not self.conditions:
            return True
        results = (c.evaluate(record) for c in self.conditions)
        return all(results) if self.combine == "AND" else any(results)

    def filter(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [r for r in records if self.evaluate(r)]

    def count(self, records: list[dict[str, Any]]) -> int:
        return sum(1 for r in records if self.evaluate(r))

    @classmethod
    def all_of(cls, *conditions: Condition) -> "RuleQuery":
        query = cls("AND")
        query.conditions = list(conditions)
        return query

    @classmethod
    def any_of(cls, *conditions: Condition) -> "RuleQuery":
        query = cls("OR")
        query.conditions = list(conditions)
        return query


# -- Convenience builders matching the brief's example queries verbatim -------------------------

def investment_below(amount: float, field: str = "minimum_investment") -> FieldCondition:
    """"Investment < ₹5 lakh" -> investment_below(500000)."""
    return FieldCondition(field, "<", amount)


def district_equals(district: str, field: str = "district") -> FieldCondition:
    """"District = Medak" -> district_equals("Medak")."""
    return FieldCondition(field, "==", district)


def skill_level_equals(level: str, field: str = "skill_level") -> FieldCondition:
    """"Skill Level = Beginner" -> skill_level_equals("Beginner")."""
    return FieldCondition(field, "==", level)


def suitable_for(audience: str, field: str = "ideal_target_audience") -> FieldCondition:
    """"Suitable for Women" / "Suitable for Students" / "Suitable for Rural Areas" ->
    suitable_for("Women"). Uses case-insensitive substring matching against a free-text audience
    field, matching how `ideal_target_audience`/`rural_urban_suitability` are actually populated in
    Package004's Business Opportunity schema (e.g. "Women entrepreneurs, rural youth")."""
    return FieldCondition(field, "icontains", audience)
