from supabase import create_client, Client
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio
from copy import deepcopy
import logging
import os
import secrets
import uuid

import requests
import resend
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, File, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel, EmailStr, Field
from starlette.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_URL, SUPABASE_KEY and SUPABASE_SERVICE_KEY are required"
    )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

supabase_admin: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)

app = FastAPI(title="SKILLBRIDGE API")
api = APIRouter(prefix="/api")
logger = logging.getLogger("skillbridge")


def _matches(document: Dict[str, Any], query: Dict[str, Any]) -> bool:
    """Match the small subset of query operators this API uses."""
    for key, expected in query.items():
        actual = document.get(key)
        if isinstance(expected, dict) and "$ne" in expected:
            if actual == expected["$ne"]:
                return False
        elif actual != expected:
            return False
    return True


def _project(document: Dict[str, Any], projection: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    result = deepcopy(document)
    if not projection:
        return result
    included = [key for key, value in projection.items() if value and key != "_id"]
    if included:
        return {key: result[key] for key in included if key in result}
    for key, value in projection.items():
        if not value:
            result.pop(key, None)
    return result


class MemoryCursor:
    def __init__(self, documents: List[Dict[str, Any]]):
        self.documents = documents

    def sort(self, field: str, direction: int):
        self.documents.sort(key=lambda item: item.get(field, ""), reverse=direction < 0)
        return self

    async def to_list(self, length: int) -> List[Dict[str, Any]]:
        return self.documents[:length]


class MemoryCollection:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []

    async def find_one(self, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None):
        for document in self.documents:
            if _matches(document, query):
                return _project(document, projection)
        return None

    def find(self, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> MemoryCursor:
        return MemoryCursor([_project(document, projection) for document in self.documents if _matches(document, query)])

    async def insert_one(self, document: Dict[str, Any]):
        self.documents.append(deepcopy(document))

    async def insert_many(self, documents: List[Dict[str, Any]]):
        self.documents.extend(deepcopy(documents))

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        for document in self.documents:
            if _matches(document, query):
                document.update(deepcopy(update.get("$set", {})))
                return
        if upsert:
            document = deepcopy(query)
            document.update(deepcopy(update.get("$setOnInsert", {})))
            document.update(deepcopy(update.get("$set", {})))
            self.documents.append(document)

    async def update_many(self, query: Dict[str, Any], update: Dict[str, Any]):
        for document in self.documents:
            if _matches(document, query):
                document.update(deepcopy(update.get("$set", {})))

    async def delete_one(self, query: Dict[str, Any]):
        for index, document in enumerate(self.documents):
            if _matches(document, query):
                self.documents.pop(index)
                return type("DeleteResult", (), {"deleted_count": 1})()
        return type("DeleteResult", (), {"deleted_count": 0})()

    async def count_documents(self, query: Dict[str, Any]) -> int:
        return sum(_matches(document, query) for document in self.documents)


class MemoryDatabase:
    """Ephemeral local storage used when no external database is configured."""
    def __init__(self):
        self.collections: Dict[str, MemoryCollection] = {}

    def __getattr__(self, name: str) -> MemoryCollection:
        return self.collections.setdefault(name, MemoryCollection())


db = MemoryDatabase()

resend.api_key = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
APP_NAME = os.environ.get("APP_NAME", "skillbridge")
APP_URL = os.environ.get("APP_URL", "http://localhost:3000")
STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
storage_key: Optional[str] = None

MIME = {"pdf": "application/pdf", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}


def init_storage(force: bool = False) -> str:
    global storage_key
    if storage_key and not force:
        return storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    return storage_key


def put_object(path: str, data: bytes, content_type: str) -> Dict[str, Any]:
    key = init_storage()
    r = requests.put(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key, "Content-Type": content_type}, data=data, timeout=120)
    if r.status_code == 404:
        key = init_storage(force=True)
        r = requests.put(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key, "Content-Type": content_type}, data=data, timeout=120)
    r.raise_for_status()
    return r.json()


def get_object(path: str):
    key = init_storage()
    r = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    if r.status_code == 404:
        key = init_storage(force=True)
        r = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    r.raise_for_status()
    return r.content, r.headers.get("Content-Type", "application/octet-stream")


