"""ValueWeave backend regression tests.

Covers:
- Health
- Ideas list + filters + filters facets
- Idea detail + related + 404
- Auth gating (401)
- Auth flow with seeded MongoDB session (Bearer token)
- Save toggle + saved listing
- Logout
"""
import os
import time
import subprocess
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://library-visibility.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

MONGO_DB = os.environ.get("DB_NAME", "test_database")


# ----------------------------- Fixtures ----------------------------------
@pytest.fixture(scope="session")
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def seeded_session():
    """Seed user + session directly in MongoDB; return (user_id, token, email)."""
    ts = int(time.time() * 1000)
    user_id = f"test-user-{ts}"
    token = f"test_session_{ts}"
    email = f"qa.test+{ts}@valueweave.test"
    js = f"""
    use('{MONGO_DB}');
    db.users.insertOne({{
      user_id: '{user_id}',
      email: '{email}',
      name: 'QA Tester',
      picture: 'https://via.placeholder.com/150',
      created_at: new Date().toISOString()
    }});
    db.user_sessions.insertOne({{
      user_id: '{user_id}',
      session_token: '{token}',
      expires_at: new Date(Date.now() + 7*24*60*60*1000).toISOString(),
      created_at: new Date().toISOString()
    }});
    """
    r = subprocess.run(["mongosh", "--quiet", "--eval", js], capture_output=True, text=True, timeout=20)
    assert r.returncode == 0, f"mongosh seed failed: {r.stderr}"
    yield {"user_id": user_id, "token": token, "email": email}
    # cleanup
    cleanup = f"""
    use('{MONGO_DB}');
    db.users.deleteOne({{user_id:'{user_id}'}});
    db.user_sessions.deleteMany({{user_id:'{user_id}'}});
    db.idea_saves.deleteMany({{user_id:'{user_id}'}});
    """
    subprocess.run(["mongosh", "--quiet", "--eval", cleanup], capture_output=True, text=True, timeout=20)


@pytest.fixture(scope="session")
def auth_headers(seeded_session):
    return {"Authorization": f"Bearer {seeded_session['token']}"}


