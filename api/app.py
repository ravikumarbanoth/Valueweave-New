#!/usr/bin/env python3
"""
ValueWeave Platform v2.2 — API application and HTTP server (Work Package 3)

Built on `http.server` from the standard library, with no third-party dependency.
That is a deliberate constraint inherited from the Knowledge Engine: this platform
runs and is reviewable on a bare Python install. A production deployment would put
this behind a real WSGI/ASGI server, and the split between `Application` (routing
and dispatch, transport-agnostic) and `create_server` (the socket) is where that
swap happens.

WHAT THIS SCAFFOLD DELIBERATELY DOES NOT DO
-------------------------------------------
No authentication, no rate limiting, no API versioning in the URL. The v2.1 audit
named both missing pieces as blocking for a public deployment, and inventing a
token scheme now would be worse than the honest gap — it would look like security.
`/version` says `authentication: none` so a consumer cannot mistake the situation.

No write endpoints, and non-GET methods are refused at the router with a 405 that
explains why rather than a bare status code.
"""

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from api import API_VERSION
from api.errors import ApiError
from api import handlers

# (display path, compiled pattern, handler). Patterns are anchored and matched in
# order, so `/entities` cannot be shadowed by `/entities/{id}`. The display path is
# what a client is shown in a 404 — a regex is not an answer to "what can I call?".
ROUTES = [
    ("/entities", re.compile(r"^/entities/?$"), handlers.list_entities),
    ("/entities/{id}", re.compile(r"^/entities/(?P<entity_id>[^/]+)/?$"), handlers.get_entity),
    ("/relationships", re.compile(r"^/relationships/?$"), handlers.list_relationships),
    ("/relationships/{id}", re.compile(r"^/relationships/(?P<relationship_id>[^/]+)/?$"),
     handlers.get_relationship),
    ("/packages", re.compile(r"^/packages/?$"), handlers.list_packages),
    ("/packages/{id}", re.compile(r"^/packages/(?P<package_id>[^/]+)/?$"), handlers.get_package),
    ("/search", re.compile(r"^/search/?$"), handlers.search),
    ("/graph", re.compile(r"^/graph/?$"), handlers.graph),
    ("/health", re.compile(r"^/health/?$"), handlers.health),
    ("/version", re.compile(r"^/version/?$"), handlers.version),
]

WARNING = ("No row in this knowledge base has had human data-steward review. "
           "Every entity is VST-NEEDS_REVIEW. Confidence scores are estimates of "
           "source strength, not verification.")


class Application:
    """Routing and dispatch, with no knowledge of sockets. Directly testable."""

    def __init__(self, repository=None):
        self.repo = repository or handlers.Repository()

    def routes(self):
        return [display for display, _, _ in ROUTES]

    def handle(self, method, path, query=""):
        """
        Dispatch one request. Returns (status, payload dict).

        Never raises: an unexpected exception becomes a 500 with a stable shape,
        because a client parsing JSON should not suddenly receive a stack trace.
        """
        try:
            if method != "GET":
                raise ApiError.unsupported_method(method, path)

            path = urlparse(path).path.rstrip("/") or "/"
            if path == "/":
                return 200, self._envelope(handlers.version(self.repo, {}))

            params = {k: v[0] for k, v in parse_qs(query, keep_blank_values=True).items()}
            for _display, pattern, fn in ROUTES:
                m = pattern.match(path)
                if m:
                    result = fn(self.repo, params, **m.groupdict())
                    status = result.pop("_status", 200)
                    return status, self._envelope(result)

            raise ApiError(404, "NO_ROUTE",
                           f"no route for {path!r}; see GET /version for the endpoint list",
                           path=path, available=self.routes())
        except ApiError as exc:
            return exc.status, exc.to_dict()
        except Exception as exc:                                   # noqa: BLE001
            return 500, {"error": {"code": "INTERNAL", "status": 500,
                                   "message": f"{type(exc).__name__}: {exc}"}}

    def _envelope(self, result):
        """Wrap a handler payload in the standard envelope.

        `meta.warning` is computed, not hard-coded: it is emitted only while
        unverified rows actually exist, so it will vanish by itself the day
        stewardship makes it false.
        """
        counts = self.repo.verification_counts()
        unverified = sum(v for k, v in counts.items() if k != "VST-VERIFIED")
        meta = {
            "api_version": API_VERSION,
            "graph_version": "2.0.0",
            "entities": len(self.repo.entities),
            "relationships": len(self.repo.relationships),
            "verification": counts,
        }
        if unverified:
            meta["warning"] = WARNING
        out = {k: v for k, v in result.items() if not k.startswith("_")}
        out["meta"] = meta
        return out


class _Handler(BaseHTTPRequestHandler):
    server_version = f"ValueWeave/{API_VERSION}"
    application = None            # injected by create_server

    def _respond(self, method):
        parsed = urlparse(self.path)
        status, payload = self.application.handle(method, parsed.path, parsed.query)
        pretty = "pretty" in parse_qs(parsed.query)
        body = json.dumps(payload, indent=2 if pretty else None,
                          ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # Read-only public data: permit browser access without a proxy.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if method != "HEAD":
            self.wfile.write(body)

    def do_GET(self):
        self._respond("GET")

    def do_HEAD(self):
        self._respond("HEAD")

    def do_POST(self):
        self._respond("POST")

    def do_PUT(self):
        self._respond("PUT")

    def do_DELETE(self):
        self._respond("DELETE")

    def do_PATCH(self):
        self._respond("PATCH")

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")


def create_server(host="127.0.0.1", port=8000, application=None):
    app = application or Application()
    handler = type("BoundHandler", (_Handler,), {"application": app})
    return ThreadingHTTPServer((host, port), handler)
