"""HTMLTableParser — extracts a `<table>` from an HTML document into a list of dict records,
using only the stdlib `html.parser` (no BeautifulSoup/lxml dependency).

This handles the common case of a government/statistics page publishing a single data table with a
header row (`<th>` cells, or a first `<tr>` of `<td>` cells if no `<th>` is present). Documents with
multiple tables should pass `table_index` to select which one; nested tables and colspan/rowspan
merging are out of scope for this stdlib-only implementation — such pages are exactly the kind of
"complex webpage" the roadmap defers to the future AI-assisted extractor rather than growing this
parser into a full HTML layout engine.
"""

from __future__ import annotations

from html.parser import HTMLParser
from typing import Any

from knowledge_engine.parsers.base import BaseParser, ParseError


class _TableExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self._in_table = 0
        self._current_table: list[list[str]] = []
        self._current_row: list[str] = []
        self._current_cell_chunks: list[str] = []
        self._in_cell = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._in_table += 1
            if self._in_table == 1:
                self._current_table = []
        elif tag == "tr" and self._in_table:
            self._current_row = []
        elif tag in ("td", "th") and self._in_table:
            self._in_cell = True
            self._current_cell_chunks = []

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self._in_table:
            self._current_row.append("".join(self._current_cell_chunks).strip())
            self._in_cell = False
        elif tag == "tr" and self._in_table:
            if self._current_row:
                self._current_table.append(self._current_row)
        elif tag == "table":
            if self._in_table == 1 and self._current_table:
                self.tables.append(self._current_table)
            self._in_table = max(0, self._in_table - 1)

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._current_cell_chunks.append(data)


class HTMLTableParser(BaseParser):
    name = "html_table_parser"
    version = "0.1.0"

    def parse(self, payload: Any, table_index: int = 0, **kwargs: Any) -> list[dict[str, Any]]:
        if not isinstance(payload, str):
            raise ParseError(f"HTMLTableParser expects a str payload, got {type(payload).__name__}")

        extractor = _TableExtractor()
        try:
            extractor.feed(payload)
        except Exception as exc:  # html.parser can raise a handful of exception types on malformed input
            raise ParseError(f"failed to parse HTML payload: {exc}") from exc

        if not extractor.tables:
            raise ParseError("no <table> elements found in HTML payload")
        if table_index >= len(extractor.tables):
            raise ParseError(
                f"table_index {table_index} out of range; document has {len(extractor.tables)} table(s)"
            )

        rows = extractor.tables[table_index]
        if len(rows) < 2:
            raise ParseError("table has a header row but no data rows")

        header, *data_rows = rows
        records = []
        for row in data_rows:
            record = {header[i] if i < len(header) else f"column_{i}": value for i, value in enumerate(row)}
            records.append(record)
        return records
