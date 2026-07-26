# Rule Engine — User Intelligence

How a rule works, how outcomes combine into a score, and why the three statuses are
the most important design decision in the module.

`user_intelligence/rules.py`

---

## 1. A rule returns three things

```python
Outcome(
    rule="SK1-RESOLVED",
    status=APPLIED,           # APPLIED | NO_SIGNAL | UNAVAILABLE
    value=100.0,              # 0–100, or None
    weight=2.0,
    reason="5 of 5 skills resolve to the knowledge graph",
    evidence=[Evidence(...), ...],
)
```

**A number with no evidence is not a result.** Every `APPLIED` outcome carries the
entities and edges that produced it, and a test asserts that any applied score has
non-empty evidence. That is what makes `explain()` possible, and an explanation you
cannot produce is a score nobody should act on.

---

## 2. The three statuses

| Status | Means | `value` |
|---|---|---|
| `APPLIED` | Computed, with signal found | 0–100 |
| `NO_SIGNAL` | Computed. The answer is *nothing*. | `0.0` |
| `UNAVAILABLE` | Could not compute — an input is missing | `None` |

### Why `NO_SIGNAL` and `UNAVAILABLE` are not the same thing

They look identical in a naive UI — both produce an empty panel — and they mean
opposite things.

- **`NO_SIGNAL`** is a fact about the world as the knowledge base sees it: *no
  researched business requires your skills*. That is a real, reportable zero.
- **`UNAVAILABLE`** is a fact about **us**: *there is no `assessment_results` table,
  so we cannot assess this*. Any number here would be fiction.

Collapsing them into `score = 0` would tell a user their district has no
opportunity when the truth is that we have not collected it yet. That single
conflation is the most likely way a knowledge platform disappoints the person using
it, and it is why the distinction is in the type system rather than in a comment.

---

## 3. Combining outcomes

`combine()` folds a list of outcomes into one `ScoreResult`:

```python
computable   = [o for o in outcomes if o.status in (APPLIED, NO_SIGNAL)]
score        = Σ(value × weight) / Σ(weight)      # over computable only
```

### Unavailable outcomes leave the denominator

Two rules, one applied at 100 and one unavailable:

| Treatment | Score | Says |
|---|---:|---|
| Count UNAVAILABLE as 0 | 50 | "the user is halfway there" — **false** |
| **Exclude it** | **100** | "on what we could measure, full marks" |

The second is the truth. The reason string then names what was skipped:

> `5 of 5 skills resolve to the knowledge graph (rules skipped for missing inputs: LR3-PROVIDER)`

If **every** outcome is unavailable, the score is `None` and the status is
`UNAVAILABLE`. A `None` score is honest; a `0` is not.

### Status of the combined result

| Condition | Status |
|---|---|
| At least one `APPLIED` outcome with a positive value | `APPLIED` |
| All computable outcomes at zero | `NO_SIGNAL`, with `low_means` as the reason |
| No computable outcomes at all | `UNAVAILABLE` |

---

## 4. Weights

Default 1.0. Raised to 2.0 on the rule that carries the most signal for its score —
`SK1-RESOLVED` for the skill profile, `BR1-SKILL_COVERAGE` for business readiness,
`FR1-SCHEME_REACH` for funding.

Weights are **reasoned, not calibrated.** Nothing in the platform records whether a
recommendation was useful, so there is no outcome data to fit them to. The v2.1
audit named that as the blocker for a real recommendation engine, and it remains
true. Presenting these as tuned would be the dishonest option; they are documented
defaults that a later calibration pass should replace.

---

## 5. Confidence is inherited, never invented

```python
@property
def confidence(self):
    scores = [e.confidence for e in self.evidence if e.confidence]
    return min(scores) if scores else 0
```

**The minimum, not the mean.** A conclusion is as trustworthy as its weakest
supporting row, and averaging lets one confidence-85 entity mask a confidence-50
one. A user acting on the result deserves the pessimistic number.

`confidence` is kept strictly apart from `score`:

| | Question it answers |
|---|---|
| `score` | How well does this fit *this user*? |
| `confidence` | How much can the underlying rows be *trusted*? |

Both are needed because a perfect match on weak data is a real situation, and one
number cannot describe it.

### Editorial content reports zero

An idea-library entry carries no confidence score in its source. Its evidence may
include a graph entity — a resolved district at confidence 73 — but that is
confidence in the district, not in the idea. `business_ideas` therefore sets
`confidence=0` explicitly for editorial items, with a `confidence_note` saying why,
and `test_editorial_sources_do_not_borrow_a_confidence_score` enforces it.

---

## 6. Evidence

```python
Evidence(kind="edge", ref="vwr:000156", label="REQUIRES_SKILL",
         detail="Millet Processing Unit -> Welding", confidence=77,
         source_package="Package008_MSME", source_dataset="skill_mapping.csv",
         source_row_id="kmap-016")
```

| `kind` | Refers to |
|---|---|
| `entity` | A graph node, by `global_entity_id` |
| `edge` | A graph edge, by `relationship_id`, carrying package/dataset/row |
| `crosswalk` | A Step 0 vocabulary decision, including `NO_COUNTERPART` |
| `profile_field` | A user's own field — `city`, `skills`, completeness |
| `supabase` | A live row the caller supplied — a connection, an article |

Graph evidence traces to a CSV row, so any score expands into
`Package008_MSME/skill_mapping.csv:kmap-016`. That is the same provenance chain the
API and the knowledge graph already carry, extended to per-user conclusions.

---

## 7. Reproducibility

`Outcome.fingerprint()` hashes the rule id, status, value to four decimal places,
and the sorted evidence references. `ScoreResult.fingerprint()` chains those.
`IntelligenceResult.result_hash()` covers everything **except `generated_at`**.

Enforced by construction and by test:

| Guarantee | How |
|---|---|
| No randomness | `test_no_randomness_anywhere` greps for `random`, `uuid4`, `shuffle` |
| No AI | `test_no_ai_or_model_dependency` greps for eight model libraries |
| No database access | `test_engine_never_queries_supabase` greps for clients |
| Ordered iteration | Every traversal sorts; `UserContext` normalises to sorted tuples |
| Stable across processes | `test_hash_is_stable_across_a_fresh_snapshot` |

The ordered-iteration point deserves emphasis: a rule that iterated a `set` would
be reproducible within one process and not across two — invisible until it matters,
which is the worst kind of non-determinism.

---

## 8. Adding a rule

1. Write a function returning `applied` / `no_signal` / `unavailable`
2. Append its id to the relevant `ScoreSpec.rules` in `config.py`
3. Bump `RULES_VERSION`
4. Add a test

Two conventions worth keeping:

**Prefer `NO_SIGNAL` with a specific reason over `APPLIED` with a low value.** The
reason is the product. `"no researched business requires these skills — 86
REQUIRES_SKILL edges exist in total, so this is often a coverage gap"` tells a user
something; `12.0` does not.

**Cite the graph's own numbers when explaining sparsity.** Several rules name the
edge count behind their limitation. It converts a vague apology into a checkable
claim, and it will read as obviously stale once the graph grows — which is the
point.

---

## 9. `RULES_VERSION`

`1.0.0`. Stored on every output row, part of every table's primary key.

A recommendation a user acted on must remain explainable after the rules change, so
rows are keyed `(user_id, rules_version)` rather than by user alone. Changing logic
therefore adds rows rather than overwriting the ones that explain past behaviour.

Bump it whenever a rule changes in a way that alters output. Not bumping it is the
one mistake that makes the whole audit trail worthless.