SEED_OPPORTUNITIES: List[Dict[str, Any]] = [
    {"id": "frontend-intern", "title": "Frontend Developer Intern", "org": "TechNova", "type": "Internship", "location": "Remote", "mode": "Remote", "skills": ["React", "JavaScript", "UI/UX"], "deadline": "25 Aug 2026", "base_score": 94, "color": "violet", "owner_email": "maya@demo.com", "description": "Join a product team building the next generation of collaborative tools. Ship thoughtful interfaces with experienced mentors."},
    {"id": "ai-research", "title": "AI / ML Research Intern", "org": "Nexa Labs", "type": "Research", "location": "Pune, India", "mode": "Hybrid", "skills": ["Python", "Machine Learning"], "deadline": "31 Aug 2026", "base_score": 76, "color": "cyan", "owner_email": "maya@demo.com", "description": "Explore applied machine learning research and turn experiments into useful product intelligence."},
    {"id": "fullstack", "title": "Full Stack Developer", "org": "Orbit Systems", "type": "Full-time", "location": "Bengaluru, India", "mode": "On-site", "skills": ["React", "Node.js", "Cloud"], "deadline": "12 Sep 2026", "base_score": 82, "color": "blue", "owner_email": "maya@demo.com", "description": "Build reliable, elegant software for teams that care about craft, speed, and customer impact."},
    {"id": "design", "title": "UI/UX Design Internship", "org": "Morrow Studio", "type": "Internship", "location": "Remote", "mode": "Remote", "skills": ["Figma", "UI/UX"], "deadline": "04 Sep 2026", "base_score": 71, "color": "pink", "owner_email": "maya@demo.com", "description": "Shape clear, expressive experiences across a growing family of products."},
    {"id": "cyber", "title": "Cybersecurity Intern", "org": "SecureGrid", "type": "Internship", "location": "Hyderabad, India", "mode": "Hybrid", "skills": ["Python", "Cloud"], "deadline": "18 Sep 2026", "base_score": 68, "color": "amber", "owner_email": "founders@securegrid.demo", "description": "Help teams build safer systems through practical security research and automation."},
    {"id": "freelance", "title": "React Developer Freelance Project", "org": "Pollen Commerce", "type": "Freelance", "location": "Remote", "mode": "Remote", "skills": ["React", "TypeScript"], "deadline": "29 Aug 2026", "base_score": 88, "color": "green", "owner_email": "maya@demo.com", "description": "Create an inviting storefront experience for an independent marketplace with a global audience."},
    {"id": "robotics", "title": "Robotics Research Project", "org": "Axiom Robotics", "type": "Project", "location": "Chennai, India", "mode": "On-site", "skills": ["Python", "IoT"], "deadline": "22 Sep 2026", "base_score": 62, "color": "orange", "owner_email": "founders@axiom.demo", "description": "Collaborate with a curious research group exploring perception and motion."},
    {"id": "startup", "title": "Startup Product Intern", "org": "Goodfolk", "type": "Startup", "location": "Remote", "mode": "Remote", "skills": ["Communication", "UI/UX"], "deadline": "15 Sep 2026", "base_score": 79, "color": "lime", "owner_email": "maya@demo.com", "description": "Work closely with founders to bring new ideas from first sketch to first customer."},
    {"id": "data-analyst", "title": "Data Analyst Intern", "org": "Beacon Metrics", "type": "Internship", "location": "Remote", "mode": "Remote", "skills": ["Python", "Data Science", "Communication"], "deadline": "27 Aug 2026", "base_score": 74, "color": "cyan", "owner_email": "founders@beacon.demo", "description": "Turn messy datasets into decisions the whole team can rally around."},
    {"id": "devops", "title": "DevOps Engineer (Contract)", "org": "Kite Cloud", "type": "Contract", "location": "Remote", "mode": "Remote", "skills": ["Cloud", "DevOps", "Node.js"], "deadline": "10 Sep 2026", "base_score": 80, "color": "blue", "owner_email": "maya@demo.com", "description": "Automate deploys and observability for a fast-moving developer platform."},
]

APP_STATUSES = ["Applied", "Under Review", "Shortlisted", "Interview", "Selected", "Rejected"]


def _match_score(user_skills: List[str], opp_skills: List[str], base: int) -> int:
    if not opp_skills:
        return base
    u = {s.strip().lower() for s in user_skills or []}
    o = [s.strip().lower() for s in opp_skills]
    overlap = sum(1 for s in o if s in u)
    ratio = overlap / len(o)
    boost = round(ratio * 40)
    return max(38, min(99, base - 20 + boost + (10 if overlap >= 2 else 0)))


