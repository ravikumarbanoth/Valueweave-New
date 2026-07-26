"""Parser Engine — base interface.

A Parser turns a raw payload (typically a `collectors.base.FetchResult.payload`, but parsers accept
plain strings too so they can be used directly on file contents without a Collector in the loop) into
a list of flat `dict` records ready for provenance-tagging and validation.

Parsers do not fetch data and do not attach provenance — those are the Collector Engine's and
Provenance Engine's jobs respectively. This keeps a Parser reusable across any Collector that can
produce its expected payload shape.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ParseError(Exception):
    """Raised when a payload cannot be parsed into records. Callers should treat this as a hard
    failure for that payload — unlike Collectors, Parsers are expected to raise rather than return
    a sentinel error value, since a caller needs to know parsing failed before attempting to use an
    empty or partial record list."""


class BaseParser(ABC):
    """The interface every Parser plugin must implement."""

    #: Registered name, matching the style used by `collectors.base.BaseCollector.name`.
    name: str = "base_parser"

    #: Semantic version of this parser implementation.
    version: str = "0.1.0"

    @abstractmethod
    def parse(self, payload: Any, **kwargs: Any) -> list[dict[str, Any]]:
        """Parse `payload` into a list of flat records (dicts of column name -> value).

        Implementations must raise `ParseError` (not return an empty list) when the payload cannot
        be interpreted at all, so a caller can distinguish "parsed, zero records found" from
        "parsing failed."
        """
        raise NotImplementedError
