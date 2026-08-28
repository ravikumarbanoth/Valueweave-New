#!/usr/bin/env python3
import unittest

from knowledge_engine.stage2 import DeterministicIntel


class Stage2SmokeTests(unittest.TestCase):
    def setUp(self):
        self.d = DeterministicIntel()

    def assert_analyze(self, q):
        out = self.d.analyze(q)
        self.assertIn("intent", out)
        self.assertIn("entities", out)
        self.assertIn("groups", out)
        self.assertIsInstance(out["entities"], list)
        self.assertIsInstance(out["groups"], dict)

    def test_ev_technician_course(self):
        self.assert_analyze("EV technician course")

    def test_electrician_jobs_medak(self):
        self.assert_analyze("electrician jobs in Medak")

    def test_mobile_repair(self):
        self.assert_analyze("mobile repair near me")

    def test_cctv_technician(self):
        self.assert_analyze("CCTV technician training and jobs")

    def test_telugu_and_tanglish(self):
        # Telugu script + Tanglish variants should not crash the analyzer
        self.assert_analyze("ఎలక్ట్రిషియన్ ఉద్యోగాలు మేడక్")
        self.assert_analyze("electrician jobs Medak telugu")


if __name__ == "__main__":
    unittest.main()
