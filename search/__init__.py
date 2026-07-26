"""ValueWeave Search — exact, prefix, alias and fuzzy search across the knowledge graph."""

from search.index import Document, SearchIndex
from search.engine import MatchMode, SearchEngine, SearchResult, Scope

__all__ = ["SearchIndex", "Document", "SearchEngine", "SearchResult", "MatchMode", "Scope"]
