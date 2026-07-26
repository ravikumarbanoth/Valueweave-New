"""APICollector — generic REST/JSON API collector.

Handles the common case (GET a URL, optionally with query params/headers, get back JSON) without any
API-specific code. A source that needs bespoke pagination, auth flows, or response shapes should
subclass `APICollector` and override `fetch`/`_fetch_page` rather than growing this class with
per-API special cases — that keeps the plugin architecture honest.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Optional

from knowledge_engine.collectors.base import BaseCollector, FetchResult


class APICollector(BaseCollector):
    name = "api_collector"
    version = "0.1.0"

    def fetch(
        self,
        source: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: float = 15.0,
        paginate: Optional[Callable[[dict[str, Any]], Optional[str]]] = None,
        max_pages: int = 50,
        **kwargs: Any,
    ) -> FetchResult:
        """Fetch JSON from `source`.

        Args:
            source: The base API URL.
            params: Optional query-string parameters for the first request.
            headers: Optional request headers (e.g. an API key header).
            timeout: Per-request timeout in seconds.
            paginate: Optional callable that takes the decoded JSON of a page and returns the next
                page's URL, or None to stop. When provided, all pages' JSON bodies are collected into
                a list under `payload["pages"]`. When omitted, `payload` is just the single decoded
                JSON response.
            max_pages: Safety cap on how many pages `paginate` may request, so a misconfigured
                pagination callback cannot loop indefinitely against a live API.
        """
        url = source
        if params:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{urllib.parse.urlencode(params)}"

        request_headers = {"Accept": "application/json", "User-Agent": "ValueWeave-KnowledgeEngine/0.1.0"}
        request_headers.update(headers or {})

        pages: list[Any] = []
        next_url: Optional[str] = url
        pages_fetched = 0
        try:
            while next_url and pages_fetched < max_pages:
                request = urllib.request.Request(next_url, headers=request_headers)
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    body = response.read()
                    decoded = json.loads(body.decode("utf-8"))
                pages.append(decoded)
                pages_fetched += 1
                next_url = paginate(decoded) if paginate else None
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            return FetchResult(
                payload=None,
                source_url=source,
                collector_name=self.name,
                collector_version=self.version,
                status="error",
                error=f"API fetch failed for {source}: {exc}",
            )

        payload: Any = {"pages": pages} if paginate else pages[0]
        return FetchResult(
            payload=payload,
            source_url=source,
            collector_name=self.name,
            collector_version=self.version,
            metadata={"pages_fetched": pages_fetched},
        )

    def supports(self, source: str) -> bool:
        # Never auto-selected: an API endpoint is indistinguishable from a plain JSON file URL by
        # string alone, and pagination/auth needs are API-specific. Callers must request this
        # collector by name.
        return False
