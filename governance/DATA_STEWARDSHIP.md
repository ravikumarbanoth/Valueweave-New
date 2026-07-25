# Data Stewardship — Lifecycle Model (Module 9)

## The seven states

```
DRAFT -> COLLECTED -> VALIDATED -> REVIEWED -> APPROVED -> PUBLISHED -> ARCHIVED
```

| State | Meaning | Entered by | Exit condition |
|---|---|---|---|
| `DRAFT` | Scoped, not yet collected | Package steward | Collection begins |
| `COLLECTED` | Data gathered with provenance | Collector | All provenance fields present |
| `VALIDATED` | Passes the owning package's checks | Automated validator | Zero violations |
| `REVIEWED` | A human has read it against sources | Package steward | Reviewer recorded |
| `APPROVED` | Cleared for release | Package steward | Sign-off recorded |
| `PUBLISHED` | In a released package and in the graph | Release process | — |
| `ARCHIVED` | Superseded; retained for audit | Steward | Never deleted |

## Where every entity actually is

**All 647 entities are `PUBLISHED`.**

That is accurate for the state machine as defined — they are in released packages and in
the graph — but it hides something the model should make visible: they reached
`PUBLISHED` **without passing through `REVIEWED` or `APPROVED`**, because no steward
exists to perform those transitions.

Every package row carries `verification_status = VST-NEEDS_REVIEW`. The lifecycle says
`PUBLISHED`; the verification status says nobody has checked it. Both are true, and the
tension between them is the honest description of the platform's current state.

## Transition rules

| From | To | Requires |
|---|---|---|
| `DRAFT` | `COLLECTED` | Provenance on every field |
| `COLLECTED` | `VALIDATED` | Package validator exits 0 |
| `VALIDATED` | `REVIEWED` | A named human reviewer |
| `REVIEWED` | `APPROVED` | Steward sign-off, `verification_status` -> `VST-VERIFIED` |
| `APPROVED` | `PUBLISHED` | Included in a released package version |
| `PUBLISHED` | `ARCHIVED` | Successor exists, or the entity is retired |
| any | `DRAFT` | Never — corrections create a new version |

Backward transitions are not permitted. A published entity found to be wrong is corrected
through a new package version, which preserves the audit trail.

## Enforcement

`lifecycle_state` is validated against the registered states by graph check **G8**.
The *transitions* are not enforced by any tool — there is no workflow engine, and with
zero stewards assigned there is nothing to enforce them against.

## What would make this real

1. **Assign a Package Steward per package.** Eight people, or one person eight times.
2. **Review the highest-leverage rows first** — the 40 MSME businesses, the 40 schemes,
   the 45 crops, the 45 skills. Roughly 170 rows carry most of the graph's connectivity.
3. **Record the reviewer** in each package's `verification_status` and move approved rows
   to `VST-VERIFIED`.
4. **Then** the lifecycle model describes reality rather than intent.
