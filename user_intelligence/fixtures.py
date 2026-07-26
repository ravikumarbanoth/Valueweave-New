#!/usr/bin/env python3
"""
Synthetic users for testing and demonstration.

No real profile is used, and none of these is a plausible identity — they are
shaped to exercise particular code paths, and named after the path rather than
after a person.

The four cases cover the range the engine has to survive: a user whose skills
resolve well, one whose skills are real but entirely absent from Package006 (the
common case, given the 22.8% resolve rate), one with an empty profile, and one
whose district exists but whose skills do not.
"""

from user_intelligence.context import UserContext

#: Skills chosen because Step 0's crosswalk resolves them.
RESOLVING_SKILLS = ("Welding", "Plumbing", "Food Processing", "Organic Farming",
                    "Carpentry")
#: Skills users actually claim that Package006 does not cover at all.
UNRESOLVABLE_SKILLS = ("Data Entry", "Digital Marketing", "SEO", "Graphic Design",
                       "Beautician Services")


def resolving_user():
    """Skills resolve, district resolves. The best case the data allows."""
    return UserContext(
        user_id="fixture-resolving",
        name="Fixture Resolving", city="Medak", district="Medak",
        bio="Runs a small fabrication workshop.",
        skills=RESOLVING_SKILLS,
        interests=("Agriculture", "Food Business"),
        looking_for="co-founder",
        profile_complete=True,
        archetype="Operator", top_sectors=("Agriculture",), budget="under-5L",
        accepted_connection_ids=("conn-1", "conn-2"),
        collaborator_skills=("Python Programming", "Video Editing"),
    )


def unresolvable_user():
    """Real skills, none in Package006. The common case; must not look broken."""
    return UserContext(
        user_id="fixture-unresolvable",
        name="Fixture Unresolvable", city="Hyderabad", district="Hyderabad",
        skills=UNRESOLVABLE_SKILLS,
        interests=("Digital Services",),
        profile_complete=True,
    )


def empty_user():
    """Nothing but an id. Every rule must degrade rather than raise."""
    return UserContext(user_id="fixture-empty")


def district_only_user():
    """District resolves, skills do not. Isolates the district rules."""
    return UserContext(
        user_id="fixture-district-only",
        name="Fixture District", city="Guntur", district="Guntur",
        skills=("Data Entry",), profile_complete=False)


ALL = {
    "resolving": resolving_user,
    "unresolvable": unresolvable_user,
    "empty": empty_user,
    "district_only": district_only_user,
}


def candidate_profiles():
    """Caller-supplied collaborator candidates."""
    return [
        {"id": "peer-1", "name": "Peer One", "city": "Medak",
         "skills": ["Python Programming", "Full Stack Web Development"],
         "interests": ["Agriculture"]},
        {"id": "peer-2", "name": "Peer Two", "city": "Hyderabad",
         "skills": ["Welding"], "interests": ["Manufacturing"]},
        {"id": "peer-3", "name": "Peer Three", "city": "Medak",
         "skills": ["Data Entry"], "interests": []},
    ]


def research_articles():
    return [
        {"id": "a1", "slug": "medak-food-processing", "district": "Medak",
         "sector": "Agriculture", "title": "Food processing in Medak",
         "summary": "Opportunities in Medak district for agro-processing."},
        {"id": "a2", "slug": "unrelated-topic", "district": "Chennai",
         "sector": "Textiles", "title": "Something else",
         "summary": "Not relevant to the fixtures."},
    ]
