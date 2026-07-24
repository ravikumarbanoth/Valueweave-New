"""XMLParser — normalizes XML text into a list of dict records using the stdlib only.

Handles the common "flat repeated-element" shape:

    <root>
      <record><field_a>1</field_a><field_b>x</field_b></record>
      <record><field_a>2</field_a><field_b>y</field_b></record>
    </root>

Each repeated element's direct children become flat dict keys/values. Attributes on the record
element itself are included with an `@`-prefixed key (e.g. `@id`) to avoid colliding with child-tag
keys. Nested (non-leaf) child elements are serialized to their inner XML string rather than silently
dropped, so no data is lost even for shapes this simple flattener doesn't fully understand.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter
from typing import Any, Optional

from knowledge_engine.parsers.base import BaseParser, ParseError


class XMLParser(BaseParser):
    name = "xml_parser"
    version = "0.1.0"

    def parse(
        self,
        payload: Any,
        record_tag: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        if not isinstance(payload, str):
            raise ParseError(f"XMLParser expects a str payload, got {type(payload).__name__}")
        try:
            root = ET.fromstring(payload)
        except ET.ParseError as exc:
            raise ParseError(f"failed to parse XML payload: {exc}") from exc

        tag = record_tag or self._detect_record_tag(root)
        elements = root.findall(f".//{tag}")
        if not elements:
            raise ParseError(
                f"no elements found for record_tag {tag!r}; pass record_tag explicitly if the "
                "document's repeated element name could not be auto-detected"
            )
        return [self._flatten(el) for el in elements]

    @staticmethod
    def _detect_record_tag(root: ET.Element) -> str:
        child_tags = [child.tag for child in root]
        if not child_tags:
            raise ParseError("XML root element has no children to infer a record tag from")
        tag_counts = Counter(child_tags)
        most_common_tag, count = tag_counts.most_common(1)[0]
        if count < 2:
            raise ParseError(
                "could not auto-detect a repeated record element (no tag appears more than once "
                "under the root); pass record_tag explicitly"
            )
        return most_common_tag

    @staticmethod
    def _flatten(element: ET.Element) -> dict[str, Any]:
        record: dict[str, Any] = {f"@{k}": v for k, v in element.attrib.items()}
        for child in element:
            if len(child) == 0:
                record[child.tag] = (child.text or "").strip()
            else:
                record[child.tag] = ET.tostring(child, encoding="unicode").strip()
        return record
