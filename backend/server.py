"""ValueWeave backend — Idea Library + Emergent Google Auth.

Public endpoints:
  - GET /api/                 health
  - GET /api/ideas            list ideas with optional filters
  - GET /api/ideas/filters    available filter facets
  - GET /api/ideas/{slug}     idea detail
  - GET /api/ideas/{slug}/related   related ideas

Auth endpoints (Emergent Google Auth):
  - POST /api/auth/session    exchange session_id -> session_token (sets cookie)
  - GET  /api/auth/me         current user (cookie OR Bearer)
  - POST /api/auth/logout     clear session

Gated endpoints (require auth):
  - POST /api/ideas/{slug}/save        toggle save
  - GET  /api/ideas/saved              list saved ideas
"""
from fastapi import FastAPI, APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
import logging
import httpx
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from ideas_data import IDEAS_SEED, get_all_sectors, get_all_execution_types, get_all_ideal_for

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="ValueWeave API")
api = APIRouter(prefix="/api")

logger = logging.getLogger("valueweave")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s :: %(message)s")

EMERGENT_AUTH_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class Idea(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    slug: str
    title: str
    short_description: str
    detailed_description: str
    sector: str
    tags: List[str] = []
    problem_solved: str
    target_customers: str
    beginner_friendly: bool
    execution_type: str
    remote_possible: bool
    minimum_investment: int
    medium_scale_investment: int
    advanced_scale_investment: int
    estimated_monthly_revenue_min: int
    estimated_monthly_revenue_max: int
    risk_level: str
    scalability_level: str
    suitable_district_types: List[str] = []
    district_demand_level: str
    competition_level: str
    growth_trend: str
    ai_proof_level: str
    automation_resistance_score: int
    ideal_team_size_min: int
    ideal_team_size_max: int
    team_roles_needed: List[str] = []
    skills_required: List[str] = []
    contribution_types_needed: List[str] = []
    ideal_for: List[str] = []
    eligible_government_schemes: List[str] = []
    licensing_complexity: str
    setup_difficulty: str
    featured: bool = False
    trending_score: int = 0
    save_count: int = 0
    team_interest_count: int = 0


class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None


class SessionExchange(BaseModel):
    session_id: str


# ---------------------------------------------------------------------------
# In-memory ideas (seed data + id assignment)
# ---------------------------------------------------------------------------
_IDEAS: List[Idea] = []
_IDEAS_BY_SLUG = {}


def _hydrate_ideas():
    global _IDEAS, _IDEAS_BY_SLUG
    _IDEAS = []
    _IDEAS_BY_SLUG = {}
    for raw in IDEAS_SEED:
        idea = Idea(id=f"idea_{raw['slug']}", **raw)
        _IDEAS.append(idea)
        _IDEAS_BY_SLUG[idea.slug] = idea


_hydrate_ideas()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
async def get_current_user(request: Request) -> Optional[User]:
    """Return User if valid session_token (cookie or Bearer), else None."""
    token = request.cookies.get("session_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
    if not token:
        return None

    session = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if not session:
        return None

    expires_at = session.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at and expires_at < datetime.now(timezone.utc):
        return None

    user_doc = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    if not user_doc:
        return None
    return User(**user_doc)


async def require_user(request: Request) -> User:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


# ---------------------------------------------------------------------------
# Public: health
# ---------------------------------------------------------------------------
@api.get("/")
async def root():
    return {"app": "ValueWeave", "status": "ok", "ideas_count": len(_IDEAS)}


# ---------------------------------------------------------------------------
# Public: ideas
# ---------------------------------------------------------------------------
@api.get("/ideas/filters")
async def ideas_filters():
    return {
        "sectors": get_all_sectors(),
        "execution_types": get_all_execution_types(),
        "ideal_for": get_all_ideal_for(),
        "investment_buckets": [
            {"key": "under_1l", "label": "Under ₹1L", "max": 100000},
            {"key": "1l_to_5l", "label": "₹1L – ₹5L", "min": 100000, "max": 500000},
            {"key": "5l_to_15l", "label": "₹5L – ₹15L", "min": 500000, "max": 1500000},
            {"key": "above_15l", "label": "Above ₹15L", "min": 1500000},
        ],
    }


@api.get("/ideas", response_model=List[Idea])
async def list_ideas(
    sector: Optional[str] = None,
    execution_type: Optional[str] = None,
    beginner_friendly: Optional[bool] = None,
    ideal_for: Optional[str] = None,
    investment_bucket: Optional[str] = None,
    q: Optional[str] = None,
    featured_only: bool = False,
    limit: int = 100,
):
    results = list(_IDEAS)
    if sector:
        results = [i for i in results if i.sector.lower() == sector.lower()]
    if execution_type:
        results = [i for i in results if i.execution_type.lower() == execution_type.lower()]
    if beginner_friendly is not None:
        results = [i for i in results if i.beginner_friendly == beginner_friendly]
    if ideal_for:
        results = [i for i in results if ideal_for in i.ideal_for]
    if featured_only:
        results = [i for i in results if i.featured]
    if investment_bucket:
        buckets = {
            "under_1l": (0, 100000),
            "1l_to_5l": (100000, 500000),
            "5l_to_15l": (500000, 1500000),
            "above_15l": (1500000, 10**9),
        }
        if investment_bucket in buckets:
            lo, hi = buckets[investment_bucket]
            results = [i for i in results if lo <= i.minimum_investment < hi]
    if q:
        ql = q.lower()
        results = [
            i for i in results
            if ql in i.title.lower()
            or ql in i.short_description.lower()
            or ql in i.sector.lower()
            or any(ql in t.lower() for t in i.tags)
        ]
    # Sort: featured first, then by trending_score
    results.sort(key=lambda i: (not i.featured, -i.trending_score))
    return results[:limit]


@api.get("/ideas/saved", response_model=List[Idea])
async def list_saved_ideas(request: Request):
    user = await require_user(request)
    saved = await db.idea_saves.find({"user_id": user.user_id}, {"_id": 0}).to_list(1000)
    slugs = {s["idea_slug"] for s in saved}
    return [i for i in _IDEAS if i.slug in slugs]


@api.get("/ideas/{slug}", response_model=Idea)
async def get_idea(slug: str):
    idea = _IDEAS_BY_SLUG.get(slug)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


@api.get("/ideas/{slug}/related", response_model=List[Idea])
async def related_ideas(slug: str, limit: int = 3):
    idea = _IDEAS_BY_SLUG.get(slug)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    candidates = [i for i in _IDEAS if i.slug != slug and i.sector == idea.sector]
    if len(candidates) < limit:
        extra = [
            i for i in _IDEAS
            if i.slug != slug and i.execution_type == idea.execution_type and i not in candidates
        ]
        candidates.extend(extra)
    candidates.sort(key=lambda i: -i.trending_score)
    return candidates[:limit]


@api.post("/ideas/{slug}/save")
async def toggle_save_idea(slug: str, request: Request):
    user = await require_user(request)
    if slug not in _IDEAS_BY_SLUG:
        raise HTTPException(status_code=404, detail="Idea not found")
    existing = await db.idea_saves.find_one({"user_id": user.user_id, "idea_slug": slug}, {"_id": 0})
    if existing:
        await db.idea_saves.delete_one({"user_id": user.user_id, "idea_slug": slug})
        return {"saved": False, "slug": slug}
    await db.idea_saves.insert_one({
        "user_id": user.user_id,
        "idea_slug": slug,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"saved": True, "slug": slug}


# ---------------------------------------------------------------------------
# Auth: Emergent Google
# ---------------------------------------------------------------------------
@api.post("/auth/session")
async def auth_session(payload: SessionExchange, response: Response):
    """Exchange session_id -> session_token, store user + session, set cookie."""
    async with httpx.AsyncClient(timeout=10.0) as h:
        r = await h.get(EMERGENT_AUTH_URL, headers={"X-Session-ID": payload.session_id})
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session_id")
    data = r.json()
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Auth provider returned no email")

    existing = await db.users.find_one({"email": email}, {"_id": 0})
    if existing:
        user_id = existing["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": data.get("name", existing.get("name", "")),
                       "picture": data.get("picture", existing.get("picture", ""))}}
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({
            "user_id": user_id,
            "email": email,
            "name": data.get("name", ""),
            "picture": data.get("picture", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    session_token = data.get("session_token") or uuid.uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )
    return {"user": User(**user_doc).model_dump(), "session_token": session_token}


@api.get("/auth/me")
async def auth_me(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@api.post("/auth/logout")
async def auth_logout(request: Request, response: Response):
    token = request.cookies.get("session_token") or ""
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
    if token:
        await db.user_sessions.delete_one({"session_token": token})
    response.delete_cookie("session_token", path="/")
    return {"ok": True}


# ---------------------------------------------------------------------------
# Wire-up
# ---------------------------------------------------------------------------
app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db():
    client.close()
