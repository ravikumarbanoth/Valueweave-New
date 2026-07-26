"""JSONParser — normalizes JSON (text or already-decoded) into a list of dict records."""

from __future__ import annotations

import json
from typing import Any, Optional

from knowledge_engine.parsers.base import BaseParser, ParseError


class JSONParser(BaseParser):
    name = "json_parser"
    version = "0.1.0"

    def parse(
        self,
        payload: Any,
        records_path: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Parse `payload` into a list of records.

        Args:
            payload: A JSON string, or an already-decoded `dict`/`list` (e.g. from
                `APICollector`, which decodes JSON itself).
            records_path: A dot-separated path (e.g. "data.results") locating the list of records
                within a top-level JSON object. If omitted and `payload` decodes to a dict, the
                parser looks for a single list-valued top-level key; if omitted and `payload`
                decodes to a list, that list is used directly.
        """
        data = payload
        if isinstance(payload, (str, bytes)):
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ParseError(f"failed to parse JSON payload: {exc}") from exc

        if records_path:
            for key in records_path.split("."):
                if not isinstance(data, dict) or key not in data:
                    raise ParseError(f"records_path {records_path!r} not found in payload")
                data = data[key]

        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    raise ParseError(
                        "JSON payload's record list must contain objects; "
                        f"found {type(item).__name__}"
                    )
            return data

        if isinstance(data, dict):
            list_valued_keys = [k for k, v in data.items() if isinstance(v, list)]
            if len(list_valued_keys) == 1:
                return self.parse(data[list_valued_keys[0]])
            if not list_valued_keys:
                # A single JSON object with no nested list is treated as one record.
                return [data]
            raise ParseError(
                "JSON payload has multiple list-valued top-level keys "
                f"({list_valued_keys}); pass records_path to disambiguate"
            )

        raise ParseError(f"unsupported JSON payload shape: {type(data).__name__}")
