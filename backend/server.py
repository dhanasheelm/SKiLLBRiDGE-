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
client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]
app = FastAPI(title="SKILLBRIDGE API")
api = APIRouter(prefix="/api")


SEED_OPPORTUNITIES: List[Dict[str, Any]] = [
    {"id": "frontend-intern", "title": "Frontend Developer Intern", "org": "TechNova", "type": "Internship", "location": "Remote", "mode": "Remote", "skills": ["React", "JavaScript", "UI/UX"], "deadline": "25 Aug 2026", "base_score": 94, "color": "violet", "description": "Join a product team building the next generation of collaborative tools. Ship thoughtful interfaces with experienced mentors."},
    {"id": "ai-research", "title": "AI / ML Research Intern", "org": "Nexa Labs", "type": "Research", "location": "Pune, India", "mode": "Hybrid", "skills": ["Python", "Machine Learning"], "deadline": "31 Aug 2026", "base_score": 76, "color": "cyan", "description": "Explore applied machine learning research and turn experiments into useful product intelligence."},
    {"id": "fullstack", "title": "Full Stack Developer", "org": "Orbit Systems", "type": "Full-time", "location": "Bengaluru, India", "mode": "On-site", "skills": ["React", "Node.js", "Cloud"], "deadline": "12 Sep 2026", "base_score": 82, "color": "blue", "description": "Build reliable, elegant software for teams that care about craft, speed, and customer impact."},
    {"id": "design", "title": "UI/UX Design Internship", "org": "Morrow Studio", "type": "Internship", "location": "Remote", "mode": "Remote", "skills": ["Figma", "UI/UX"], "deadline": "04 Sep 2026", "base_score": 71, "color": "pink", "description": "Shape clear, expressive experiences across a growing family of products."},
    {"id": "cyber", "title": "Cybersecurity Intern", "org": "SecureGrid", "type": "Internship", "location": "Hyderabad, India", "mode": "Hybrid", "skills": ["Python", "Cloud"], "deadline": "18 Sep 2026", "base_score": 68, "color": "amber", "description": "Help teams build safer systems through practical security research and automation."},
    {"id": "freelance", "title": "React Developer Freelance Project", "org": "Pollen Commerce", "type": "Freelance", "location": "Remote", "mode": "Remote", "skills": ["React", "TypeScript"], "deadline": "29 Aug 2026", "base_score": 88, "color": "green", "description": "Create an inviting storefront experience for an independent marketplace with a global audience."},
    {"id": "robotics", "title": "Robotics Research Project", "org": "Axiom Robotics", "type": "Project", "location": "Chennai, India", "mode": "On-site", "skills": ["Python", "IoT"], "deadline": "22 Sep 2026", "base_score": 62, "color": "orange", "description": "Collaborate with a curious research group exploring perception and motion."},
    {"id": "startup", "title": "Startup Product Intern", "org": "Goodfolk", "type": "Startup", "location": "Remote", "mode": "Remote", "skills": ["Communication", "UI/UX"], "deadline": "15 Sep 2026", "base_score": 79, "color": "lime", "description": "Work closely with founders to bring new ideas from first sketch to first customer."},
    {"id": "data-analyst", "title": "Data Analyst Intern", "org": "Beacon Metrics", "type": "Internship", "location": "Remote", "mode": "Remote", "skills": ["Python", "Data Science", "Communication"], "deadline": "27 Aug 2026", "base_score": 74, "color": "cyan", "description": "Turn messy datasets into decisions the whole team can rally around."},
    {"id": "devops", "title": "DevOps Engineer (Contract)", "org": "Kite Cloud", "type": "Contract", "location": "Remote", "mode": "Remote", "skills": ["Cloud", "DevOps", "Node.js"], "deadline": "10 Sep 2026", "base_score": 80, "color": "blue", "description": "Automate deploys and observability for a fast-moving developer platform."},
]


def _match_score(user_skills: List[str], opp_skills: List[str], base: int) -> int:
    if not opp_skills:
        return base
    u = {s.strip().lower() for s in user_skills or []}
    o = [s.strip().lower() for s in opp_skills]
    overlap = sum(1 for s in o if s in u)
    ratio = overlap / len(o)
    boost = round(ratio * 40)
    return max(38, min(99, base - 20 + boost + (10 if overlap >= 2 else 0)))


class UserPayload(BaseModel):
    email: str
    name: str
    role: str = "student"
    profile: Dict[str, Any] = Field(default_factory=dict)
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    goal: str = ""
    college: str = ""
    degree: str = ""
    location: str = ""


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


@app.on_event("startup")
async def seed_opportunities():
    for op in SEED_OPPORTUNITIES:
        await db.opportunities.update_one({"id": op["id"]}, {"$set": op}, upsert=True)


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


@api.get("/opportunities", response_model=List[Dict[str, Any]])
async def list_opportunities(email: Optional[str] = None):
    docs = await db.opportunities.find({}, {"_id": 0}).to_list(200)
    user_skills: List[str] = []
    if email:
        u = await db.users.find_one({"email": email}, {"_id": 0, "skills": 1})
        if u:
            user_skills = u.get("skills", [])
    for d in docs:
        d["score"] = _match_score(user_skills, d.get("skills", []), d.get("base_score", 70))
    docs.sort(key=lambda x: x["score"], reverse=True)
    return docs


@api.get("/opportunities/{opp_id}", response_model=Dict[str, Any])
async def get_opportunity(opp_id: str, email: Optional[str] = None):
    doc = await db.opportunities.find_one({"id": opp_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Opportunity not found")
    user_skills: List[str] = []
    if email:
        u = await db.users.find_one({"email": email}, {"_id": 0, "skills": 1})
        if u:
            user_skills = u.get("skills", [])
    doc["score"] = _match_score(user_skills, doc.get("skills", []), doc.get("base_score", 70))
    return doc


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
