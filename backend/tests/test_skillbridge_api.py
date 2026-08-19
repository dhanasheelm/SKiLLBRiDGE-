import os
import uuid
import requests


def base_url():
    if not os.environ.get("REACT_APP_BACKEND_URL"):
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    os.environ["REACT_APP_BACKEND_URL"] = line.strip().split("=", 1)[1]
    return os.environ["REACT_APP_BACKEND_URL"].rstrip("/")


def test_health_database_connected():
    response = requests.get(f"{base_url()}/api/health", timeout=20)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_user_upsert_persists_profile():
    email = f"TEST_{uuid.uuid4().hex}@example.com"
    payload = {"email": email, "name": "TEST Demo", "role": "professional", "skills": ["Figma"], "goal": "Designer"}
    created = requests.post(f"{base_url()}/api/users", json=payload, timeout=20)
    assert created.status_code == 200
    assert created.json()["skills"] == ["Figma"]
    fetched = requests.get(f"{base_url()}/api/users/{email}", timeout=20)
    assert fetched.status_code == 200
    assert fetched.json()["goal"] == "Designer"


def test_application_persists_and_saved_toggle_round_trip():
    email = f"TEST_{uuid.uuid4().hex}@example.com"
    app_payload = {"email": email, "opportunity_id": "frontend-intern", "resume_name": "resume.pdf", "skills": ["React"], "cover_letter": "TEST cover"}
    created = requests.post(f"{base_url()}/api/applications", json=app_payload, timeout=20)
    assert created.status_code == 200
    assert created.json()["resume_name"] == "resume.pdf"
    listed = requests.get(f"{base_url()}/api/applications/{email}", timeout=20)
    assert listed.status_code == 200 and listed.json()[0]["cover_letter"] == "TEST cover"
    toggled = requests.post(f"{base_url()}/api/saved/toggle", json={"email": email, "opportunity_id": "frontend-intern"}, timeout=20)
    assert toggled.json()["saved"] is True
    assert "frontend-intern" in requests.get(f"{base_url()}/api/saved/{email}", timeout=20).json()
    removed = requests.post(f"{base_url()}/api/saved/toggle", json={"email": email, "opportunity_id": "frontend-intern"}, timeout=20)
    assert removed.json()["saved"] is False