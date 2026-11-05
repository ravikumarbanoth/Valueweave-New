"""
ValueWeave Knowledge Intelligence — derived views over the canonical graph.

WHAT THIS IS, AND WHAT ALREADY EXISTED
---------------------------------------
`knowledge_engine/stage2.py` and `frontend/lib/search/intelligence.js` already
do QUERY intelligence: they read a sentence and return intent, entities,
location and which result groups are thin. That is the question "what is
missing from THIS PAGE".

This package asks the other one: **what is missing from the GRAPH**. For a
given entity, which useful dimensions does the repository actually hold, and
which are simply absent? Those are different questions with different answers,
and neither module answers this one.

It reads the graph, the relationships and the research articles, joins them,
and says what is there and what is not. It writes no entity, no relationship
and no package row.

    packages/  ->  knowledge_graph/  ->  THIS LAYER (derived, disposable)

Git is canonical. `knowledge_graph/` is compiled from it. Everything here is
compiled from THAT, which makes it the third derivation and the first one safe
to delete and rebuild without review — because nothing in it is a new claim
about the world.

THE FOUR TRUST LEVELS, AND WHY THEY ARE NOT DECORATION
-------------------------------------------------------
CANONICAL         in the graph, from a published package
DERIVED           computed from canonical data by a rule in this package
INFERRED          suggested by a rule and NOT safe to state as fact
RESEARCH_REQUIRED a hole, recorded so a person can fill it

A DERIVED edge is a restatement — "these two are joined in relationships.csv"
is not a new fact. An INFERRED one is a guess, however reasonable, and the
moment one is written without its label somebody downstream reads it as
knowledge. There is no `promote()` here for that reason: the only route toward
canonical is the existing review queue.
"""

CANONICAL = "CANONICAL"
DERIVED = "DERIVED"
INFERRED = "INFERRED"
RESEARCH_REQUIRED = "RESEARCH_REQUIRED"

TRUST_LEVELS = (CANONICAL, DERIVED, INFERRED, RESEARCH_REQUIRED)
