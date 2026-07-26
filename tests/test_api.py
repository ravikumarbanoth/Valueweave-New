#!/usr/bin/env python3
"""Work Package 6 — API tests.

`Application.handle()` is transport-agnostic, so most of these run without binding
a socket. One class binds a real port, because "it works in-process" and "it works
over HTTP" are different claims and the second is the one a client depends on.
"""

import json
import sys
import threading
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api.app import Application, create_server        # noqa: E402

ALL_ENDPOINTS = ["/entities", "/relationships", "/packages", "/search?q=a",
                 "/graph", "/health", "/version"]


class EnvelopeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Application()

    def test_every_endpoint_returns_200_and_an_envelope(self):
        for path in ALL_ENDPOINTS:
            with self.subTest(path=path):
                p, _, q = path.partition("?")
                status, payload = self.app.handle("GET", p, q)
                self.assertEqual(status, 200)
                self.assertIn("data", payload)
                self.assertIn("meta", payload)

    def test_meta_carries_the_verification_warning(self):
        _, payload = self.app.handle("GET", "/graph")
        self.assertIn("warning", payload["meta"],
                      "unverified rows exist; every response must say so")
        self.assertIn("VST-NEEDS_REVIEW", payload["meta"]["warning"])

    def test_warning_is_computed_not_hardcoded(self):
        """It must disappear on its own once everything is verified."""
        app = Application()
        for e in app.repo.entities:
            e["verification_status"] = "VST-VERIFIED"
        _, payload = app.handle("GET", "/graph")
        self.assertNotIn("warning", payload["meta"])

    def test_root_serves_the_version_document(self):
        status, payload = self.app.handle("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("endpoints", payload["data"])

    def test_responses_are_json_serialisable(self):
        for path in ALL_ENDPOINTS:
            with self.subTest(path=path):
                p, _, q = path.partition("?")
                _, payload = self.app.handle("GET", p, q)
                json.dumps(payload)


class EntityEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Application()

    def test_list_is_paginated(self):
        _, payload = self.app.handle("GET", "/entities", "limit=5")
        self.assertEqual(len(payload["data"]), 5)
        self.assertEqual(payload["page"]["limit"], 5)
        self.assertTrue(payload["page"]["has_more"])
        self.assertEqual(payload["page"]["total"], len(self.app.repo.entities))

    def test_offset_advances(self):
        _, first = self.app.handle("GET", "/entities", "limit=2&offset=0")
        _, second = self.app.handle("GET", "/entities", "limit=2&offset=2")
        self.assertNotEqual([e["global_entity_id"] for e in first["data"]],
                            [e["global_entity_id"] for e in second["data"]])

    def test_type_filter(self):
        _, payload = self.app.handle("GET", "/entities", "type=Crop&limit=500")
        self.assertTrue(payload["data"])
        self.assertTrue(all(e["entity_type"] == "Crop" for e in payload["data"]))

    def test_single_entity_includes_relationships_and_degree(self):
        _, payload = self.app.handle("GET", "/entities/vw:crop:turmeric")
        d = payload["data"]
        self.assertEqual(d["canonical_name"], "Turmeric")
        self.assertIn("outgoing", d["relationships"])
        self.assertEqual(d["degree"],
                         len(d["relationships"]["outgoing"]) + len(d["relationships"]["incoming"]))

    def test_unknown_entity_is_404(self):
        status, payload = self.app.handle("GET", "/entities/vw:crop:does-not-exist")
        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["code"], "NOT_FOUND")


class RelationshipEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Application()

    def test_every_relationship_carries_provenance(self):
        _, payload = self.app.handle("GET", "/relationships", "limit=500")
        for r in payload["data"]:
            with self.subTest(rel=r["relationship_id"]):
                self.assertTrue(r["provenance"]["package"])
                self.assertTrue(r["provenance"]["dataset"])
                self.assertTrue(r["provenance"]["row_id"])

    def test_endpoints_are_expanded_to_names(self):
        _, payload = self.app.handle("GET", "/relationships", "limit=1")
        r = payload["data"][0]
        self.assertIsNotNone(r["from_name"])
        self.assertIsNotNone(r["to_name"])

    def test_entity_filter_returns_both_directions(self):
        _, payload = self.app.handle("GET", "/relationships",
                                     "entity=vw:crop:turmeric&limit=500")
        self.assertTrue(payload["data"])
        for r in payload["data"]:
            self.assertIn("vw:crop:turmeric", (r["from_entity"], r["to_entity"]))

    def test_unknown_relationship_is_404(self):
        status, _ = self.app.handle("GET", "/relationships/vwr:999999")
        self.assertEqual(status, 404)


class PackageEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Application()

    def test_only_released_packages_are_listed(self):
        _, payload = self.app.handle("GET", "/packages")
        ids = [p["package_id"] for p in payload["data"]]
        self.assertNotIn("Package006_Skills", ids)
        self.assertTrue(all(p["datasets"] > 0 for p in payload["data"]))

    def test_single_package_reports_what_it_owns(self):
        _, payload = self.app.handle("GET", "/packages/Package007_Government_Schemes")
        self.assertIn("GovernmentScheme", payload["data"]["owns_entity_types"])

    def test_unknown_package_is_404(self):
        status, _ = self.app.handle("GET", "/packages/Package099_Nope")
        self.assertEqual(status, 404)


class SearchEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Application()

    def test_query_is_required(self):
        status, payload = self.app.handle("GET", "/search")
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "BAD_REQUEST")

    def test_search_returns_ranked_results(self):
        _, payload = self.app.handle("GET", "/search", "q=turmeric&limit=5")
        self.assertTrue(payload["data"])
        self.assertEqual(payload["data"][0]["match_mode"], "EXACT")

    def test_invalid_mode_is_a_400_not_a_500(self):
        status, payload = self.app.handle("GET", "/search", "q=x&mode=SEMANTIC")
        self.assertEqual(status, 400)
        self.assertIn("EXACT", payload["error"]["message"])


class ErrorHandlingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Application()

    def test_write_methods_are_refused(self):
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            with self.subTest(method=method):
                status, payload = self.app.handle(method, "/entities")
                self.assertEqual(status, 405)
                self.assertEqual(payload["error"]["code"], "METHOD_NOT_ALLOWED")

    def test_unknown_route_lists_readable_paths(self):
        status, payload = self.app.handle("GET", "/nowhere")
        self.assertEqual(status, 404)
        available = payload["error"]["detail"]["available"]
        self.assertIn("/entities/{id}", available)
        self.assertFalse(any(p.startswith("^") for p in available),
                         "a client should be shown paths, not regexes")

    def test_unknown_query_parameter_is_rejected(self):
        status, payload = self.app.handle("GET", "/entities", "typ=Crop")
        self.assertEqual(status, 400)
        self.assertIn("typ", payload["error"]["message"])

    def test_limit_above_maximum_is_rejected(self):
        status, _ = self.app.handle("GET", "/entities", "limit=100000")
        self.assertEqual(status, 400)

    def test_negative_offset_is_rejected(self):
        status, _ = self.app.handle("GET", "/entities", "offset=-1")
        self.assertEqual(status, 400)

    def test_trailing_slash_is_equivalent(self):
        a = self.app.handle("GET", "/graph")
        b = self.app.handle("GET", "/graph/")
        self.assertEqual(a[0], b[0])
        self.assertEqual(a[1]["data"], b[1]["data"])


class HttpTransportTest(unittest.TestCase):
    """One class that binds a real socket. In-process success is not HTTP success."""

    @classmethod
    def setUpClass(cls):
        cls.server = create_server("127.0.0.1", 0)      # 0 = let the OS pick
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path):
        url = f"http://127.0.0.1:{self.port}{path}"
        # Explicitly bypass any ambient proxy: this is a loopback test server.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())

    def test_health_over_http(self):
        status, payload = self._get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload["data"]["status"], "ok")

    def test_content_type_is_json(self):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f"http://127.0.0.1:{self.port}/version", timeout=10) as resp:
            self.assertIn("application/json", resp.headers["Content-Type"])

    def test_error_status_reaches_the_client(self):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            opener.open(f"http://127.0.0.1:{self.port}/nowhere", timeout=10)
            self.fail("expected HTTP 404")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
