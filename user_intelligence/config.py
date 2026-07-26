#!/usr/bin/env python3
"""
Configuration — what is scored, what is recommended, and what is missing.

INPUT AVAILABILITY IS PART OF THE CONFIGURATION
-----------------------------------------------
The brief names six inputs. Three of them do not exist in this repository:

    profiles            EXISTS
    connections         EXISTS
    knowledge schema    EXISTS (migration written, not yet applied)
    assessment_results  DOES NOT EXIST — no table in any migration
    teams               DOES NOT EXIST — no table, no route
    idea_library        NOT A TABLE — static JSON at frontend/lib/idea-library/

Rather than fail, or silently pretend, `INPUTS` declares each one's status and
every rule declares which inputs it needs. A rule whose inputs are unavailable
returns `UNAVAILABLE` with the reason — not a zero, and not a guess. A score of 0
would be a claim about the user; UNAVAILABLE is a claim about our data, which is
the true one.

The same applies downstream: two of the ten recommendation categories the brief
lists have no backing data at all, and say so.
"""

from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AVAILABLE, MISSING, STATIC, PENDING = "AVAILABLE", "MISSING", "STATIC_FILE", "PENDING_MIGRATION"


@dataclass(frozen=True)
class InputSpec:
    name: str
    status: str
    detail: str


#: Every input the engine may read, and whether it is actually there.
INPUTS = {
    "profiles": InputSpec(
        "profiles", AVAILABLE,
        "Supabase. id, name, city, bio, skills[], interests[], looking_for."),
    "connections": InputSpec(
        "connections", AVAILABLE,
        "Supabase. Opportunity-scoped, 1:1, pending/accepted/rejected."),
    "collaborator_profiles": InputSpec(
        "collaborator_profiles", AVAILABLE,
        "Supabase. archetype, district, top_sectors[], budget, ep_score."),
    "opportunities": InputSpec(
        "opportunities", AVAILABLE,
        "Supabase. category, skills_needed[], location, collaboration_type."),
    "research_articles": InputSpec(
        "research_articles", AVAILABLE, "Supabase. Powers the Research category."),
    "knowledge_graph": InputSpec(
        "knowledge_graph", AVAILABLE,
        "Git artifacts: 647 entities, 865 edges. Read directly, so the engine "
        "runs offline and Git stays the source of truth."),
    "vocabulary_crosswalk": InputSpec(
        "vocabulary_crosswalk", AVAILABLE,
        "governance/vocabulary/*.csv from Step 0. The only bridge from free-text "
        "profile skills to graph entities."),
    "idea_library": InputSpec(
        "idea_library", STATIC,
        "NOT a Supabase table. 122 ideas in frontend/lib/idea-library/ideas.json. "
        "Read from disk; a future migration would not change any rule."),
    "knowledge_projection": InputSpec(
        "knowledge_projection", PENDING,
        "Supabase `knowledge` schema. Migration written in Step 1, not yet "
        "applied. The engine reads Git instead, which is equivalent by design."),
    "assessment_results": InputSpec(
        "assessment_results", MISSING,
        "No such table in any migration. No assessment feature exists. Rules "
        "that would use it return UNAVAILABLE."),
    "teams": InputSpec(
        "teams", MISSING,
        "No such table and no /teams route. `connections` with status=accepted is "
        "the closest real working group, and is what the collaboration rules use."),
}


@dataclass(frozen=True)
class ScoreSpec:
    key: str
    label: str
    description: str
    #: Input names this score needs. Any MISSING input makes it UNAVAILABLE.
    requires: tuple
    #: Contributing rule ids, in the order they are applied.
    rules: tuple
    #: What a low score means, so a UI can say something useful about it.
    low_means: str = ""


#: The eight profiles the brief asks for.
SCORES = (
    ScoreSpec("skill_profile", "User Skill Profile",
              "Which claimed skills resolve to the knowledge graph, at what NSQF "
              "level, and which have no researched counterpart.",
              ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
              ("SK1-RESOLVED", "SK2-DEPTH", "SK3-BREADTH", "SK4-DEMAND")),
    ScoreSpec("business_readiness", "Business Readiness",
              "Whether the user's resolved skills and district cover what a "
              "researched business actually requires.",
              ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
              ("BR1-SKILL_COVERAGE", "BR2-DISTRICT", "BR3-CATEGORY_FIT"),
              low_means="Skills do not yet cover any researched business's requirements."),
    ScoreSpec("learning_roadmap", "Learning Roadmap",
              "Ordered skill gaps between what the user has and what their best "
              "matched businesses need.",
              ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
              ("LR1-GAP", "LR2-SEQUENCE", "LR3-PROVIDER")),
    ScoreSpec("district_opportunity", "District Opportunity Score",
              "How much researched opportunity exists in the user's district.",
              ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
              ("DO1-RESOLVE", "DO2-DENSITY", "DO3-DIVERSITY"),
              low_means="Little researched data for this district yet — a coverage "
                        "gap, not an absence of opportunity."),
    ScoreSpec("collaboration_score", "Collaboration Score",
              "Readiness and demonstrated activity as a collaborator.",
              ("profiles", "connections"),
              ("CO1-PROFILE", "CO2-ACCEPTED", "CO3-COMPLEMENTARITY")),
    ScoreSpec("ai_readiness", "AI Readiness",
              "Exposure to AI-augmentable skills and AI-ready businesses.",
              ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
              ("AI1-SKILL_AUGMENTATION", "AI2-BUSINESS_READINESS", "AI3-TOOLING")),
    ScoreSpec("funding_readiness", "Funding Readiness",
              "Reachable schemes and financial institutions given the user's "
              "matched businesses and district.",
              ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
              ("FR1-SCHEME_REACH", "FR2-BANK_REACH", "FR3-PROFILE_COMPLETENESS")),
    ScoreSpec("startup_readiness", "Startup Readiness",
              "Composite of the seven above, weighted.",
              ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
              ("ST1-COMPOSITE",)),
)

