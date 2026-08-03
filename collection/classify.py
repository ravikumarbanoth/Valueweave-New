#!/usr/bin/env python3
"""
What kind of thing did we just collect?

WHY RULES AND NOT A MODEL
-------------------------
Two reasons, and the second is the one that matters.

A classifier that is wrong 10% of the time is fine when a human reviews
everything, which is the workflow here — so accuracy is not the constraint.
What IS the constraint is that a reviewer must be able to see WHY something was
put in front of them, and disagree with the reason. "Classified as Scheme
because the title contains 'yojana' and 'subsidy'" is arguable. "Classified as
Scheme, confidence 0.87" is not; it can only be accepted or ignored, and
reviewers who cannot argue with a system stop reading it.

The second reason: this repository's rule is no fabricated data. A model that
assigns a category has invented a fact about a record. A rule that fires on a
word the record actually contains has quoted one.

  Every classification carries the terms that produced it. Nothing is
  classified silently, and UNCLASSIFIED is a legitimate, common outcome.

ADDING A CATEGORY
-----------------
One entry in `RULES` below. No code changes, no retraining, no migration —
Phase 9's plug-and-play requirement, applied to the taxonomy. A test asserts
every target names a real knowledge-graph entity type or an explicit
non-entity kind, so a category cannot be added that nothing downstream can use.
"""

import re
from dataclasses import dataclass, field

#: Targets that ARE knowledge-graph entity types. A candidate classified as one
#: of these can become a package row after review.
ENTITY_TARGETS = {
    "GovernmentScheme", "Skill", "TrainingProvider", "Certification",
    "BusinessOpportunity", "MSME", "Industry", "District", "Crop",
    "Institution", "Machinery", "FinancialInstitution", "Market",
}

#: Targets that are NOT entity types. They are real kinds of incoming material
#: that the graph has no row for — an event, a job posting, a news item — and
#: naming them is better than forcing them into an entity type that will read
#: as a fabricated fact once published.
NON_ENTITY_TARGETS = {"Research", "Event", "Job", "News", "Technology"}

TARGETS = ENTITY_TARGETS | NON_ENTITY_TARGETS

UNCLASSIFIED = "UNCLASSIFIED"


@dataclass
class Rule:
    """One category, and the words that mean it.

    `any_of` fires the rule. `all_of` is an additional requirement — used where
    a single word is too broad ("training" alone is everywhere; "training" plus
    "provider" or "centre" is a TrainingProvider).

    `weight` breaks ties between rules that both fire, and is deliberately a
    small integer rather than a probability: it is a curator's ordering, not a
    measurement, and dressing it as one would be the same dishonesty as a
    confidence score.
    """

    target: str
    any_of: tuple = ()
    all_of: tuple = ()
    none_of: tuple = ()
    weight: int = 10


