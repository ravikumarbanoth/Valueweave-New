# Validation Engine Specification

Module 3, `validation/`. Reusable, side-effect-free data-quality checks over a batch of flat record
dicts, matching the checks run by hand against every ValueWeave package's `validation_report.md`
since Package001_Geography.

## 1. Interface

```python
class ValidationRule(ABC):
    name: str

    @abstractmethod
    def check(self, records: list[dict], context: dict) -> list[RuleViolation]: ...
```

A rule **never mutates records**. A check that could plausibly "fix" a record (fill a missing field,
normalize a date format) belongs in the Parser Engine, upstream of validation — Validation exists to
report problems, not silently paper over them.

`context` carries cross-record information a rule may need without forcing every rule's constructor
to take every possible piece of context:

| Context key | Used by | Shape |
|---|---|---|
| `datasets` | `ForeignKeyRule` | `dict[str, list[dict]]` — other datasets in the same package |
| `existing_keys` | `DuplicateDetectionRule` | iterable of key tuples already committed elsewhere |
| `as_of_date` | `DataFreshnessRule` | `datetime.date`, defaults to today if omitted |

## 2. The 7 Built-In Rules

### RequiredFieldsRule(fields: list[str])
Fails a record if any named field is missing or blank. The literal `PENDING_VERIFICATION` sentinel
counts as *present* (it's a disclosed known-unknown, not missing data) — matching the convention used
throughout Package001-004.

### ForeignKeyRule(field, references_dataset, references_field="id")
Fails a record if `field`'s value isn't found among `context["datasets"][references_dataset]`'s
`references_field` values. A value of `""`, `None`, or `PENDING_VERIFICATION` is treated as "no FK
asserted" and skipped, not a violation — an unpopulated optional reference isn't a broken one.

### DuplicateDetectionRule(key_fields: list[str])
Fails every record sharing a `key_fields` tuple with another record — within the current batch, and
against `context["existing_keys"]` when supplied (for the cross-dataset ID-collision check every
package has run since Package001).

### SourceValidationRule(allow_local_paths=False)
Fails a record if `data_source` is blank, or if any `;`-separated entry in `source_url` isn't a
well-formed `http(s)://` URL (unless `allow_local_paths=True`, for fixtures/tests that cite local
files).

### ConfidenceScoringRule(max_score=100)
Fails a record if `confidence_score` isn't an integer, or falls outside `[0, max_score]`. Set
`max_score` to a package-specific ceiling (e.g. 85, matching Package004's discipline that no row
should score above 85 while WebFetch access remains blocked) to enforce that ceiling mechanically.

### SchemaValidationRule(schema: list[dict])
Fails a record whose fields don't match a `schemas/schema_catalog.json`-shaped column list: every
declared column must be present; `type: "enum"` values must be in the declared `values` list (unless
the value is `PENDING_VERIFICATION`); `type: "integer"` columns must parse as int (same exception).

### DataFreshnessRule(max_age_days, date_field="collection_date", as_of=None)
Fails a record whose `date_field` is older than `max_age_days` relative to `as_of` (or today).
Used by the Update Engine's re-verification cadence — a package can require, say, government-scheme
records be re-checked at least annually.

## 3. Running Rules: ValidationEngine

```python
engine = ValidationEngine([RequiredFieldsRule([...]), DuplicateDetectionRule([...]), ...])
report = engine.run(records, context={...})
passing_records, report = engine.valid_records(records, context={...})
```

`ValidationReport` aggregates every rule's violations and exposes `.passed`, `.pass_count`,
`.failed_record_indices`, `.violations_for_rule(name)`, and `.summary()` (a dict suitable for direct
inclusion in a metadata file or printed report).

## 4. Configuring Rules Per Dataset

Different datasets need different rules — `msme_entrepreneurship_support_schemes` has no foreign
keys, while a future `Package005` dataset referencing Package001_Geography's districts would add a
`ForeignKeyRule`. Configure a `ValidationEngine` per dataset (or per package, if every dataset shares
the same rule set) rather than building one universal rule list — `package_builder.PackageBuilder`
takes an `extra_rules: dict[dataset_name, list[ValidationRule]]` parameter for exactly this reason.

## 5. What Validation Does NOT Do

- It does not decide what happens to failing records (drop them, flag them, block the whole batch) —
  that's the caller's decision. `ValidationEngine.valid_records()` is a convenience that drops failing
  records from its first return value, but the full report (including which records failed and why)
  is always available for a caller that wants a different policy (e.g. "block the whole batch if
  more than 10% of records fail").
- It does not promote `verification_status` — that's an explicit governance action outside this
  engine's scope, matching every package's `codex_handoff.md` guidance.
- It does not call any AI model. A future "does this claim look fabricated" AI-assisted check would
  be a new rule implementing `ValidationRule`, following the same interface as every rule here — see
  `ai_integration_plan.md`.
