import json
import sys

import requests


BASE = "https://ai-match-hub-10.preview.emergentagent.com"
EMAIL = "aarav.iteration6@example.com"


def main():
    response = requests.get(f"{BASE}/api/users/{EMAIL}", timeout=20)
    print(f"GET /api/users/{EMAIL} -> {response.status_code}")
    if response.status_code != 200:
        print(response.text)
        return 1
    user = response.json()
    safe = {k: user.get(k) for k in ["name", "email", "role", "goal", "college", "degree", "location", "skills", "interests"]}
    print(json.dumps(safe, indent=2, sort_keys=True))
    assert user["name"] == "Aarav Iteration Six"
    assert user["email"] == EMAIL
    assert user["role"] == "student"
    assert user["goal"] == "AI Product Engineer"
    assert "GraphQL" in user.get("skills", [])
    assert "Open Source" in user.get("interests", [])
    return 0


if __name__ == "__main__":
    sys.exit(main())