"""CSVParser — normalizes CSV text into a list of dict records."""

from __future__ import annotations

import csv
import io
from typing import Any

from knowledge_engine.parsers.base import BaseParser, ParseError


class CSVParser(BaseParser):
    name = "csv_parser"
    version = "0.1.0"

    def parse(self, payload: Any, delimiter: str = ",", **kwargs: Any) -> list[dict[str, Any]]:
        if not isinstance(payload, str):
            raise ParseError(f"CSVParser expects a str payload, got {type(payload).__name__}")
        try:
            reader = csv.DictReader(io.StringIO(payload), delimiter=delimiter)
            records = [dict(row) for row in reader]
        except csv.Error as exc:
            raise ParseError(f"failed to parse CSV payload: {exc}") from exc
        if reader.fieldnames is None:
            raise ParseError("CSV payload has no header row")
        return records
