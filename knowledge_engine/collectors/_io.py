"""Shared local-file/HTTP fetch helper used by every built-in collector.

Kept separate from `base.py` because it's an implementation detail of the stdlib-based collectors,
not part of the plugin interface itself — a future collector (e.g. an S3-backed one) has no reason to
depend on this module.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


class FetchError(Exception):
    """Raised internally when a read fails; collectors catch this and populate FetchResult.error."""


def read_source(source: str, timeout: float = 15.0, headers: dict[str, str] | None = None) -> tuple[bytes, dict[str, Any]]:
    """Read raw bytes from `source`, which may be a local file path or an http(s) URL.

    Returns (content_bytes, metadata). Raises FetchError on any failure — callers are expected to
    catch this and convert it into a `FetchResult(status="error")` rather than letting it propagate,
    per `BaseCollector.fetch`'s contract.
    """
    if source.startswith("http://") or source.startswith("https://"):
        request = urllib.request.Request(source, headers=headers or {"User-Agent": "ValueWeave-KnowledgeEngine/0.1.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content = response.read()
                metadata = {
                    "http_status": response.status,
                    "content_type": response.headers.get("Content-Type"),
                }
                return content, metadata
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            raise FetchError(f"HTTP fetch failed for {source}: {exc}") from exc

    path = Path(source)
    if not path.exists():
        raise FetchError(f"local file does not exist: {source}")
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise FetchError(f"failed to read local file {source}: {exc}") from exc
    return content, {"file_size_bytes": len(content)}
