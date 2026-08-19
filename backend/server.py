from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import os
import uuid

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")
mongo_url = os.getenv("MONGO_URL")
db_name = os.getenv("DB_NAME")
if not mongo_url or not db_name:
    raise RuntimeError(
        "Missing database configuration. Set MONGO_URL and DB_NAME in backend/.env "
        "(see backend/.env.example)."
    )
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]
app = FastAPI(title="SKILLBRIDGE API")
api = APIRouter(prefix="/api")


class UserPayload(BaseModel):
    email: str
    name: str
    role: str = "student"
    profile: Dict[str, Any] = Field(default_factory=dict)
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    goal: str = ""


class ApplicationPayload(BaseModel):
    email: str
    opportunity_id: str
    resume_name: str = ""
    skills: List[str] = Field(default_factory=list)
    cover_letter: str = ""
    status: str = "Applied"


class SavePayload(BaseModel):
    email: str
    opportunity_id: str


def clean(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not doc:
        return doc
    doc.pop("_id", None)
    return doc


@api.get("/")
async def root():
    return {"service": "skillbridge", "status": "ok"}


@api.get("/health")
async def health():
    await db.command("ping")
    return {"status": "ok", "database": "connected"}


@api.post("/users", response_model=Dict[str, Any])
async def upsert_user(payload: UserPayload):
    doc = payload.model_dump()
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"email": payload.email}, {"$set": doc, "$setOnInsert": {"id": str(uuid.uuid4())}}, upsert=True)
    return clean(await db.users.find_one({"email": payload.email}, {"_id": 0}))


@api.get("/users/{email}", response_model=Dict[str, Any])
async def get_user(email: str):
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(404, "User not found")
    return user


@api.post("/applications", response_model=Dict[str, Any])
async def create_application(payload: ApplicationPayload):
    doc = payload.model_dump()
    doc.update({"id": str(uuid.uuid4()), "applied_at": datetime.now(timezone.utc).isoformat()})
    await db.applications.update_one({"email": payload.email, "opportunity_id": payload.opportunity_id}, {"$set": doc}, upsert=True)
    return clean(await db.applications.find_one({"email": payload.email, "opportunity_id": payload.opportunity_id}, {"_id": 0}))


@api.get("/applications/{email}", response_model=List[Dict[str, Any]])
async def list_applications(email: str):
    return await db.applications.find({"email": email}, {"_id": 0}).sort("applied_at", -1).to_list(100)


@api.post("/saved/toggle", response_model=Dict[str, Any])
async def toggle_saved(payload: SavePayload):
    existing = await db.saved.find_one({"email": payload.email, "opportunity_id": payload.opportunity_id}, {"_id": 0})
    if existing:
        await db.saved.delete_one({"email": payload.email, "opportunity_id": payload.opportunity_id})
        return {"saved": False, "opportunity_id": payload.opportunity_id}
    await db.saved.insert_one({**payload.model_dump(), "saved_at": datetime.now(timezone.utc).isoformat()})
    return {"saved": True, "opportunity_id": payload.opportunity_id}


@api.get("/saved/{email}", response_model=List[str])
async def list_saved(email: str):
    docs = await db.saved.find({"email": email}, {"_id": 0, "opportunity_id": 1}).to_list(100)
    return [doc["opportunity_id"] for doc in docs]


@api.get("/notifications/{email}", response_model=List[Dict[str, Any]])
async def notifications(email: str):
    docs = await db.notifications.find({"email": email}, {"_id": 0}).sort("created_at", -1).to_list(100)
    if docs:
        return docs
    seed = [{"id": str(uuid.uuid4()), "email": email, "message": "Your profile is 90% complete", "read": False, "created_at": datetime.now(timezone.utc).isoformat()}]
    await db.notifications.insert_many(seed)
    return seed


@api.post("/notifications/{email}/read")
async def mark_notifications_read(email: str):
    await db.notifications.update_many({"email": email}, {"$set": {"read": True}})
    return {"updated": True}


app.include_router(api)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","), allow_methods=["*"], allow_headers=["*"])
logging.basicConfig(level=logging.INFO)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
