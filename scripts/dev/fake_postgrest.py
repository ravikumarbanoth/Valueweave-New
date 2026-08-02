"""A minimal PostgREST stand-in serving the real knowledge_graph CSVs.

    python3 scripts/dev/fake_postgrest.py . 5599
    cd frontend
    NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:5599 \
    NEXT_PUBLIC_SUPABASE_ANON_KEY=dev npm run build && npx next start -p 3000

Why this is in the repository: the search outage of this commit could not be
reproduced or verified in any environment without a live Supabase, and a bug
you cannot reproduce locally is a bug you fix by guessing. This serves the 647
real entities and 865 real relationships out of knowledge_graph/, so a
production `next start` can be driven end-to-end on a laptop or in CI.

It implements only the filters lib/knowledge.js actually sends, and returns
HTTP 400 for anything else. That matters more than the coverage: the first
version of this file quietly ignored unhandled filters, which made the
PRE-FIX build look like it returned correct results for a query it had in fact
dropped. A stub that silently widens a query manufactures the very bug under
test.
"""
import csv, json, re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote

ROOT = sys.argv[1]
PORT = int(sys.argv[2])

def load(path, extra=None):
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["sync_deleted_at"] = None
        r.update(extra or {})
    return rows

ENTITIES = load(f"{ROOT}/knowledge_graph/entities/entities.csv")
for e in ENTITIES:
    e["confidence_score"] = int(e["confidence_score"] or 0)
RELS = load(f"{ROOT}/knowledge_graph/relationships/relationships.csv")
TABLES = {"kg_entities": ENTITIES, "kg_relationships": RELS,
          "kg_vocabulary_map": [], "kg_districts": [], "kg_skills": [],
          "kg_schemes": [], "kg_businesses": [], "kg_industries": [],
          "kg_agriculture": []}
UNHANDLED = []

class Unhandled(Exception):
    """Raised rather than ignored.

    The first version of this file appended unhandled filters to a list and
    returned the rows unfiltered. That made `?type=skill&q=electrician` on the
    PRE-FIX build look like it returned 24 correct results, when in truth the
    harness had dropped the ilike. A stub that quietly widens a query
    manufactures the very bug under test.
    """


def apply_filter(rows, key, raw):
    op, _, val = raw.partition(".")
    if op == "is" and val == "null":
        return [r for r in rows if not r.get(key)]
    if op == "eq":
        return [r for r in rows if str(r.get(key)) == val]
    if op == "in":
        wanted = {v.strip('"') for v in val.strip("()").split(",")}
        return [r for r in rows if r.get(key) in wanted]
    if op == "gte":
        return [r for r in rows if float(r.get(key) or 0) >= float(val)]
    if op in ("like", "ilike"):
        # PostgREST accepts `*` and `%` as the wildcard; supabase-js emits `%`.
        # Handling only `*` made every `.ilike('%term%')` match nothing, which
        # looked exactly like the app not searching. Both, now.
        pat = re.split(r"[*%]", val.strip('"'))
        fold = str.lower if op == "ilike" else (lambda x: x)
        rx = re.compile("^" + ".*".join(re.escape(fold(part)) for part in pat) + "$")
        return [r for r in rows if rx.match(fold(str(r.get(key) or "")))]
    raise Unhandled(f"{key}={raw}")

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        u = urlparse(self.path)
        m = re.match(r"^/rest/v1/(\w+)$", u.path)
        if not m:
            return self.send_error(404)
        print("REQ " + self.path, flush=True)
        rows = list(TABLES.get(m.group(1), []))
        try:
            rows = self._filter(rows, u)
        except Unhandled as exc:
            body = json.dumps({"message": f"harness does not implement {exc}"}).encode()
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            print(f"UNHANDLED FILTER: {exc}", flush=True)
            return
        qs = parse_qs(u.query, keep_blank_values=True)
        rows = self._order_and_slice(rows, qs)
        return self._respond(rows, qs)

    def _filter(self, rows, u):
        qs = parse_qs(u.query, keep_blank_values=True)
        for key, vals in qs.items():
            if key in ("select", "order", "limit", "offset"):
                continue
            if key == "or":
                clause = unquote(vals[0]).strip("()")
                keep = []
                for part in re.findall(r"(\w+)\.in\.\(([^)]*)\)", clause):
                    col, ids = part[0], {v.strip('"') for v in part[1].split(",")}
                    keep += [r for r in rows if r.get(col) in ids]
                seen, out = set(), []
                for r in keep:
                    k = id(r)
                    if k not in seen:
                        seen.add(k); out.append(r)
                rows = out
                continue
            for v in vals:
                rows = apply_filter(rows, key, v)
        return rows

    def _order_and_slice(self, rows, qs):
        for spec in qs.get("order", []):
            for part in reversed(spec.split(",")):
                col, *mods = part.split(".")
                rows.sort(key=lambda r: (r.get(col) is None, r.get(col)),
                          reverse="desc" in mods)

        return rows

    def _respond(self, rows, qs):
        total = len(rows)
        rng = self.headers.get("Range")
        lo = 0
        if rng and "-" in rng:
            lo, hi = (int(x) if x else 0 for x in rng.split("-"))
            rows = rows[lo:hi + 1]
        if "limit" in qs:
            rows = rows[: int(qs["limit"][0])]

        body = json.dumps(rows).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Range", f"{lo}-{lo + max(len(rows) - 1, 0)}/{total}")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        for h in ("Origin", "Headers", "Methods"):
            self.send_header(f"Access-Control-Allow-{h}", "*")
        self.end_headers()

if __name__ == "__main__":
    print(f"serving {len(ENTITIES)} entities, {len(RELS)} relationships on :{PORT}", flush=True)
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
