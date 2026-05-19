from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid
import httpx
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
from datetime import datetime, timezone, timedelta


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

EMERGENT_AUTH_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
SESSION_DURATION_DAYS = 7


# ---------- Models ----------
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # profile fields
    city: Optional[str] = None
    bio: Optional[str] = None
    skills: List[str] = []
    interests: List[str] = []
    looking_for: Optional[str] = None  # one of intent slugs
    profile_complete: bool = False


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    looking_for: Optional[str] = None


class OpportunityCreate(BaseModel):
    title: str
    description: str
    category: str  # ai-tech, local-business, ev-electronics, drone, agri, student, trades, digital
    skills_needed: List[str] = []
    location: str
    collaboration_type: str  # cofounder, partner, team-member, freelance, mentor
    commitment: str  # full-time, part-time, project-based, casual


class Opportunity(OpportunityCreate):
    model_config = ConfigDict(extra="ignore")
    opportunity_id: str
    owner_id: str
    owner_name: str
    owner_picture: Optional[str] = None
    created_at: datetime


class ConnectionCreate(BaseModel):
    opportunity_id: str
    message: str


class Connection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    connection_id: str
    opportunity_id: str
    opportunity_title: str
    from_user_id: str
    from_user_name: str
    from_user_picture: Optional[str] = None
    to_user_id: str
    to_user_name: str
    message: str
    status: str  # pending, accepted, rejected
    created_at: datetime


# ---------- Auth Helpers ----------
async def get_current_user(request: Request) -> User:
    """Read session_token from cookie OR Authorization header, validate, return user."""
    token = request.cookies.get("session_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_doc = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")

    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")

    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    # parse datetime
    if isinstance(user_doc.get("created_at"), str):
        user_doc["created_at"] = datetime.fromisoformat(user_doc["created_at"])
    return User(**user_doc)


# ---------- Auth Routes ----------
@api_router.post("/auth/session")
async def auth_session(request: Request, response: Response):
    """Exchange session_id (from X-Session-ID header) for a session_token cookie."""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-ID header")

    async with httpx.AsyncClient(timeout=15.0) as http_client:
        resp = await http_client.get(
            EMERGENT_AUTH_URL,
            headers={"X-Session-ID": session_id},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session_id")
    data = resp.json()

    email = data["email"]
    name = data.get("name") or email.split("@")[0]
    picture = data.get("picture")
    session_token = data["session_token"]

    # upsert user
    existing = await db.users.find_one({"email": email}, {"_id": 0})
    now = datetime.now(timezone.utc)
    if existing:
        user_id = existing["user_id"]
        # refresh picture/name
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "picture": picture}},
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "created_at": now.isoformat(),
            "city": None,
            "bio": None,
            "skills": [],
            "interests": [],
            "looking_for": None,
            "profile_complete": False,
        })

    # save session
    expires_at = now + timedelta(days=SESSION_DURATION_DAYS)
    await db.user_sessions.insert_one({
        "session_token": session_token,
        "user_id": user_id,
        "expires_at": expires_at.isoformat(),
        "created_at": now.isoformat(),
    })

    # set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=SESSION_DURATION_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )

    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if isinstance(user_doc.get("created_at"), str):
        user_doc["created_at"] = datetime.fromisoformat(user_doc["created_at"])
    return {"user": User(**user_doc).model_dump(mode="json"), "session_token": session_token}


@api_router.get("/auth/me")
async def auth_me(user: User = Depends(get_current_user)):
    return user.model_dump(mode="json")


@api_router.post("/auth/logout")
async def auth_logout(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if token:
        await db.user_sessions.delete_one({"session_token": token})
    response.delete_cookie("session_token", path="/", samesite="none", secure=True)
    return {"ok": True}


# ---------- Profile Routes ----------
@api_router.put("/users/me")
async def update_me(update: ProfileUpdate, user: User = Depends(get_current_user)):
    patch = {k: v for k, v in update.model_dump().items() if v is not None}
    # mark complete when essential fields present
    merged = {**user.model_dump(), **patch}
    if merged.get("city") and merged.get("skills") and merged.get("looking_for"):
        patch["profile_complete"] = True
    await db.users.update_one({"user_id": user.user_id}, {"$set": patch})
    user_doc = await db.users.find_one({"user_id": user.user_id}, {"_id": 0})
    if isinstance(user_doc.get("created_at"), str):
        user_doc["created_at"] = datetime.fromisoformat(user_doc["created_at"])
    return User(**user_doc).model_dump(mode="json")


@api_router.get("/users/{user_id}")
async def get_user(user_id: str):
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    if isinstance(user_doc.get("created_at"), str):
        user_doc["created_at"] = datetime.fromisoformat(user_doc["created_at"])
    # add a fake email for the model
    user_doc["email"] = ""
    return User(**user_doc).model_dump(mode="json")


# ---------- Opportunities Routes ----------
@api_router.post("/opportunities")
async def create_opportunity(payload: OpportunityCreate, user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    opp_id = f"opp_{uuid.uuid4().hex[:12]}"
    doc = {
        "opportunity_id": opp_id,
        "owner_id": user.user_id,
        "owner_name": user.name,
        "owner_picture": user.picture,
        "created_at": now.isoformat(),
        **payload.model_dump(),
    }
    await db.opportunities.insert_one(doc)
    doc["created_at"] = now
    return Opportunity(**doc).model_dump(mode="json")


@api_router.get("/opportunities")
async def list_opportunities(
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    owner_id: Optional[str] = None,
    limit: int = Query(50, le=100),
):
    query = {}
    if category:
        query["category"] = category
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if owner_id:
        query["owner_id"] = owner_id
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"skills_needed": {"$regex": search, "$options": "i"}},
        ]
    cursor = db.opportunities.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    items = await cursor.to_list(limit)
    for it in items:
        if isinstance(it.get("created_at"), str):
            it["created_at"] = datetime.fromisoformat(it["created_at"])
    return [Opportunity(**it).model_dump(mode="json") for it in items]


