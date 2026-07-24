# Rule Engine Specification

Module 8, `rule_engine/`. A small, dependency-free structured query engine over lists of record
dicts — the engine that will power ValueWeave's user-facing filtering before any LLM-based query
understanding is added.

## 1. Operators

`rule_engine.operators.OPERATORS` maps operator strings to `(record_value, query_value) -> bool`
functions:

| Operator | Meaning | Numeric coercion? |
|---|---|---|
| `<`, `<=`, `>`, `>=` | Ordering comparison | Yes — strips `₹` and `,` before parsing as float |
| `==`, `!=` | Equality | Case-insensitive for string-vs-string comparisons |
| `in`, `not_in` | Membership in a query-supplied collection | No |
| `contains` | Case-sensitive substring | No |
| `icontains` | Case-insensitive substring | No |

Numeric fields read from a CSV are always strings (`"500000"`, not `500000`) — the ordering operators
handle this transparently by attempting `float()` coercion (after stripping common currency
formatting) before comparing. A field genuinely containing "5 lakh" as free text is **not** parsed as
500000 by this engine — normalizing unit words like "lakh"/"crore" into plain numbers is a Parser
Engine responsibility (upstream), not something the Rule Engine guesses at query time.

## 2. FieldCondition and RuleQuery

```python
FieldCondition(field="minimum_investment", operator="<", value=500000)
```

A single condition. `RuleQuery` composes conditions:

```python
query = RuleQuery.all_of(
    FieldCondition("minimum_investment", "<", 500000),
    FieldCondition("district", "==", "Medak"),
    FieldCondition("skill_level", "==", "Beginner"),
)
results = query.filter(opportunity_records)
```

`RuleQuery.all_of(...)` combines with AND; `RuleQuery.any_of(...)` combines with OR. Nest queries via
`.where_group()` to mix logic:

```python
# District = Medak AND (Skill Level = Beginner OR Skill Level = Intermediate)
skill_ok = RuleQuery.any_of(
    FieldCondition("skill_level", "==", "Beginner"),
    FieldCondition("skill_level", "==", "Intermediate"),
)
query = RuleQuery.all_of(FieldCondition("district", "==", "Medak")).where_group(skill_ok)
```

Both `FieldCondition` and `RuleQuery` implement `.evaluate(record) -> bool`, so a `RuleQuery` can
nest another `RuleQuery` as one of its conditions — the `Condition` protocol makes this duck-typed
composition work without a separate "group" class.

## 3. Convenience Builders Matching the Brief's Example Queries

The brief names these exact examples; each has a matching convenience function so the mapping from
"the user-facing query" to "the code" is direct:

| Brief example | Code |
|---|---|
| "Investment < ₹5 lakh" | `investment_below(500000)` |
| "District = Medak" | `district_equals("Medak")` |
| "Skill Level = Beginner" | `skill_level_equals("Beginner")` |
| "Suitable for Women" | `suitable_for("Women")` |
| "Suitable for Students" | `suitable_for("Students")` |
| "Suitable for Rural Areas" | `suitable_for("Rural")` |

```python
query = RuleQuery.all_of(
    investment_below(500000),
    district_equals("Medak"),
    suitable_for("Women"),
)
matches = query.filter(package004_business_opportunity_records)
```

`suitable_for()` defaults to matching against `ideal_target_audience` with case-insensitive substring
matching, because that's how Package004's Business Opportunity schema actually represents suitability
(free text like `"Women entrepreneurs, rural youth"`), not as a set of boolean flag columns. Pass a
different `field` argument for a dataset that does use a dedicated boolean/enum suitability column.

## 4. Performance Note

`RuleQuery.filter()` is a plain linear scan (`O(n)` per query) — appropriate for the record volumes
every ValueWeave package has shipped so far (tens to low hundreds of rows per dataset). Indexing
(e.g. building a `district -> record indices` lookup) is a `ROADMAP.md` Phase 4 concern once the Rule
Engine is wired to a live API endpoint serving a larger combined dataset.

## 5. What the Rule Engine Does NOT Do

- It does not parse natural-language queries ("what can I start in Medak for under 5 lakh") — that
  translation from natural language to `RuleQuery` calls is exactly the kind of thing an LLM layer
  could do *on top of* this engine later, but this module only executes already-structured queries.
- It does not call any AI model.
- It does not query a live database directly in this release — it operates on an in-memory
  `list[dict]` (e.g. the records loaded from a package's CSV). Wiring it to a live Knowledge Database
  query is `ROADMAP.md` Phase 1/4.
