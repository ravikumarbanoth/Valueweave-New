"""
ValueWeave User Intelligence Engine (Platform v3.0, Step 1.5).

Connects a user profile to the knowledge graph and produces reusable intelligence:
eight scored profiles and ten categories of recommendation, all rule-based, all
reproducible, all carrying the evidence that produced them.

    profiles.skills (free text)
        │  vocabulary crosswalk (Step 0)
        ▼
    knowledge graph entities and edges
        │  rules
        ▼
    scores + recommendations, each with reason / evidence / confidence

No AI, no model, no randomness. The same inputs produce the same outputs, and
`result_hash` proves it.
"""

__version__ = "1.0.0"

#: Bumped whenever a rule changes in a way that alters output. Stored on every
#: row so a recommendation can be traced to the logic that produced it, and so a
#: stale row is identifiable rather than merely old.
RULES_VERSION = "1.0.0"

from user_intelligence.config import SCORES, RECOMMENDATION_CATEGORIES
from user_intelligence.engine import IntelligenceEngine

__all__ = ["IntelligenceEngine", "SCORES", "RECOMMENDATION_CATEGORIES",
           "RULES_VERSION", "__version__"]
