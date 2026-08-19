"""Tests for iteration 5 new features: forgot password, owned opportunities, applicants,
status updates, portfolio upload/download."""
import io
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


BU = base_url()


# ---- Forgot password ----
def test_forgot_password_returns_200_never_crashes():
    r = requests.post(f"{BU}/api/auth/forgot", json={"email": "aarav@demo.com"}, timeout=30)
    assert r.status_code == 200
    body = r.json()
    assert "sent" in body
    if body["sent"]:
        assert body.get("email_id")
    else:
        assert "reason" in body and "reset_link" in body


# ---- Owned opportunities ----
def test_owned_opportunities_maya_has_7_plus():
    r = requests.get(f"{BU}/api/opportunities/mine/maya@demo.com", timeout=20)
    assert r.status_code == 200
    docs = r.json()
    assert isinstance(docs, list) and len(docs) >= 7
    for d in docs:
        assert "applicant_count" in d
        assert d["owner_email"] == "maya@demo.com"


# ---- Applicants (owner enforcement) ----
def test_applicants_wrong_owner_403():
    r = requests.get(
        f"{BU}/api/opportunities/frontend-intern/applicants",
        params={"owner_email": "someone@wrong.com"}, timeout=20,
    )
    assert r.status_code == 403


def test_applicants_owner_returns_array_with_expected_fields():
    # Ensure at least one application exists for frontend-intern
    email = f"TEST_{uuid.uuid4().hex}@example.com"
    requests.post(f"{BU}/api/users", json={"email": email, "name": "TEST Applicant", "skills": ["React"]}, timeout=20)
    requests.post(f"{BU}/api/applications", json={
        "email": email, "opportunity_id": "frontend-intern", "cover_letter": "TEST cover",
    }, timeout=20)
    r = requests.get(
        f"{BU}/api/opportunities/frontend-intern/applicants",
        params={"owner_email": "maya@demo.com"}, timeout=20,
    )
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list) and len(arr) >= 1
    ours = next((a for a in arr if a["email"] == email), None)
    assert ours is not None
    for key in ("applicant", "match_score", "status", "cover_letter", "applied_at"):
        assert key in ours
    assert isinstance(ours["match_score"], int)


# ---- PATCH status ----
def test_patch_status_updates_and_creates_notification_and_403_when_not_owner():
    email = f"TEST_{uuid.uuid4().hex}@example.com"
    requests.post(f"{BU}/api/users", json={"email": email, "name": "TEST N", "skills": ["React"]}, timeout=20)
    app_res = requests.post(f"{BU}/api/applications", json={
        "email": email, "opportunity_id": "frontend-intern", "cover_letter": "x",
    }, timeout=20).json()
    app_id = app_res["id"]

    # Non-owner
    r = requests.patch(
        f"{BU}/api/applications/{app_id}/status",
        json={"status": "Shortlisted", "owner_email": "not@owner.com"}, timeout=20,
    )
    assert r.status_code == 403

    # Owner
    r = requests.patch(
        f"{BU}/api/applications/{app_id}/status",
        json={"status": "Shortlisted", "owner_email": "maya@demo.com"}, timeout=20,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "Shortlisted"

    # Verify persistence via GET
    listed = requests.get(f"{BU}/api/applications/{email}", timeout=20).json()
    assert listed[0]["status"] == "Shortlisted"

    # Notification created
    notifs = requests.get(f"{BU}/api/notifications/{email}", timeout=20).json()
    assert any("Shortlisted" in n["message"] for n in notifs)


# ---- Portfolio upload ----
MIN_PDF = b"%PDF-1.4\n%TEST\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


def test_portfolio_upload_pdf_and_fetch():
    files = {"file": ("test.pdf", MIN_PDF, "application/pdf")}
    r = requests.post(
        f"{BU}/api/portfolio/upload",
        params={"email": "maya@demo.com"}, files=files, timeout=60,
    )
    if r.status_code == 503:
        # Object storage temporarily unavailable - report gracefully
        import pytest
        pytest.skip(f"Storage unavailable: {r.text}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["content_type"] == "application/pdf"
    assert body["portfolio_name"] == "test.pdf"
    assert body["portfolio_url"].startswith("/api/portfolio/file/")
    assert body["size"] >= len(MIN_PDF) - 5

    # Fetch back
    fetch = requests.get(f"{BU}{body['portfolio_url']}", timeout=60)
    assert fetch.status_code == 200
    assert fetch.headers.get("content-type", "").startswith("application/pdf")
    assert fetch.content.startswith(b"%PDF")


def test_portfolio_upload_rejects_bad_extension():
    files = {"file": ("bad.exe", b"MZ...", "application/octet-stream")}
    r = requests.post(
        f"{BU}/api/portfolio/upload",
        params={"email": "maya@demo.com"}, files=files, timeout=30,
    )
    assert r.status_code == 400


def test_portfolio_upload_rejects_oversize():
    big = b"%PDF-1.4\n" + b"0" * (10 * 1024 * 1024 + 10)
    files = {"file": ("big.pdf", big, "application/pdf")}
    r = requests.post(
        f"{BU}/api/portfolio/upload",
        params={"email": "maya@demo.com"}, files=files, timeout=90,
    )
    assert r.status_code == 413


# ---- Regression: existing endpoints ----
def test_regression_existing_endpoints():
    assert requests.get(f"{BU}/api/opportunities?email=aarav@demo.com", timeout=20).status_code == 200
    assert requests.get(f"{BU}/api/applications/aarav@demo.com", timeout=20).status_code == 200
    assert requests.get(f"{BU}/api/notifications/aarav@demo.com", timeout=20).status_code == 200
    assert requests.get(f"{BU}/api/saved/aarav@demo.com", timeout=20).status_code == 200