SCORES_BY_KEY = {s.key: s for s in SCORES}

#: Weights for the composite. They sum to 1.0, asserted by a test — a composite
#: whose weights drift produces a number nobody can reproduce.
STARTUP_WEIGHTS = {
    "skill_profile": 0.25,
    "business_readiness": 0.25,
    "funding_readiness": 0.15,
    "district_opportunity": 0.15,
    "collaboration_score": 0.10,
    "learning_roadmap": 0.05,
    "ai_readiness": 0.05,
}


@dataclass(frozen=True)
class CategorySpec:
    key: str
    label: str
    #: Graph entity types, or a named non-graph source.
    sources: tuple
    requires: tuple
    rules: tuple
    #: Set when the category has no backing data. The recommender then returns
    #: NO_DATA_SOURCE with this explanation instead of an empty list.
    no_data_reason: str = ""
    #: Recorded where data exists but is too sparse to rank well.
    sparse_note: str = ""


#: The ten categories the brief asks for. Two have no data; both say so.
RECOMMENDATION_CATEGORIES = (
    CategorySpec("business_ideas", "Business Ideas",
                 ("idea_library", "BusinessOpportunity", "MSME"),
                 ("profiles", "vocabulary_crosswalk", "knowledge_graph", "idea_library"),
                 ("RB1-SKILL_MATCH", "RB2-DISTRICT_FIT", "RB3-SECTOR_INTEREST")),
    CategorySpec("government_schemes", "Government Schemes",
                 ("GovernmentScheme",),
                 ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
                 ("RS1-VIA_BUSINESS", "RS2-VIA_DISTRICT", "RS3-VIA_SKILL")),
    CategorySpec("courses", "Courses",
                 ("Certification", "TrainingProvider"),
                 ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
                 ("RC1-FOR_GAP_SKILL", "RC2-PROVIDER_IN_DISTRICT"),
                 sparse_note="TRAINED_BY has 3 edges in the whole graph, so most "
                             "gap skills resolve to no provider. Certifications are "
                             "matched by category instead, which is weaker."),
    CategorySpec("research", "Research",
                 ("research_articles",),
                 ("profiles", "research_articles"),
                 ("RR1-DISTRICT_TAG", "RR2-SECTOR_TAG")),
    CategorySpec("mentors", "Mentors",
                 (),
                 ("profiles",),
                 (),
                 no_data_reason=(
                     "No mentor data exists anywhere in the platform: no Mentor "
                     "entity type, no mentors table, no mentor flag on profiles. "
                     "`collaborator_profiles.archetype` records self-declared "
                     "archetypes, none of which means 'mentor'. Recommending "
                     "mentors would require inventing them.")),
    CategorySpec("collaborators", "Collaborators",
                 ("profiles", "collaborator_profiles"),
                 ("profiles", "connections", "collaborator_profiles"),
                 ("RL1-COMPLEMENTARY_SKILL", "RL2-SAME_DISTRICT",
                  "RL3-SHARED_SECTOR")),
    CategorySpec("events", "Events",
                 (),
                 ("profiles",),
                 (),
                 no_data_reason=(
                     "No event data exists: no Event entity type, no events table, "
                     "no calendar source. Nothing in the knowledge base or the "
                     "application records an event.")),
    CategorySpec("markets", "Markets",
                 ("Market",),
                 ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
                 ("RM1-VIA_BUSINESS", "RM2-BY_DIGITAL_INTENSITY"),
                 sparse_note="11 Market entities and 12 SELLS_TO edges. Ranking is "
                             "possible but shallow."),
    CategorySpec("msmes", "MSMEs",
                 ("MSME",),
                 ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
                 ("RN1-SKILL_MATCH", "RN2-DISTRICT", "RN3-RISK_FIT")),
    CategorySpec("industries", "Industries",
                 ("Industry",),
                 ("profiles", "vocabulary_crosswalk", "knowledge_graph"),
                 ("RI1-VIA_SKILL", "RI2-VIA_INTEREST", "RI3-VIA_DISTRICT")),
)

CATEGORIES_BY_KEY = {c.key: c for c in RECOMMENDATION_CATEGORIES}

# ---------------------------------------------------------------- thresholds
#: A recommendation below this match score is not emitted. Set from the data
#: rather than from taste: with 86 REQUIRES_SKILL edges and a 22.8% skill resolve
#: rate, a lower floor produces long lists of one-weak-signal matches.
MIN_MATCH_SCORE = 20

#: Per-category cap. Recommendations are ranked, so the tail is the weak part.
MAX_PER_CATEGORY = 20

#: Confidence bands, matching the Knowledge Engine's ConfidenceTier so a user
#: sees the same vocabulary the packages use.
CONFIDENCE_BANDS = ((70, 100, "GOVERNMENT_GRADE"), (55, 69, "PORTAL_OR_NEWS"),
                    (0, 54, "COMMUNITY_QUALITATIVE"))

#: Every row the engine writes carries this. All 2,299 knowledge rows are
#: VST-NEEDS_REVIEW, so every recommendation rests on unreviewed data and must
#: say so. Computed, not hard-coded — see engine.py.
UNVERIFIED_NOTICE = (
    "Based on knowledge-base rows that no human has reviewed "
    "(verification_status = VST-NEEDS_REVIEW). Confidence reflects source "
    "strength, not correctness.")

OUTPUT_TABLES = ("user_skill_profile", "user_business_profile",
                 "user_learning_profile", "user_recommendations",
                 "user_activity_summary")
