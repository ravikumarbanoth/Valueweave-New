# Update Engine Workflow Specification

Module 7, `update_engine/`. Implements the workflow named directly in the Phase-2 brief as an
explicit, testable state machine: `CHECK_SOURCE → DETECT_CHANGES → VALIDATE → UPDATE_DATABASE →
GENERATE_DRAFT → HUMAN_APPROVAL → STABLE_RELEASE`.

## 1. States

```
NOT_STARTED
  → CHECKING_SOURCE
    → [FAILED, if the collector's fetch fails]
    → DETECTING_CHANGES
      → [FAILED, if parsing fails]
      → NO_CHANGES_DETECTED   (terminal — nothing to do this cycle)
      → VALIDATING
        → UPDATING_DATABASE
          → GENERATING_DRAFT
            → PENDING_HUMAN_APPROVAL
              → STABLE_RELEASE   (via approve())
              → REJECTED         (via reject())
```

`WorkflowState.is_terminal` is `True` for `NO_CHANGES_DETECTED`, `STABLE_RELEASE`, `REJECTED`, and
`FAILED` — a workflow instance's job is done once it reaches one of these.

## 2. Stage-by-Stage Contract

### `check_source()`
Calls the configured `BaseCollector.fetch(source)`. If `FetchResult.ok` is `False`, transitions
straight to `FAILED` with the collector's error message. Never raises for an expected fetch failure —
consistent with `BaseCollector.fetch()`'s own contract (see `collector_plugin_spec.md`).

### `detect_changes(previous_records=None)`
Parses the fetched payload via the configured `BaseParser.parse()`. If parsing raises `ParseError`,
transitions to `FAILED`. Otherwise runs `change_detector(previous_records, current_records)` (default:
plain inequality) — if no change is detected, transitions to the terminal `NO_CHANGES_DETECTED` state
rather than continuing to validate/update a batch that's identical to what's already on record.

### `validate(context=None)`
Runs the configured `ValidationEngine` over the parsed records. **Does not itself fail the workflow**
on validation violations — a report with violations still proceeds to `UPDATE_DATABASE`, where only
the passing records are actually persisted (`ValidationReport.failed_record_indices` are excluded).
This mirrors how Package001-004 have always handled row-level validation problems: some rows pass,
some don't, and the failing ones are documented rather than blocking the entire batch. A caller
wanting stricter "abort on any violation" behavior should check `workflow.validation_report.passed`
between `validate()` and `update_database()` and call `reject()`-equivalent logic itself.

### `update_database(database, key_field="id")`
Writes every record that passed validation into `database` (any `MutableMapping`, e.g. a plain
`dict` today or a real Knowledge Database adapter once Phase 1 lands — see `ROADMAP.md`), keyed by
`key_field`. Populates `self.accepted_records`.

### `generate_draft()`
Calls the configured `on_generate_draft(accepted_records)` hook (e.g. wiring it to
`PackageBuilder.build()` to produce a real package draft folder), or defaults to just holding the
accepted records list if no hook is given. Always transitions onward to `PENDING_HUMAN_APPROVAL` —
this is the one state transition that happens unconditionally, because the whole point of this stage
existing is to produce something for a human to review next.

### `approve(approver, note="")` / `reject(approver, reason)`
The human gate. Both raise `WorkflowStateError` if called from any state other than
`PENDING_HUMAN_APPROVAL` — there is no way to reach `STABLE_RELEASE` without this method being called
explicitly, by design, per the brief's instruction that a human approval step is required.

## 3. Running the Automatable Prefix

```python
workflow = UpdateWorkflow(
    name="msme_schemes_update",
    collector=CSVCollector(),
    source="https://example.gov.in/msme_schemes.csv",
    parser=CSVParser(),
    validation_engine=ValidationEngine([...]),
    on_generate_draft=lambda records: package_builder.build(spec_from(records)),
)

state = workflow.run_to_approval(database=knowledge_db, previous_records=last_known_records)
# state is one of: FAILED, NO_CHANGES_DETECTED, or PENDING_HUMAN_APPROVAL

if state == WorkflowState.PENDING_HUMAN_APPROVAL:
    ...  # a human reviews workflow.draft, then:
    workflow.approve("data-steward@valueweave.in", "Reviewed against source, looks correct")
```

`run_to_approval()` never reaches `STABLE_RELEASE` on its own — that always requires a separate,
explicit `approve()` call, even when invoked from an automated scheduler (see `ROADMAP.md` Phase 6).

## 4. Auditability

Every transition is appended to `workflow.history` (`TransitionRecord(state, timestamp, note)`).
`workflow.history_summary()` returns this as plain dicts, ready to serialize into a package's
`reports/` folder or a database audit log — every update cycle leaves a complete record of what
happened and when, including who approved or rejected it and why.

## 5. What the Update Engine Does NOT Do

- It does not call any AI model at any stage in this release.
- It does not schedule itself — nothing currently calls `check_source()` on a timer. Wiring a
  scheduler is `ROADMAP.md` Phase 6, and even then the human-approval gate remains mandatory.
- It does not decide *how* to detect changes beyond the pluggable `change_detector` callable — a
  real deployment will likely want a smarter detector that ignores volatile fields like
  `collection_date`/`last_verified` when comparing "did the substantive data change."