# ----------------------------- Health -------------------------------------
class TestHealth:
    def test_root(self, api_client):
        r = api_client.get(f"{API}/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["ideas_count"] == 29


# ----------------------------- Ideas list ---------------------------------
class TestIdeasList:
    def test_list_returns_29(self, api_client):
        r = api_client.get(f"{API}/ideas")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 29
        # Featured come first in default sort
        first_idx = next((i for i, x in enumerate(data) if not x["featured"]), len(data))
        for x in data[:first_idx]:
            assert x["featured"] is True

    def test_filter_featured_only(self, api_client):
        r = api_client.get(f"{API}/ideas", params={"featured_only": "true"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert all(x["featured"] for x in data)

    def test_filter_beginner_friendly(self, api_client):
        r = api_client.get(f"{API}/ideas", params={"beginner_friendly": "true"})
        assert r.status_code == 200
        data = r.json()
        assert all(x["beginner_friendly"] is True for x in data)
        # Should narrow vs total
        assert len(data) < 29

    def test_filter_search_q(self, api_client):
        r = api_client.get(f"{API}/ideas", params={"q": "soil"})
        assert r.status_code == 200
        data = r.json()
        slugs = [x["slug"] for x in data]
        assert "soil-testing-micro-lab" in slugs

    def test_filter_investment_bucket(self, api_client):
        r = api_client.get(f"{API}/ideas", params={"investment_bucket": "under_1l"})
        assert r.status_code == 200
        data = r.json()
        for x in data:
            assert x["minimum_investment"] < 100000

    def test_filter_sector_nonexistent_empty(self, api_client):
        r = api_client.get(f"{API}/ideas", params={"sector": "NonExistent"})
        assert r.status_code == 200
        assert r.json() == []

    def test_filter_execution_and_ideal_for(self, api_client):
        # Get a known sector and execution_type from filters endpoint
        f = api_client.get(f"{API}/ideas/filters").json()
        if f["sectors"]:
            sector = f["sectors"][0]
            r = api_client.get(f"{API}/ideas", params={"sector": sector})
            assert r.status_code == 200
            assert all(x["sector"].lower() == sector.lower() for x in r.json())
        if f["execution_types"]:
            et = f["execution_types"][0]
            r = api_client.get(f"{API}/ideas", params={"execution_type": et})
            assert r.status_code == 200
            assert all(x["execution_type"].lower() == et.lower() for x in r.json())
        if f["ideal_for"]:
            ideal = f["ideal_for"][0]
            r = api_client.get(f"{API}/ideas", params={"ideal_for": ideal})
            assert r.status_code == 200
            assert all(ideal in x["ideal_for"] for x in r.json())


# ----------------------------- Filters facets -----------------------------
class TestFiltersFacets:
    def test_filters_endpoint(self, api_client):
        r = api_client.get(f"{API}/ideas/filters")
        assert r.status_code == 200
        data = r.json()
        for key in ("sectors", "execution_types", "ideal_for", "investment_buckets"):
            assert key in data
            assert isinstance(data[key], list)
        keys = [b["key"] for b in data["investment_buckets"]]
        assert keys == ["under_1l", "1l_to_5l", "5l_to_15l", "above_15l"]


# ----------------------------- Idea detail --------------------------------
class TestIdeaDetail:
    @pytest.mark.parametrize("slug", ["soil-testing-micro-lab", "ai-automation-service"])
    def test_detail_full_schema(self, api_client, slug):
        r = api_client.get(f"{API}/ideas/{slug}")
        assert r.status_code == 200
        d = r.json()
        # Rich fields presence
        rich_fields = [
            "problem_solved", "target_customers", "ideal_for", "team_roles_needed",
            "eligible_government_schemes", "minimum_investment", "medium_scale_investment",
            "advanced_scale_investment", "skills_required", "suitable_district_types",
        ]
        for f in rich_fields:
            assert f in d, f"missing field {f}"
        assert d["slug"] == slug
        assert isinstance(d["ideal_for"], list)
        assert isinstance(d["team_roles_needed"], list)

    def test_detail_not_found(self, api_client):
        r = api_client.get(f"{API}/ideas/nonexistent")
        assert r.status_code == 404

    def test_related(self, api_client):
        r = api_client.get(f"{API}/ideas/soil-testing-micro-lab/related")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert all(x["slug"] != "soil-testing-micro-lab" for x in data)


# ----------------------------- Auth gating --------------------------------
class TestAuthGating:
    def test_saved_unauthenticated(self, api_client):
        r = api_client.get(f"{API}/ideas/saved")
        assert r.status_code == 401

    def test_save_unauthenticated(self, api_client):
        r = api_client.post(f"{API}/ideas/soil-testing-micro-lab/save")
        assert r.status_code == 401

    def test_me_unauthenticated(self, api_client):
        r = api_client.get(f"{API}/auth/me")
        assert r.status_code == 401


# ----------------------------- Auth flow ----------------------------------
class TestAuthFlow:
    def test_me_with_bearer(self, api_client, auth_headers, seeded_session):
        r = api_client.get(f"{API}/auth/me", headers=auth_headers)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["user_id"] == seeded_session["user_id"]
        assert data["email"] == seeded_session["email"]

    def test_save_toggle(self, api_client, auth_headers):
        # First save -> True
        r1 = api_client.post(f"{API}/ideas/soil-testing-micro-lab/save", headers=auth_headers)
        assert r1.status_code == 200, r1.text
        assert r1.json()["saved"] is True

        # Verify it shows in saved list
        r2 = api_client.get(f"{API}/ideas/saved", headers=auth_headers)
        assert r2.status_code == 200
        slugs = [x["slug"] for x in r2.json()]
        assert "soil-testing-micro-lab" in slugs

        # Toggle off
        r3 = api_client.post(f"{API}/ideas/soil-testing-micro-lab/save", headers=auth_headers)
        assert r3.status_code == 200
        assert r3.json()["saved"] is False

        r4 = api_client.get(f"{API}/ideas/saved", headers=auth_headers)
        assert "soil-testing-micro-lab" not in [x["slug"] for x in r4.json()]

    def test_save_invalid_slug(self, api_client, auth_headers):
        r = api_client.post(f"{API}/ideas/nonexistent/save", headers=auth_headers)
        assert r.status_code == 404


# ----------------------------- Logout -------------------------------------
class TestLogout:
    def test_logout_with_bearer_invalidates(self, api_client):
        # Seed fresh session for this test (don't pollute auth_headers session)
        ts = int(time.time() * 1000)
        user_id = f"test-user-logout-{ts}"
        token = f"test_logout_{ts}"
        js = f"""
        use('{MONGO_DB}');
        db.users.insertOne({{user_id:'{user_id}', email:'lo+{ts}@v.test', name:'L', created_at:new Date().toISOString()}});
        db.user_sessions.insertOne({{user_id:'{user_id}', session_token:'{token}', expires_at:new Date(Date.now()+7*24*60*60*1000).toISOString(), created_at:new Date().toISOString()}});
        """
        subprocess.run(["mongosh", "--quiet", "--eval", js], capture_output=True, text=True, timeout=20)

        h = {"Authorization": f"Bearer {token}"}
        # Confirm session works
        r1 = api_client.get(f"{API}/auth/me", headers=h)
        assert r1.status_code == 200

        # Logout
        r2 = api_client.post(f"{API}/auth/logout", headers=h)
        assert r2.status_code == 200
        assert r2.json().get("ok") is True

        # Should now be unauthenticated
        r3 = api_client.get(f"{API}/auth/me", headers=h)
        assert r3.status_code == 401

        # cleanup user
        subprocess.run(["mongosh", "--quiet", "--eval",
                        f"use('{MONGO_DB}'); db.users.deleteOne({{user_id:'{user_id}'}});"],
                       capture_output=True, text=True, timeout=20)
