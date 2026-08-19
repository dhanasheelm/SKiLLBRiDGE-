"""Backend tests for dynamic opportunities & personalised scoring (iteration 4)."""
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


BASE = base_url()


# GET /api/opportunities returns >=10 seeded opps with required fields
def test_opportunities_list_returns_seeded_data():
    r = requests.get(f"{BASE}/api/opportunities", timeout=20)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) >= 10
    required = {"id", "title", "org", "skills", "base_score"}
    for opp in data:
        missing = required - set(opp.keys())
        assert not missing, f"Opportunity {opp.get('id')} missing {missing}"
        assert isinstance(opp["skills"], list)
        assert "score" in opp  # score is always injected


# GET single opportunity
def test_single_opportunity_returns_object():
    r = requests.get(f"{BASE}/api/opportunities/frontend-intern", timeout=20)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "frontend-intern"
    assert data["org"] == "TechNova"
    assert "score" in data


def test_single_opportunity_not_found():
    r = requests.get(f"{BASE}/api/opportunities/does-not-exist", timeout=20)
    assert r.status_code == 404


# Personalised score changes based on user skills (deterministic)
def test_personalised_score_reflects_user_skills():
    # user1 has React,JavaScript,UI/UX -> frontend-intern should score high
    email1 = f"TEST_{uuid.uuid4().hex}@example.com"
    requests.post(f"{BASE}/api/users", json={"email": email1, "name": "TEST U1", "skills": ["React", "JavaScript", "UI/UX"]}, timeout=20)
    r1 = requests.get(f"{BASE}/api/opportunities/frontend-intern?email={email1}", timeout=20).json()

    # user2 with unrelated skills should score lower
    email2 = f"TEST_{uuid.uuid4().hex}@example.com"
    requests.post(f"{BASE}/api/users", json={"email": email2, "name": "TEST U2", "skills": ["Cybersecurity"]}, timeout=20)
    r2 = requests.get(f"{BASE}/api/opportunities/frontend-intern?email={email2}", timeout=20).json()

    assert r1["score"] > r2["score"], f"expected personalised score bump: {r1['score']} vs {r2['score']}"

    # determinism — call again
    r1b = requests.get(f"{BASE}/api/opportunities/frontend-intern?email={email1}", timeout=20).json()
    assert r1["score"] == r1b["score"]


# updating user skills reflects in subsequent opportunity list
def test_updating_skills_changes_scores():
    email = f"TEST_{uuid.uuid4().hex}@example.com"
    requests.post(f"{BASE}/api/users", json={"email": email, "name": "TEST U3", "skills": []}, timeout=20)
    before = requests.get(f"{BASE}/api/opportunities?email={email}", timeout=20).json()
    frontend_before = next(o for o in before if o["id"] == "frontend-intern")["score"]

    requests.post(f"{BASE}/api/users", json={"email": email, "name": "TEST U3", "skills": ["React", "JavaScript", "UI/UX"]}, timeout=20)
    after = requests.get(f"{BASE}/api/opportunities?email={email}", timeout=20).json()
    frontend_after = next(o for o in after if o["id"] == "frontend-intern")["score"]

    assert frontend_after > frontend_before


# Sorted by score descending
def test_opportunities_sorted_by_score_desc():
    r = requests.get(f"{BASE}/api/opportunities", timeout=20).json()
    scores = [o["score"] for o in r]
    assert scores == sorted(scores, reverse=True)