#: The taxonomy. Ordered by how specific each rule is, not alphabetically —
#: reading top to bottom should read like a person narrowing down.
RULES = [
    Rule("GovernmentScheme", weight=30,
         any_of=("yojana", "scheme", "subsidy", "margin money", "grant",
                 "sarkari", "pradhan mantri", "mission", "abhiyan",
                 "financial assistance", "beneficiary")),
    # "empanelment", "licence" and "license" were in this rule and were wrong
    # in both directions on the first run against the fixtures: "empanelment of
    # training providers" classified as Certification instead of
    # TrainingProvider, and "work available for licensed electrical
    # contractors" classified as Certification instead of a business
    # opportunity. A word that appears NEAR a certification is not a word that
    # means one.
    # "nsqf" is not here either, for the same reason: it is a LEVEL, and it
    # appears in every skill, training and provider document in the sector. A
    # term that appears in all three categories cannot choose between them.
    Rule("Certification", weight=28,
         any_of=("qualification pack", "certification", "certificate course",
                 "trade certificate", "accreditation body", "accredited course")),
    Rule("TrainingProvider", weight=26, all_of=("train",),
         any_of=("provider", "centre", "center", "institute", "iti", "academy",
                 "polytechnic", "empanel", "accreditation")),
    Rule("Skill", weight=24,
         any_of=("skill", "apprentice", "technician", "operator", "artisan",
                 "trade test", "vocational", "upskilling", "reskilling")),
    Rule("BusinessOpportunity", weight=22,
         any_of=("opportunity", "tender", "licences invited", "licenses invited",
                 "applications invited", "registration window", "expression of interest",
                 "franchise", "dealership", "start a", "setting up")),
    Rule("MSME", weight=20,
         any_of=("msme", "micro enterprise", "small enterprise", "udyam",
                 "cottage industry", "self employment")),
    Rule("Industry", weight=18,
         any_of=("industrial estate", "industrial park", "cluster", "manufacturing zone",
                 "industry", "sector policy")),
    # Distinct weights all the way down. Two rules on the same weight resolve
    # alphabetically, which is arbitrary dressed as a decision — "Common
    # facility centre for millet processing" came out as Crop over Machinery
    # because C sorts before M.
    Rule("Machinery", weight=17,
         any_of=("machinery", "equipment", "plant and machinery", "common facility centre",
                 "cnc", "lathe")),
    Rule("Crop", weight=16,
         any_of=("crop", "millet", "paddy", "horticulture", "kharif", "rabi",
                 "farmer producer", "fpo", "agriculture produce")),
    Rule("Institution", weight=15,
         any_of=("university", "college", "school", "campus", "admission")),
    Rule("FinancialInstitution", weight=14,
         any_of=("bank", "credit society", "nbfc", "cooperative bank", "lending")),
    Rule("Market", weight=13,
         any_of=("mandi", "market yard", "e-nam", "enam", "procurement", "export promotion")),
    Rule("District", weight=12,
         any_of=("district industries centre", "district collector", "mandal", "revenue division")),

    # Not entity types. Named rather than forced.
    Rule("Research", weight=10,
         any_of=("study", "report", "white paper", "survey findings", "research")),
    Rule("Event", weight=9,
         any_of=("workshop", "seminar", "conclave", "expo", "job mela", "webinar",
                 "conference", "summit")),
    Rule("Job", weight=7,
         any_of=("vacancy", "recruitment", "hiring", "walk-in", "job posting",
                 "notification for the post")),
    Rule("Technology", weight=6,
         any_of=("robotics", "semiconductor", "drone", "artificial intelligence",
                 "automation", "electronics", "battery", "solar", "electric vehicle")),
    Rule("News", weight=4,
         any_of=("press release", "inaugurated", "launched", "announced", "statement")),
]

#: Fields worth reading. A feed item's title and description carry the meaning;
#: its <guid> and <pubDate> carry none, and matching on them would classify by
#: accident of formatting.
TEXT_FIELDS = ("title", "summary", "description", "content_text", "content",
               "name", "subject", "category", "courses_offered")


@dataclass
class Classification:
    target: str = UNCLASSIFIED
    weight: int = 0
    matched: list = field(default_factory=list)
    alternatives: list = field(default_factory=list)
    is_entity: bool = False
    reason: str = ""


def _text(record):
    parts = []
    for field_name in TEXT_FIELDS:
        value = (record or {}).get(field_name)
        if value:
            parts.append(str(value))
    return " ".join(parts).lower()


def _fires(rule, text):
    matched = [term for term in rule.any_of if term in text]
    if rule.any_of and not matched:
        return None
    required = [term for term in rule.all_of if term in text]
    if len(required) != len(rule.all_of):
        return None
    if any(term in text for term in rule.none_of):
        return None
    return matched + required


def classify(record, forced=""):
    """Classify one record. `forced` is the registry's `classify_as` column.

    A register of training providers is a list of training providers; making
    the classifier re-derive that from prose it does not contain would be
    guessing where the source already told us. Forcing is recorded in `reason`
    so a reviewer can see that no rule ran.
    """
    if forced:
        return Classification(target=forced, weight=100, matched=[],
                              is_entity=forced in ENTITY_TARGETS,
                              reason=f"declared in the registry as {forced}")

    text = _text(record)
    if not text.strip():
        return Classification(reason="no text fields to read")

    hits = []
    for rule in RULES:
        matched = _fires(rule, text)
        if matched:
            hits.append((rule, matched))

    if not hits:
        return Classification(reason="no rule matched")

    hits.sort(key=lambda pair: (-pair[0].weight, pair[0].target))
    best, matched = hits[0]
    return Classification(
        target=best.target,
        weight=best.weight,
        matched=matched,
        alternatives=[r.target for r, _ in hits[1:4]],
        is_entity=best.target in ENTITY_TARGETS,
        reason="matched " + ", ".join(f"“{m}”" for m in matched[:4]),
    )


def classify_all(records, forced=""):
    return [classify(record, forced=forced) for record in records or []]


def distribution(classifications):
    """Counts per target, for the monitoring output."""
    counts = {}
    for c in classifications or []:
        counts[c.target] = counts.get(c.target, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
