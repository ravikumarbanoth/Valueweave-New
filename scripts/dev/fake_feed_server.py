#!/usr/bin/env python3
"""A minimal feed server with honest HTTP caching semantics.

    python3 scripts/dev/fake_feed_server.py 5601

Why this is in the repository: the claim "we do not download everything every
day" rests entirely on conditional requests working — `If-None-Match` out, a
`304 Not Modified` with no body back. That behaviour cannot be tested against a
live government feed, for two reasons that both matter: this sandbox cannot
reach one (the proxy returns 403), and even with a network you cannot ask a
real server to *change* on command, which is the other half of what needs
testing.

So this serves the real fixtures with real ETag and Last-Modified headers,
answers `If-None-Match` and `If-Modified-Since` correctly, and exposes a
`/_mutate` endpoint that edits an item so the next fetch is genuinely different.
That makes the full cycle — unchanged, changed, unchanged again — reproducible
in a test.

It implements only the semantics the collectors actually use. Anything else is
a 404 rather than a guess, for the same reason `fake_postgrest.py` returns 400
on an unhandled filter: a stub that quietly widens its behaviour manufactures a
green test for a broken pipeline.
"""
import email.utils
import hashlib
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES = ROOT / "collection" / "fixtures"
#: Only read from the command line when run as a script — a test imports
#: this module and `sys.argv[1]` is then the test runner's own argument.
DEFAULT_PORT = 5601

#: path -> (bytes, last_modified_epoch). Loaded once and mutated in memory, so
#: a test never has to write to the repository to simulate a publisher.
STATE = {}
for path in sorted(FIXTURES.iterdir()):
    if path.is_file():
        STATE[f"/{path.name}"] = [path.read_bytes(), time.time() - 3600]

CONTENT_TYPES = {
    ".rss": "application/rss+xml", ".atom": "application/atom+xml",
    ".jsonfeed": "application/feed+json", ".csv": "text/csv",
    ".xml": "application/xml", ".json": "application/json",
}

REQUESTS = []          # every request, for a test to assert on
NOT_MODIFIED = []      # the ones answered 304


def etag_of(body):
    return '"' + hashlib.sha256(body).hexdigest()[:24] + '"'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/_mutate":
            target = parse_qs(parsed.query).get("path", [""])[0]
            if target not in STATE:
                return self.send_error(404, "no such fixture")
            body, _ = STATE[target]
            # The LAST title, not the first. In both RSS and JSON Feed the
            # first one is the FEED's title, and mutating that changes the
            # payload while leaving every item identical — which is precisely
            # the case per-item change detection is designed to shrug off, so
            # the test would have proved the opposite of what it claims.
            hits = list(re.finditer(rb'(<title>|"title": ")', body))
            if not hits:
                return self.send_error(422, "fixture has no title to mutate")
            at = hits[-1]
            body = body[:at.end()] + b"MUTATED " + body[at.end():]
            STATE[target] = [body, time.time()]
            return self._send(200, b'{"mutated":true}', "application/json", None, None)

        if parsed.path == "/_stats":
            payload = (b'{"requests":%d,"not_modified":%d}'
                       % (len(REQUESTS), len(NOT_MODIFIED)))
            return self._send(200, payload, "application/json", None, None)

        if parsed.path not in STATE:
            return self.send_error(404)

        body, modified_at = STATE[parsed.path]
        etag = etag_of(body)
        last_modified = email.utils.formatdate(modified_at, usegmt=True)
        REQUESTS.append(parsed.path)

        # RFC 9110: If-None-Match wins outright when present; If-Modified-Since
        # is only consulted in its absence. Checking both and OR-ing them would
        # serve a 304 for a changed body whose timestamp had not ticked.
        if_none_match = self.headers.get("If-None-Match")
        if_modified_since = self.headers.get("If-Modified-Since")
        fresh = False
        if if_none_match:
            fresh = if_none_match.strip() == etag
        elif if_modified_since:
            try:
                since = email.utils.parsedate_to_datetime(if_modified_since).timestamp()
                fresh = modified_at <= since + 1
            except (TypeError, ValueError):
                fresh = False

        if fresh:
            NOT_MODIFIED.append(parsed.path)
            return self._send(304, b"", None, etag, last_modified)

        suffix = Path(parsed.path).suffix
        return self._send(200, body, CONTENT_TYPES.get(suffix, "text/plain"),
                          etag, last_modified)

    def _send(self, status, body, content_type, etag, last_modified):
        self.send_response(status)
        if content_type:
            self.send_header("Content-Type", content_type)
        if etag:
            self.send_header("ETag", etag)
        if last_modified:
            self.send_header("Last-Modified", last_modified)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)


def serve(port=DEFAULT_PORT):
    server = HTTPServer(("127.0.0.1", port), Handler)
    return server


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    print(f"serving {len(STATE)} fixtures on http://127.0.0.1:{port}", flush=True)
    serve(port).serve_forever()
