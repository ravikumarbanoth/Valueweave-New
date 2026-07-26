# Provenance Engine Specification

Module 4. `core/provenance.py` (the model) + `provenance/` (schema + operational helpers).

## 1. The 8 Fields

Every ValueWeave package since Package001_Geography has carried the same evidence trail per record.
`ProvenanceRecord` is that trail as a typed, validated Python object:

| Field | Type | Matches CSV column | Notes |
|---|---|---|---|
| `source` | `str` | `data_source` | Human-readable description, e.g. "data.gov.in Open Government Data Platform" |
| `source_url` | `list[str]` | `source_url` (`; `-joined) | One or more URLs; must be non-empty |
| `collection_date` | `date` | `collection_date` | ISO 8601 |
| `last_verified` | `Optional[date]` | *(not a separate CSV column in Package001-004; tracked internally)* | Defaults to `collection_date` |
| `collector` | `str` | *(folded into `data_source`/`notes` by convention in hand-built packages; a first-class field here)* | e.g. `"csv_collector/0.1.0"` — see `FetchResult.collector_label` |
| `confidence` | `int` (0-100) | `confidence_score` | Calibrated per `core.types.ConfidenceTier` |
| `verification_status` | `VerificationStatus` | `verification_status` | Defaults to `VST-NEEDS_REVIEW` |
| `package_version` | `Optional[str]` | *(not a CSV column; tracked in the manifest instead)* | Which package version this record was collected for |

`notes` is a 9th, free-text field carried alongside these 8 — required whenever any field on the
parent record holds the `PENDING_VERIFICATION` sentinel, per the `[field_name]: explanation`
convention.

## 2. Confidence Calibration

`core.types.ConfidenceTier` encodes the exact bands used by hand across Package001-004:

| Tier | Range | Meaning |
|---|---|---|
| `GOVERNMENT_GRADE` | 70-100 | Traced to a specific government/authoritative document |
| `PORTAL_OR_NEWS` | 55-69 | A named organization/news source without primary-document backing |
| `COMMUNITY_QUALITATIVE` | 0-54 | Tier-5 qualitative color only (forums, YouTube creators, etc.) — must be flagged in `notes`, never the sole basis for a numeric claim |

`ConfidenceTier.for_score(score)` returns which band a score falls in, for reporting/auditing.

`core.types.SourceTier` encodes the 5-tier source-priority order (Government → Official Organization →
Verified Social Media → Trusted News → Community/Qualitative) used to sanity-check that a record's
confidence is consistent with its source's tier.

## 3. Re-Verification Discipline

`ProvenanceRecord.re_verify(as_of, new_confidence)`:

- Raises if `new_confidence` is lower than the current value — a fact found to be *less* reliable than
  previously recorded should become a new record (with a note explaining why), not a silent downgrade
  of the same one.
- Raises if `new_confidence - confidence > 8` — the exact "+8 per re-verification pass" discipline
  applied by hand during Package004's enrichment pass, enforced mechanically here rather than relying
  on a reviewer remembering the rule.

## 4. Serialization

- `to_csv_fields()` → the 6 flat columns (`data_source`, `source_url`, `collection_date`,
  `confidence_score`, `verification_status`, `notes`) every package's dataset CSVs carry, ready to
  merge into a record dict before writing.
- `to_dict()` / `from_dict()` → full-fidelity round-trip (including `last_verified` and
  `package_version`, which the CSV form omits) for the future Knowledge Database (see `ROADMAP.md`
  Phase 1).

## 5. ProvenanceTracker — Attaching Provenance to Parsed Records

```python
ProvenanceTracker.attach_uniform(records, provenance)         # one ProvenanceRecord for the whole batch
ProvenanceTracker.attach_per_record(records, derive_fn)        # a distinct one per record
ProvenanceTracker.default_provenance(source=..., source_url=..., confidence=..., collector=...)
```

`attach_uniform` is the common case: a single CSV/API fetch produces one shared source/URL/date for
every row it contributed. `attach_per_record` handles the case where different rows within one parsed
batch cite different sources (e.g. an aggregated feed where each item has its own link).

### Sentinel Discipline, Enforced Mechanically

```python
ProvenanceTracker.mark_pending_verification(record, field, explanation)
ProvenanceTracker.find_sentinel_violations(records)
```

`mark_pending_verification` sets a field to the bare `PENDING_VERIFICATION` string and appends the
explanation to `notes` correctly formatted, so a caller never has to remember the exact convention.

`find_sentinel_violations` scans a batch for the exact bug found and fixed **by hand three times**
across Package002, Package003, and Package004 (a cell containing `"PENDING_VERIFICATION - some
explanation"` instead of the bare sentinel). Running this before every commit — as the Package Builder
does automatically during its final validation pass — turns a recurring manual-review catch into a
mechanical one.

## 6. What Provenance Does NOT Do

- It does not decide *whether* a record should carry `PENDING_VERIFICATION` for a given field — that
  judgment (is this source strong enough to state as fact?) is made upstream, by whoever configures a
  Collector/Parser pipeline or reviews a draft. The Provenance Engine just makes recording that
  judgment mechanically consistent.
- It never sets `verification_status` to `VST-VERIFIED`. Every record constructed by
  `ProvenanceTracker.default_provenance()` starts at `VST-NEEDS_REVIEW`; promoting a record is a
  separate, explicit action outside this module.