def clean(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not doc:
        return doc
    doc.pop("_id", None)
    return doc


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
    portfolio_url: str = ""
    portfolio_name: str = ""


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


class ForgotPayload(BaseModel):
    email: EmailStr


class StatusUpdatePayload(BaseModel):
    status: str
    owner_email: str


class OpportunityPayload(BaseModel):
    title: str
    org: str
    type: str = "Internship"
    location: str = "Remote"
    mode: str = "Remote"
    duration: str = "3 months"
    stipend: str = "Unpaid / discuss"
    openings: int = 1
    deadline: str
    skills: List[str] = Field(default_factory=list)
    description: str
    eligibility: str = "Open to all motivated applicants"
    application_type: str = "SkillBridge application"
    external_url: str = ""
    owner_email: str
    status: str = "Active"
    verified: bool = False


@app.on_event("startup")
async def on_start():
    for op in SEED_OPPORTUNITIES:
        await db.opportunities.update_one({"id": op["id"]}, {"$set": op}, upsert=True)
    try:
        init_storage()
        logger.info("Object storage initialized")
    except Exception as exc:
        logger.warning("Object storage init failed: %s", exc)


@api.get("/")
async def root():
    return {"service": "skillbridge", "status": "ok"}


@api.get("/health")
async def health():
    return {"status": "ok", "database": "supabase"}


@api.post("/users", response_model=Dict[str, Any])
async def upsert_user(payload: UserPayload):
    try:
        auth_users = await asyncio.to_thread(
            supabase_admin.auth.admin.list_users
        )

        auth_user = next(
            (
                user
                for user in auth_users
                if user.email
                and user.email.lower() == payload.email.lower()
            ),
            None
        )

        if not auth_user:
            raise HTTPException(
                status_code=404,
                detail="Supabase Auth user not found. Please sign up first."
            )

        doc = payload.model_dump()
        doc["id"] = auth_user.id
        doc["updated_at"] = datetime.now(timezone.utc).isoformat()

        result = await asyncio.to_thread(
            lambda: supabase_admin
                .table("profiles")
                .upsert(doc, on_conflict="id")
                .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to save profile"
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Supabase profile upsert failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to save user profile"
        )


@api.get("/users/{email}", response_model=Dict[str, Any])
async def get_user(email: str):
    try:
        result = await asyncio.to_thread(
            lambda: supabase_admin
                .table("profiles")
                .select("*")
                .eq("email", email)
                .limit(1)
                .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Supabase profile fetch failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch user profile"
        )

@api.get("/opportunities", response_model=List[Dict[str, Any]])
async def list_opportunities(email: Optional[str] = None):
    docs = await db.opportunities.find({"status": {"$ne": "Paused"}}, {"_id": 0}).to_list(200)
    user_skills: List[str] = []
    if email:
        u = await db.users.find_one({"email": email}, {"_id": 0, "skills": 1})
        if u:
            user_skills = u.get("skills", [])
    for d in docs:
        d["score"] = _match_score(user_skills, d.get("skills", []), d.get("base_score", 70))
    docs.sort(key=lambda x: x["score"], reverse=True)
    return docs


@api.get("/opportunities/mine/{owner_email}", response_model=List[Dict[str, Any]])
async def list_my_opportunities(owner_email: str):
    docs = await db.opportunities.find({"owner_email": owner_email}, {"_id": 0}).to_list(200)
    for d in docs:
        d["applicant_count"] = await db.applications.count_documents({"opportunity_id": d["id"]})
    return docs


@api.post("/opportunities", response_model=Dict[str, Any])
async def create_opportunity(payload: OpportunityPayload):
    doc = payload.model_dump()
    doc.update({"id": f"opp-{uuid.uuid4().hex[:10]}", "base_score": 70, "color": "violet", "created_at": datetime.now(timezone.utc).isoformat()})
    await db.opportunities.insert_one(doc)
    return clean(doc)


@api.patch("/opportunities/{opp_id}", response_model=Dict[str, Any])
async def update_opportunity(opp_id: str, payload: OpportunityPayload):
    current = await db.opportunities.find_one({"id": opp_id, "owner_email": payload.owner_email}, {"_id": 0})
    if not current:
        raise HTTPException(403, "Not the owner of this opportunity")
    doc = payload.model_dump()
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.opportunities.update_one({"id": opp_id}, {"$set": doc})
    return clean(await db.opportunities.find_one({"id": opp_id}, {"_id": 0}))


@api.post("/opportunities/{opp_id}/duplicate", response_model=Dict[str, Any])
async def duplicate_opportunity(opp_id: str, owner_email: str = Query(...)):
    source = await db.opportunities.find_one({"id": opp_id, "owner_email": owner_email}, {"_id": 0})
    if not source:
        raise HTTPException(403, "Not the owner of this opportunity")
    source.update({"id": f"opp-{uuid.uuid4().hex[:10]}", "title": f"Copy of {source['title']}", "status": "Draft", "created_at": datetime.now(timezone.utc).isoformat()})
    await db.opportunities.insert_one(source)
    return clean(source)


@api.delete("/opportunities/{opp_id}")
async def delete_opportunity(opp_id: str, owner_email: str = Query(...)):
    result = await db.opportunities.delete_one({"id": opp_id, "owner_email": owner_email})
    if not result.deleted_count:
        raise HTTPException(403, "Not the owner of this opportunity")
    return {"deleted": True}


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


@api.get("/opportunities/{opp_id}/applicants", response_model=List[Dict[str, Any]])
async def list_applicants(opp_id: str, owner_email: str = Query(...)):
    opp = await db.opportunities.find_one({"id": opp_id, "owner_email": owner_email}, {"_id": 0})
    if not opp:
        raise HTTPException(403, "Not the owner of this opportunity")
    apps = await db.applications.find({"opportunity_id": opp_id}, {"_id": 0}).sort("applied_at", -1).to_list(200)
    for a in apps:
        u = await db.users.find_one({"email": a["email"]}, {"_id": 0, "name": 1, "skills": 1, "location": 1, "goal": 1, "portfolio_url": 1, "portfolio_name": 1, "college": 1})
        a["applicant"] = u or {"name": a["email"].split("@")[0], "skills": [], "location": ""}
        a["match_score"] = _match_score(a["applicant"].get("skills", []), opp.get("skills", []), opp.get("base_score", 70))
    return apps


@api.post("/applications", response_model=Dict[str, Any])
async def create_application(payload: ApplicationPayload):
    doc = payload.model_dump()
    doc.update({"id": str(uuid.uuid4()), "applied_at": datetime.now(timezone.utc).isoformat()})
    await db.applications.update_one({"email": payload.email, "opportunity_id": payload.opportunity_id}, {"$set": doc}, upsert=True)
    return clean(await db.applications.find_one({"email": payload.email, "opportunity_id": payload.opportunity_id}, {"_id": 0}))


@api.patch("/applications/{app_id}/status", response_model=Dict[str, Any])
async def update_application_status(app_id: str, payload: StatusUpdatePayload):
    if payload.status not in APP_STATUSES:
        raise HTTPException(400, f"Status must be one of {APP_STATUSES}")
    app_doc = await db.applications.find_one({"id": app_id}, {"_id": 0})
    if not app_doc:
        raise HTTPException(404, "Application not found")
    opp = await db.opportunities.find_one({"id": app_doc["opportunity_id"], "owner_email": payload.owner_email}, {"_id": 0})
    if not opp:
        raise HTTPException(403, "Not the owner of this opportunity")
    await db.applications.update_one({"id": app_id}, {"$set": {"status": payload.status, "updated_at": datetime.now(timezone.utc).isoformat()}})
    await db.notifications.insert_one({"id": str(uuid.uuid4()), "email": app_doc["email"], "message": f"Your application for {opp['title']} is now {payload.status}", "type": "status", "read": False, "created_at": datetime.now(timezone.utc).isoformat()})
    return clean(await db.applications.find_one({"id": app_id}, {"_id": 0}))


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
    seed = [
        {"id": str(uuid.uuid4()), "email": email, "message": "Your profile is 90% complete", "type": "profile", "read": False, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "email": email, "message": "You have new opportunity matches to review", "type": "match", "read": False, "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    await db.notifications.insert_many([dict(s) for s in seed])
    return await db.notifications.find({"email": email}, {"_id": 0}).sort("created_at", -1).to_list(100)


@api.post("/notifications/{email}/read")
async def mark_notifications_read(email: str):
    await db.notifications.update_many({"email": email}, {"$set": {"read": True}})
    return {"updated": True}


@api.post("/auth/forgot")
async def forgot_password(payload: ForgotPayload):
    token = secrets.token_urlsafe(24)
    await db.password_resets.insert_one({"email": payload.email, "token": token, "created_at": datetime.now(timezone.utc).isoformat()})
    reset_link = f"{APP_URL}/reset-password?token={token}"
    html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#0b0d16;padding:36px 0;font-family:Arial,sans-serif;">
      <tr><td align="center">
        <table width="480" cellpadding="0" cellspacing="0" style="background:#141a2b;border:1px solid #2a3350;padding:32px;">
          <tr><td style="color:#66e4ee;font-size:11px;letter-spacing:2px;padding-bottom:10px;">SKILLBRIDGE · RESET LINK</td></tr>
          <tr><td style="color:#f6f7fb;font-size:22px;padding-bottom:12px;">Reset your SKILLBRIDGE password</td></tr>
          <tr><td style="color:#9299ad;font-size:14px;line-height:1.6;padding-bottom:22px;">We received a request to reset the password on this account. Use the button below within 15 minutes to choose a new one. If you didn’t request this, ignore this email.</td></tr>
          <tr><td align="left" style="padding-bottom:24px;"><a href="{reset_link}" style="background:#66e4ee;color:#080a12;padding:12px 18px;font-weight:700;text-decoration:none;">Reset password →</a></td></tr>
          <tr><td style="color:#5b6280;font-size:11px;">Or paste this link: <br /><span style="color:#9a7aff;word-break:break-all;">{reset_link}</span></td></tr>
        </table>
      </td></tr>
    </table>
    """
    if not resend.api_key:
        return {"sent": False, "reason": "Email service not configured", "reset_link": reset_link}
    try:
        result = await asyncio.to_thread(resend.Emails.send, {"from": SENDER_EMAIL, "to": [payload.email], "subject": "Reset your SKILLBRIDGE password", "html": html})
        return {"sent": True, "email_id": result.get("id"), "recipient": payload.email}
    except Exception as e:
        logger.error("Resend failure: %s", e)
        return {"sent": False, "reason": str(e), "reset_link": reset_link}


@api.post("/portfolio/upload", response_model=Dict[str, Any])
async def upload_portfolio(email: str = Query(...), file: UploadFile = File(...)):
    ext = (file.filename or "file").split(".")[-1].lower() if "." in (file.filename or "") else "bin"
    if ext not in MIME:
        raise HTTPException(400, f"Unsupported file type .{ext}. Allowed: pdf, png, jpg, jpeg, webp")
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(413, "File must be smaller than 10 MB")
    path = f"{APP_NAME}/portfolios/{email}/{uuid.uuid4()}.{ext}"
    try:
        result = put_object(path, data, MIME[ext])
    except Exception as e:
        logger.error("Storage upload failed: %s", e)
        raise HTTPException(503, "Storage unavailable")
    stored = {"id": str(uuid.uuid4()), "email": email, "storage_path": result["path"], "original_filename": file.filename, "content_type": MIME[ext], "size": result.get("size", len(data)), "is_deleted": False, "created_at": datetime.now(timezone.utc).isoformat()}
    await db.portfolio_files.insert_one(dict(stored))
    portfolio_url = f"/api/portfolio/file/{result['path']}"
    await db.users.update_one({"email": email}, {"$set": {"portfolio_url": portfolio_url, "portfolio_name": file.filename}})
    stored.pop("_id", None)
    return {"portfolio_url": portfolio_url, "portfolio_name": file.filename, "size": stored["size"], "content_type": stored["content_type"]}


@api.get("/portfolio/file/{path:path}")
async def get_portfolio(path: str):
    record = await db.portfolio_files.find_one({"storage_path": path, "is_deleted": False}, {"_id": 0})
    if not record:
        raise HTTPException(404, "Portfolio file not found")
    data, ct = get_object(path)
    return Response(content=data, media_type=record.get("content_type", ct))


app.include_router(api)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","), allow_methods=["*"], allow_headers=["*"])
logging.basicConfig(level=logging.INFO)
