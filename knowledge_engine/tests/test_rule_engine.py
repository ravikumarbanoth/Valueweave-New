import unittest

from knowledge_engine.rule_engine import (
    FieldCondition,
    RuleQuery,
    district_equals,
    investment_below,
    skill_level_equals,
    suitable_for,
)

OPPORTUNITIES = [
    {
        "name": "Mushroom Cultivation",
        "district": "Medak",
        "minimum_investment": "120000",
        "skill_level": "Beginner",
        "ideal_target_audience": "Women entrepreneurs, rural youth, students",
    },
    {
        "name": "Cybersecurity Consulting",
        "district": "Hyderabad",
        "minimum_investment": "800000",
        "skill_level": "Advanced",
        "ideal_target_audience": "Urban IT professionals",
    },
    {
        "name": "Cold-Pressed Oil Extraction",
        "district": "Medak",
        "minimum_investment": "450000",
        "skill_level": "Beginner",
        "ideal_target_audience": "Rural entrepreneurs, women",
    },
]


class OperatorTest(unittest.TestCase):
    def test_numeric_comparison_coerces_strings(self):
        cond = FieldCondition("minimum_investment", "<", 500000)
        self.assertTrue(cond.evaluate(OPPORTUNITIES[0]))
        self.assertFalse(cond.evaluate(OPPORTUNITIES[1]))

    def test_currency_formatted_value_is_coerced(self):
        cond = FieldCondition("minimum_investment", "<", "₹5,00,000")
        self.assertTrue(cond.evaluate(OPPORTUNITIES[0]))

    def test_equality_is_case_insensitive_for_strings(self):
        cond = FieldCondition("district", "==", "medak")
        self.assertTrue(cond.evaluate(OPPORTUNITIES[0]))

    def test_missing_field_is_false_not_error(self):
        cond = FieldCondition("nonexistent_field", "==", "x")
        self.assertFalse(cond.evaluate(OPPORTUNITIES[0]))

    def test_unknown_operator_raises_at_construction(self):
        with self.assertRaises(ValueError):
            FieldCondition("district", "~=", "Medak")


class RuleQueryTest(unittest.TestCase):
    def test_all_of_requires_every_condition(self):
        query = RuleQuery.all_of(
            investment_below(500000),
            district_equals("Medak"),
        )
        results = query.filter(OPPORTUNITIES)
        self.assertEqual({r["name"] for r in results}, {"Mushroom Cultivation", "Cold-Pressed Oil Extraction"})

    def test_any_of_requires_at_least_one_condition(self):
        query = RuleQuery.any_of(
            skill_level_equals("Advanced"),
            district_equals("Medak"),
        )
        results = query.filter(OPPORTUNITIES)
        self.assertEqual(len(results), 3)  # all 3 match either Advanced skill or Medak district

    def test_suitable_for_matches_free_text_audience(self):
        query = RuleQuery.all_of(suitable_for("Women"))
        results = query.filter(OPPORTUNITIES)
        self.assertEqual({r["name"] for r in results}, {"Mushroom Cultivation", "Cold-Pressed Oil Extraction"})

    def test_brief_example_query_combination(self):
        query = RuleQuery.all_of(
            investment_below(500000),
            district_equals("Medak"),
            skill_level_equals("Beginner"),
            suitable_for("Women"),
        )
        results = query.filter(OPPORTUNITIES)
        self.assertEqual({r["name"] for r in results}, {"Mushroom Cultivation", "Cold-Pressed Oil Extraction"})

    def test_nested_group_mixes_and_or(self):
        skill_group = RuleQuery.any_of(
            skill_level_equals("Beginner"),
            skill_level_equals("Intermediate"),
        )
        query = RuleQuery.all_of(district_equals("Medak")).where_group(skill_group)
        results = query.filter(OPPORTUNITIES)
        self.assertEqual(len(results), 2)

    def test_empty_query_matches_everything(self):
        self.assertEqual(len(RuleQuery().filter(OPPORTUNITIES)), len(OPPORTUNITIES))

    def test_count(self):
        query = RuleQuery.all_of(district_equals("Medak"))
        self.assertEqual(query.count(OPPORTUNITIES), 2)


if __name__ == "__main__":
    unittest.main()
