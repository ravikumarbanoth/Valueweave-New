#!/usr/bin/env python3
import unittest

from tests.js_harness import NODE, JsHarness


class SearchIntelligenceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.h = JsHarness()

    @classmethod
    def tearDownClass(cls):
        cls.h.cleanup()

    @unittest.skipIf(NODE is None, "node is required — the code under test is JavaScript")
    def test_analyze_search_query_returns_intent_and_gaps(self):
        js = '''
        const { analyzeSearchQuery } = await import("$LIB/search/intelligence.js");
        const result = analyzeSearchQuery("electrician jobs in Medak", [
          { id: "skills", total: 0 },
          { id: "business", total: 0 },
          { id: "education", total: 0 },
          { id: "research", total: 0 },
        ]);
        console.log(JSON.stringify(result));
        '''
        out = self.h.run(js)
        self.assertEqual(out["intent"], "job")
        self.assertEqual(out["location"], "Medak")
        self.assertTrue(isinstance(out["entities"], list))
        self.assertGreaterEqual(len(out["entities"]), 1)
        self.assertIn("Job and occupation content", out["gaps"])

    @unittest.skipIf(NODE is None, "node is required — the code under test is JavaScript")
    def test_multilingual_intent_and_location_detection(self):
        cases = [
            ("నాకు electrician course కావాలి", "learn", None),
            ("medak lo electrician course", "learn", "Medak"),
            ("మెదక్లో ఎలక్ట్రిషియన్ పని నేర్చుకోవాలి", "learn", "Medak"),
            ("వరంగల్లో సోలార్ బిజినెస్", "business", "Warangal"),
            ("హైదరాబాద్‌లో ఈవీ ఉద్యోగాలు", "job", "Hyderabad"),
            ("PMEGP subsidy scheme", "scheme", None),
        ]
        for query, expected_intent, expected_location in cases:
            with self.subTest(query=query):
                js = f'''
                const {{ analyzeSearchQuery }} = await import("$LIB/search/intelligence.js");
                const result = analyzeSearchQuery({repr(query)});
                console.log(JSON.stringify(result));
                '''
                out = self.h.run(js)
                self.assertEqual(out["intent"], expected_intent,
                                 f"Failed intent for query: {query}")
                if expected_location:
                    self.assertEqual(out["location"], expected_location,
                                     f"Failed location for query: {query}")


if __name__ == "__main__":
    unittest.main()