@api_router.get("/opportunities/{opp_id}")
async def get_opportunity(opp_id: str):
    doc = await db.opportunities.find_one({"opportunity_id": opp_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if isinstance(doc.get("created_at"), str):
        doc["created_at"] = datetime.fromisoformat(doc["created_at"])
    return Opportunity(**doc).model_dump(mode="json")


@api_router.delete("/opportunities/{opp_id}")
async def delete_opportunity(opp_id: str, user: User = Depends(get_current_user)):
    doc = await db.opportunities.find_one({"opportunity_id": opp_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    if doc["owner_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await db.opportunities.delete_one({"opportunity_id": opp_id})
    await db.connections.delete_many({"opportunity_id": opp_id})
    return {"ok": True}


# ---------- Connections Routes ----------
@api_router.post("/opportunities/{opp_id}/connect")
async def create_connection(opp_id: str, payload: ConnectionCreate, user: User = Depends(get_current_user)):
    opp = await db.opportunities.find_one({"opportunity_id": opp_id}, {"_id": 0})
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if opp["owner_id"] == user.user_id:
        raise HTTPException(status_code=400, detail="Cannot connect to your own opportunity")
    # prevent duplicate
    existing = await db.connections.find_one({
        "opportunity_id": opp_id,
        "from_user_id": user.user_id,
    }, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Already requested")

    now = datetime.now(timezone.utc)
    conn_id = f"conn_{uuid.uuid4().hex[:12]}"
    doc = {
        "connection_id": conn_id,
        "opportunity_id": opp_id,
        "opportunity_title": opp["title"],
        "from_user_id": user.user_id,
        "from_user_name": user.name,
        "from_user_picture": user.picture,
        "to_user_id": opp["owner_id"],
        "to_user_name": opp["owner_name"],
        "message": payload.message,
        "status": "pending",
        "created_at": now.isoformat(),
    }
    await db.connections.insert_one(doc)
    doc["created_at"] = now
    return Connection(**doc).model_dump(mode="json")


@api_router.get("/connections/sent")
async def list_sent(user: User = Depends(get_current_user)):
    cursor = db.connections.find({"from_user_id": user.user_id}, {"_id": 0}).sort("created_at", -1)
    items = await cursor.to_list(200)
    for it in items:
        if isinstance(it.get("created_at"), str):
            it["created_at"] = datetime.fromisoformat(it["created_at"])
    return [Connection(**it).model_dump(mode="json") for it in items]


@api_router.get("/connections/received")
async def list_received(user: User = Depends(get_current_user)):
    cursor = db.connections.find({"to_user_id": user.user_id}, {"_id": 0}).sort("created_at", -1)
    items = await cursor.to_list(200)
    for it in items:
        if isinstance(it.get("created_at"), str):
            it["created_at"] = datetime.fromisoformat(it["created_at"])
    return [Connection(**it).model_dump(mode="json") for it in items]


@api_router.put("/connections/{conn_id}")
async def update_connection(conn_id: str, status: str, user: User = Depends(get_current_user)):
    if status not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid status")
    conn = await db.connections.find_one({"connection_id": conn_id}, {"_id": 0})
    if not conn:
        raise HTTPException(status_code=404, detail="Not found")
    if conn["to_user_id"] != user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await db.connections.update_one({"connection_id": conn_id}, {"$set": {"status": status}})
    conn["status"] = status
    if isinstance(conn.get("created_at"), str):
        conn["created_at"] = datetime.fromisoformat(conn["created_at"])
    return Connection(**conn).model_dump(mode="json")


# ---------- Root ----------
@api_router.get("/")
async def root():
    return {"message": "ValueWeave API", "status": "ok"}


# ---------- Mount ----------
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
