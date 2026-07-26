#!/usr/bin/env python3
"""
UserContext — everything the rules may read about one user, assembled once.

Rules never touch Supabase or the filesystem. They read a frozen context, which
makes them pure functions of their input and therefore trivially testable and
provably reproducible.

MISSING INPUTS ARE CARRIED, NOT HIDDEN
--------------------------------------
`assessment_results` and `teams` do not exist. The context records that as data —
`unavailable_inputs` — rather than raising or defaulting to empty. A rule can then
return UNAVAILABLE with a specific reason, and the eventual UI can say "we don't
have your assessment yet" instead of showing a zero.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from user_intelligence.config import INPUTS, MISSING, ROOT

IDEAS_PATH = ROOT / "frontend" / "lib" / "idea-library" / "ideas.json"
SECTORS_PATH = ROOT / "frontend" / "lib" / "idea-library" / "sectors.json"


@dataclass
class UserContext:
    user_id: str
    name: str = ""
    city: str = ""
    bio: str = ""
    skills: tuple = ()
    interests: tuple = ()
    looking_for: str = ""
    profile_complete: bool = False

    #: collaborator_profiles
    archetype: str = ""
    district: str = ""
    top_sectors: tuple = ()
    budget: str = ""
    ep_score: int = None

    #: connections, split by status
    accepted_connection_ids: tuple = ()
    pending_connection_ids: tuple = ()
    #: skills of users this person has an accepted connection with
    collaborator_skills: tuple = ()

    #: opportunities this user owns
    owned_opportunity_skills: tuple = ()

    #: Inputs the brief names that do not exist. Rules read this.
    unavailable_inputs: dict = field(default_factory=dict)

    def __post_init__(self):
        # Normalise to tuples so the context is hashable and iteration order is
        # stable — a set here would make output non-reproducible across processes.
        for attr in ("skills", "interests", "top_sectors", "collaborator_skills",
                     "owned_opportunity_skills", "accepted_connection_ids",
                     "pending_connection_ids"):
            value = getattr(self, attr) or ()
            setattr(self, attr, tuple(sorted({str(v).strip() for v in value if v})))
        if not self.unavailable_inputs:
            self.unavailable_inputs = {
                name: spec.detail for name, spec in sorted(INPUTS.items())
                if spec.status == MISSING
            }

    @property
    def location_term(self):
        """The district-ish string to resolve. `district` is explicit; `city` is not."""
        return (self.district or self.city or "").split(",")[0].strip()

    def missing(self, *names):
        """Return the first named input that is unavailable, or None."""
        for n in names:
            if n in self.unavailable_inputs:
                return n
        return None

    def to_dict(self):
        return {
            "user_id": self.user_id, "name": self.name, "city": self.city,
            "district": self.district, "skills": list(self.skills),
            "interests": list(self.interests), "top_sectors": list(self.top_sectors),
            "archetype": self.archetype, "budget": self.budget,
            "profile_complete": self.profile_complete,
            "accepted_connections": len(self.accepted_connection_ids),
            "pending_connections": len(self.pending_connection_ids),
            "collaborator_skills": list(self.collaborator_skills),
            "unavailable_inputs": sorted(self.unavailable_inputs),
        }


def from_supabase_rows(profile, collaborator=None, connections=(), peers=(),
                       opportunities=()):
    """
    Build a context from rows already fetched by the caller.

    The engine does not query Supabase itself — a caller passes rows in. That keeps
    the engine free of a client dependency, testable without credentials, and
    usable from a Next.js route handler that has already loaded the user.
    """
    accepted, pending = [], []
    for c in connections or ():
        (accepted if c.get("status") == "accepted" else pending).append(c.get("id"))

    peer_skills = []
    for p in peers or ():
        peer_skills.extend(p.get("skills") or [])

    opp_skills = []
    for o in opportunities or ():
        opp_skills.extend(o.get("skills_needed") or [])

    collaborator = collaborator or {}
    return UserContext(
        user_id=profile.get("id", ""),
        name=profile.get("name", "") or "",
        city=profile.get("city", "") or "",
        bio=profile.get("bio", "") or "",
        skills=tuple(profile.get("skills") or ()),
        interests=tuple(profile.get("interests") or ()),
        looking_for=profile.get("looking_for", "") or "",
        profile_complete=bool(profile.get("profile_complete")),
        archetype=collaborator.get("archetype", "") or "",
        district=collaborator.get("district", "") or "",
        top_sectors=tuple(collaborator.get("top_sectors") or ()),
        budget=collaborator.get("budget", "") or "",
        ep_score=collaborator.get("ep_score"),
        accepted_connection_ids=tuple(x for x in accepted if x),
        pending_connection_ids=tuple(x for x in pending if x),
        collaborator_skills=tuple(peer_skills),
        owned_opportunity_skills=tuple(opp_skills),
    )


def load_idea_library():
    """
    The 122 ideas, from disk.

    `idea_library` is not a Supabase table — it is static JSON the frontend
    imports. Reading the same file means the engine and the app cannot disagree
    about what an idea is.
    """
    if not IDEAS_PATH.exists():
        return [], {}
    ideas = json.loads(IDEAS_PATH.read_text(encoding="utf-8"))
    sectors = {}
    if SECTORS_PATH.exists():
        sectors = {s["id"]: s["label"]
                   for s in json.loads(SECTORS_PATH.read_text(encoding="utf-8"))}
    ideas.sort(key=lambda i: i.get("slug", ""))       # deterministic order
    return ideas, sectors
