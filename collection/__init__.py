"""ValueWeave automated collection — the front of the knowledge pipeline.

    sources -> fetch -> detect -> classify -> dedupe -> review queue -> a person

Nothing in this package writes to `packages/`, to the knowledge graph, or to
Supabase. Its whole output is a queue in Git that a human reads.
"""
