"""RSSParser — normalizes RSS 2.0 and Atom feeds into a list of dict records, stdlib only.

Handles both feed families' repeated-entry element (`<item>` for RSS 2.0, `<entry>` for Atom) and is
namespace-agnostic so Atom's default `http://www.w3.org/2005/Atom` namespace doesn't need special
casing by the caller.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from knowledge_engine.parsers.base import BaseParser, ParseError

_ENTRY_LOCAL_NAMES = {"item", "entry"}


class RSSParser(BaseParser):
    name = "rss_parser"
    version = "0.1.0"

    def parse(self, payload: Any, **kwargs: Any) -> list[dict[str, Any]]:
        if not isinstance(payload, str):
            raise ParseError(f"RSSParser expects a str payload, got {type(payload).__name__}")
        try:
            root = ET.fromstring(payload)
        except ET.ParseError as exc:
            raise ParseError(f"failed to parse RSS/Atom payload: {exc}") from exc

        entries = [el for el in root.iter() if _local_name(el.tag) in _ENTRY_LOCAL_NAMES]
        if not entries:
            raise ParseError("no <item> (RSS) or <entry> (Atom) elements found in feed")
        return [self._flatten(entry) for entry in entries]

    @staticmethod
    def _flatten(entry: ET.Element) -> dict[str, Any]:
        record: dict[str, Any] = {}
        for child in entry:
            key = _local_name(child.tag)
            if key == "link" and not (child.text or "").strip():
                # Atom represents the link as <link href="..."/> rather than text content.
                value = child.attrib.get("href", "")
            else:
                value = (child.text or "").strip()
            if key in record:
                # A repeated tag (e.g. multiple <category> elements) becomes a "; "-joined string,
                # matching the multi-source-URL convention used elsewhere in the engine rather than
                # silently overwriting the first occurrence.
                record[key] = f"{record[key]}; {value}" if value else record[key]
            else:
                record[key] = value
        return record


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag
