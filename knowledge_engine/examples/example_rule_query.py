"""Runnable example: the Rule Engine answering the exact example queries from the Phase-2 brief
("Investment < ₹5 lakh", "District = Medak", "Skill Level = Beginner", "Suitable for Women",
"Suitable for Students", "Suitable for Rural Areas") against a small in-memory dataset.

Run with: python examples/example_rule_query.py
"""

from __future__ import annotations

from knowledge_engine.rule_engine import RuleQuery, district_equals, investment_below, skill_level_equals, suitable_for

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


def main() -> None:
    print("Query: Investment < ₹5 lakh AND District = Medak AND Skill Level = Beginner AND Suitable for Women")
    query = RuleQuery.all_of(
        investment_below(500000),
        district_equals("Medak"),
        skill_level_equals("Beginner"),
        suitable_for("Women"),
    )
    for record in query.filter(OPPORTUNITIES):
        print(f"  - {record['name']}")

    print("\nQuery: Suitable for Students")
    students_query = RuleQuery.all_of(suitable_for("Students"))
    for record in students_query.filter(OPPORTUNITIES):
        print(f"  - {record['name']}")

    print("\nQuery: Suitable for Rural Areas (matching against ideal_target_audience)")
    rural_query = RuleQuery.all_of(suitable_for("Rural"))
    for record in rural_query.filter(OPPORTUNITIES):
        print(f"  - {record['name']}")


if __name__ == "__main__":
    main()
