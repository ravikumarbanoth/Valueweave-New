"""Comparison/membership operators used by `rule_engine.engine.RuleQuery`.

Every operator function has the signature `(record_value, query_value) -> bool` and tolerates
record values being strings (as they always are when read straight from a package CSV) by attempting
a numeric coercion for the ordering operators before falling back to string comparison.
"""

from __future__ import annotations

from typing import Any, Callable


def _to_number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    # Strip common currency/formatting characters so "₹5,00,000" and "5 lakh"-style pre-normalized
    # numeric strings compare correctly; callers are expected to normalize "5 lakh" -> 500000
    # upstream (e.g. in the Parser Engine) rather than this operator guessing at unit words.
    cleaned = text.replace("₹", "").replace(",", "").strip()
    return float(cleaned)


def _lt(record_value: Any, query_value: Any) -> bool:
    return _to_number(record_value) < _to_number(query_value)


def _lte(record_value: Any, query_value: Any) -> bool:
    return _to_number(record_value) <= _to_number(query_value)


def _gt(record_value: Any, query_value: Any) -> bool:
    return _to_number(record_value) > _to_number(query_value)


def _gte(record_value: Any, query_value: Any) -> bool:
    return _to_number(record_value) >= _to_number(query_value)


def _eq(record_value: Any, query_value: Any) -> bool:
    if isinstance(record_value, str) and isinstance(query_value, str):
        return record_value.strip().lower() == query_value.strip().lower()
    return record_value == query_value


def _neq(record_value: Any, query_value: Any) -> bool:
    return not _eq(record_value, query_value)


def _in(record_value: Any, query_value: Any) -> bool:
    return record_value in query_value


def _not_in(record_value: Any, query_value: Any) -> bool:
    return record_value not in query_value


def _contains(record_value: Any, query_value: Any) -> bool:
    return str(query_value) in str(record_value)


def _icontains(record_value: Any, query_value: Any) -> bool:
    return str(query_value).lower() in str(record_value).lower()


OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    "<": _lt,
    "<=": _lte,
    ">": _gt,
    ">=": _gte,
    "==": _eq,
    "!=": _neq,
    "in": _in,
    "not_in": _not_in,
    "contains": _contains,
    "icontains": _icontains,
}
